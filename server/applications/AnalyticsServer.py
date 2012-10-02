# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'
import tornado.web
import inspect
import os
import sys
import tornado.ioloop
import logging
from components.jinja import *
from models.Config import Config
from controllers import  IndexController, UserController
from controllers.admin import AdminUserController, AdminIndexController, AdminAppController, AdminRulesController, AdminSettingsController, AdminTagController
from controllers.api import APIController
from controllers.dashboard import ResultController, AjaxController, DashboardController, CreateTaskController
from controllers.cluster import NameNodeController
from controllers.install import InstallController
from jinja2 import Environment, PackageLoader
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime

class AnalyticsServer(tornado.web.Application):

    def __init__(self, debug = False):
        # define app root path
        thisPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
        self.appRoot = os.path.abspath(thisPath + '/../../')

        level = logging.WARNING
        if debug:
            level = logging.INFO

        formatter = logging.Formatter('%(asctime)s %(filename)s(%(lineno)s)[%(funcName)s] %(threadName)s %(levelname)-8s %(message)s')
        self.logger = logging.getLogger('AnalyticsServer')
        self.logger.setLevel(level)

        # sterr out
        if debug:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(formatter)
            handler.setLevel(level)
            self.logger.addHandler(handler)
        handler = logging.FileHandler(self.appRoot + '/log/analyticsServer_' + datetime.now().strftime('%d-%m-%y') + '.log', 'a+')
        handler.setLevel(level)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info('AnalyticsServer started')

        # define app setting
        settings = {
            "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            "login_url": "/user/login",
            "static_url_prefix": "/static",
            "debug" : debug,
        }

        # call parent constuctor
        super(AnalyticsServer, self).__init__(handlers = self.getHandlers(), default_host = "", transforms = None,
            wsgi = False, **settings)

        self.loadConfiguration()
        self.determineIsInstall()
        self.jinjaEnvironment = Environment(loader = PackageLoader('static', 'template'))
        self.jinjaEnvironment.filters['datetofiled'] = datetofiled
        self.jinjaEnvironment.filters['smartDatePeriod'] = smartDatePeriod
        self.jinjaEnvironment.filters['smartDateInterval'] = smartDateInterval
        self.scoped_session = None
        if self.isInstalled:
            self.initDBScopedSession()

    def initDBScopedSession(self):
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


    def start(self):
        self.listen(8888)
        loopInstance = tornado.ioloop.IOLoop.instance()
        loopInstance.start()

    def loadConfiguration(self):
        self.config = Config()
        self.config.readConfigFile(os.path.abspath(self.appRoot + '/server.cfg'))

    def getAppConfigPath(self):
        return self.appRoot + '/app_configs/'

    def getResultPath(self):
        return self.appRoot + '/result/'

    def getLogPath(self):
        return self.appRoot + '/log/'

    def determineIsInstall(self):
        '''
        Простое определение - установлено ли приложение
        '''
        self.isInstalled =  os.path.exists(self.appRoot + '/server.cfg')

    def getHandlers(self):
        thisPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
        return [
            (r"/", IndexController.IndexAction),

            # --------- DASHBOARD -----------

            (r"/dashboard/?", DashboardController.SwitchApp),
            (r"/dashboard/app/([^/]+)/?", DashboardController.IndexAction),
            (r"/dashboard/app/([^/]+)/result/?", ResultController.ResultAction),
            (r"/dashboard/app/([^/]+)/new/?", CreateTaskController.CreateAction),
            (r"/dashboard/empty/?", DashboardController.EmptyAppAction),
            (r"/dashboard/selectapp/?", DashboardController.SelectAppAction),

            # --------- LOGIN & LOGOUT ---------

            (r"/user/login/?", UserController.AuthAction),
            (r"/user/logout/?", UserController.LogoutAction),

            # --------- ADMIN -----------

            (r"/admin/?", AdminIndexController.IndexAction),
            (r"/admin/users/?", AdminUserController.UserAction),
            (r"/admin/users/edit?", AdminUserController.EditUserAction),

            (r"/admin/apps/?", AdminAppController.IndexAction),
            (r"/admin/app/edit/?", AdminAppController.EditAction),

            (r"/admin/rules/?", AdminRulesController.IndexAction),
            (r"/admin/rules/switch?", AdminRulesController.SwitchAjaxAction),

            (r'/admin/settings/?', AdminSettingsController.IndexAction),

            (r'/admin/app/([^/]+)/tags/?', AdminTagController.TagEditAction),
            # --------- CLUSTER -----------
            (r'/cluster/namenode/?', NameNodeController.IndexAction),

            # --------- AJAX -----------

            (r"/ajax/key_autocomplete/?", AjaxController.KeyAutocompleteAction),
            (r"/ajax/key_configuration/?", AjaxController.KeyConfigurationAction),
            (r"/ajax/get_key_form/?", AjaxController.GetKeyForm),
            (r"/ajax/getKeys/([^/]+)/?", AjaxController.GetKeys),
            (r"/ajax/getTasksProgress/?", AjaxController.GatTasksProgress),
            (r"/ajax/copyTaskKey/?", AjaxController.CopyTaskKey),

            (r"/api/putConfig/?", APIController.PutConfigAction),

            (r"/install/?", InstallController.InstallAction),
            (r"/install/final/?", InstallController.FinalInstallAction),



            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": os.path.abspath(thisPath + '/../static')}),
        ]