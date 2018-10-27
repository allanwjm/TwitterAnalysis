#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymysql
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
f = open(sys.argv[1] + '-' + sys.argv[2] + '-' + sys.argv[3] + '.json', 'w')

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='toor', db='twitter', charset='utf8')
cursor = conn.cursor()
cursor.execute("set names utf8");

sql = """select t.* from (select t1.processed_text, t1.sa2_name as suburb from original_""" + sys.argv[2] + """_coordinate as t1 where sa2_name is not null and lang = 'en' and weekday = """ + sys.argv[3] + """ and created_at between '""" + sys.argv[1] + """-01-01' and '""" + sys.argv[1] + """-12-31' union select t2.processed_text, t2.neighborhood as suburb from original_""" + sys.argv[2] + """_neighborhood as t2 where lang = 'en' and weekday = """ + sys.argv[3] + """ and created_at between '""" + sys.argv[1] + """-01-01' and '""" + sys.argv[1] + """-12-31') as t order by suburb"""
cursor.execute(sql)
result = cursor.fetchall()

dic = dict()
for item in result:
	dic.setdefault(item[1], []).append(item[0])

json.dump(dic, f)

conn.close()
f.close()


