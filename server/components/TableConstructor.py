# -*- coding: utf-8 -*-


class TableConstructor():
    """
    Генерирует данные для таблицы
    """
    def __init__(self, data, nameService, task):
        self.data = data
        self.nameConstructor = nameService
        self.task = task
        self.prepareData()

    def prepareData(self):
        tableCode = ''
        self.result = {tableCode: {
            'horizontalData': [],
            'verticalData': [],
        }}

        for key in self.data:
            columnHeaders = []
            columnHeadersSet = False

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

                self.result[tableCode]['horizontalData'].append(
                    {
                        'header': rowHeader,
                        'sum': rowSum,
                        'avg': self._format(rowSum / len(rowValues)),
                        'values': rowValues,
                        'tagHeader': ', '.join(tagHeader),
                        'seriesIndex': key,
                        'chartIndex': seriesIndex,
                    }
                )

                self.result[tableCode]['columnHeaders'] = columnHeaders

        self.sortTableData()

    def prepareVerticalData(self):
        """
        Строит данные для таблицы с вертикальными датами (даты в строках)
        """
        tableCode = ''
        self.result = {tableCode: {
            'verticalData': [],
            }}

        for key, dataItem in self.data.iteritems():
            columnHeaders = {}
            columnHeadersSet = False

            tsValues = {}
            for seriesIndex, seriesData in dataItem.iteritems():
                # собираем заголовки столбцов
                rowHeader = self.nameConstructor.getKeyNameByIndex(key)
                tagHeader = []
                if 'conditions' in seriesData['params']:
                    for eventCode, tagCode, tagValue in seriesData['conditions']:
                        tagHeader.append(self.nameConstructor.getTagValueName(eventCode, tagCode, tagValue))
                columnHeaders[seriesIndex] = (rowHeader, ', '.join(tagHeader))

                # пакуем данные
                # сумма серии
                rowSum = 0
                for ts, value in seriesData['data']:
                    if ts not in tsValues:
                        tsValues[ts] = {}

                    tsValues[ts][seriesIndex] = value
                    rowSum += value

            # проходим по каждому таймстампу чтобы сформировать строку таблицы
            for ts in tsValues:
                values = {}
                # и по каждому индексу серии
                for seriesIndex in columnHeaders:
                    if seriesIndex in tsValues[ts]:
                        values[seriesIndex] = tsValues[ts][seriesIndex]
                    else:
                        values[seriesIndex] = None

                self.result[tableCode]['verticalData'].append(
                    {
                        'header': ts,
                        'values': values,
                    }
                )

            self.result[tableCode]['verticalColumnHeaders'] = columnHeaders

    def sortTableData(self):
        for tableCode in self.result:
            self.result[tableCode]['horizontalData'] = sorted(self.result[tableCode]['horizontalData'], key=lambda data: -data['sum'])

    def getData(self):
        return  self.result

    def getVerticalData(self, table=''):
        if 'verticalColumnHeaders' not in self.result[table]:
            self.prepareVerticalData()
        return self.result[table]['verticalColumnHeaders'], self.result[table]['verticalData']

    def _format(self, value):
        value = '%.3f'%value
        return value.rstrip('0').rstrip('.')