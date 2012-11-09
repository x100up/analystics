# -*- coding: utf-8 -*-
from controllers.BaseController import AjaxController
from models.Config import Config
from components.webhdfs import WebHDFS, WebHDFSException
from services.HiveService import HiveService
from models.HDFS import HDFS_item, HDFSPath
from hive_service.ttypes import HiveServerException


class HDFSController(AjaxController):

    def getHDFSClient(self):
        host = self.getConfigValue(Config.HDFS_HOST)
        port = self.getConfigValue(Config.HDFS_PORT)
        username = self.getConfigValue(Config.HDFS_USERNAME)
        return WebHDFS(host, int(port), username)

class GetPathAction(HDFSController):

    def post(self, *args, **kwargs):

        path = self.get_argument('path')

        rootPath = self.getConfigValue(Config.HDFS_STAT_ROOT)

        self.webhdfs = self.getHDFSClient()

        list = self.webhdfs.list(rootPath + path)
        files = []
        for values in list:
            values['dir'] = path
            files.append(HDFS_item.create(values))

        if path[0] == '/':
            path = path[1:]

        paths = path.replace("//","/").split('/')

        body = self.render('hdfs/blocks/fileListBody.jinja2', {'files': files}, _return=True)

        navigator = self.render('hdfs/blocks/navigator.jinja2', {'paths': paths}, _return=True)

        hdfspath = HDFSPath(path)
        hiveDB = hdfspath.getHiveDb()
        print hiveDB
        hiveTable =  hdfspath.getHiveTable()
        hiveTablePartition =  hdfspath.getHiveTablePartition()

        self.renderJSON({'body':body, 'navigator':navigator, 'hive':{
            'db':hiveDB,
            'table':hiveTable,
            'partition':hiveTablePartition,
        }})


class GetPathStat(HDFSController):

    def post(self, *args, **kwargs):

        path = self.get_argument('path')
        currentPath = self.getConfigValue(Config.HDFS_STAT_ROOT)

        self.webhdfs = self.getHDFSClient()
        data = self.webhdfs.dirSummary(currentPath + path)

        total = self.render('hdfs/blocks/pathTotal.jinja2', data, _return=True)
        self.renderJSON({'html':total})

class HiveController(AjaxController):

    def query(self, query):
        host = self.getConfigValue(Config.HIVE_HOST)
        port = self.getConfigValue(Config.HIVE_PORT)
        hiveClient = HiveService(host, port)
        return hiveClient.execute(query)

class GetHiveStatus(HiveController):

    def post(self, *args, **kwargs):
        data = {'db':{'exists':False}}
        db = self.get_argument('db')

        result = self.query('DESCRIBE DATABASE {}'.format(db))

        isExist = result[0][0] == db
        data['db']['exists'] = isExist



        table = self.get_argument('table', default=None)
        partition = self.get_arguments('partition[]')

        print partition
        if table:
            data['table'] = {'exists':False}
            self.query('USE {}'.format(db))
            result = self.query('DESCRIBE stat_{}'.format(table))
            isExist = result[0][0] != 'Table stat_{} does not exist'.format(table)
            data['table']['exists'] = isExist

            if isExist and partition:
                data['partition'] = {}
                isExist = False
                try:
                    q = 'DESCRIBE stat_{} PARTITION(year={},month={},day=45)'.format(table, partition[0], partition[1], partition[2])
                    print q
                    result = self.query(q)
                    isExist = result[0][0] != 'Partition {}year={}, month={}, day={}{} for table stat_{} does not exist'.format('{',partition[0], partition[1], partition[2], '}',table)
                except HiveServerException as ex:
                    print ex

                data['partition']['exists'] = isExist

        self.renderJSON(data)