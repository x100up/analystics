# coding=utf-8
from sqlalchemy.exc import OperationalError
from components import dbutils
from scripts.baseScript import BaseAnalyticsScript

class UpdateDbScript(BaseAnalyticsScript):

    def run(self):
        print 'start DB migrate'

        try:
            DBSession = self.getDBSession()
        except OperationalError as op_error:
            print u'Ошибка соединения с MySQL: ' + op_error.message
        except BaseException as ex:
            print u'Исключение SQLALCHEMY: ' + ex.message
        else:
            dbutils.migrate(connection = DBSession)