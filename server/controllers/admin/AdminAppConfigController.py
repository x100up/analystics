# coding=utf-8

from AdminIndexController import AdminAction, AdminAjaxAction
from services.AppService import AppService
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


class IndexAction(BaseEditConfigAction):
    def get(self, *args, **kwargs):
        app, = args
        self.render('admin/appConfig/index.jinja2', {'appCode': app})


#-----------------------------------------------------------------------------------------------------------------------
#                                                   Events
#-----------------------------------------------------------------------------------------------------------------------

class EventListAction(BaseEditConfigAction):

    def get(self, *args, **kwargs):
        appCode = args[0]
        events = self.getAppConfig(args[0]).getEvents()
        events = sorted(events, key=lambda x: x.getName(), reverse=False)
        self.render('admin/appConfig/eventsList.jinja2', {'events': events, 'appCode':appCode, 'js_vars':{'appCode': appCode}})

class EditEvent(AdminAjaxAction, BaseEditConfigAction):

    def get(self, *args, **kwargs):
        appCode, = args
        eventCode = self.get_argument('eventCode', default=False)
        self.show(appCode, eventCode)


    def post(self, *args, **kwargs):
        '''
        Сохраняем пост
        '''
        appCode = self.get_argument('appCode', None)
        appConfig = self.getAppConfig(appCode)
        oldCode = self.get_argument('key_code_old', False)
        bunches = self.get_arguments('eventBunches', [])
        generalTags = self.get_arguments('generalTags', [])

        if oldCode:
            appEvent = appConfig.getEvent(oldCode)
        else:
            appEvent = AppEvent()

        appEvent.code = self.get_argument('key_code', None)
        appEvent.name = self.get_argument('key_name', None)
        appEvent.bunches = bunches

        # оставляем только персональные теги
        tags = {}
        for tagCode in appEvent.tags or []:
            if appEvent.tags[tagCode]:
                tags[tagCode] = appEvent.tags[tagCode]

        appEvent.tags = tags

        # добавляем выбранные общие
        for tagCode in generalTags:
            appEvent.tags[tagCode] = {}

        appConfig.addAppEvent(appEvent)

        if not oldCode == appEvent.code:
            appConfig.deleteEvent(oldCode)

        self.appService.saveConfig(appConfig.dumpToJSON())

        self.show(appCode, appEvent.code)

    def show(self, appCode, eventCode):
        appConfig = self.getAppConfig(appCode)
        if eventCode:
            event = appConfig.getEvent(eventCode)
            eventBunches = [bunch.code for bunch in appConfig.getEventBunches(eventCode)]
            personalTags = sorted(appConfig.getPersonalEventTags(eventCode), key=lambda x: x.getName(), reverse=False)
            eventGeneralTags = [appTag.code for appTag in appConfig.getGeneralEventTags(eventCode)]
        else:
            event = AppEvent()
            eventBunches = []
            personalTags = []
            eventGeneralTags = []

        bunches = appConfig.getBunches()

        generalTags = sorted(appConfig.getGeneralTags(), key=lambda x: x.getName(), reverse=False)

        self.render('admin/appConfig/editEvent.jinja2', {
            'event': event,
            'bunches': bunches,
            'appCode': appCode,
            'eventBunches': eventBunches,
            'generalTags': generalTags,
            'personalTags': personalTags,
            'eventGeneralTags': eventGeneralTags,
            'eventCode': eventCode,
            'js_vars': {'appCode': appCode}
        })



#-----------------------------------------------------------------------------------------------------------------------
#                                                   TAGS
#-----------------------------------------------------------------------------------------------------------------------

class TagListAction(BaseEditConfigAction):

    def get(self, *args, **kwargs):
        appCode = args[0]
        self.render('admin/appConfig/tagList.jinja2', {'tags':self.appService.getNewAppConfig(appCode).getGeneralTags(), 'app':appCode, 'js_vars':{'appCode': appCode}})

class EditTag(AdminAjaxAction, BaseEditConfigAction):

    def get(self, *args, **kwargs):
        appCode = self.get_argument('appCode')
        tagCode = self.get_argument('tagCode', default = False)
        eventCode = self.get_argument('eventCode', default = False)
        appConfig = self.getAppConfig(appCode)
        if eventCode and tagCode:
            tag = appConfig.getPersonalTag(eventCode, tagCode)
        elif tagCode:
            tag = appConfig.getGeneralTag(tagCode)
        else:
            tag = AppTag()
        self.render('admin/appConfig/editTag.jinja2', {'tag': tag, 'appCode': appCode, 'eventCode': eventCode})

    def post(self, *args, **kwargs):
        appCode = self.get_argument('appCode')
        appConfig = self.getAppConfig(appCode)

        tagOldCode = self.get_argument('tag_old_code', default = False)
        eventCode = self.get_argument('eventCode', default = False)

        # создаем или берем событие на основе формы
        if tagOldCode:
            if eventCode:
                tag = appConfig.getPersonalTag(eventCode, tagOldCode)
            else:
                tag = appConfig.getGeneralTag(tagOldCode)
        else:
            tag = AppTag()

        tag.name = self.get_argument("tag_name")
        tag.code = self.get_argument('tag_code')
        tag.type = self.get_argument("tag_type")

        if tag.type == 'choose':
            count = int(self.get_argument('tag_values_count', default=0))
            values = {}
            for index in range(0, count + 1):
                key = self.get_argument('tag_values_key_{}'.format(index), default=None)
                if key is None:
                    continue
                values[key] = self.get_argument('tag_values_value_{}'.format(index), default=None)

            if not len(values):
                self.errors.append(u'Для типа выбора (тег {0}) должен быть хотя бы один вариант'.format(tagCode))

            tag.values = values



        if tagOldCode and not tagOldCode == tag.code:
            appConfig.deleteTag(tagOldCode, eventCode)

        appConfig.addTag(tag, eventCode)

        if not self.errors:
            self.appService.saveConfig(appConfig.dumpToJSON())


#-----------------------------------------------------------------------------------------------------------------------
#                                                   BUNCHES
#-----------------------------------------------------------------------------------------------------------------------

class BunchListAction(BaseEditConfigAction):
    def get(self, *args, **kwargs):
        appCode, = args
        appConfig = self.getAppConfig(appCode)
        self.render('admin/appConfig/bunchList.jinja2',
                {'bunches': appConfig.getBunches(), 'app':appCode,
                 'js_vars': {'appCode': appCode}})


class EditBunchAction(AdminAjaxAction, BaseEditConfigAction):

    def get(self, *args, **kwargs):
        appCode = self.get_argument('appCode')
        bunchCode = self.get_argument('bunchCode')
        appConfig = self.getAppConfig(appCode)
        bunch = appConfig.getBunch(bunchCode)
        self.render('admin/appConfig/editBunch.jinja2', {'bunch': bunch, 'tags': appConfig.getGeneralTags(), 'appCode': appCode})

    def post(self, *args, **kwargs):
        appCode = self.get_argument('appCode')
        appConfig = self.getAppConfig(appCode)
        oldBunchCode = self.get_argument('bunch_old_code', False)

        if oldBunchCode:
            bunch = appConfig.getBunch(oldBunchCode)
        else:
            bunch = AppTagBunch()

        bunch.code = self.get_argument('bunch_code', '')
        bunch.name = self.get_argument('bunch_name', '')
        bunch.tags = self.get_arguments('bunch_tag', [])

        if oldBunchCode and not oldBunchCode == bunch.code:
            appConfig.deleteBunch(oldBunchCode)

        appConfig.addBunch(bunch)
        self.appService.saveConfig(appConfig.dumpToJSON())
        self.renderJSON({'success': True})
