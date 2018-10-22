import multiprocessing

import MySQLdb.cursors
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

HOST = 'localhost'
USER = 'root'
PASSWD = 'toor'
DB = 'twitter'
PORT = 3306


def process_table(table):
    sql_select = 'SELECT `id`, `text` FROM `%s` WHERE `lang` = "en";' % table
    conn_select = MySQLdb.connect(
        host=HOST, user=USER, passwd=PASSWD, db=DB, port=PORT, charset='utf8mb4',
        cursorclass=MySQLdb.cursors.SSCursor)
    c_select = conn_select.cursor()

    sql_update = 'UPDATE `twitter`.`%s` SET `vader_pos`=%%s, `vader_neu`=%%s, `vader_neg`=%%s, `vader_compound`=%%s WHERE `id`=%%s;' % table
    conn_update = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, port=PORT, charset='utf8mb4')
    c_update = conn_update.cursor()

    analyzer = SentimentIntensityAnalyzer()
    try:
        c_select.execute(sql_select)
        while True:
            rows = c_select.fetchmany(5000)

            if len(rows) <= 0:
                break

            values = []
            for tid, text in rows:
                scores = analyzer.polarity_scores(text)
                values.append((
                    scores['pos'],
                    scores['neu'],
                    scores['neg'],
                    scores['compound'],
                    tid))

            c_update.executemany(sql_update, values)
            conn_update.commit()

        return None
    except KeyboardInterrupt:
        return None
    finally:
        c_update.close()
        conn_update.close()
        c_select.close()
        conn_select.close()
        print('Finish: %s' % table)


def main():
    tables = [
        'original_adelaide_coordinate',
        'original_adelaide_neighborhood',
        'original_brisbane_coordinate',
        'original_brisbane_neighborhood',
        'original_canberra_coordinate',
        'original_canberra_neighborhood',
        'original_hobart_coordinate',
        'original_hobart_neighborhood',
        'original_melbourne_coordinate',
        'original_melbourne_neighborhood',
        'original_perth_coordinate',
        'original_perth_neighborhood',
        'original_sydney_coordinate',
        'original_sydney_neighborhood',
    ]

    pool = multiprocessing.Pool(len(tables))
    try:
        pool.map(process_table, tables)
    except KeyboardInterrupt:
        print('KeyboardInterrupt!')


if __name__ == '__main__':
    main()
