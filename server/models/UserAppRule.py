from sqlalchemy import Column, Integer, Enum, ForeignKey

from Base import Base
from models.App import App


class UserAppRule(Base):
    RULE_ALLOW = 'ALLOW'
    RULE_DENY = 'DENY'

    __tablename__ = "userAppRule"
    appId = Column(Integer, ForeignKey('app.appId'),  nullable=False, primary_key=True, autoincrement=False)
    userId = Column(Integer, ForeignKey('user.userId'),  nullable=False, primary_key=True, autoincrement=False)
    rule = Column(Enum('ALLOW', 'DENY'), default='ALLOW')

class RuleCollection():

    def __init__(self, session):
        self.dbSession = session

    def loadAll(self, ):
        rules = self.dbSession.query(UserAppRule).all()
        self.rules = {}
        for rule in rules:
            if not self.rules.has_key(rule.appId):
                self.rules[rule.appId] = {}
            self.rules[rule.appId][rule.userId] = rule

    def isAllow(self, userId, appId):
        if self.rules.has_key(appId):
            if self.rules[appId].has_key(userId):
                return self.rules[appId][userId].rule == UserAppRule.RULE_ALLOW
        return False

    def getUserApps(self, userId):
        q = self.dbSession.query(App).filter(UserAppRule.rule == UserAppRule.RULE_ALLOW, UserAppRule.userId == userId, UserAppRule.appId == App.appId)
        return q.all()