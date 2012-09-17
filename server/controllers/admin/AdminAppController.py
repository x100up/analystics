# -*- coding: utf-8 -*-
from __builtin__ import len
from exceptions import RuntimeError
from AdminIndexController import AdminAction
from models.App import App
from service.AppService import AppService
import tornado.web

class IndexAction(AdminAction):

    def prepare(self):
        self.adminAuthenticated()
        self.apps = []

    def loadAppList(self):
        db = self.getDBSession()
        self.apps = db.query(App).filter_by(status = App.STATUS_ACTIVE).all()
        appService = AppService(self.application.getAppConfigPath())
        self.app_files = appService.getKnowAppList()
        exist_app_code = []
        for app in self.apps:
            exist_app_code.append(app.code)

        self.new_app_code = [app_code for app_code in self.app_files if app_code not in set(exist_app_code)]

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.loadAppList()
        self.run()

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        action = self.get_argument('action', False)
        if action == u'Удалить':
            ids = self.get_arguments('appIds')
            if ids:
                db = self.getDBSession()
                db.query(App).filter(App.appId.in_(ids)).update({'status': App.STATUS_DELETED}, synchronize_session = 'fetch')
                db.commit()

        self.loadAppList()
        self.run()

    def run(self):
        self.render('admin/apps.jinja2', {'apps': self.apps, 'new_app_codes': self.new_app_code, 'app_files': self.app_files})



class EditAction(AdminAction):

    def prepare(self):
        self.errors = []
        self.app = None

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.adminAuthenticated()

        appId = self.get_argument('appId', None)
        if appId:
            db = self.getDBSession()
            self.app = db.query(App).filter(App.appId == appId).first()
        else:
            self.app = App()
            self.app.code = self.app.name = self.get_argument('code', '')

        self.run()

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        self.adminAuthenticated()

        db = self.getDBSession()

        appId = self.get_argument('appId', '')
        if len(appId):
            self.app = db.query(App).filter(App.appId == appId).first()
            if not self.app:
                raise RuntimeError('Can`t find app for editing')
        else:
            self.app = App()

        name = self.get_argument('name', '')
        code = self.get_argument('code', '')
        errors = []

        if len(name) == 0:
            errors.append(u'Название не должно быть пустое')
        else:
            self.app.name = name

        if len(code) == 0:
            errors.append(u'Код не должен быть пустым')
        else:
            self.app.code = code

        if not len(errors):
            db.merge(self.app)
            db.commit()
            self.redirect('/admin/apps/')
        else:
            self.run()

    def run(self):
        self.render('admin/app_edit.jinja2', {'app': self.app, 'errors': self.errors})
