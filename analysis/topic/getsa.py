#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymysql
import sys 
import io
import json
import matplotlib.path as mplPath
from tqdm import tqdm
import re

# def isInsidePolygon(pt, poly):
#     flag = False
#     i = -1
#     l = len(poly)
#     j = l - 1
#     while i < l - 1:
#         i += 1
#         print(i, poly[i], j, poly[j])
#         if ((poly[i]["lat"] <= pt["lat"] and pt["lat"] < poly[j]["lat"]) or (poly[j]["lat"] <= pt["lat"] and pt["lat"] < poly[i]["lat"])):
#             if (pt["lng"] < (poly[j]["lng"] - poly[i]["lng"]) * (pt["lat"] - poly[i]["lat"]) / (poly[j]["lat"] - poly[i]["lat"]) + poly[i]["lng"]):
#                 flag = not flag
#         j = i
#     return flag

def isInsidePolygon(pt, poly):
	return mplPath.Path(poly).contains_point(pt)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
f = open('perth.json', 'r')
jsonFile = json.load(f)
polygons = []
for outerItem in jsonFile['features']:
	polygon = []
	polygon_dict = {}
	for innerItem in outerItem['geometry']['coordinates'][0][0]:
		polygon.append([innerItem[1], innerItem[0]])
	polygon_dict['polygon'] = polygon
	polygon_dict['properties'] = outerItem['properties']
	polygons.append(polygon_dict)

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='toor', db='twitter', charset='utf8')
cursor = conn.cursor()
cursor.execute("set names utf8");

sql = """select * from original_perth_coordinate"""
cursor.execute(sql)
result = cursor.fetchall()

for item in tqdm(result):
    for poly in polygons:
    	if isInsidePolygon([item[4], item[3]], poly['polygon']):
    		matchObj = re.match(r'(.*?) [-(]', str(poly['properties']['sa2_name_2016']))
    		if matchObj:
    			sa2Name = matchObj.group(1)
    		else:
    			sa2Name = str(poly['properties']['sa2_name_2016'])

    		# if str(poly['properties']['sa2_name_2016']) != 'canberra':
    		sql = """update original_perth_coordinate set sa1_code = '""" + str(poly['properties']['sa1_maincode_2016']) + """', sa2_code = '""" + str(poly['properties']['sa2_maincode_2016']) + """', sa2_name = '""" + sa2Name + """, Perth (WA)' where id = """ + str(item[0])
    		# else:
    		# 	sql = """update original_canberra_coordinate set sa1_code = '""" + str(poly['properties']['sa1_maincode_2016']) + """', sa2_code = '""" + str(poly['properties']['sa2_maincode_2016']) + """', sa2_name = '""" + sa2Name + """, Brisbane' where id = """ + str(item[0])
    		try:
    			cursor.execute(sql)
    			conn.commit()
    		except:
    			conn.rollback()
conn.close()
f.close()


