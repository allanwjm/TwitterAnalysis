import pymysql
import nltk
from tqdm import tqdm

stopwordsList = set(nltk.corpus.stopwords.words('english'))
lemmatizer = nltk.WordNetLemmatizer()
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='toor', db='twitter', charset='utf8')
cursor = conn.cursor()
cursor.execute("set names utf8");

sql = """select * from original_perth_coordinate where processed_text is null"""
cursor.execute(sql)
result = cursor.fetchall()

for item in tqdm(result):
	new_Tokens = []
	tokens = nltk.word_tokenize(item[2])
	for token in tokens:
		token = token.lower()
		if token.isalpha() and 'http' not in token and 'https' not in token and len(token) >= 3 and token not in stopwordsList:
			new_Tokens.append(lemmatizer.lemmatize(lemmatizer.lemmatize(token, pos = 'v')))
	sentence = ' '.join(new_Tokens)
	sql = """update original_perth_coordinate set processed_text = '""" + sentence + """' where id = """ + str(item[0])
	try:
		cursor.execute(sql)
		conn.commit()
	except:
		conn.rollback()
conn.close()
