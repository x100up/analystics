# -*- coding: utf-8 -*-
from BaseController import AjaxController
from service.AppService import getAppKeyConfig, getConfigTags
import re

class KeyAutocompleteAction(AjaxController):

    def get(self, *args, **kwargs):
        appName = self.get_argument('app', None)
        query = self.get_argument('query', None)
        if appName is None:
            self.send_ajax_error('Неверный запрос')

        config = getAppKeyConfig(appName)
        keysList = config['keys'].keys()

        regexp = re.compile('^' + query + '.*')
        list = filter(lambda x:regexp.match(x) , keysList)

        self.renderJSON({'query' : query, 'suggestions' : list})


class KeyConfigurationAction(AjaxController):

    def get(self, *args, **kwargs):
        keyName = self.get_argument('key', None)
        appName = self.get_argument('app', None)
        config = getAppKeyConfig(appName)

        raw_json = {
            "mustHaveTags": getConfigTags(config, keyName, 'must'),
            "canHaveTags": getConfigTags(config, keyName, 'can'),
        }




        self.renderJSON(raw_json)


