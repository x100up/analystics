# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'
import tornado.web
import inspect
import os
import tornado.ioloop

from models.Config import Config
from controllers import  IndexController, UserController
from controllers.admin import AdminUserController, AdminIndexController, AdminAppController, AdminRulesController
from controllers.api import APIController
from controllers.dashboard import ResultController, AjaxController, DashboardController, CreateTaskController
from controllers.install import InstallController

class AnalyticsServer(tornado.web.Application):

    def __init__(self, debug = False):
        # define app root path
        thisPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
        self.appRoot = os.path.abspath(thisPath + '/../../')
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
        self.isInstalled =  os.path.exists('server.cfg')


    def getHandlers(self):
        thisPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
        #print os.path.abspath(thisPath + '/../static')

        return [
            (r"/", IndexController.IndexAction),

            (r"/dashboard/?", DashboardController.SwitchApp),
            (r"/dashboard/app/([^/]+)/?", DashboardController.IndexAction),
            (r"/dashboard/app/([^/]+)/result/?", ResultController.ResultAction),
            (r"/dashboard/app/([^/]+)/new/?", CreateTaskController.CreateAction),
            (r"/dashboard/empty/?", DashboardController.EmptyAppAction),
            (r"/dashboard/selectapp/?", DashboardController.SelectAppAction),

            (r"/user/login/?", UserController.AuthAction),
            (r"/user/logout/?", UserController.LogoutAction),

            (r"/admin/?", AdminIndexController.IndexAction),
            (r"/admin/users/?", AdminUserController.UserAction),
            (r"/admin/users/edit?", AdminUserController.EditUserAction),

            (r"/admin/apps/?", AdminAppController.IndexAction),
            (r"/admin/app/edit/?", AdminAppController.EditAction),

            (r"/admin/rules/?", AdminRulesController.IndexAction),
            (r"/admin/rules/switch?", AdminRulesController.SwitchAjaxAction),

            (r"/ajax/key_autocomplete/?", AjaxController.KeyAutocompleteAction),
            (r"/ajax/key_configuration/?", AjaxController.KeyConfigurationAction),
            (r"/ajax/get_key_form/?", AjaxController.GetKeyForm),
            (r"/ajax/getKeys/([^/]+)/?", AjaxController.GetKeys),

            (r"/api/putConfig/?", APIController.PutConfigAction),

            (r"/install/?", InstallController.InstallAction),
            (r"/install/final/?", InstallController.FinalInstallAction),

            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": os.path.abspath(thisPath + '/../static')}),
        ]