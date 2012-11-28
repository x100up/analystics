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

        values = []
        for date, value in self.data:
            values.append(value)

        self.sum = sum(values)
        self.avg = 0
        if values:
            self.avg = self.sum / len(values)

    def getForJSON(self):
        return {
            'params': {
                'tag': self.key,
                'conditions': self.conditions,
                'op': self.operation,
                'color': self.color,
                'visible': self.visible
            },
            'data': self.data,
            'id': self.id
        }