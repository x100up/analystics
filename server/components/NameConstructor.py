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

            operation = ''
            print params
            for param in params:
                print param
                if param['op'] == 'group':
                    tag_key = param['tag']
                    if tagSettings.has_key(tag_key) and tagSettings[tag_key].has_key('name'):
                        tag_name = tagSettings[tag_key]['name']
                        operation += tag_name + '=' + str(param['value'])

                else:
                    if param['op'] == 'avg':
                        operation += u'/среднее'
                    elif param['op'] == 'sum':
                        operation += u'/сумма'
                    elif param['op'] == 'count':
                        operation += u'/кол-во'


            return  key_name + operation

        return 'not name for task item: ' + str(index)

    def getTableName(self, index, params):
        '''
        return key name by taskItem index
        '''

        tagSettings = self.appConfig['tagSettings']

        taskItem = self.task.getTaskItem(index)
        if taskItem:
            tag_name = u'Количество'
            operation = ''
            key = taskItem.key
            key_name = key
            if self.appConfig['keys'].has_key(key) and self.appConfig['keys'][key].has_key('name'):
                key_name = self.appConfig['keys'][key]['name']

            operation = ''
            for param in params:
                if param['op'] == 'group':
                    tag_key = param['tag']
                    if tagSettings.has_key(tag_key) and tagSettings[tag_key].has_key('name'):
                        tag_name = tagSettings[tag_key]['name']
                        operation += ' ' + tag_name + '=' + self.getParamNameValue(tag_key, param['value'])
                else:
                    if param['op'] == 'avg':
                        operation += u'/среднее'
                    elif param['op'] == 'sum':
                        operation += u'/сумма'
                    elif param['op'] == 'count':
                        operation += u'/кол-во'


            return key_name + operation

        return 'not name for task item: ' + str(index)

    def getParamNameValue(self, tagName, value):
        '''

        '''
        tag_value = value

        if tagName in self.appConfig['tags']:
            tagConf = self.appConfig['tagSettings'][tagName]

            type = None
            if tagConf.has_key('type'):
                type = tagConf['type']

                if type == 'choose':
                    if tagConf.has_key('values') and tagConf['values'].has_key(value):
                        tag_value = tagConf['values'][value]

                elif type == 'boolean':
                    if bool(value):
                        tag_value = u'Да'
                    else:
                        tag_value = u'Нет'

        return tag_value

    def getSeriaName(self):
        return 'seria name'
