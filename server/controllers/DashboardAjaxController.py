# -*- coding: utf-8 -*-
from BaseController import AjaxController
from service.AppService import AppService
import re

class KeyAutocompleteAction(AjaxController):

    def get(self, *args, **kwargs):
        appName = self.get_argument('app', None)
        query = self.get_argument('query', None)
        if appName is None:
            self.send_ajax_error('Неверный запрос')

        appService = AppService(self.getConfig('core', 'app_config_path'))
        config = appService.getAppKeyConfig(appName)
        keysList = config['keys'].keys()

        regexp = re.compile('^' + query + '.*')
        list = filter(lambda x:regexp.match(x) , keysList)

        self.renderJSON({'query' : query, 'suggestions' : list})


class KeyConfigurationAction(AjaxController):

    def post(self, *args, **kwargs):
        keyName = self.get_argument('key', None)
        appName = self.get_argument('app', None)
        index = self.get_argument('index', 1)

        appService = AppService(self.getConfig('core', 'app_config_path'))
        tags = {
            "mustHaveTags": appService.getConfigTags(appName, keyName, 'must'),
            "canHaveTags": appService.getConfigTags(appName, keyName, 'can'),
        }

        self.render('blocks/tag_container.jinja2', {'tags':tags, 'key': keyName, 'index': index})


