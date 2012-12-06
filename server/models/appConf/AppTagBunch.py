# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'

class AppTagBunch():

    def __init__(self, data):
        self.code = None
        self.name = None
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

    def toObject(self):
        return {
            'code': self.code,
            'name': self.name,
            'tags': self.tags,
            }