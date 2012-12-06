# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'

class AppTag():

    def __init__(self, data = None):
        self.groups = []
        self.type = "string"
        self.code = \
        self.name = \
        None
        self.values = []

        if data:
            self.createFromDict(data)

    def getName(self):
        if self.name:
            return self.name
        return self.code

    def getDescription(self):
        return ''

    def createFromDict(self, data):
        if data.has_key('type'):
            self.type = data['type']

        if data.has_key('name'):
            self.name = data['name']

        if data.has_key('values'):
            self.values = data['values']

        if data.has_key('code'):
            self.code = data['code']


    def toObject(self):
        return {
            'code': self.code,
            'name': self.name,
            'values': self.values,
            'type': self.type,
        }