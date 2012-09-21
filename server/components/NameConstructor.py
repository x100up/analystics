# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'


class NameConstructor(object):

    def __init__(self, appConfig, task):
        self.appConfig = appConfig
        self.task = task

    def getKeyNameByIndex(self, index):
        '''
        return key name by taskItem index
        '''
        taskItem = self.task.getTaskItem(index)
        if taskItem:
            key = taskItem.key
            if self.appConfig['keys'].has_key(key) and self.appConfig['keys'][key].has_key('name'):
                return self.appConfig['keys'][key]['name']
        return 'not name for index ' + str(index)

    def getParamNameValue(self, tagName, value):
        '''

        '''
        tag_name = tagName
        tag_value = value

        if self.appConfig['tags'].has_key(tagName):
            tagConf = self.appConfig['tags'][tagName]
            if tagConf.has_key('name'):
                tag_name = tagConf['name']

            type = None
            if tagConf.has_key('type'):
                type = tagConf['type']

            extra = []
            if tagConf.has_key('extra'):
                extra = tagConf['extra']

            if type == 'choose':
                if 'keyValues' in extra and tagConf['values'].has_key(value):
                    tag_value = tagConf['values'][value]

            elif type == 'boolean':
                if bool(value):
                    tag_value = u'Да'
                else:
                    tag_value = u'Нет'

        return u'{0} = {1}'.format(tag_name, tag_value)

    def getSeriaName(self):
        return 'seria name'
