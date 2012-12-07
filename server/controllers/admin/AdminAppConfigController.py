# coding=utf-8

from AdminIndexController import AdminAction
from services.AppService import AppService
from components.AnalyticsException import AnalyticsException
from models.appConf.AppEvent import AppEvent


class BaseEditConfigAction(AdminAction):
    def prepare(self):
        super(BaseEditConfigAction, self).prepare()
        self.errors = []
        self.appService = AppService(self.application.getAppConfigPath())

    def getAppConfig(self, appCode):
        return self.appService.getNewAppConfig(appCode)

    def listDiff(self, a, b):
        b = set(b)
        return [aa for aa in a if aa not in b]


class EventEditAction(BaseEditConfigAction):

    def get(self, *args, **kwargs):
        self.render('admin/appConfig/editEvents.jinja2', {'events': self.getAppConfig(args[0]).getEvents()})

    def post(self, *args, **kwargs):
        appConfig = self.getAppConfig(args[0])

        eventIndexes = self.get_arguments('key_index')
        if eventIndexes:
            eventCodes = []
            for index in eventIndexes:
                appEvent = AppEvent()
                appEvent.code = self.get_argument('key_{}_code'.format(index), None)
                appEvent.name = self.get_argument('key_{}_name'.format(index), None)
                oldEventCode = self.get_argument('key_{}_code_old'.format(index), None)
                appConfig.mergeAppEvent(appEvent, oldEventCode)
                eventCodes.append(appEvent.code)

            # удаляем удаленные
            existCodes = appConfig.getEventsCodes()

            forRemove = self.listDiff(existCodes, eventCodes)
            if forRemove:
                for code in forRemove:
                    appConfig.deleteEvent(code)

        self.appService.saveConfig(appConfig.dumpToJSON())

        self.render('admin/appConfig/editEvents.jinja2', {'events':self.appService.getNewAppConfig(args[0]).getEvents()})



class TagEditAction(AdminAction):
    def prepare(self):
        super(TagEditAction, self).prepare()
        self.errors = []
        self.appService = AppService(self.application.getAppConfigPath())

    def post(self, *args, **kwargs):
        app_code, = args
        self.app_code = app_code

        tag_indexes = self.get_arguments('tag_index')

        tags = {}
        tag_codes = {}
        for tag_index in tag_indexes:
            tag_code = self.get_argument('tag_{}_code'.format(tag_index), False)
            if not tag_code:
                continue

            tag_codes[tag_index] = tag_code

            tags[tag_code] = {}
            tags[tag_code]['type'] = self.get_argument("tag_{}_type".format(tag_index))
            tags[tag_code]['name'] = self.get_argument("tag_{}_name".format(tag_index), default='')
            if tags[tag_code]['type'] == 'choose':
                count = int(self.get_argument('tag_{}_values_count'.format(tag_index), default=0))
                values = {}
                isDict = False

                for index in range(0, count + 1):
                    key = self.get_argument('tag_{}_values_key_{}'.format(tag_index, index), default=None)
                    value = self.get_argument('tag_{}_values_value_{}'.format(tag_index, index), default=None)
                    if key is None:
                        continue
                    if not isDict:
                        isDict = not value is None
                    values[key] = value

                if not isDict:
                    values = values.keys()

                if not len(values):
                    self.errors.append(u'Для типа выбора (тег {0}) должен быть хотя бы один вариант'.format(tag_code))

                tags[tag_code]['values'] = values

        bunch_indexes = self.get_arguments('bunch_index')
        bunches = {}
        bunch_codes = {}
        for bunch_index in bunch_indexes:
            bunch_code = self.get_argument('bunch_code_{}'.format(bunch_index), False)
            bunch_name = self.get_argument('bunch_name_{}'.format(bunch_index), False)
            bunch_codes[bunch_index] = bunch_code
            bunches[bunch_code] = {'tags':[]}
            if bunch_name:
                bunches[bunch_code]['name'] = bunch_name

            tag_indexes = self.get_arguments('bunch_tag_{}'.format(bunch_index))
            for tag_index in tag_indexes:
                bunches[bunch_code]['tags'].append(tag_codes[tag_index])


            tag_indexes = self.get_arguments('key_tag_' + index)
            if tag_indexes:
                for tag_index in tag_indexes:
                    tag_code = tag_codes[tag_index]
                    if tag_code and tags.has_key(tag_code):
                        if not keys[eventCode].has_key('tags'):
                            keys[eventCode]['tags'] = {}
                        keys[eventCode]['tags'][tag_code] = {}

                bunch_indexes = self.get_arguments('key_bunch_' + index)
                if bunch_indexes:
                    keys[eventCode]['bunches'] = {}
                    for bunch_index in bunch_indexes:
                        keys[eventCode]['bunches'][bunch_codes[bunch_index]] = {}

        if not self.errors:
            self.appService.saveSettings(app_code, tags = tags, keys = keys, bunches = bunches)

        self.run(tags, keys, bunches)


    def showTags(self, app_code):
        tags = {}
        try:
            raw_tags = self.appService.getTagList(app_code)
            settings = self.appService.getTagSettings(app_code)
            for tag in raw_tags:
                tags[tag] = {}
                if settings.has_key(tag):
                    tags[tag] = settings[tag]
        except AnalyticsException as analyticsException:
            self.errors.append(analyticsException.message)

        keys = {}
        bunches = {}
        try:
            bunches = self.appService.getBunches(app_code)
            keys = self.appService.getKeys(app_code)
        except AnalyticsException as analyticsException:
            self.errors.append(analyticsException.message)

        self.run(tags, keys, bunches)

    def get(self, *args, **kwargs):
        app_code, = args

        if not self.appService.isConfigExist(app_code):
            self.appService.createEmptyConfig(app_code)
        self.app_code = app_code
        self.showTags(app_code)


    def run(self, appConfig):
        dict = {
            'appConfig': appConfig,
            'errors': self.errors
        }

        tag_indexes = {}
        i = 0
        for tag_name, tag_data in tags.items():
            tag_indexes[tag_name] = i
            i += 1

        bunch_indexes = {}
        bunch_cache = {}
        i = 0
        for bunch_code, bunch_data in bunches.items():
            bunch_indexes[bunch_code] = i
            bunch_cache[i] = []
            for tag_code in bunch_data['tags']:
                bunch_cache[i].append(tag_indexes[tag_code])
            i += 1

        # кеш связей
        relation_cache = {'tag':{}, 'bunch':{}}
        for index, key_code in enumerate(keys):
            index = int(index)
            relation_cache['tag'][index] = []
            relation_cache['bunch'][index] = []
            key_data = keys[key_code]
            if key_data.has_key(AppService.TAGS_JSON_INDEX):
                for tag_code in key_data[AppService.TAGS_JSON_INDEX].keys():
                    relation_cache['tag'][index].append(tag_indexes[tag_code])
            if key_data.has_key(AppService.BUNCHES_JSON_INDEX):
                for bunch_code in key_data[AppService.BUNCHES_JSON_INDEX].keys():
                    relation_cache['bunch'][index].append(bunch_indexes[bunch_code])

        dict['js_vars'] = {'relation_cache': relation_cache, 'bunch_cache':bunch_cache, 'appCode': self.app_code}
        self.render('admin/editTags.jinja2', dict)