# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'

class ChartSeries:

    def __init__(self, data, taskItemIndex):
        self.data = data
        self.name = '1'
        self.operation = 'count'
        self.conditions = []
        self.operationName = ''
        self.id = None
        self.key = None
        self.taskItemIndex = taskItemIndex
        self.color = '#666666'
        self.visible = False
        self.seriesIndex = None
        self.taskItemIndex = None

        values = []
        for date, value in self.data:
            values.append(value)

        self.sum = sum(values)
        self.avg = 0
        if values:
            self.avg = self.sum / len(values)

    def getTagValue(self, tagCode):
        for tagName, valueName, tag, value in self.conditions:
            if tag == tagCode:
                return valueName

        return None

    def getTagsCodes(self):
        tagCodes = []
        for tagName, valueName, tag, value in self.conditions:
            if not tag in tagCodes:
                tagCodes.append(tag)
        return tagCodes

    def getForJSON(self):
        return {
            'params': {
                'tag': self.key,
                'conditions': self.conditions,
                'op': self.operation,
                'color': self.color[0],
                'visible': self.visible
            },
            'data': self.data,
            'id': self.id,
            'seriesIndex': self.seriesIndex,
            'taskItemIndex': self.taskItemIndex
        }