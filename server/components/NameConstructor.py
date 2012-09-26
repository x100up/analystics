# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'


class NameConstructor(object):

    def __init__(self, appConfig, task):
        self.appConfig = appConfig
        self.task = task

    def getKeyNameByIndex(self, index, params):
        '''
        return key name by taskItem index
        '''

        tagSettings = self.appConfig['tagSettings']

        taskItem = self.task.getTaskItem(index)
        if taskItem:
            key_name = '#' + str(index)
            tag_name = u'Количество'
            operation = ''

            key = taskItem.key
            if self.appConfig['keys'].has_key(key) and self.appConfig['keys'][key].has_key('name'):
                key_name = self.appConfig['keys'][key]['name'] + key_name

            if params.has_key('tag'):
                tag_key = params['tag']
                if tagSettings.has_key(tag_key) and tagSettings[tag_key].has_key('name'):
                    tag_name = tagSettings[tag_key]['name']

            if params.has_key('op'):
                if params['op'] == 'avg':
                    operation = u'среднее'
                elif params['op'] == 'sum':
                    operation = u'сумма'


            return tag_name  + '(' + key_name + ')' + operation

        return 'not name for task item: ' + str(index)

    def getParamNameValue(self, tagName, value):
        '''

        '''
        tag_name = tagName
        tag_value = value

        if tagName in self.appConfig['tags']:
            tagConf = self.appConfig['tagSettings'][tagName]
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
