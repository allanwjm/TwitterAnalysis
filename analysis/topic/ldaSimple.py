import json, nltk
import pymysql
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
# f = open('Arncliffe-sydney-3-2016.txt', 'r')

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='toor', db='twitter', charset='utf8')
cursor = conn.cursor()
cursor.execute("set names utf8");

try:
    n_features = 1000
    tf_vectorizer = CountVectorizer(max_features=n_features,
                                    stop_words='english')
    sql = """select t.* from (select processed_text, sa2_code as suburb from original_adelaide_coordinate where lang = 'en' and weekday = 0 and created_at between '2014-01-01 00:00:00' and '2014-12-31 23:59:59' and sa1_code = '40204104743') as t order by suburb"""
    cursor.execute(sql)
    result = cursor.fetchall()
    text = []
    for item in result:
    	text.append(item[0])
    try:
    	cursor.execute(sql)
    	conn.commit()
    except:
    	conn.rollback()

    tf = tf_vectorizer.fit_transform(text)
    # tf = tf_vectorizer.fit_transform([f.read()])

    n_topics = 5
    lda = LatentDirichletAllocation(n_topics=n_topics, max_iter=50,
                                    learning_method='online',
                                    learning_offset=50.,
                                    random_state=0)

    lda.fit(tf)

    def print_top_words(model, feature_names, n_top_words):
        for topic_idx, topic in enumerate(model.components_):
            print("Topic %d:" % topic_idx)
            print(" ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]))

    n_top_words = 5

    tf_feature_names = tf_vectorizer.get_feature_names()
    print_top_words(lda, tf_feature_names, n_top_words)
# f.close()
except:
    print('Please try another place')

conn.close()


