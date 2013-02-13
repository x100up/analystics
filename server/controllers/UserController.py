# coding=utf-8
from BaseController import BaseController
from models.User import User
from models.UserAppRule import UserAppRule, RuleCollection
import tornado.web
import hashlib

class AuthAction(BaseController):
    def get(self, *args, **kwargs):
        self.render('user/login.jinja2')

    def post(self):
        login = self.get_argument('login', False)
        password = self.get_argument('pass', False)

        db = self.getDBSession()
        user = db.query(User).filter_by(login = login, password = hashlib.sha256(password).hexdigest()).first()
        if user:
            self.set_secure_cookie("user.login", user.login)
            self.redirect("/dashboard")




        else:
            self.get(self)

class LogoutAction(BaseController):
    """
        Выход из приложения
    """
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.clear_cookie("user.login")
        self.redirect("/user/logout")
