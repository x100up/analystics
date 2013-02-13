# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'

class AppEvent():

    def __init__(self, data = None):
        self.groups = []
        self.code = ''
        self.name = ''
        self.bunches = None
        self.description = None
        self.tags = None
        self.hasUser = False

        if data:
            self.createFromDict(data)

    def getName(self):
        if self.name:
            return self.name
        return self.code

    def createFromDict(self, data):
        if 'bunches' in data:
            self.bunches = data['bunches']

        if 'group' in data:
            self.groups = data['group']

        if 'code' in data:
            self.code = data['code']

        if 'description' in data:
            self.description = data['description']

        if 'name' in data:
            self.name = data['name']

        if 'tags' in data:
            self.tags = data['tags']

        if 'hasUser' in data:
            self.hasUser = bool(data['hasUser'])

    def toObject(self):
        return {
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'group': self.groups,
            'tags': self.tags,
            'bunches': self.bunches,
            'hasUser': self.hasUser
        }