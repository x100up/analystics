# -*- coding: utf-8 -*-

from models.ChartSeries import ChartSeries

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



                series = ChartSeries(seriesData['data'])
                series.name = self.nameService.getKeyNameByIndex(taskItemIndex)
                if params.has_key('conditions'):
                    series.conditions = self.nameService.prepareConditions(params['conditions'])
                series.operation = seriesData['params']['op']
                series.operationName = self.nameService.getOperationName(seriesData['params']['op'])
                self._series.append(series)


                seriesData['id'] = series.id = i
                i = i + 1

                tagValues = []
                #for tagName, tagValue in seriesData['params'].items():
                #    tagValues.append(self.nameService.getParamNameValue(tagName, tagValue))

                #seriesData['opt'] =  {
                #    'tagValues' : ', '.join(tagValues),
                #    'interval': self.task.interval
                #}

    def getSeries(self):
        print self._series
        return self._series



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
            'data': self.data
        }