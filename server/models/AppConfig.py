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
        self.prepareData()

    def prepareData(self):
        if self.data.has_key('keys'):
            for eventCode in self.data['keys']:
                self.data['keys'][eventCode]['code'] = eventCode
                if self.data['keys'][eventCode].has_key('description'):
                    self.data['keys'][eventCode]['name'] = self.data['keys'][eventCode]['description']
            self.events = self.data['keys']

        if self.data.has_key('tags'):
            for tagCode in self.data['tags']:
                self.data['tags'][tagCode]['code'] = tagCode
            self.tags = self.data['tags']

        if self.data.has_key('tagGroups'):
            self.tagGroups = self.data['tagGroups']

        if self.data.has_key('eventGroups'):
            self.eventGroups = self.data['eventGroups']


    def getEvents(self):
        return self.events.values()

    def getTags(self):
        return self.tags.values()

    def getEventGroups(self):
        return self.eventGroups

    def getTagGroups(self):
        return self.tagGroups

    def clearEventsGroups(self):
        self.eventGroups = {}
        for event in self.getEvents():
            if event.has_key('group'):
                del event['group']

    def clearTagGroups(self):
        self.tagGroups = {}
        for tag in self.getTags():
            if tag.has_key('group'):
                del tag['group']

    def addEventGroup(self, groupName):
        index = len(self.eventGroups)
        self.eventGroups[index] = groupName
        return index

    def addTagGroup(self, groupName):
        index = len(self.tagGroups)
        self.tagGroups[index] = groupName
        return index

    def setEventGroup(self, groupId, eventCode):
        if self.events.has_key(eventCode):
            if not self.events[eventCode].has_key('group'):
                self.events[eventCode]['group'] = []
            self.events[eventCode]['group'].append(groupId)
        else:
            raise Exception('No event with code {}'.format(eventCode))

    def setTagGroup(self, groupId, tagCode):
        if self.tags.has_key(tagCode):
            if not self.tags[tagCode].has_key('group'):
                self.tags[tagCode]['group'] = []
            self.tags[tagCode]['group'].append(groupId)
        else:
            raise Exception('No tag with code {}'.format(eventCode))

    def isEventInGroup(self, eventCode, groupId):
        if self.events.has_key(eventCode):
            return self.events[eventCode].has_key('group') and int(groupId) in self.events[eventCode]['group']
        else:
            raise Exception('No event with code {}'.format(eventCode))

    def isTagInGroup(self, tagCode, groupId):
        if self.tags.has_key(tagCode):
            return self.tags[tagCode].has_key('group') and int(groupId) in self.tags[tagCode]['group']
        else:
            raise Exception('No tag with code {}'.format(tagCode))

    def dumpToJSON(self):
        return {
            'appname': self.data['appname'],
            'bunches': self.data['bunches'],
            'keys': self.events,
            'eventGroups': self.eventGroups,
            'tagGroups': self.tagGroups,
            'tags': self.tags
        }

