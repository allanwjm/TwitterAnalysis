#! /usr/bin/python
# -*- coding: utf-8 -*-
from pyspark.sql import SQLContext, Row, SparkSession
from pyspark.ml.feature import CountVectorizer
from pyspark.mllib.clustering import LDA, LDAModel
from pyspark.mllib.linalg import Vector, Vectors
from pyspark import *
import pymysql
import sys, re

#import os
#import sys
#import io
#os.environ["PYSPARK_PYTHON"]="/usr/bin/python2"
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='toor', db='twitter', charset='utf8')
cursor = conn.cursor()
cursor.execute("set names utf8");
path = sys.argv[1]
sc = SparkContext()
spark = SparkSession.builder.appName("Python Spark SQL basic example").config("spark.some.config.option", "some-value").getOrCreate()
data = sc.textFile(path).zipWithIndex().map(lambda (words,idd): Row(idd= idd, words = words.split(" ")))
docDF = spark.createDataFrame(data)
Vector = CountVectorizer(inputCol="words", outputCol="vectors")
model = Vector.fit(docDF)
result = model.transform(docDF)

corpus = result.select("idd", "vectors").rdd.map(lambda (x,y): [x,Vectors.fromML(y)]).cache()
# Cluster the documents into three topics using LDA
ldaModel = LDA.train(corpus, k=5,maxIterations=100,optimizer='online')
topics = ldaModel.topicsMatrix()
vocabArray = model.vocabulary

wordNumbers = 5  # number of words per topic
topicIndices = sc.parallelize(ldaModel.describeTopics(maxTermsPerTopic = wordNumbers))

def topic_render(topic):  # specify vector id of words to actual words
    terms = topic[0]
    result = []
    for i in range(wordNumbers):
        term = vocabArray[terms[i]]
        result.append(term)
    return result

topics_final = topicIndices.map(lambda topic: topic_render(topic)).collect()
pathSplit = re.split('[-.]', path)
topicString = ''
# f = open('test.txt', 'w')
for topic in range(len(topics_final)):
    # f.write("Topic" + str(topic) + ":\n")
    topicString += '\nTopic' + str(topic) + '\n'
    for term in topics_final[topic]:
		# f.write(term + "\n")
		topicString += term + '\n'
sql = """INSERT INTO """ + pathSplit[1] + """(topic, suburb, year, day) VALUES ('""" + topicString + """', '""" + pathSplit[0] + """', '""" + pathSplit[3] + """', '""" + pathSplit[2] + """')"""
try:
	cursor.execute(sql)
	conn.commit()
except:
	conn.rollback()
conn.close()
# f.close()


