#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import sqlite3 
import time
from datetime import datetime
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)

def time_of_day_dict(dt=None, ts=None, tod_dict=None):
    '''
    Принимает объект datetime (dt) или timestamp (ts), и словарь tod_dict {час : наименование времени}
    Возвращает строку c временем суток. 
    При отсутствии аргументов - возвращает строку с текущим временем суток.
 
        Словарь по умолчанию: 
        {0: 'ночь', 1: 'ночь', 2: 'ночь',
         3: 'раннее утро', 4: 'раннее утро', 5: 'раннее утро',
         6: 'утро', 7: 'утро', 8: 'утро',
         9: 'первая половина дня', 10: 'первая половина дня', 11: 'первая половина дня',
         12: 'обед', 13: 'обед', 14: 'обед',
         15: 'после обеда', 16: 'после обеда', 17: 'после обеда',
         18: 'вечер', 19: 'вечер', 20: 'вечер',
         21: 'поздний вечер', 22: 'поздний вечер', 23: 'поздний вечер' }
 
    Eсли час не отражен в словаре, возвращает None
    Требует import datetime
    N.B. ф-я в 2-3 раза быстрее, чем ф-я time_of_day()
    '''
 
    # определение словаря
    if tod_dict:
        pass
    else:
        tod_dict = {0: 'ночь', 1: 'ночь', 2: 'ночь',
                    3: 'раннее утро', 4: 'раннее утро', 5: 'раннее утро',
                    6: 'утро', 7: 'утро', 8: 'утро',
                    9: 'первая половина дня', 10: 'первая половина дня', 11: 'первая половина дня',
                    12: 'обед', 13: 'обед', 14: 'обед',
                    15: 'после обеда', 16: 'после обеда', 17: 'после обеда',
                    18: 'вечер', 19: 'вечер', 20: 'вечер',
                    21: 'поздний вечер', 22: 'поздний вечер', 23: 'поздний вечер'}
 
    # определение оцениваемого времени
    if dt:
        if isinstance(dt, datetime):
            dt = dt
        else:
            print('некорректный формат dt: %s \n требуется объект datetime.datetime' % (type(dt)))
            return None
    elif ts:
        if isinstance(ts, (int, float)):
            if ts > 0:
                dt = datetime.fromtimestamp(ts)
                print(dt.ctime())
            else:
                print('отрицательное значение ts недопустимо')
                return None
        else:
            print('некорректный формат ts: %s \n требуется значение int или float' % (type(ts)))
            return None
    else:
        dt = datetime.now()
    h = dt.hour
 
    # подбор
    if h in tod_dict:
        tod = tod_dict[h]
        return tod
    else:
        print('Значение времени отсутствует в словаре')
        return None

@app.route('/', methods = ['GET', 'POST'])
def index():

	# Подключение к базе данных
	conn = sqlite3.connect('parserdb.sqlite')
	cursor = conn.cursor()

	# Ответ на первый вопрос
	# Получаем топ 10 стран посетителей сайта
	response = list()
	cursor.execute('SELECT COUNT() as count, country, ip FROM "history" GROUP BY country ORDER BY count DESC LIMIT 10')
	rows = cursor.fetchall()
	for row in rows:
		response.append(row)

	m = list()
	goods = list()
	if request.method == 'POST':
		c = request.form.get('category')
		if c == "/":
			c = ""

		# Ответ на второй вопрос
		# Получаем данные по категории
		cursor.execute (
			'''
			SELECT COUNT(url) as count, country, ip,url FROM "history" WHERE url = '%s' GROUP BY url, country ORDER BY count desc
			''' % (c)
		)
		rows = cursor.fetchall()
		for row in rows:
		 	m.append(row) # [[count, country, ip,url]]

		# Ответ на третий вопрос

		dt = set()
		freq = dict()
		cursor.execute('''SELECT `datetime`,url FROM "history" WHERE url = '%s' '''% (c))
		rows = cursor.fetchall()
		for row in rows:
			date = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
			day = time_of_day_dict(date) 
			dt.add(day)

			# Словарь частот времен суток
			if not day in freq:
				freq[day] = 0
			freq[day] += 1

		for i in dt:
			goods.append([freq[i], i])

	# Получаем количество групп для элемента select
	cate = list()
	filtr = ['success_pay_']

	cursor.execute('SELECT url FROM "history" GROUP BY url')
	rows = cursor.fetchall()
	for row in rows:
		s = row[0]

		# Корень сайта
		if s == "":
			s = "/"

		# Если ссылка не раздел
		if s[-1] != '/': 
			continue
		
		# Фильтруем разделы типа success_pay
		flag = False
		for i in filtr:
			if len(s) >= len(i):
				if s[0:len(i)] == i:
					flag = True
					break

		if flag:
			continue

 		cate.append(s)

 	# Закрытие подключения к базе
	cursor.close()
	conn.close()

	return render_template("index.html", 
		cat = cate, 
		answ = m, 
		resp = response, 
		goods = goods
	)

if __name__ == '__main__':
    app.run(debug = False)