# coding: utf-8

import os
import sys
import warnings
from datetime import datetime
from multiprocessing import JoinableQueue
from multiprocessing import Process
from multiprocessing import Value
from queue import Empty

import pymysql as mysql
import ujson as json
from pymysql import Warning

warnings.filterwarnings('ignore', category=Warning)

QUEUE_SIZE = 30000
MYSQL_SIZE = 500

TAG_STOP = 0
TAG_NEIGH = 1
TAG_COORD = 2
TAG_TO_CITY = 3

PASSWORD = '8031'


def preprocess_worker(queue_line, queue_mysql, count_coord, count_neigh, stop_flag):
    while True:
        try:
            line = queue_line.get(timeout=1)
        except Empty:
            if stop_flag.value == 1:
                break
            else:
                continue

        try:
            t = json.loads(line.strip().rstrip(','))['doc']
        except ValueError:
            queue_line.task_done()
            continue

        if t['coordinates'] is not None:
            count_coord.value += 1
            tid = int(t['id_str'])
            user_id = t['user']['id']
            text = t['text']
            longitude = t['coordinates']['coordinates'][0]
            latitude = t['coordinates']['coordinates'][1]
            lang = t['lang']
            created_at = datetime.strptime(t['created_at'], '%a %b %d %H:%M:%S %z %Y')
            weekday = created_at.weekday()

            if lang is None or len(lang) > 2:
                lang = '--'

            queue_mysql.put((TAG_COORD, (tid, user_id, text, longitude, latitude, lang, created_at, weekday)))

        elif t['place'] is not None and t['place']['place_type'] == 'neighborhood':
            count_neigh.value += 1

            tid = int(t['id_str'])
            user_id = t['user']['id']
            text = t['text']
            neighborhood = t['place']['full_name']
            lang = t['lang']
            created_at = datetime.strptime(t['created_at'], '%a %b %d %H:%M:%S %z %Y')
            weekday = created_at.weekday()

            if lang is None or len(lang) > 2:
                lang = '--'

            queue_mysql.put((TAG_NEIGH, (tid, user_id, text, neighborhood, lang, created_at, weekday)))

        queue_line.task_done()


def preprocess(queue_mysql, city, year):
    filename = 'data/%s-%s.json' % (city, year)
    print('---------- ' * 3)
    print('Processing: %s' % filename)

    count_all = 0
    stop_flag = Value('i', 0)
    count_coord = Value('i', 0)
    count_neigh = Value('i', 0)

    queue_line = JoinableQueue(QUEUE_SIZE)
    worker = Process(
        target=preprocess_worker,
        args=(queue_line, queue_mysql, count_coord, count_neigh, stop_flag))
    worker.start()

    # Loading loop
    fp = open(filename, 'r')
    for line in fp:
        count_all += 1
        queue_line.put(line)

    queue_line.join()
    stop_flag.value = 1
    worker.join()

    if count_all > 0:
        count_coord = count_coord.value
        ratio_coord = 100.0 * count_coord / count_all
        count_neigh = count_neigh.value
        ratio_neigh = 100.0 * count_neigh / count_all
        count_discard = count_all - count_coord - count_neigh
        ratio_discard = 100.0 * count_discard / count_all
        print('Line count: %d' % count_all)
        print('With coordinates: %d (%.3f%%)' % (count_coord, ratio_coord))
        print('With neighbours: %d (%.3f%%)' % (count_neigh, ratio_neigh))
        print('Discarded: %d (%.3f%%)' % (count_discard, ratio_discard))
    else:
        print('No Lines found!')


def mysql_worker(queue_mysql):
    conn = mysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password=PASSWORD,
        charset='utf8mb4',
        db='twitter')

    c = conn.cursor()
    sql_coord = None
    sql_neigh = None
    data_coord = []
    data_neigh = []

    while True:
        tag, data = queue_mysql.get()
        queue_mysql.task_done()
        if tag == TAG_STOP:
            if data_neigh:
                c.executemany(sql_neigh, data_neigh)
            if data_coord:
                c.executemany(sql_coord, data_coord)
            conn.commit()
            break
        if tag == TAG_NEIGH:
            data_neigh.append(data)
            if sql_neigh and len(data_neigh) > MYSQL_SIZE:
                c.executemany(sql_neigh, data_neigh)
                data_neigh = []
                conn.commit()
        if tag == TAG_COORD:
            data_coord.append(data)
            if sql_coord and len(data_coord) > MYSQL_SIZE:
                c.executemany(sql_coord, data_coord)
                data_coord = []
                conn.commit()
        if tag == TAG_TO_CITY:
            if data_neigh:
                c.executemany(sql_neigh, data_neigh)
            if data_coord:
                c.executemany(sql_coord, data_coord)
            data_neigh = []
            data_coord = []
            conn.commit()

            sql_coord = """
                        INSERT IGNORE INTO `twitter`.`original_%s_coordinate`
                        (`id`, `user_id`, `text`, `longitude`, `latitude`, `lang`, `created_at`, `weekday`) 
                        VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s)
                    """ % data
            sql_neigh = """
                        INSERT IGNORE INTO `twitter`.`original_%s_neighborhood`
                        (`id`, `user_id`, `text`, `neighborhood`, `lang`, `created_at`, `weekday`) 
                        VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s)
                """ % data


def main(city):
    start = datetime.now()

    print('Starts at: %s' % str(start)[:-7])

    queue_mysql = JoinableQueue(maxsize=QUEUE_SIZE)
    process_mysql = Process(target=mysql_worker, args=(queue_mysql,))
    process_mysql.start()

    print('Main process PID: %s' % os.getpid())
    print('MySQL worker PID: %s' % process_mysql.pid)

    # cities = ['melbourne', 'sydney', 'perth', 'brisbane', 'adelaide', 'canberra', 'hobart']
    years = ['2014', '2015', '2016', '2017', '2018']

    # for city in cities:
    queue_mysql.put((TAG_TO_CITY, city))
    for year in years:
        filename = 'data/%s-%s.json' % (city, year)
        if os.path.isfile(filename):
            preprocess(queue_mysql, city, year)

    print('---------- ' * 3)
    print('Wait MySQL process exit...')
    queue_mysql.put((TAG_STOP, None))
    queue_mysql.join()
    process_mysql.join()

    end = datetime.now()
    print('Ends at: %s' % str(end)[:-7])
    print('Total: %.3f seconds' % (end - start).total_seconds())


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please input the city!')
    else:
        main(sys.argv[1])
