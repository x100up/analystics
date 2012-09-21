# -*- coding: utf-8 -*-
from controllers.BaseController import BaseController
from services.NameNodeService import NameNodeService
from models.Config import Config

class IndexAction(BaseController):
    def prepare(self):
        self.errors = []

    def get(self, *args, **kwargs):

        nameNodeService = NameNodeService(self.getConfigValue(Config.HADOOP_NAMENODE))
        try:
            self.allData = nameNodeService.load()
        except BaseException as exception:
            self.errors.append(exception.message)
            self.run()
            return None


        self.run()


    def run(self):
        self.render('cluster/namenode.jinja2', {'allData': self.allData})