# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'

class AppEvent():

    def __init__(self, data = None):
        self.groups = []
        self.code = \
        self.bunches = \
        self.name = \
        self.description = \
        self.tags = \
        None

        if data:
            self.createFromDict(data)

    def getName(self):
        if self.name:
            return self.name
        return self.code

    def createFromDict(self, data):
        if data.has_key('bunches'):
            self.bunches = data['bunches']

        if data.has_key('group'):
            self.groups = data['group']

        if data.has_key('code'):
            self.code = data['code']

        if data.has_key('description'):
            self.description = data['description']

        if data.has_key('name'):
            self.name = data['name']

        if data.has_key('tags'):
            self.tags = data['tags']

    def toObject(self):
        return {
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'group': self.groups,
            'tags': self.tags,
            'bunches': self.bunches,
        }