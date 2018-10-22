import gzip
import os
import pickle

import MySQLdb
from DBUtils.PooledDB import PooledDB

base_path = os.path.split(os.path.realpath(__file__))[0]

_sa1_data = {}
_sa2_data = {}
_pool = None


def sa1_shapes(city):
    if city not in _sa1_data:
        filepath = os.path.join(base_path, 'shapefile', '%s-sa1.pkl.gz' % city)
        _sa1_data[city] = pickle.load(gzip.open(filepath, 'rb'))
    return _sa1_data[city]


def sa2_shapes(city):
    if city not in _sa2_data:
        filepath = os.path.join(base_path, 'shapefile', '%s-sa2.pkl.gz' % city)
        _sa2_data[city] = pickle.load(gzip.open(filepath, 'rb'))
    return _sa2_data[city]


def mysql_connect():
    global _pool
    if _pool is None:
        _pool = PooledDB(
            MySQLdb, 5,
            host='127.0.0.1',
            user='root',
            passwd='toor',
            db='twitter',
            port=3306,
            charset='utf8mb4')
    return _pool.connection()
