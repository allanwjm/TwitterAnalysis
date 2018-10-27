#!/usr/bin/python
# -*- coding: utf-8 -*-

import json, sys, re
# reload(sys)
# sys.setdefaultencoding('UTF8')

try:
	f = open(sys.argv[1] + "-" + sys.argv[2] + "-" + sys.argv[3] + ".json", "r")
	test = json.load(f)
	for item in test.items():
		if ',' in item[0]:
			o = open(re.match('(.*),', item[0]).group(1) + "-" + sys.argv[2] + "-" + sys.argv[3] + "-" + sys.argv[1] + ".txt", "w")
		else:
			o = open(re.match('(.*)', item[0]).group(1) + "-" + sys.argv[2] + "-" + sys.argv[3] + "-" + sys.argv[1] + ".txt", "w")
		for string in item[1]:
			o.write(string)
		o.close()
	f.close()
except:
	pass