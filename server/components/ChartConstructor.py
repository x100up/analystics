# -*- coding: utf-8 -*-

from models.ChartSeries import ChartSeries
from models.ChartSeriesGroup import ChartSeriesGroup

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
        tagCloud = {}
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
                    for eventCode, cloudKey, value in params['conditions']:
                        key = (eventCode, cloudKey)
                        if not tagCloud.has_key(key):
                            tagCloud[key] = {}
                        if not tagCloud[key].has_key(value):
                            tagCloud[key][value] = 0

                        tagCloud[key][value] = tagCloud[key][value] + series.sum

                series.operation = seriesData['params']['op']
                series.operationName = self.nameService.getOperationName(seriesData['params']['op'])
                series.key = taskItem.key
                self._series.append(series)

                # выставляем ID-шники
                seriesData['id'] = series.id = i
                series.seriesIndex = seriesIndex
                series.taskItemIndex = taskItemIndex
                i = i + 1

        # группируем
        self.generateSeriesGroup()


        if self.seriesGroups:
            for seriesGroup in self.seriesGroups:
                seriesGroup.name = self.nameService.getSeriesGroupName(seriesGroup)
                seriesGroup.secondName = self.nameService.getSeriesGroupSecondName(seriesGroup)

            self.seriesGroups = sorted(self.seriesGroups, key=lambda seriesGroup: seriesGroup.maxAvg, reverse=True)
            self.seriesGroups[0].setVisible(True)


        self.tagCloud = {}

        if tagCloud:
            for cloudKey in tagCloud:
                eventCode, tagCode = cloudKey
                tagValueMaxWeight = max([weight for value, weight in tagCloud[cloudKey].items()])
                tagCloudGroup = []
                for value in tagCloud[cloudKey]:
                    name = self.nameService.getTagValueName(eventCode, tagCode, value)
                    if tagCloud[cloudKey][value] == 0:
                        weight = 0
                    else:
                        weight = float(tagCloud[cloudKey][value]) / tagValueMaxWeight

                    tagCloudGroup.append({
                        'text': name,
                        'weight': weight,
                        'tag': cloudKey,
                        'value': value,
                        })


                tagCloudGroup = sorted(tagCloudGroup, key=lambda item: item['weight'], reverse=True)
                self.tagCloud[self.nameService.getTagName(eventCode, tagCode)] = tagCloudGroup




    def getSeries(self):
        return self.seriesGroups

    def getTagCloud(self):
        return self.tagCloud

    def generateSeriesGroup(self):
        self.seriesGroups = []
        keys = []

        for series in self._series:
            if not series.key in keys:
                keys.append(series.key)


        # разделяем по операциям
        _series = self.sliceByOperations(self._series)

        # если мы выбираем не один ключ
        # разделяем по набору тегов
        if len(keys) > 1:
            _tmp = {}
            for hardKey in _series:
                _tmp.update(self.groupByTags(_series[hardKey], hardKey[0]))
            _series = _tmp
        # группируем по значению
        for hardKey in _series:
            self.seriesGroups += self.groupByValues(_series[hardKey], hardKey)


    def sliceByOperations(self, seriesList):
        byOperation = {}
        for series in seriesList:
            op = (series.operation,)
            if not byOperation.has_key(op):
                byOperation[op] = []
            byOperation[op].append(series)
        return byOperation

    def groupByTags(self, seriesList, operation) :
        byTags = {}
        for series in seriesList:
            hardKey = (operation, ) + (tuple(sorted(series.getTagsCodes())),)
            if not byTags.has_key(hardKey):
                byTags[hardKey] = []
            byTags[hardKey].append(series)
        return byTags



    def groupByValues(self, seriesList, hardKey):
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

        # sort raw groups
        for exponent in rawGroups:
            rawGroups[exponent] = sorted(rawGroups[exponent], key = lambda series: series.avg, reverse=True)

        maxChartInGroups = 6

        loop = True
        while loop:
            loop = False
            for exponent in rawGroups:
                if not exponent == 0 and len(rawGroups[exponent]) < maxChartInGroups:
                    # в группе меньше чем макс, ищем рядом
                    _temp = {}
                    for i in [1, -1]:
                        if rawGroups.has_key(exponent + i) and ( len(rawGroups[exponent]) + len(rawGroups[exponent + i]) <= maxChartInGroups):
                            _temp[i] = len(rawGroups[exponent + i])

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
                elif len(rawGroups[exponent]) > maxChartInGroups:
                    # если в серии больше 6-ти, то разделяем
                    rawGroups[exponent - 0.5] = rawGroups[exponent][0:6]
                    rawGroups[exponent + 0.5] = rawGroups[exponent][6:]
                    del rawGroups[exponent]
                    loop = True
                    break
                else:
                    pass
            # не было группировок - выходим

        # делаем объекты групп
        seriesGroups = []
        for exponent in rawGroups:
            seriesGroups.append(ChartSeriesGroup(rawGroups[exponent], exponent, hardKey[0]))

        return seriesGroups




    def getChartSeriesJSON(self):
        result  = []
        for seriesGroup in self.seriesGroups:
            result.append(seriesGroup.getForJSON())
        return result


    def getResult(self):
        return {
            'chartconf': {
                'subtitle' : {'text' :  ' '},
                'title' : { 'text': ''},
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