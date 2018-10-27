#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymysql
import re
import json
import sys
import math
import io
from tqdm import tqdm

def euclideanDistance(pt1, pt2):
	x1, y1 = pt1
	x2, y2 = pt2
	return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
f = open('sydney.json', 'r')
jsonFile = json.load(f)

polygons = []
for outerItem in jsonFile['features']:
	# polygon = []
	polygon_dict = {}
	x = y = 0.0
	outerLen = len(outerItem['geometry']['coordinates'][0][0])
	for innerItem in outerItem['geometry']['coordinates'][0][0]:
		x += innerItem[1]
		y += innerItem[0]
		# polygon.append([innerItem[1], innerItem[0]])
	x /= outerLen
	y /= outerLen
	polygon_dict['polygon'] = [x, y]
	polygon_dict['properties'] = outerItem['properties']
	polygons.append(polygon_dict)

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='toor', db='twitter', charset='utf8')
cursor = conn.cursor()
cursor.execute("set names utf8");

sql = """select * from original_sydney_coordinate"""
cursor.execute(sql)
result = cursor.fetchall()

for item in tqdm(result):
	minDistance = 99999.0
	resultDict = {}
	for poly in polygons:
		distance = euclideanDistance([item[4], item[3]], poly['polygon'])
		if distance < minDistance:
			minDistance = distance
			resultDict = poly['properties']

	matchObj = re.match(r'(.*?) [-(]', str(resultDict['sa2_name_2016']))

	if matchObj:
		sa2Name = matchObj.group(1)
	else:
		sa2Name = str(resultDict['sa2_name_2016'])

	if sa2Name != 'Sydney':
		sql = """update original_sydney_coordinate set sa1_code = '""" + str(resultDict['sa1_maincode_2016']) + """', sa2_code = '""" + str(resultDict['sa2_maincode_2016']) + """', sa2_name = '""" + sa2Name + """, Sydney' where id = """ + str(item[0])
	else:
		sql = """update original_sydney_coordinate set sa1_code = '""" + str(resultDict['sa1_maincode_2016']) + """', sa2_code = '""" + str(resultDict['sa2_maincode_2016']) + """', sa2_name = '""" + sa2Name + """, New South Wales' where id = """ + str(item[0])
	try:
		cursor.execute(sql)
		conn.commit()
	except:
		conn.rollback()
conn.close()
f.close()



