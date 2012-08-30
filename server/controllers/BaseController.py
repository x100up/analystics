from jinja2 import Template, Environment, PackageLoader
from sqlalchemy.orm import sessionmaker
import tornado.web, json
from sqlalchemy import create_engine
from models.User import User

class BaseController(tornado.web.RequestHandler):

    dbSessionMaker = False
    def getSessionMaker(self):
        if not self.dbSessionMaker:
            mysqlConfig = self.getConfig("mysql")
            engine = create_engine('mysql://' + mysqlConfig['user'] + ':' + mysqlConfig['password'] + '@'
                                   + mysqlConfig['host'] + '/' + mysqlConfig['dbname']+'?init_command=set%20names%20%22utf8%22', encoding='utf8', convert_unicode=True)
            self.dbSessionMaker = sessionmaker(bind=engine, autoflush=False)
            engine.execute('SET NAMES utf8')
        return self.dbSessionMaker

    def getDBSession(self):
        return  self.getSessionMaker()()

    def get_current_user(self):
        login = self.get_secure_cookie('user.login')
        if login:
            session = self.getDBSession()
            user = session.query(User).filter_by(login = login).first()
            session.flush()
            return user

        return None

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

    def render(self, template_name, dict = None):
        if dict is None:
            dict = {}
        dict['is_login'] = self.get_secure_cookie('user.login')

        env = Environment(loader = PackageLoader('static', 'template'))
        self.write(env.get_template(template_name).render(**dict))


class AjaxController(BaseController):

    def send_ajax_error(self):
        pass

    def renderJSON(self, data):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(data))