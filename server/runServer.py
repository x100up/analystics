import os, tornado.web, tornado.ioloop, ConfigParser
from controllers import  IndexController, UserController
from controllers.admin import AdminUserController, AdminIndexController, AdminAppController, AdminRulesController
from controllers.api import APIController
from controllers.dashboard import ResultController, AjaxController, DashboardController, CreateTaskController

config = {
    'core': {
        'result_path' : 'result',
        'port' : 8888,
        'app_config_path': 'app_configs'
    },
    'mysql': {
        'user':'user',
        'password':'password',
        'host':'localhost',
        'dbname':'stat'
    },
    'hive': {
        'host': 'localhost',
        'port': 10000,
        'prefix': 'stat_'
    },
}

configParser = ConfigParser.RawConfigParser()
configParser.read(['server.cnf'])

sections = configParser.sections()
for section in sections:
    if config.has_key(section):
        items = configParser.items(section)
        for k, v in items:
            if config[section].has_key(k):
                config[section][k] = v
            else:
                print 'warning: config section ' + section + ' hasn`t property ' + k

# tornado app settings
settings = {
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/user/login",
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "debug" : True,
    "config" : config
}

# routing
application = tornado.web.Application([
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

],   **settings)


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()