from Base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum

class Worker(Base):
    STATUS_ALIVE = 'ALIVE'
    STATUS_SUCCESS = 'SUCCESS'
    STATUS_DIED = 'DIED'
    STATUS_ERROR = 'ERROR'

    __tablename__ = 'worker'
    workerId = Column(Integer, primary_key = True, autoincrement=True)
    startDate = Column(DateTime,  nullable = False)
    endDate = Column(DateTime)
    status = Column(Enum('ALIVE', 'SUCCESS', 'DIED', 'ERROR'))
    userId = Column(Integer, ForeignKey('user.userId'),  nullable = False)
    appId = Column(Integer, ForeignKey('app.appId'),  nullable = False)
    hadoopAppID = Column(String, nullable = True, default = None)
