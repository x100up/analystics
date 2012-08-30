# -*- coding: utf-8 -*-
from __builtin__ import len
from exceptions import RuntimeError
from AdminIndexController import AdminAction
import tornado.web
from models.App import App

class IndexAction(AdminAction):
    @tornado.web.authenticated
    def get(self):
        self.adminAuthenticated()

        db = self.getDBSession()
        apps = db.query(App).all()

        self.render('admin/apps.jinja2', {'apps': apps})

class EditAction(AdminAction):
    @tornado.web.authenticated
    def get(self):
        self.adminAuthenticated()

        appId = self.get_argument('appId', None)
        if appId:
            db = self.getDBSession()
            app = db.query(App).filter(App.appId == appId).first()
        else:
            app = App()

        self.render('admin/app_edit.jinja2', {'app': app})

    def post(self):
        self.adminAuthenticated()

        db = self.getDBSession()
        appId = self.get_argument('appId', '')
        if len(appId):
            app = db.query(App).filter(App.appId == appId).first()
            if not app:
                raise RuntimeError('Can`t find app for editing')
        else:
            app = App()

        name = self.get_argument('name', '')
        code = self.get_argument('code', '')
        errors = []

        if len(name) == 0:
            errors.append(u'Название не должно быть пустое')
        else:
            app.name = name

        if len(code) == 0:
            errors.append(u'Код не должен быть пустым')
        else:
            app.code = code

        if not len(errors):
            db.merge(app)
            db.commit()
            self.redirect('/admin/apps/')
        else:
            self.render('admin/app_edit.jinja2', {'app':app, 'errors' : errors})

