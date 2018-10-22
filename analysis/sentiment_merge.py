import MySQLdb
import dataloader

conn_write = MySQLdb.connect(
    host='127.0.0.1', user='root', passwd='toor',
    db='twitter', port=3309, charset='utf8mb4')
c_write = conn_write.cursor()

for table, shapes in [
    ('original_adelaide_coordinate', dataloader.sa2_shapes('adelaide')),
    ('original_brisbane_coordinate', dataloader.sa2_shapes('brisbane')),
    ('original_canberra_coordinate', dataloader.sa2_shapes('canberra')),
    ('original_hobart_coordinate', dataloader.sa2_shapes('hobart')),
    ('original_melbourne_coordinate', dataloader.sa2_shapes('melbourne')),
    ('original_perth_coordinate', dataloader.sa2_shapes('perth')),
    ('original_sydney_coordinate', dataloader.sa2_shapes('sydney')),
]:
    print(table)
    city = table[9]

    conn_read = MySQLdb.connect(
        host='127.0.0.1', user='root', passwd='toor',
        db='twitter', port=3309, charset='utf8mb4',
        cursorclass=MySQLdb.cursors.SSCursor)
    c_read = conn_read.cursor()

    c_read.execute("""
        SELECT
            `created_at`,
            `sa1_code`,
            `sa2_code`,
            `vader_pos`,
            `vader_neu`,
            `vader_neg`,
            `vader_compound`
        FROM `%s`
        WHERE `lang` = 'en';
    """ % table)

    while True:
        rows = c_read.fetchmany(10000)
        if len(rows) == 0:
            break

        data = []
        for created_at, sa1, sa2, pos, neu, neg, comp in rows:
            if sa2 in shapes:
                data.append((
                    city, sa1, sa2,
                    created_at.year,
                    created_at.month,
                    created_at.weekday(),
                    created_at.hour,
                    pos, neu, neg, comp,
                ))

        c_write.executemany("""
            INSERT INTO `sentiment` (
                 `city`, `sa1_code`, `sa2_code`,
                 `year`, `month`, `weekday`, `hour`,
                 `pos`, `neu`, `neg`, `compound`
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s
            );
        """, data)
        conn_write.commit()

    c_read.close()
    conn_read.close()

c_write.close()
conn_write.close()
