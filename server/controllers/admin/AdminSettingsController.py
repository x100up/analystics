# -*- coding: utf-8 -*-
import logging
from AdminIndexController import AdminAction
from models.Config import Config

class IndexAction(AdminAction):

    def prepare(self):
        super(IndexAction, self).prepare()
        self.config = self.application.config
        self.errors = []

    def get(self, *args, **kwargs):
        self.run()

    def post(self, *args, **kwargs):

        def_host = self.request.host.split(':')[0]

        old_host = self.config.get(Config.APP_HOST)
        old_port = self.config.get(Config.APP_PORT)

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
            if old_host != self.config.get(Config.APP_HOST) or old_port != self.config.get(Config.APP_PORT):
                self.redirect('http://' + self.config.get(Config.APP_HOST, def_host) + ':' + self.config.get(Config.APP_PORT) + '/admin/settings')
                self.application.start()

        self.run()

    def run(self):
        self.render('admin/settings.jinja2', {'config':self.config, 'errors': self.errors})
