from dataloader import mysql_connect
from dataloader import sa2_shapes


def get_sentiment(city, years, weekdays):
    shapes = sa2_shapes(city)
    conn = mysql_connect()
    c = conn.cursor()
    table = 'twitter.original_%s_coordinate' % city
    sql = """
        SELECT 
            sa2_code,
            COUNT(*),
            AVG(vader_compound) 
        FROM %s 
        WHERE
            `lang` = "en" AND 
            `weekday` IN (%s)
        GROUP BY sa2_code;
    """ % (table, ', '.join(['%s'] * len(weekdays)))
    c.execute(sql, weekdays)
    result = c.fetchall()

    data = {}
    data['areas'] = []
    score_min = 999
    score_max = -999
    sa2_set = set()
    for sa2_code, count, score in result:
        if sa2_code in shapes.keys():
            if score < score_min:
                score_min = score
            if score > score_max:
                score_max = score
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
