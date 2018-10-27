#! /usr/bin/python
# -*- coding: utf-8 -*-
from pyspark.sql import SQLContext, Row, SparkSession
from pyspark.ml.feature import CountVectorizer
from pyspark.mllib.clustering import LDA, LDAModel
from pyspark.mllib.linalg import Vector, Vectors
from pyspark import *

#import os
#import sys
#import io
#os.environ["PYSPARK_PYTHON"]="/usr/bin/python2"
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path = "Adelaide Airport-adelaide-0-2016.txt"
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
f = open('test.txt', 'w')
for topic in range(len(topics_final)):
    f.write("Topic" + str(topic) + ":\n")
    for term in topics_final[topic]:
		f.write(term + "\n")
f.close()
