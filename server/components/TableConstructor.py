# -*- coding: utf-8 -*-
class TableConstructor():

    def __init__(self, data, nameService, task):
        self.data = data
        self.nameConstructor = nameService
        self.task = task
        self.prepareData()

    def prepareData(self):
        self.result = {}

        for key in self.data:
            self.result[key] = {'table_name': self.nameConstructor.getTableName(key)}
            table_headers = []
            table_headers_adds = []
            data = {}
            ops = []
            for series in self.data[key]:
                params = self.data[key][series]['params']
                operation = 'count'
                if params.has_key('op'):
                    operation = params['op']

                if operation == 'count' or operation == 'group':
                    table_headers.append(u'Количество')
                elif operation == 'avg':
                    table_headers.append(u'Среднее')
                elif operation == 'sum':
                    table_headers.append(u'Сумма')
                else:
                    table_headers.append(params)

                extra = ''
                if params.has_key('extra'):
                    extra = params['extra']

                conditions = []
                add_headers = []
                if extra == 'userunique':
                    add_headers.append(u'уникальная')

                if params.has_key('conditions'):
                    conditions = params['conditions']

                for kv in conditions:
                    k, v = kv
                    add_headers.append(k + '=' + v)

                table_headers_adds.append(add_headers)

                # пакуем данные
                column_values = []
                for ts, value in self.data[key][series]['data']:
                    column_values.append(value)

                    if not data.has_key(ts):
                        data[ts] = ()
                    data[ts] = data[ts] + (self._format(value),)



                columnSum = sum(column_values)
                ops.append({'sum': self._format(columnSum), 'avg': self._format(columnSum/len(column_values))})

            sorted_data = []
            for ts in sorted(data.iterkeys()):
                sorted_data.append((ts, data[ts]))

            self.result[key]['table_headers'] = enumerate(table_headers)
            self.result[key]['table_headers_adds'] = table_headers_adds
            self.result[key]['data'] = sorted_data
            self.result[key]['interval'] = self.task.interval
            self.result[key]['ops'] = ops

    def getData(self):
        return  self.result

    def _format(self, value):
        value = '%.3f'%value
        return value.rstrip('0').rstrip('.')