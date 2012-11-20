# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'

class ChartSeries:

    def __init__(self, data):
        self.data = data
        self.name = '1'
        self.operation = 'count'
        self.conditions = []
        self.operationName = ''
        self.id = None
        self.display = True

        values = []
        for date, value in self.data:
            values.append(value)

        self.sum = sum(values)
        self.avg = 0
        if values:
            self.avg = self.sum / len(values)