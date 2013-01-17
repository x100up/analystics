__author__ = 'x100up'

import logging
import re, os, inspect, json
from models.Config import Config
from optparse import OptionParser
from services.HiveService import HiveService
from services.AppService import AppService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.App import App
from components.webhdfs import WebHDFS, WebHDFSException, AnalyticsWebHDFS

class BaseAnalyticsScript():

    def __init__(self):
        self.scoped_session = self.analyticsWebHDFS = None
        # set logger
        logging.basicConfig(level = logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

        # set configurations
        rootPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory

        self.config = Config()
        self.config.readConfigFile(os.path.abspath(os.path.abspath(rootPath + '/../server.cfg')))

        optParser = OptionParser()
        optParser.add_option("-a", "--app", dest="appname", help="application name")
        optParser.add_option("-x", "--all", dest="all_apps", help="all applications", action="store_true")

        (options, args) = optParser.parse_args()
        self.options = options.__dict__
        self.appService = AppService(rootPath + '/../app_configs/')
        self.availableApps = appService.getAppConfigList()

        if options['appname'] is None and options['all_apps'] is None:
            print 'App name or --all is not set'
            print 'Availale app names: ' + str(self.availableApps)
            self.terminate()


    def getAppCodes(self):
        return []

    def getAppConfig(self, appCode):
        '''
        -> AppConfig
        '''
        return self.appService.getAppConfig(appCode)

    def getApp(self, appCode):
        return self.getDBSession().query(App).filter_by(code = appCode).first()

    def getWebHDFSClient(self):
        if not self.analyticsWebHDFS:
            host = self.config.get(Config.HDFS_HOST)
            port = int(self.config.get(Config.HDFS_PORT))
            username = self.config.get(Config.HDFS_USERNAME)
            statRoot = self.config.get(Config.HDFS_STAT_ROOT)
            self.analyticsWebHDFS = AnalyticsWebHDFS(host, port, username, statRoot)
        return self.analyticsWebHDFS

    def getDBSession(self):
        if not self.scoped_session:
            mysql_user = self.config.get(Config.MYSQL_USER)
            mysql_password = self.config.get(Config.MYSQL_PASSWORD)
            mysql_host = self.config.get(Config.MYSQL_HOST)
            mysql_dbname = self.config.get(Config.MYSQL_DBNAME)

            conn_str = 'mysql://'
            if mysql_user:
                conn_str += mysql_user
                if mysql_password:
                    conn_str += ':' + mysql_password
                conn_str += '@'
            conn_str += mysql_host + '/' + mysql_dbname

            engine = create_engine(conn_str + '?init_command=set%20names%20%22utf8%22',
                encoding = 'utf8',
                convert_unicode = True,
                pool_recycle = 3600)
            engine.execute('SET NAMES utf8')
            self.scoped_session = scoped_session(sessionmaker(bind = engine, autoflush = False))
        return self.scoped_session

    def terminate(self):
        exit()