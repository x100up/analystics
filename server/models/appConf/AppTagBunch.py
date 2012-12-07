# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'

class AppTagBunch():

    def __init__(self, data = None):
        self.code = ''
        self.name = ''
        self.tags = []
        if data:
            self.createFromDict(data)

    def createFromDict(self, data):
        if data.has_key('code'):
            self.code = data['code']

        if data.has_key('name'):
            self.name = data['name']

        if data.has_key('tags'):
            self.tags = data['tags']

    def getName(self):
        if self.name:
            return self.name
        return self.code

    def toObject(self):
        return {
            'code': self.code,
            'name': self.name,
            'tags': self.tags,
            }