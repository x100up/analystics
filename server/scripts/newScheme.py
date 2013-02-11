# -*- coding: utf-8 -*-
from scripts.baseScript import BaseAnalyticsScript

class NewScheme(BaseAnalyticsScript):

    def run(self):
        self.hiveclient = self.getHiveClient()
        self.getOldTables()


    def getOldTables(self):
        self.hiveclient.execute('USE topface')
        tables = self.hiveclient.execute('SHOW TABLES')
        print tables
