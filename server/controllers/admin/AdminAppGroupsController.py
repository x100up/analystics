# coding=utf-8

from AdminIndexController import AdminAction
from services.AppService import AppService

class IndexAction(AdminAction):
    def _prepare(self, appCode):
        self.appService = AppService(self.application.getAppConfigPath())
        self.appConfig = self.appService.getNewAppConfig(appCode=appCode)

    def get(self, *args, **kwargs):
        app = self.checkAppAccess(args)
        self._prepare(app.code)
        self.renderPage()

    def renderPage(self):
        self.render('admin/groups/app_groups.jinja2', {
            'appConfig':self.appConfig,
            'js_vars': {
                'groupsCount': 0
            }
        })

    def post(self, *args, **kwargs):
        app = self.checkAppAccess(args)
        self._prepare(app.code)
        # events
        eventGroupIterator = self.get_argument('eventGroupIterator', default=None)
        groups = {}
        if eventGroupIterator:
            for index in range(0, int(eventGroupIterator) + 1):
                groupName = self.get_argument('group_event_' + str(index), default=None)
                if groupName:
                    groups[index] = groupName

        eventGroups = {}
        for event in self.appConfig.getEvents():
            groupIDs = self.get_arguments('group_event_' + event.code)
            if groupIDs:
                for groupId in groupIDs:
                    groupId = int(groupId)
                    if not eventGroups.has_key(groupId):
                        eventGroups[groupId] = []
                    eventGroups[groupId].append(event.code)

        self.appConfig.clearEventsGroups()

        for index in groups:
            i = self.appConfig.addEventGroup(groups[index])
            if eventGroups.has_key(index):
                for eventCode in eventGroups[index]:
                    self.appConfig.setEventGroup(i, eventCode)

        # tags
        tagGroupIterator = self.get_argument('tagGroupIterator', default=None)
        groups = {}
        if tagGroupIterator:
            for index in range(0, int(tagGroupIterator) + 1):
                groupName = self.get_argument('group_tag_' + str(index), default=None)
                if groupName:
                    groups[index] = groupName

        tagGroups = {}
        for tag in self.appConfig.getTags():
            groupIds = self.get_arguments('group_tag_' + tag['code'])
            if groupIds:
                for groupId in groupIds:
                    groupId = int(groupId)
                    if not tagGroups.has_key(groupId):
                        tagGroups[groupId] = []
                    tagGroups[groupId].append(tag['code'])

        self.appConfig.clearTagGroups()
        for index in groups:
            i = self.appConfig.addTagGroup(groups[index])
            if tagGroups.has_key(index):
                for tagCode in tagGroups[index]:
                    self.appConfig.setTagGroup(i, tagCode)

        self.appService.newSaveConfig(self.appConfig)

        self.renderPage()
