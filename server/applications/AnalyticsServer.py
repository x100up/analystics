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
from controllers.admin import AdminUserController, AdminIndexController, AdminAppController, AdminRulesController
from controllers.admin import AdminSettingsController, AdminAppConfigController, AdminAppSpellController, AdminAppGroupsController, AdminClusterController
from controllers.admin import AdminProxy
from controllers.api import APIController
from controllers.dashboard import ResultController, AjaxController, DashboardController, CreateTaskController, TemplateController
from controllers.cluster import NameNodeController
from controllers.install import InstallController
from controllers.hdfs import HDFSController, HDFSAJAXController
from controllers.hadoop import HiveAJAXController

from jinja2 import Environment, PackageLoader
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime

class AnalyticsServer(tornado.web.Application):

    spellFolder = None

    def __init__(self, debug = False):
        # define app root path
        thisPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
        self.appRoot = os.path.abspath(thisPath + '/../../')

        self.spellFolder = self.appRoot + '/app_configs/spells/'

        level = logging.WARNING
        if debug:
            level = logging.INFO

        formatter = logging.Formatter('%(asctime)s %(filename)s(%(lineno)s)[%(funcName)s] %(threadName)s %(levelname)-8s %(message)s')
        self.logger = logging.getLogger('AnalyticsServer')
        self.logger.setLevel(level)
        self.internalData = {}

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
        self.jinjaEnvironment.filters['smartDate'] = smartDate
        self.jinjaEnvironment.filters['smartDatePeriod'] = smartDatePeriod
        self.jinjaEnvironment.filters['smartDateInterval'] = smartDateInterval
        self.jinjaEnvironment.filters['excelDate'] = excelDate
        self.jinjaEnvironment.filters['excelTime'] = excelTime
        self.jinjaEnvironment.filters['dateFromTS'] = dateFromTS
        self.jinjaEnvironment.filters['toJsVar'] = toJsVar
        self.jinjaEnvironment.filters['minInt'] = minInt
        self.jinjaEnvironment.filters['numberFormat'] = numberFormat
        self.jinjaEnvironment.filters['showMonth'] = showMonth

        self.scoped_session = None
        self.loopInstance = None
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
        port = int(self.config.get('app_port', 48888))
        address = self.config.get('app_host', "")
        self.listen(port = port, address = address )
        self.loopInstance = tornado.ioloop.IOLoop.instance()
        self.logger.info('application run {}:{}'.format(address, port))
        self.loopInstance.start()



    def loadConfiguration(self):
        self.config = Config()
        self.config.readConfigFile(os.path.abspath(self.appRoot + '/server.cfg'))

    def getAppConfigPath(self):
        return self.appRoot + '/app_configs/'

    def getResultPath(self):
        return self.appRoot + '/result/'

    def getLogPath(self):
        return self.appRoot + '/log/'

    def getTemplatePath(self):
        return self.appRoot + '/template/'

    def determineIsInstall(self):
        """
        Простое определение - установлено ли приложение
        """
        self.isInstalled =  os.path.exists(self.appRoot + '/server.cfg')

    def setData(self, key, value):
        self.internalData[key] = value

    def getData(self, key):
        return self.internalData[key]

    def deleteData(self, key):
        del self.internalData[key]

    def getHandlers(self):
        thisPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
        return [
            (r"/", IndexController.IndexAction),

            # --------- DASHBOARD -----------

            (r"/dashboard/?", DashboardController.SwitchApp),
            (r"/dashboard/app/([^/]+)/?", DashboardController.IndexAction),
            (r"/dashboard/app/([^/]+)/first/?", DashboardController.FirstAction),
            (r"/dashboard/app/([^/]+)/result/?", ResultController.ResultAction),
            (r"/dashboard/app/([^/]+)/result/table/(\d+)/?", ResultController.TableAction),
            (r"/dashboard/app/([^/]+)/new/?", CreateTaskController.CreateAction),
            (r"/dashboard/app/([^/]+)/recalculate/?", CreateTaskController.RecalculateAction),
            (r"/dashboard/app/([^/]+)/templates/?", TemplateController.IndexAction),
            (r"/dashboard/empty/?", DashboardController.EmptyAppAction),
            (r"/dashboard/selectapp/?", DashboardController.SelectAppAction),
            (r"/dashboard/app/([^/]+)/new_task/([^/]+)/?", CreateTaskController.ShowNewTaskAction),
            (r"/dashboard/app/([^/]+)/status/([^/]+)/?", ResultController.ShowTaskStatus),
            (r"/ajax/dashboard/app/([^/]+)/workers/([^/]+)/??", DashboardController.GetWorkers),

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
            (r'/admin/cluster?', AdminClusterController.IndexAction),
            (r'/admin/historyServer/?', AdminProxy.HistoryServerView),
            (r'/admin/resourceManager/?', AdminProxy.ResourceManagerView),
            (r'/admin/proxy/([^/]+)/([^/]+)/(.+)?', AdminProxy.CoreProxy),






            (r'/admin/app/([^/]+)/settings/?', AdminAppConfigController.IndexAction),
            (r'/admin/app/([^/]+)/eventsList/?', AdminAppConfigController.EventListAction),
            (r"/admin/app/([^/]+)/editEvent/?", AdminAppConfigController.EditEvent),

            (r'/admin/app/([^/]+)/editTags/?', AdminAppConfigController.TagListAction),
            (r"/ajax/editTag/?", AdminAppConfigController.EditTag),


            (r'/admin/app/([^/]+)/editBunches/?', AdminAppConfigController.BunchListAction),
            (r'/ajax/editBunch/?', AdminAppConfigController.EditBunchAction),


            (r'/admin/app/([^/]+)/spell/?', AdminAppSpellController.IndexAction),
            (r'/admin/app/([^/]+)/groups/?', AdminAppGroupsController.IndexAction),
            # --------- CLUSTER -----------
            (r'/cluster/namenode/?', NameNodeController.IndexAction),

            # --------- AJAX -----------
            (r"/ajax/key_configuration/?", AjaxController.KeyConfigurationAction),
            (r"/ajax/get_key_form/?", AjaxController.GetKeyForm),
            (r"/ajax/getTasksProgress/?", AjaxController.GatTasksProgress),
            (r"/ajax/copyTaskKey/?", AjaxController.CopyTaskKey),
            (r"/ajax/saveWorkerName?", AjaxController.SaveWorkerName),


            #(r"/ajax/add_new_key?", AjaxController.AddNewKey),
            (r"/ajax/add_new_tag?", AjaxController.AddNewTag),
            (r"/ajax/add_new_bunch?", AjaxController.AddNewBunch),
            (r"/ajax/getDateSelector/?", AjaxController.GetDateSelector),


            (r"/ajax/getTagUniqueValues/?", HiveAJAXController.getTagUniqueValues),
            (r"/ajax/downloadCSV/?", AjaxController.DownloadCSVAction),

            (r"/ajax/admin/getClusterState/?", AdminClusterController.ClusterStateAction),

            # ----------- TEMPLATE ---------------
            #(r"/template/create/([^/]+)/?", TemplateController.CreateTemplateAction),

            # ----------- HDFS ---------------
            (r"/hdfs/?", HDFSController.IndexAction),
            (r"/hdfs/ajax/getPath/?", HDFSAJAXController.GetPathAction),
            (r"/hdfs/ajax/getPathStat/?", HDFSAJAXController.GetPathStat),
            (r"/hdfs/ajax/getHiveStat/?", HDFSAJAXController.GetHiveStatus),

            (r"/api/putConfig/?", APIController.PutConfigAction),

            (r"/install/?", InstallController.InstallAction),
            (r"/install/final/?", InstallController.FinalInstallAction),





            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": os.path.abspath(thisPath + '/../static')}),
        ]