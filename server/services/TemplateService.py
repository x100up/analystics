# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'

from models.TaskTemplate import TaskTemplate
from sqlalchemy.sql import and_

class TemplateService():
    def __init__(self, dbSession):
        self.dbSession = dbSession

    def getUserTemplates(self, appId, userId):
        return self.dbSession.query(TaskTemplate).filter(
            and_(
                TaskTemplate.appId == appId,
                TaskTemplate.userId == userId
                )
            ).all()
            #.order_by(TaskTemplate.userId != userId,TaskTemplate.shared == TaskTemplate.SHARED_YES)\\


    def getAppTemplates(self, appId):
        return self.dbSession.query(TaskTemplate).filter(
            and_(
                TaskTemplate.appId == appId,
                TaskTemplate.shared == TaskTemplate.SHARED_YES
            )
        ).all()






