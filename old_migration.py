#!/usr/bin/python
# -*- coding: utf-8
import MySQLdb
import MySQLdb.cursors
import re
import os
import random
from datetime import timedelta, datetime

table_re = re.compile("^Statistics_\d{4}_\d{2}_\d{2}$")

# подключаемся к базе данных (не забываем указать кодировку, а то в базу запишутся иероглифы)
connection = MySQLdb.connect(host="localhost", user="root", passwd="123123", db="statistics", charset='utf8',
                     cursorclass = MySQLdb.cursors.SSCursor)
cursor = connection.cursor()

sql = 'SHOW TABLES'
cursor.execute(sql)

tables = []
while True :
    try :
        tablename, = cursor.next()
        if table_re.match(tablename):
            tables.append(tablename)
    except Exception :
        break
cursor.close()

def dumpLines(lines, path, filename):
    try :
        path = 'dump/' + path
        if not os.path.exists(path):
            os.makedirs(path)
        print 'write to {}'.format(path)
        f = open(path + '/' + filename, 'w')
        f.write("\n".join(lines))
        f.close()
    except Exception as ex:
        print 'Exception on write file "{}" :: {}'.format(path + '/' + filename, ex.message)

def dumpKeyCache():
    for path in key_data_cache:
        i = 1
        lines = []
        for tags, repeat_count, date in key_data_cache[path]:
            _str = []
            for k, v in tags.items():
                _str.append(k + '=' + str(v))

            _str = ';'.join(_str)
            _str = _str + ',0,'
            for i in range(0, repeat_count):
                d = date + timedelta(minutes = random.randint(0, 9))
                lines.append(_str + '{},{},{},{},{},{},{}'.format(d.strftime('%Y-%m-%d %H-%M-%S'), d.hour, d.minute, d.second, d.year, d.month, d.day))

            if (lines > 300):
                dumpLines(lines, path, 'data' + str(i))
                lines = []
                i = i + 1
        if lines:
            dumpLines(lines, path, 'data' + str(i))

    print 'start copy portion of data to HDFS.'
    print os.system('sudo -u hdfs hadoop fs  -copyFromLocal dump/ /statistics/dump')
    print 'rm -rf dump:' + str(os.system('rm -rf dump'))





def processRow(data, _type, value):
    repeat_count = value
    data = data.split('|')
    tags = {}
    lastkey = False
    # парсим теги
    if len(data) > 1:
        for item in data[1].split('_'):
            kv = item.split(':')
            if len(kv) == 2:
                lastkey = kv[0]
                tags[kv[0]] = kv[1]
            elif lastkey:
                tags[lastkey] += '_' + kv[0]

    key = data[0]

    if key.find('page_open_timers') == 0:
        tags['time'] = value
        tags['page'] = '.'.join(key.split('.')[1:])
        key = 'page_open_timers'
        repeat_count = 1
    elif key == 'coins':
        pass
    elif key == 'premium':
        key = 'buy_premium'
    elif key == 'premium':
        key = 'buy_premium'
    else:
        # messages
        key = key.lower().replace('.', '__')

    path = '{}/{}/{}/{}'.format(key, date.year, date.month, date.day)

    return (path, tags, repeat_count)


key_data_cache = {}
rows_in_cache = 0

for table in tables:
    sql = 'SELECT `name`, `type`, `time`, `value` FROM {}'.format(table)
    print 'Start migrate table {}'.format(table)
    cursor = connection.cursor()
    cursor.execute(sql)
    while True :
        try :
            data, _type, date, value =  cursor.next()
            path, tags, repeat_count = processRow(data, _type, value)
            if not key_data_cache.has_key(path):
                key_data_cache[path] = []

            key_data_cache[path].append((tags, repeat_count, date))
            rows_in_cache += 1

            if rows_in_cache > 500000:
                dumpKeyCache()
                key_data_cache = {}
                rows_in_cache = 0

        except Exception as ex:
            break

    if rows_in_cache:
        dumpKeyCache()
        key_data_cache = {}
        rows_in_cache = 0

    cursor.close()