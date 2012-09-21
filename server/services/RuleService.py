from models.UserAppRule import UserAppRule

class RuleService():

    def __init__(self, db_session):
        self.db_session = db_session

    def isAllow(self, userId, appId):
        '''
        return boolean
        '''
        rule = self.db_session.query(UserAppRule).filter(UserAppRule.userId == userId, UserAppRule.appId == appId,
            UserAppRule.rule == UserAppRule.RULE_ALLOW)
        if rule:
            return True
        return False