import os
import pickle

import pymysql

base_path = os.path.split(os.path.realpath(__file__))[0]

_sa1_data = None
_sa2_data = None


def sa1_data():
    global _sa1_data
    if _sa1_data is None:
        _sa1_data = pickle.load(open(os.path.join(base_path, 'cache', 'sa1.pkl'), 'rb'))
    return _sa1_data


def sa2_data():
    global _sa2_data
    if _sa2_data is None:
        _sa2_data = pickle.load(open(os.path.join(base_path, 'cache', 'sa2.pkl'), 'rb'))
    return _sa2_data


def mysql_connect():
    return pymysql.connect(
        host='localhost',
        user='root',
        passwd='toor',
        db='twitter',
        port=3309,
        charset='utf8mb4')


def mysql_connect_sscursor():
    return pymysql.connect(
        host='localhost',
        user='root',
        passwd='toor',
        db='twitter',
        port=3309,
        charset='utf8mb4')
