CREATE TABLE `sentiment` (
  `id`       bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `city`     char(1)                      DEFAULT NULL,
  `sa1_code` char(11)                     DEFAULT NULL,
  `sa2_code` char(9)                      DEFAULT NULL,
  `year`     smallint(5) unsigned         DEFAULT NULL,
  `month`    tinyint(3) unsigned          DEFAULT NULL,
  `weekday`  tinyint(3) unsigned          DEFAULT NULL,
  `hour`     tinyint(3) unsigned          DEFAULT NULL,
  `pos`      float                        DEFAULT NULL,
  `neu`      float                        DEFAULT NULL,
  `neg`      float                        DEFAULT NULL,
  `compound` float                        DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `city` (`city`),
  KEY `sa1` (`sa1_code`),
  KEY `sa2` (`sa2_code`),
  KEY `year` (`year`),
  KEY `month` (`month`),
  KEY `weekday` (`weekday`),
  KEY `hour` (`hour`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4