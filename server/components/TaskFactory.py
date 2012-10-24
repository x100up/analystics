# -*- coding: utf-8 -*-
from models.Task import Task, TaskItem
from components.dateutil import repMonth
from datetime import datetime

def createTaskFromRequestArguments(arguments):
    appname, = arguments['appname']
    interval, = arguments['group_interval']
    task = Task(appname = appname, interval = interval)
    indexes = arguments['indexes']
    for index in indexes:
        if not arguments.has_key('key_' + index):
            continue

        key, = arguments['key_' + index]
        if not key:
            continue

        start = datetime.strptime(repMonth(arguments['start_'+ index][0]), "%d %m %Y %H:%M")
        end = datetime.strptime(repMonth(arguments['end_'+ index][0]), "%d %m %Y %H:%M")

        taskItem = TaskItem(key = key, start = start, end = end, index = index)
        # разбираем тег для ключа
        tagNames = []
        tag_name = 'tag_' + index + '_name'
        if arguments.has_key(tag_name):
            tagNames = arguments[tag_name]

        for tagName in tagNames:
            # значения тега
            values = None
            val_index = 'tag_' + index + '_' + tagName
            if arguments.has_key(val_index):
                # convert to unicode
                values = [val.decode('utf-8') for val in arguments[val_index]]

            if not values is None:
                taskItem.addCondition(tagName, values)
            # операции с тегом
            op_index = 'tag_' + index + '_' + tagName + '_ops'
            if arguments.has_key(op_index):
                ops = arguments[op_index][0]
                if not ops is None:
                    taskItem.setTagOperations(tagName, ops.split('/'))

        task.addTaskItem(taskItem)

    return  task