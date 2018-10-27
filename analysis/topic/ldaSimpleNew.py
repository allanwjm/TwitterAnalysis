import json, nltk
import pymysql
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pyLDAvis
import pyLDAvis.sklearn
# f = open('Arncliffe-sydney-3-2016.txt', 'r')
def runTest(*args):
    print(args)
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='toor', db='twitter', charset='utf8')
    cursor = conn.cursor()
    cursor.execute("set names utf8");

    try:
        n_features = 1000
        tf_vectorizer = CountVectorizer(max_features=n_features,
                                        stop_words='english')
#        sql = """select t.* from (select processed_text, sa2_code as suburb from original_adelaide_coordinate where lang = 'en' and weekday = """ + args[0] + """ and created_at between '2014-01-01 00:00:00' and '2014-12-31 23:59:59' and sa2_code = '402041047') as t order by suburb"""
        if args[0] != '':
            sql = """select t.* from (select processed_text, sa2_code as suburb from original_""" + args[6] + """_coordinate where lang = 'en' and weekday = """ + args[0] + """ and created_at between '""" + args[1] + """ """ + args[2] + """' and '""" + args[3] + """ """ + args[4] + """' and sa2_code = '""" + args[5] + """') as t order by suburb"""
        else:
            sql = """select t.* from (select processed_text, sa2_code as suburb from original_""" + args[6] + """_coordinate where lang = 'en' and created_at between '""" + args[1] + """ """ + args[2] + """' and '""" + args[3] + """ """ + args[4] + """' and sa2_code = '""" + args[5] + """') as t order by suburb"""
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

        n_topics = int(args[7])
        print(n_topics)
        lda = LatentDirichletAllocation(n_topics=n_topics, max_iter=50,
                                        learning_method='online',
                                        learning_offset=50.,
                                        random_state=0)

        lda.fit(tf)

        def print_top_words(model, feature_names, n_top_words):
            temp = {}
            for topic_idx, topic in enumerate(model.components_):
                key = "Topic %d:" % topic_idx
                value = " ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])
                temp[key] = value
            return temp
        n_top_words = int(args[8])
        print(n_top_words)
        tf_feature_names = tf_vectorizer.get_feature_names()
#        data = pyLDAvis.sklearn.prepare(lda, tf, tf_vectorizer)
#        pyLDAvis.show(data)
        return print_top_words(lda, tf_feature_names, n_top_words)
    # f.close()
    except:
        print('Please try another place')

    conn.close()


