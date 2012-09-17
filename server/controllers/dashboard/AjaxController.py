# -*- coding: utf-8 -*-
from controllers.BaseController import AjaxController
from service.AppService import AppService
from models.Task import TaskItem
from datetime import timedelta
import re

class KeyAutocompleteAction(AjaxController):

    def get(self, *args, **kwargs):
        appName = self.get_argument('app', None)
        query = self.get_argument('query', None)
        if appName is None:
            self.send_ajax_error('Неверный запрос')

        appService = AppService(self.application.getAppConfigPath())
        config = appService.getAppConfig(appName)
        keysList = config['keys'].keys()

        regexp = re.compile('^' + query + '.*')
        list = filter(lambda x:regexp.match(x) , keysList)

        self.renderJSON({'query' : query, 'suggestions' : list})


class KeyConfigurationAction(AjaxController):

    def post(self, *args, **kwargs):
        keyName = self.get_argument('key', None)
        appName = self.get_argument('app', None)
        index = self.get_argument('index', 1)

        appService = AppService(self.application.getAppConfigPath())
        tags = {
            "mustHaveTags": appService.getAppTags(appName, keyName, 'mustHave'),
            "canHaveTags": appService.getAppTags(appName, keyName, 'canHave'),
            "autoLoadTags": appService.getAppTags(appName, keyName, 'autoLoad'),
        }

        self.render('blocks/tag_container.jinja2', {'tags':tags, 'key': keyName, 'index': index, 'values':{}})

class GetKeyForm(AjaxController):
    def post(self, *args, **kwargs):
        keyIndex = self.get_argument('index')
        taskItem = TaskItem(delta = timedelta(days = -1))
        taskItem.index = keyIndex
        self.render('blocks/key_container.jinja2', {'taskItem':taskItem})

class GetKeys(AjaxController):
    def get(self, appName):
        keyIndex = self.get_argument('index')
        self.checkAppAccess(appName)
        appService = AppService(self.application.getAppConfigPath())
        keys = appService.getKeys(appName)
        self.render('blocks/key_select.jinja2', {'_keys':keys, 'index':keyIndex})


