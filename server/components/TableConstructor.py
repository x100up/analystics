# -*- coding: utf-8 -*-
from sqlalchemy.sql.functions import sum

class TableConstructor():

    def __init__(self, data, nameService, task):
        self.data = data
        self.nameConstructor = nameService
        self.task = task
        self.prepareData()

    def prepareData(self):
        tableCode = ''
        self.result = {tableCode: {
            'rowsData': None
        }}
        self.result[tableCode]['rowsData'] = []


        for key in self.data:
            columnHeaders = []
            columnHeadersSet = False

            data = {}
            for seriesIndex in self.data[key]:
                rowHeader = self.nameConstructor.getKeyNameByIndex(key)
                tagHeader = []
                if self.data[key][seriesIndex]['params'].has_key('conditions'):
                    for eventCode, tagCode, tagValue in self.data[key][seriesIndex]['params']['conditions']:
                        tagHeader.append(self.nameConstructor.getTagValueName(eventCode, tagCode, tagValue))

                # пакуем данные
                rowValues = []
                rowSum = 0
                for ts, value in self.data[key][seriesIndex]['data']:
                    rowSum += value

                    if not columnHeadersSet:
                        columnHeaders.append(ts)

                    rowValues.append(value)

                columnHeadersSet = True


                self.result[tableCode]['rowsData'].append(
                        {
                        'header': rowHeader,
                        'sum': rowSum,
                        'avg': self._format(rowSum/len(rowValues)),
                        'values': rowValues,
                        'tagHeader': ', '.join(tagHeader),
                        'seriesIndex': key,
                        'chartIndex': seriesIndex,
                        }
                )

                self.result[tableCode]['columnHeaders'] = columnHeaders


        self.sortTableData()




    def sortTableData(self):
        for tableCode in self.result:
            self.result[tableCode]['rowsData'] = sorted(self.result[tableCode]['rowsData'], key=lambda data: -data['sum'])



    def getData(self):
        return  self.result

    def _format(self, value):
        value = '%.3f'%value
        return value.rstrip('0').rstrip('.')