#!/usr/bin/python
# coding=utf-8
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from components import dbutils
from models.Config import Config
import inspect
import os

rootPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory

config = Config()
config.readConfigFile(os.path.abspath(os.path.abspath(rootPath + '/../server.cfg')))

conn_str = 'mysql://'
if config.get(Config.MYSQL_USER):
    conn_str += config.get(Config.MYSQL_USER)
    if config.get(Config.MYSQL_PASSWORD):
        conn_str += ':' + config.get(Config.MYSQL_PASSWORD)

    conn_str += '@'

conn_str += config.get(Config.MYSQL_HOST)
engine = create_engine(conn_str + '/' + config.get(Config.MYSQL_DBNAME) + '?init_command=set%20names%20%22utf8%22', encoding='utf8', convert_unicode=True)
try:
    connection = engine.connect()
except OperationalError as op_error:
    print u'Ошибка соединения с MySQL: ' + op_error.message
except BaseException as ex:
    print u'Исключение SQLALCHEMY: ' + ex.message
else:
    dbutils.migrate(connection = connection)