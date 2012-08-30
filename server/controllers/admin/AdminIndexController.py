# -*- coding: utf-8 -*-

from controllers.BaseController import BaseController
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


