# -*- coding: utf-8 -*-

class ChartConstructor():
    '''
    Подготавливает данные для построеня графика
    '''
    def __init__(self, data, nameService):
        self.data = data
        self.nameService = nameService
        self.prepareData()

    def prepareData(self):
        # generate serias names
        for taskItemIndex in self.data:
            taskItemData = self.data[taskItemIndex]
            for serasIndex in taskItemData:
                seriaData = taskItemData[serasIndex]
                seriaName = self.nameService.getKeyNameByIndex(taskItemIndex)
                seriaData['name'] = seriaName

                tagValues = []
                for tagName, tagValue in seriaData['params'].items():
                    tagValues.append(self.nameService.getParamNameValue(tagName, tagValue))

                seriaData['tagValues'] = ', '.join(tagValues)



    def getResult(self):
        return {
            'chartconf': {
                'subtitle' : {'text' :  'job '},
                'title' : { 'text': 'График'},
                'yAxis': { 'title': {'text': 'Количество'}},
                },
            'data': self.data
        }