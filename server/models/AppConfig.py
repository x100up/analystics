
from models.appConf.EventGroup import EventGroup
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
            self.tagGroups = self.data['tagGroups']

        if self.data.has_key('eventGroups'):
            self.eventGroups = self.data['eventGroups']
            for rawEventGroups in self.data['eventGroups']:
                eventGroup = EventGroup(rawEventGroups)
                self.eventGroups[eventGroup.index] = eventGroup

        if self.data.has_key('bunches'):
            for rawBunch in self.data['bunches']:
                appTagBunch = AppTagBunch(rawBunch)
                self.bunches[appTagBunch.code] = appTagBunch


    def getEvents(self):
        return self.events

    def getEvent(self, eventCode):
        return self.events[eventCode]

    def getTags(self):
        return self.tags.values()

    def getTag(self, tagCode):
        return self.tags[tagCode]

    def getEventGroups(self):
        return self.eventGroups

    def getTagGroups(self):
        return self.tagGroups

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
        for tag in self.getTags():
            if tag.has_key('group'):
                del tag['group']

    def addEventGroup(self, groupName):
        index = len(self.eventGroups)
        eventGroup = EventGroup(index, groupName)
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

    def getEventTags(self, eventCode):
        appEvent = self.events[eventCode]
        tags = []

        for tagCode in appEvent.tags:
            tags.append(self.tags[tagCode])

        for bunchCode in appEvent.bunches:
            for tagCode in self.bunches[bunchCode].tags:
                tags.append(self.tags[tagCode])

        return tags


    def setTagGroup(self, groupId, tagCode):
        if self.tags.has_key(tagCode):
            if not self.tags[tagCode].has_key('group'):
                self.tags[tagCode]['group'] = []
            self.tags[tagCode]['group'].append(groupId)
        else:
            raise Exception('No tag with code {}'.format(eventCode))

    def isEventInGroup(self, eventCode, groupId):
        if self.events.has_key(eventCode):
            return groupId in self.events[eventCode].groups
        else:
            raise Exception('No event with code {}'.format(eventCode))

    def isTagInGroup(self, tagCode, groupId):
        if self.tags.has_key(tagCode):
            return self.tags[tagCode].has_key('group') and int(groupId) in self.tags[tagCode]['group']
        else:
            raise Exception('No tag with code {}'.format(tagCode))


    def isEventExist(self, eventCode):
        return self.events.has_key(eventCode)

    def dumpToJSON(self):
        return {
            'appname': self.data['appname'],
            'bunches':  [appTagBunch.toObject() for appTagBunch in self.bunches.values()],
            'keys': [appEvent.toObject() for appEvent in self.events.values()],
            'eventGroups': [eventGroup.toObject() for eventGroup in self.eventGroups.values()],
            'tagGroups': [tagGroup.toObject() for tagGroup in self.tagGroups.values()],
            'tags': [appTag.toObject() for appTag in self.tags.values()],
        }

