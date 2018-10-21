import pymysql as mysql

conn = mysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='8031',
    charset='utf8mb4',
    db='twitter')

c = conn.cursor()

for city in ['melbourne', 'sydney', 'perth', 'brisbane', 'adelaide', 'canberra', 'hobart']:
    table = 'original_%s_coordinate' % city
    c.execute("""
    CREATE TABLE IF NOT EXISTS `twitter`.`%s` (
      `id` BIGINT UNSIGNED NOT NULL,
      `user_id` BIGINT UNSIGNED NULL,
      `text` VARCHAR(255) NULL,
      `longitude` FLOAT NULL,
      `latitude` FLOAT NULL,
      `lang` CHAR(2) NULL,
      `created_at` DATETIME NULL,
      `weekday` TINYINT UNSIGNED NULL,

      PRIMARY KEY (`id`),      
      INDEX (`longitude` ASC),
      INDEX (`latitude` ASC),
      INDEX (`lang` ASC),
      INDEX (`created_at` ASC),
      INDEX (`weekday` ASC))
    """ % table)
    print('Created table: %s' % table)

    table = 'original_%s_neighborhood' % city
    c.execute("""
        CREATE TABLE IF NOT EXISTS `twitter`.`%s` (
          `id` BIGINT UNSIGNED NOT NULL,
          `user_id` BIGINT UNSIGNED NULL,
          `text` VARCHAR(255) NULL,
          `neighborhood` VARCHAR(255) NULL,
          `lang` CHAR(2) NULL,
          `created_at` DATETIME NULL,
          `weekday` TINYINT UNSIGNED NULL,

          PRIMARY KEY (`id`),      
          INDEX (`neighborhood` ASC),
          INDEX (`lang` ASC),
          INDEX (`created_at` ASC),
          INDEX (`weekday` ASC))
        """ % table)
    print('Created table: %s' % table)

    conn.commit()
