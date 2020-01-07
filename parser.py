# -*- coding: utf-8 -*-
import sqlite3
from geoip import geolite2
import os

db = 'parserdb.sqlite'
default_country = 'Unknown'
os.remove(db)

conn = sqlite3.connect(db)
cursor = conn.cursor()
print("Database created and Successfully Connected to SQLite")

cursor.execute('CREATE TABLE IF NOT EXISTS "history" ( `_id` INTEGER PRIMARY KEY AUTOINCREMENT, `ip` TEXT, `url` TEXT, `country` TEXT, `datetime` TEXT )')

# Уменьшим нагрузку на lookup
# создадим локальный реестр уже добавленных адресов
# [121.165.118.201] = KR
ips = dict()

sql_history = "INSERT INTO 'history' (`ip`, `url`, `country`,`datetime`) VALUES(?,?,?,?)"

with open('logs.txt', 'r') as f:
	# shop_api      | 2018-08-01 00:01:35 [YQ4WUDJV] INFO: 121.165.118.201 https://all_to_the_bottom.com/
	for line in f:
		line = line.rstrip()
		# [shop_api      | 2018-08-01 00:01:35 [YQ4WUDJV] , 121.165.118.201 https://all_to_the_bottom.com/]
		cols = line.split('INFO:')

		#[shop_api      ,,2018-08-01,00:01:35,[YQ4WUDJV]]
		p = cols[0].split('|')

		#[,2018-08-01,00:01:35,[YQ4WUDJV]]
		p = p[1].split(' ')

		#2018-08-01 00:01:35
		day = ' '.join(p[1:3])

		# 121.165.118.201 https://all_to_the_bottom.com/
		p = cols[1]

		# [,121.165.118.201,https://all_to_the_bottom.com/]
		a = p.split(' ')
		u = a[2].split('https://all_to_the_bottom.com/')

		# 121.165.118.201
		addr = a[1]
		
		c = default_country
		if not addr in ips:
			match = geolite2.lookup(addr)
		
			if match is not None:
				c = match.country
			else:	
				c = default_country

			if c is None:
				c = default_country
							
			ips[addr] = c
		else:
			c = ips[addr]

		#добавление в базу
		cursor.execute(sql_history, [addr, u[1], c, day])

	conn.commit()

cursor.close()
conn.close()


# - ответ на 1 вопрос теста
# cursor.execute('SELECT COUNT() as count, country, ip FROM "history" GROUP BY country ORDER BY count DESC LIMIT 10')
# rows = cursor.fetchall()
# for row in rows:
# 	print(row)

# - ответ на 2 вопрос теста
# cursor.execute ('''SELECT COUNT(url) as count, country, ip,url FROM "history" WHERE url = 'canned_food/' GROUP BY url, country ORDER BY count desc''')
# rows = cursor.fetchall()
# for row in rows:
#  	print(row)

# - ответ на 3 вопрос теста
# cursor.execute('''SELECT `datetime`,url FROM "history" WHERE url = 'caviar/' ''')
# rows = cursor.fetchall()
# dt = set()
# freq = dict()
# for row in rows:
# 	date = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
# 	day = time_of_day_dict(date) 
# 	dt.add(day)

# 	if not day in freq:
# 		freq[day] = 0
# 	freq[day] += 1

# for i in dt:
# 	print("%s : %d" % (i, freq[i]))
