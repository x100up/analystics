# -*- coding: utf-8 -*-
from controllers.BaseController import BaseController
from models.Config import Config

class IndexAction(BaseController):

    def get(self, *args, **kwargs):

        rootPath = self.getConfigValue(Config.HDFS_STAT_ROOT)



        self.render('hdfs/index.jinja2', {'js_vars':{'currentPath': '"/"', 'rootPath': rootPath}})