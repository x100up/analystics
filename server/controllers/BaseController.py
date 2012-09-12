from jinja2 import Template, Environment, PackageLoader
from sqlalchemy.orm import sessionmaker
import tornado.web, json
from sqlalchemy import create_engine
from models.User import User
from models.App import  App
from models.Config import Config
from service.RuleService import RuleService


class BaseController(tornado.web.RequestHandler):

    dbSessionMaker = False
    dbSession = False

    def getSessionMaker(self):
        if not self.dbSessionMaker:
            mysql_user = self.getConfigValue(Config.MYSQL_USER)
            mysql_password = self.getConfigValue(Config.MYSQL_PASSWORD)

            conn_str = 'mysql://'
            if mysql_user:
                conn_str += mysql_user
                if mysql_password:
                    conn_str += ':' + mysql_password
                conn_str += '@'
            conn_str += self.getConfigValue(Config.MYSQL_HOST) + '/' + self.getConfigValue(Config.MYSQL_DBNAME)

            engine = create_engine(conn_str + '?init_command=set%20names%20%22utf8%22', encoding = 'utf8', convert_unicode = True)
            engine.execute('SET NAMES utf8')

            self.dbSessionMaker = sessionmaker(bind = engine, autoflush = False)

        return self.dbSessionMaker

    def getDBSession(self):
        if not self.dbSession:
            self.dbSession = self.getSessionMaker()()
        return self.dbSession

    def get_current_user(self):
        login = self.get_secure_cookie('user.login')
        if login:
            session = self.getDBSession()
            user = session.query(User).filter_by(login = login).first()
            session.flush()
            return user

        return None

    def invalidateDBSessions(self):
        self.dbSessionMaker = False
        self.dbSession = False

    def getConfig(self, section = None, property = None):
        """
        return config
        """
        config = self.settings['config']
        if section:
            if config.has_key(section):
                if property:
                    if config[section].has_key(property):
                        return config[section][property]
                else:
                    return config[section]
            else:
                return None
        return config

    def getConfigValue(self, key):
        '''
        Return config value for key from app config
        '''
        return self.application.config.get(key)

    def render(self, template_name, dict = None):
        if dict is None:
            dict = {}

        dict['is_login'] = self.get_secure_cookie('user.login')
        u = self.get_current_user();
        if u:
            dict['__user__'] = {'name': u.fullname, 'isAdmin': u.role == User.ROLE_ADMIN}

        env = Environment(loader = PackageLoader('static', 'template'))
        self.write(env.get_template(template_name).render(**dict))

    def checkAppAccess(self, args):
        # get app code
        if type(args) is unicode:
            appCode = args
        else:
            if len(args) == 0:
                raise RuntimeError('Cant find app code in dashboard')
            appCode = args[0]

        # get user and db session
        user = self.get_current_user()
        session = self.getDBSession()

        # get app
        app = session.query(App).filter(App.code == appCode).first()
        if app is None:
            raise RuntimeError('Cant find app by code ' + appCode)

        # check access
        ruleService = RuleService(session)
        if not ruleService.isAllow(user.userId, app.appId):
            raise RuntimeError('Access denied')

        return app

    def prepare(self):
        if not self.application.isInstalled:
            self.redirect('/install/')


class AjaxController(BaseController):

    def send_ajax_error(self, error):
        self.renderJSON({'error':error})

    def renderJSON(self, data):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(data))

class InstallController(BaseController):

    def render(self, template_name, dict = None):
        '''
        Rewrite render without user
        '''
        if dict is None:
            dict = {}
        env = Environment(loader = PackageLoader('static', 'template'))
        self.write(env.get_template(template_name).render(**dict))


    def prepare(self):
        print 'pp'
        print self.application.isInstalled
        if self.application.isInstalled:
            self.redirect('/')