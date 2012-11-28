# coding=utf-8

class ChartSeriesGroup():

    colors = [
        '#FF3030', # red
        '#FF8800', # orange
        '#00B6F7', # blue
        '#95D900', # green
        '#FFEA00', # yellow
        '#BB7BF1', # violet
    ]

    def __init__(self, series, exp):
        self.series = series
        self.exp = exp
        self.visible = False
        self.process()
        self.name = u'неизвестная серия'

    def process(self):
        self.series = sorted(self.series, key=lambda series: series.avg, reverse=True)
        for i, s in enumerate(self.series):
            s.color = self.colors[i]

    def getSeries(self):
        return  self.series

    def getForJSON(self):
        result = {}
        for series in self.series:
            result[series.id] = series.getForJSON()
        return result

    def setVisible(self, value):
        self.visible = value
        for series in self.series:
            series.visible = value