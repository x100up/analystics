# coding=utf-8
from models.appConf.EventGroup import EventGroup
from models.appConf.TagGroup import TagGroup
from models.appConf.AppEvent import AppEvent
from models.appConf.AppTag import AppTag
from models.appConf.AppTagBunch import AppTagBunch

class AppConfig():
    def __init__(self, data = None):
        if data:
            self.data = data
        else:
            self.data = {}
        self.events = {}
        self.tagGroups = {}
        self.eventGroups = {}
        self.tags = {}
        self.bunches = {}
        self.prepareData()

    def prepareData(self):
        if self.data.has_key('keys'):
            for rawEvent in self.data['keys']:
                appEvent = AppEvent(rawEvent)
                self.events[appEvent.code] = appEvent

        if self.data.has_key('tags'):
            for rawTag in self.data['tags']:
                appTag = AppTag(rawTag)
                self.tags[appTag.code] = appTag

        if self.data.has_key('tagGroups'):
            for rawTagGroups in self.data['tagGroups']:
                tagGroup = TagGroup(rawTagGroups)
                self.tagGroups[tagGroup.index] = tagGroup

        if self.data.has_key('eventGroups'):
            for rawEventGroups in self.data['eventGroups']:
                eventGroup = EventGroup(rawEventGroups)
                self.eventGroups[eventGroup.index] = eventGroup

        if self.data.has_key('bunches'):
            for rawBunch in self.data['bunches']:
                appTagBunch = AppTagBunch(rawBunch)
                self.bunches[appTagBunch.code] = appTagBunch


    def getEvents(self):
        return self.events.values()

    def getEvent(self, eventCode):
        return self.events[eventCode]

    def deleteEvent(self, eventCode):
        if self.isEventExist(eventCode):
            del self.events[eventCode]


    def deleteTag(self, tagCode, eventCode = None):
        if eventCode:
            if self.isEventExist(eventCode):
                event = self.getEvent(eventCode)
                del event.tags[tagCode]
        else:
            if self.isTagExist(tagCode):
                del self.tags[tagCode]

    def getGeneralTags(self):
        """
        Общие теги
        """
        return self.tags.values()

    def getGeneralEventTags(self, eventCode):
        appEvent = self.events[eventCode]
        tags = []
        eventTags = appEvent.tags
        if eventTags:
            for tagCode in eventTags:
                if not eventTags[tagCode]:
                    tags.append(self.tags[tagCode])
        return tags


    def getPersonalEventTags(self, eventCode):
        """
        Собственные теги события
        """
        appEvent = self.events[eventCode]
        tags = []
        eventTags = appEvent.tags
        if eventTags:
            for tagCode in eventTags:
                if eventTags[tagCode]:
                    tags.append(AppTag(eventTags[tagCode]))
        return tags


    def getTag(self, eventCode, tagCode):
        if self.isEventExist(eventCode):
            event = self.events[eventCode]
            if event.tags.has_key(tagCode):
                if event.tags[tagCode]:
                    return AppTag(event.tags[tagCode])
                else:
                    return self.tags[tagCode]

    def getGeneralTag(self, tagCode):
        if self.tags.has_key(tagCode):
            return self.tags[tagCode]


    def getPersonalTag(self, eventCode, tagCode):
        event = self.getEvent(eventCode)
        return AppTag(event.tags[tagCode])

    def addTag(self, appTag, eventCode = None):
        """
        Добавление тега
        """
        if eventCode:
            if self.isEventExist(eventCode):
                self.getEvent(eventCode).tags[appTag.code] = appTag.toObject()
        else:
            self.tags[appTag.code] = appTag

    def getEventGroups(self):
        return self.eventGroups.values()


    def getBunches(self):
        return self.bunches.values()

    def getBunch(self, bunchCode):
        return self.bunches[bunchCode]

    def addBunch(self, bunch):
        self.bunches[bunch.code] = bunch

    def deleteBunch(self, bunchCode):
        if self.isBunchExist(bunchCode):
            del self.bunches[bunchCode]

    def isBunchExist(self, bunchCode):
        return self.bunches.has_key(bunchCode)

    def getTagGroups(self):
        return self.tagGroups.values()

    def getEventsInGroup(self, groupIndex):
        result = []
        for appEvent in self.events.values():
            if groupIndex in appEvent.groups:
                result.append(appEvent)
        return result

    def getEventsWithoutGroup(self):
        result = []
        for appEvent in self.events.values():
            if not appEvent.groups:
                result.append(appEvent)
        return result

    def clearEventsGroups(self):
        self.eventGroups = {}
        for appEvent in self.getEvents():
            appEvent.groups = []

    def clearTagGroups(self):
        self.tagGroups = {}
        for appTag in self.tags.values():
            appTag.groups = []

    def addEventGroup(self, groupName):
        index = len(self.eventGroups)
        eventGroup = EventGroup()
        eventGroup.index = index
        eventGroup.name = groupName
        self.eventGroups[index] = eventGroup
        return index

    def addTagGroup(self, groupName):
        index = len(self.tagGroups)
        self.tagGroups[index] = groupName
        return index

    def setEventGroup(self, groupIndex, eventCode):
        if self.events.has_key(eventCode):
            self.events[eventCode].groups.append(int(groupIndex))
        else:
            raise Exception('No event with code {}'.format(eventCode))

    def getEventTags(self, eventCode, skipBunches = False):
        """
        Возвращает все теги приложения и общие и персональьные
        """
        appEvent = self.events[eventCode]
        tags = []

        if appEvent.tags:
            for tagCode in appEvent.tags:
                if self.tags.has_key(tagCode) and self.tags[tagCode]:
                    tags.append(self.tags[tagCode])
                else:
                    tags.append(AppTag(appEvent.tags[tagCode]))



        if not skipBunches:
            for bunch in self.getEventBunches(eventCode):
                for tagCode in bunch.tags:
                    tags.append(self.tags[tagCode])

        return tags

    def getEventBunches(self, eventCode):
        """
        Возвращает группы тегов события
        """
        appEvent = self.events[eventCode]
        bunches = []
        if appEvent.bunches:
            for bunchCode in appEvent.bunches:
                bunches.append(self.bunches[bunchCode])

        return bunches



    def setTagGroup(self, groupId, tagCode):
        if self.tags.has_key(tagCode):
            if not self.tags[tagCode].has_key('group'):
                self.tags[tagCode]['group'] = []
            self.tags[tagCode]['group'].append(groupId)
        else:
            raise Exception('No tag with code {}'.format(eventCode))

    def isEventInGroup(self, eventCode, groupId):
        event = self.getEvent(eventCode)
        if event:
            return groupId in event.groups
        else:
            raise Exception('No event with code {}'.format(eventCode))

    def isTagInGroup(self, tagCode, groupId):
        if self.tags.has_key(tagCode):
            return self.tags[tagCode].has_key('group') and int(groupId) in self.tags[tagCode]['group']
        else:
            raise Exception('No tag with code {}'.format(tagCode))


    def isEventExist(self, eventCode):
        return self.events.has_key(eventCode)

    def isTagExist(self, tagCode):
        return self.tags.has_key(tagCode)

    def dumpToJSON(self):
        return {
            'appname': self.data['appname'],
            'bunches':  [appTagBunch.toObject() for appTagBunch in self.bunches.values()],
            'keys': [appEvent.toObject() for appEvent in self.events.values()],
            'eventGroups': [eventGroup.toObject() for eventGroup in self.eventGroups.values()],
            'tagGroups': [tagGroup.toObject() for tagGroup in self.tagGroups.values()],
            'tags': [appTag.toObject() for appTag in self.tags.values()],
        }

    def getAppCode(self):
        return self.data['appname']


    def addAppEvent(self, newEvent):
        self.events[newEvent.code] = newEvent



