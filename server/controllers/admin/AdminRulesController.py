# -*- coding: utf-8 -*-
from controllers.BaseController import AjaxController
from models.User import User
from models.App import App
from models.UserAppRule import UserAppRule, RuleCollection
import tornado.web
from AdminIndexController import AdminAction


class IndexAction(AdminAction):

    @tornado.web.authenticated
    def get(self):
        self.adminAuthenticated()

        db = self.getDBSession()
        users = db.query(User).all()
        apps = db.query(App).all()
        ruleCollection = RuleCollection(db)
        ruleCollection.loadAll()

        self.render('admin/rules.jinja2', {'users':users, 'apps':apps, 'ruleCollection':ruleCollection})


class SwitchAjaxAction(AjaxController, AdminAction):

    @tornado.web.authenticated
    def post(self):
        self.adminAuthenticated()
        appId = self.get_argument('appId', None)
        userId = self.get_argument('userId', None)
        action = self.get_argument('action', None)

        if appId is None:
            self.send_ajax_error(u'Отсутствует идентифкатор приложения')

        if userId is None:
            self.send_ajax_error(u'Отсутствует идентифкатор пользователя')

        if action is None:
            self.send_ajax_error(u'Отсутствует действие')

        db = self.getDBSession()

        if action == 'ALLOW':
            appRule = UserAppRule()
            appRule.userId = userId
            appRule.appId = appId
            appRule.rule = UserAppRule.RULE_ALLOW
            db.merge(appRule)
            db.commit()
        elif action == 'DENY':
            appRule = UserAppRule()
            appRule.userId = userId
            appRule.appId = appId
            appRule.rule = UserAppRule.RULE_DENY
            db.merge(appRule)
            db.commit()
        else:
            self.send_ajax_error(u'Неизвестное действие')
            return None


        self.renderJSON({'status' : action})
