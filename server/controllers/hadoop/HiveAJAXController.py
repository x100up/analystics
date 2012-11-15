# -*- coding: utf-8 -*-
from controllers.BaseController import AjaxController
from models.Config import Config
from services.HiveService import HiveService
from datetime import datetime, timedelta

class HiveController(AjaxController):

    def query(self, query):
        host = self.getConfigValue(Config.HIVE_HOST)
        port = self.getConfigValue(Config.HIVE_PORT)
        hiveClient = HiveService(host, port)
        return hiveClient.execute(query)

class getTagUniqueValues(HiveController):

    def post(self, *args, **kwargs):
        app = self.get_argument('app')
        keys = self.get_arguments('keys[]')
        tagCode = self.get_argument('tagCode')

        date = datetime.now() - timedelta(days = 1)

        querys = []
        for key in keys:
            querys.append('SELECT DISTINCT params[\'{}\'] as `value` FROM `{}`.`stat_{}` WHERE `year` = {} AND ' \
                          '`month` = {} AND `day` = {}'.format(tagCode, app, key, date.year, date.month, date.day))

        if len(querys) == 1:
            query = querys.pop()
        else:
            query = 'SELECT DISTINCT `value` FROM (' + ' UNION ALL ' .join(querys) +') FINAL'

        result = self.query(query)

        self.renderJSON({'values':['sssss', 'ssssssss', 'ffffff'], 'result': result, 'query':query})


