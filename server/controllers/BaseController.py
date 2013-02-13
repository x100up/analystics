# coding=utf-8
from jinja2 import Environment, PackageLoader
from models.User import User
from models.App import  App
from services.RuleService import RuleService
from models.UserAppRule import RuleCollection

import tornado.web, json


class BaseController(tornado.web.RequestHandler):
    dbSession = False

    def getDBSession(self):
        if not self.dbSession:
            self.dbSession = self.application.scoped_session()
        return self.dbSession

    def removeDBSessions(self):
        if self.dbSession:
            self.dbSession.close()

    def get_current_user(self):
        login = self.get_secure_cookie('user.login')
        if login:
            session = self.getDBSession()
            user = session.query(User).filter_by(login = login).first()
            session.flush()
            return user

        return None

    def getConfigValue(self, key):
        """
        Return config value for key from app config
        """
        return self.application.config.get(key)

    def render(self, template_name, params=None, _return=False, **kwargs):
        if params is None:
            params = {}

        if kwargs:
            for k in kwargs:
                params[k] = kwargs[k]

        params['static_url_prefix'] = self.application.settings['static_url_prefix']
        params['is_login'] = self.get_secure_cookie('user.login')
        user = self.get_current_user()

        if user:
            params['__user__'] = {'name': user.fullname, 'isAdmin': user.role == User.ROLE_ADMIN}
            # доступные приложения
            ruleCollection = RuleCollection(self.getDBSession())
            params['user_apps'] = ruleCollection.getUserApps(user.userId)

        params['title'] = self.title
        params['currentAppCode'] = self.currentAppCode

        html = self.application.jinjaEnvironment.get_template(template_name).render(**params)
        if _return:
            return html

        self.write(html)

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

        self.currentAppCode = app.code

        # check access
        ruleService = RuleService(session)
        if not ruleService.isAllow(user.userId, app.appId):
            raise RuntimeError('Access denied')

        return app

    def prepare(self):
        self.title = u'Аналитика'
        self.currentAppCode = None
        if not self.application.isInstalled:
            self.redirect('/install/')

    def on_finish(self):
        self.removeDBSessions()
        super(BaseController, self).on_finish()

    def showFatalError(self, err=''):
        pass


class AjaxController(BaseController):

    def send_ajax_error(self, error):
        self.renderJSON({'error':error})

    def renderJSON(self, data):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(data))


class InstallController(BaseController):

    def render(self, template_name, params=None, _return=False, **kwargs):
        """
        Rewrite render without user
        """
        if params is None:
            params = {}
        params['static_url_prefix'] = self.application.settings['static_url_prefix']
        env = Environment(loader = PackageLoader('static', 'template'))
        self.write(env.get_template(template_name).render(**params))

    def prepare(self):
        if self.application.isInstalled:
            self.redirect('/')