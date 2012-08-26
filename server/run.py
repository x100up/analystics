import tornado.ioloop
import tornado.web
import os
from controllers import DashboardController, IndexController, UserController, AdminController, DashboardAjaxController
import ConfigParser
import sys
print sys.argv

config = {
    'core': {
        'result_path' : 'result',
        'port' : 8888
    },
    'mysql': {
        'user':'user',
        'password':'password',
        'host':'localhost',
        'dbname':'stat'
    }
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
                print 'warning: config section ' + section + ' hasnt property ' + k
    else:
        print 'warning: config hasnt section ' + section



settings = {
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/user/login",
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "debug" : True,
    "config" : config
}

application = tornado.web.Application([
    (r"/", IndexController.IndexAction),

    (r"/dashboard/?", DashboardController.IndexAction),
    (r"/dashboard/run/?", DashboardController.HiveAction),
    (r"/dashboard/new/?", DashboardController.CreateAction),

    (r"/user/login/?", UserController.AuthAction),
    (r"/user/logout/?", UserController.LogoutAction),

    (r"/admin?", AdminController.IndexAction),
    (r"/admin/users/?", AdminController.UserAction),
    (r"/admin/users/edit?", AdminController.EditUserAction),


    (r"/ajax/key_autocomplete/?", DashboardAjaxController.KeyAutocompleteAction),
    (r"/ajax/key_configuration/?", DashboardAjaxController.KeyConfigurationAction),

],   **settings)


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()