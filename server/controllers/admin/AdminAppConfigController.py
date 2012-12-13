# coding=utf-8

from AdminIndexController import AdminAction
from services.AppService import AppService
from components.AnalyticsException import AnalyticsException
from models.appConf.AppEvent import AppEvent
from models.appConf.AppTag import AppTag
from models.appConf.AppTagBunch import AppTagBunch


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

class IndexAction(BaseEditConfigAction):

    def get(self, *args, **kwargs):
        app, = args

        self.render('admin/appConfig/index.jinja2', {'app': app})




class EventEditAction(BaseEditConfigAction):

    def get(self, *args, **kwargs):
        appCode = args[0]
        self.render('admin/appConfig/editEvents.jinja2', {'events': self.getAppConfig(args[0]).getEvents(), 'app':appCode})

    def post(self, *args, **kwargs):
        appCode = args[0]
        appConfig = self.getAppConfig(appCode)

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

        self.render('admin/appConfig/editEvents.jinja2', {'events':self.appService.getNewAppConfig(args[0]).getEvents(), 'app':appCode})


class EditTagAction(BaseEditConfigAction):

    def get(self, *args, **kwargs):
        appCode = args[0]
        self.render('admin/appConfig/editTags.jinja2', {'tags':self.appService.getNewAppConfig(appCode).getTags(), 'app':appCode})

    def post(self, *args, **kwargs):
        appCode, = args
        self.app_code = appCode
        appConfig = self.getAppConfig(appCode)

        tagIndexes = self.get_arguments('tag_index')
        for tagIndex in tagIndexes:
            tagCode = self.get_argument('tag_{}_code'.format(tagIndex), False)
            tagOldCode = self.get_argument('tag_{}_old_code'.format(tagIndex), False)
            if not tagCode:
                continue

            # создаем или берем событие на основе формы
            if tagOldCode:
                newTag = appConfig.getTag(tagOldCode)
            else:
                newTag = AppTag()

            # меняем его свойства
            newTag.name = self.get_argument("tag_{}_name".format(tagIndex), default='')
            newTag.code = tagCode
            newTag.type = self.get_argument("tag_{}_type".format(tagIndex))

            if newTag.type == 'choose':
                count = int(self.get_argument('tag_{}_values_count'.format(tagIndex), default=0))
                values = {}
                for index in range(0, count + 1):
                    key = self.get_argument('tag_{}_values_key_{}'.format(tagIndex, index), default=None)
                    if key is None:
                        continue
                    values[key] = self.get_argument('tag_{}_values_value_{}'.format(tagIndex, index), default=None)

                if not len(values):
                    self.errors.append(u'Для типа выбора (тег {0}) должен быть хотя бы один вариант'.format(tagCode))

                newTag.values = values

            if tagOldCode:
                appConfig.deleteTag(tagOldCode)

            appConfig.addTag(newTag)

        if not self.errors:
            self.appService.saveConfig(appConfig.dumpToJSON())

        self.render('admin/appConfig/editTags.jinja2', {'tags':appConfig.getTags(), 'app':appCode})


class EditBunchAction(BaseEditConfigAction):
    def get(self, *args, **kwargs):
        appCode, = args
        appConfig = self.getAppConfig(appCode)
        self.render('admin/appConfig/editBunches.jinja2',
                {'tags': appConfig.getTags(), 'bunches': appConfig.getBunches(), 'app':appCode,
                 'js_vars': {'appCode': appCode}})

    def post(self, *args, **kwargs):
        appCode, = args
        appConfig = self.getAppConfig(appCode)

        bunchIndexes = self.get_arguments('bunch_index')
        for bunchIndex in bunchIndexes:
            bunchCode = self.get_argument('bunch_code_{}'.format(bunchIndex), False)
            if not bunchCode:
                continue

            oldBunchCode = self.get_argument('bunch_old_code_{}'.format(bunchIndex), False)
            if oldBunchCode:
                bunch = appConfig.getBunch(oldBunchCode)
            else:
                bunch = AppTagBunch()

            bunch.code = bunchCode
            bunch.name = self.get_argument('bunch_name_{}'.format(bunchIndex), '')
            bunch.tags = self.get_arguments('bunch_tag_{}'.format(bunchIndex), [])

            if oldBunchCode:
                appConfig.deleteBunch(oldBunchCode)

            appConfig.addBunch(bunch)


        self.appService.saveConfig(appConfig.dumpToJSON())


        self.render('admin/appConfig/editBunches.jinja2',
                {'tags': appConfig.getTags(), 'bunches': appConfig.getBunches(), 'app':appCode,
                 'js_vars': {'appCode': appCode}})


class EditReferencesAction(BaseEditConfigAction):

    def get(self, *args, **kwargs):
        appCode, = args
        appConfig = self.getAppConfig(appCode)
        self.render('admin/appConfig/editReferences.jinja2', {
            'appConfig': appConfig,
            'app':appCode,
        })

    def post(self, *args, **kwargs):
        appCode, = args
        appConfig = self.getAppConfig(appCode)

        for appEvent in appConfig.getEvents():
            # теги
            tags = self.get_arguments('ref_tag_{}'.format(appEvent.code))
            appEvent.tags = {}
            if tags:
                for tag in tags:
                    appEvent.tags[tag] = {}

            # банчи
            bunches = self.get_arguments('ref_bunch_{}'.format(appEvent.code))
            appEvent.bunches = {}
            if bunches:
                for bunch in bunches:
                    appEvent.bunches[bunch] = {}

        self.appService.saveConfig(appConfig.dumpToJSON())

        self.render('admin/appConfig/editReferences.jinja2', {
            'appConfig': appConfig,
            'app':appCode,
        })