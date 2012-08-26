# -*- coding: utf-8 -*-
from BaseController import BaseController
from models.User import User
import tornado.web

class AdminAction(BaseController):
    def adminAuthenticated(self):
        '''
        Админ ли пользователь
        '''
        user = self.get_current_user()
        if user.role != User.ROLE_ADMIN:
            self.redirect('/dashboard');

class IndexAction(AdminAction):

    @tornado.web.authenticated
    def get(self):
        self.adminAuthenticated()
        self.render('admin/index.jinja2')


class UserAction(AdminAction):
    @tornado.web.authenticated
    def get(self):
        self.adminAuthenticated()
        self.render('admin/users.jinja2')


class EditUserAction(AdminAction):
    @tornado.web.authenticated
    def get(self):
        self.adminAuthenticated()
        self.render('admin/users_edit.jinja2')


    def post(self):
        self.adminAuthenticated()

        newUser = User()
        newUser.login = self.get_argument('login')
        newUser.password = self.get_argument('password')

        dbsession = self.getDBSession()
        dbsession.add(newUser)
        dbsession.commit()