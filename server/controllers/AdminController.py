# -*- coding: utf-8 -*-
from BaseController import BaseController
from models.User import User
import tornado.web



class IndexAction(BaseController):

    @tornado.web.authenticated
    def get(self):
        self.adminAuthenticated()
        self.render('admin/index.jinja2')


    def adminAuthenticated(self):
        '''
        Админ ли пользователь
        '''
        user = self.get_current_user()
        if user.role != User.ROLE_ADMIN:
            self.redirect('/dashboard');