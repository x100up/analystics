# -*- coding: utf-8 -*-
from controllers.BaseController import AjaxController
from models.Config import Config
from components.webhdfs import WebHDFS, WebHDFSException
from pprint import pprint
from models.HDFS import HDFS_item


class HDFSController(AjaxController):

    def getHDFSClient(self):
        host = self.getConfigValue(Config.HDFS_HOST)
        port = self.getConfigValue(Config.HDFS_PORT)
        username = self.getConfigValue(Config.HDFS_USERNAME)
        return WebHDFS(host, int(port), username)

class GetPathAction(HDFSController):

    def post(self, *args, **kwargs):

        path = self.get_argument('path')

        currentPath = self.getConfigValue(Config.HDFS_STAT_ROOT)

        self.webhdfs = self.getHDFSClient()

        list = self.webhdfs.list(currentPath + path)
        files = []
        for values in list:
            values['dir'] = path
            files.append(HDFS_item.create(values))

        pprint(list)

        if path[0] == '/':
            path = path[1:]

        paths = path.replace("//","/").split('/')
        print paths

        body = self.render('hdfs/blocks/fileListBody.jinja2', {'files': files}, _return=True)

        navigator = self.render('hdfs/blocks/navigator.jinja2', {'paths': paths}, _return=True)

        self.renderJSON({'body':body, 'navigator':navigator})


class GetPathStat(HDFSController):

    def post(self, *args, **kwargs):

        path = self.get_argument('path')
        currentPath = self.getConfigValue(Config.HDFS_STAT_ROOT)

        self.webhdfs = self.getHDFSClient()
        data = self.webhdfs.dirSummary(currentPath + path)

        total = self.render('hdfs/blocks/pathTotal.jinja2', data, _return=True)
        self.renderJSON({'html':total})