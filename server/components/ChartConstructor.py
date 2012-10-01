# -*- coding: utf-8 -*-

class ChartConstructor():
    '''
    Подготавливает данные для построеня графика
    '''
    def __init__(self, data, nameService, task):
        self.data = data
        self.nameService = nameService
        self.task = task
        self.prepareData()

    def prepareData(self):

        for taskItemIndex in self.data:
            taskItemData = self.data[taskItemIndex]
            for seriesIndex in taskItemData:
                seriesData = taskItemData[seriesIndex]
                # генерирует имя серии данных
                seriesData['name'] = self.nameService.getKeyNameByIndex(taskItemIndex, seriesData['params'])

                tagValues = []
                #for tagName, tagValue in seriesData['params'].items():
                #    tagValues.append(self.nameService.getParamNameValue(tagName, tagValue))

                seriesData['opt'] =  {
                    'tagValues' : ', '.join(tagValues),
                    'interval': self.task.interval
                }




    def getResult(self):
        return {
            'chartconf': {
                'subtitle' : {'text' :  'job '},
                'title' : { 'text': 'График'},
                'yAxis': { 'title': {'text': 'Количество'}},
                },
            'data': self.data
        }