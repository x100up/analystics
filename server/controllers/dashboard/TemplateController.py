# -*- coding: utf-8 -*-

from controllers.BaseController import BaseController
from components.TaskFactory import createTaskFromRequestArguments
from models.TaskTemplate import TaskTemplate, TaskTemplateFile
from datetime import datetime

class CreateTemplateAction(BaseController):

    def post(self, *args, **kwargs):
        app = self.checkAppAccess(args)
        template_shared = self.get_argument('template_shared', False)
        template_name = self.get_argument('template_name', None)
        timeRelatively = self.get_argument('template_time_relatively', False)

        # создаем задачу из аргументов
        task = createTaskFromRequestArguments(self.request.arguments)

        # создаем шаблон
        taskTemplate = TaskTemplate()
        taskTemplate.appId = app.appId
        taskTemplate.name = template_name
        taskTemplate.userId = self.get_current_user().userId
        taskTemplate.shared =  TaskTemplate.SHARED_NO
        if template_shared:
            taskTemplate.shared = TaskTemplate.SHARED_YES

        session = self.getDBSession()
        session.add(taskTemplate)
        session.commit()

        # скидываем на диск
        taskTemplateFile = TaskTemplateFile(self.application.getTemplatePath(), task = task, taskTemplate = taskTemplate)
        taskTemplateFile.timeRelatively = bool(timeRelatively)
        taskTemplateFile.baseDate = datetime.now()
        taskTemplateFile.save()

        self.redirect('/dashboard/app/{}/new?template={}'.format(app.code, taskTemplate.taskTemplateId))