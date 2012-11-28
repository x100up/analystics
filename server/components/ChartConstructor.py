# -*- coding: utf-8 -*-

from models.ChartSeries import ChartSeries
from models.ChartSeriesGroup import ChartSeriesGroup
from pprint import pprint

class ChartConstructor():
    '''
    Подготавливает данные для построеня графика
    '''
    def __init__(self, data, nameService, task):
        self.data = data
        self.nameService = nameService
        self.task = task
        self._series = []
        self.prepareData()


    def prepareData(self):
        i = 0
        for taskItemIndex in self.data:
            taskItemData = self.data[taskItemIndex]
            for seriesIndex in taskItemData:
                seriesData = taskItemData[seriesIndex]
                params = seriesData['params']

                # генерирует имя серии данных
                #seriesData['name'] = self.nameService.getKeyNameByIndex(taskItemIndex, params)
                # генерирует имя таблицы
                #seriesData['table_name'] = self.nameService.getTableName(taskItemIndex)

                taskItem = self.task.getTaskItem(taskItemIndex)

                # генерим объекты серий
                series = ChartSeries(seriesData['data'], taskItemIndex)
                series.name = self.nameService.getKeyNameByIndex(taskItemIndex)
                if params.has_key('conditions'):
                    series.conditions = self.nameService.prepareConditions(params['conditions'])
                series.operation = seriesData['params']['op']
                series.operationName = self.nameService.getOperationName(seriesData['params']['op'])
                series.key = taskItem.key
                self._series.append(series)

                # выставляем ID-шники
                seriesData['id'] = series.id = i
                i = i + 1

                # группируем
                self.generateSeriesGroup()



                tagValues = []
                #for tagName, tagValue in seriesData['params'].items():
                #    tagValues.append(self.nameService.getParamNameValue(tagName, tagValue))

                #seriesData['opt'] =  {
                #    'tagValues' : ', '.join(tagValues),
                #    'interval': self.task.interval
                #}

        if self.seriesGroups:
            for seriesGroup in self.seriesGroups:
                seriesGroup.name = self.nameService.getSeriesGroupName(seriesGroup)

            self.seriesGroups = sorted(self.seriesGroups, key=lambda seriesGroup: seriesGroup.exp, reverse=True)
            self.seriesGroups[0].setVisible(True)
            print

    def getSeries(self):
        return self.seriesGroups

    def generateSeriesGroup(self):
        groups = []
        keys = []

        for series in self._series:
            if not series.key in keys:
                keys.append(series.key)

        if len(keys) == 1:
            # если мы выбираем один ключ
            groups = self.groupByValues(self._series)
        else:
            pass


    def groupByValues(self, seriesList):
        '''
        Группирует по значениям
        '''
        rawGroups = {}
        for series in seriesList:
            if (series.avg == 0):
                exponent = 0
            else:
                exponent = len(str(int(series.avg)))

            if not rawGroups.has_key(exponent):
                rawGroups[exponent] = []
            rawGroups[exponent].append(series)

        maxChartInGroups = 6

        loop = True
        while loop:
            loop = False
            print 'start loop'
            for exponent in rawGroups:
                print 'ex = {}'.format(exponent)
                if not exponent == 0 and len(rawGroups[exponent]) < maxChartInGroups:
                    # в группе меньше чем макс, ищем рядом
                    _temp = {}
                    for i in [1, -1]:
                        if rawGroups.has_key(exponent + i):
                            _temp[i] = len(rawGroups[exponent + i])

                    print _temp

                    if _temp:
                        minDiff = None
                        minEx = None
                        for i in _temp:
                            v = abs(maxChartInGroups - _temp[i])
                            if minDiff == None or minDiff > v:
                                minDiff = v
                                minEx = i

                        if minEx:
                            rawGroups[exponent] = rawGroups[exponent] + rawGroups[exponent + minEx]
                            del rawGroups[exponent + minEx]
                            loop = True
                            break
                else:
                    pass
            # не было группировок - выходим

        # делаем объекты групп
        self.seriesGroups = []
        for exponent in rawGroups:
            self.seriesGroups.append(ChartSeriesGroup(rawGroups[exponent], exponent))




    def getChartSeriesJSON(self):
        result  = {}
        for seriesGroup in self.seriesGroups:
            result[seriesGroup.exp] = seriesGroup.getForJSON()
        return result


    def getResult(self):
        return {
            'chartconf': {
                'subtitle' : {'text' :  'job '},
                'title' : { 'text': 'График'},
                'yAxis': {
                    'min': 0,
                    'minTickInterval': 1,
                    'title': {
                        'text': 'Значения'
                        }
                    }
                },
            'data': self.getChartSeriesJSON()
        }