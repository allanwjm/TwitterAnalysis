import math
from operator import itemgetter
import csv
from dataloader import mysql_connect
from dataloader import sa2_shapes
import io


def get_sentiment(city, years, months, weekdays):
    shapes = sa2_shapes(city)
    city_letter = city[0].lower()
    conn = mysql_connect()
    c = conn.cursor()
    sql = """
            SELECT 
                sa2_code,
                COUNT(*),
                AVG(compound) 
            FROM `sentiment`
            WHERE
                `city` = %%s AND
                `year` IN (%s) AND
                `month` IN (%s) AND
                `weekday` IN (%s)
            GROUP BY sa2_code;
        """ % (
        ', '.join(['%s'] * len(years)),
        ', '.join(['%s'] * len(months)),
        ', '.join(['%s'] * len(weekdays)),
    )
    c.execute(sql, [city_letter] + years + months + weekdays)
    result = c.fetchall()
    c.close()
    conn.close()

    data = {}
    data['areas'] = []
    score_min = 999
    score_max = -999
    score_sum = 0.0
    data_count = 0
    sa2_set = set()
    for sa2_code, count, score in result:
        if sa2_code in shapes.keys():
            if score < score_min:
                score_min = score
            if score > score_max:
                score_max = score
            score_sum += count * score
            data_count += count
            sa2_set.add(sa2_code)
            data['areas'].append({
                'sa2Code': sa2_code,
                'sa2Name': shapes[sa2_code]['sa2_name'],
                'count': count,
                'score': score,
                'top': shapes[sa2_code]['top'],
                'bottom': shapes[sa2_code]['bottom'],
                'left': shapes[sa2_code]['left'],
                'right': shapes[sa2_code]['right'],
                'polygons': shapes[sa2_code]['polygons']})
    data['scoreMax'] = score_max
    data['scoreMin'] = score_min
    data['scoreAvg'] = score_sum / data_count
    data['dataCount'] = data_count

    data['areas'].sort(key=itemgetter('score'))
    for i, area in enumerate(data['areas']):
        area['step'] = int(math.floor(10.0 * i / len(data['areas'])))

    # Append areas without data
    for sa2_code in shapes.keys():
        if sa2_code not in sa2_set:
            data['areas'].append({
                'sa2Code': sa2_code,
                'sa2Name': shapes[sa2_code]['sa2_name'],
                'count': 0,
                'score': 0,
                'top': shapes[sa2_code]['top'],
                'bottom': shapes[sa2_code]['bottom'],
                'left': shapes[sa2_code]['left'],
                'right': shapes[sa2_code]['right'],
                'polygons': shapes[sa2_code]['polygons']})

    return data


def get_sentiment_csv(city, years, months, weekdays):
    city_letter = city[0].lower()
    shapes = sa2_shapes(city)
    conn = mysql_connect()
    c = conn.cursor()
    sql = """
            SELECT 
                sa2_code,
                COUNT(*),
                AVG(pos),
                AVG(neu),
                AVG(neg),
                AVG(compound) 
            FROM `sentiment`
            WHERE
                `city` = %%s AND
                `year` IN (%s) AND
                `month` IN (%s) AND
                `weekday` IN (%s)
            GROUP BY sa2_code;
        """ % (
        ', '.join(['%s'] * len(years)),
        ', '.join(['%s'] * len(months)),
        ', '.join(['%s'] * len(weekdays)),
    )
    c.execute(sql, [city_letter] + years + months + weekdays)
    result = c.fetchall()
    c.close()
    conn.close()

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, ['sa2_code', 'sa2_name', 'count', 'pos', 'neu', 'neg', 'compound'])
    writer.writeheader()

    for sa2, count, pos, neu, neg, comp in result:
        writer.writerow({
            'sa2_code': sa2,
            'sa2_name': shapes[sa2]['sa2_name'],
            'count': count,
            'pos': pos,
            'neu': neu,
            'neg': neg,
            'compound': comp,
        })

    buffer.flush()
    buffer.seek(0)
    return buffer.read()
