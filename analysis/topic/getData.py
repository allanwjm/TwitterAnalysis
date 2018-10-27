import sys
import io
import pymysql
from tqdm import tqdm

f = open('testData.txt', 'a', encoding = 'utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='toor', db='twitter', charset='utf8')
cursor = conn.cursor()
cursor.execute("set names utf8");

sql = """select processed_text from original_hobart_coordinate where processed_text != ''"""
cursor.execute(sql)
result = cursor.fetchall()

for item in tqdm(result):
	f.write(item[0])

