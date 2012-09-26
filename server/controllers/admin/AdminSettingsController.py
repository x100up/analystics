# -*- coding: utf-8 -*-
import logging
from AdminIndexController import AdminAction

class IndexAction(AdminAction):

    def prepare(self):
        self.config = self.application.config
        self.errors = []

    def get(self, *args, **kwargs):
        self.run()

    def post(self, *args, **kwargs):
        for key, value in self.request.arguments.items():
            self.config.set(key, value.pop())

        # TODO validate mysql connection

        # write config
        raw_config = self.config.getRawConfig()
        try:
            configfile = open(self.application.appRoot + '/server.cfg', 'wb')
        except BaseException as exception:
            message = u'Ошибка при записи файла конфигурации: ' + exception.message
            self.errors.append(message)
            logging.getLogger('AnalyticsServer').error(message)
        else:
            raw_config.write(configfile)
            configfile.close()
            self.application.loadConfiguration()

        self.run()

    def run(self):
        self.render('admin/settings.jinja2', {'config':self.config, 'errors': self.errors})
