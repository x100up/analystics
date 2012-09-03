from Base import Base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Enum

class Worker(Base):
    STATUS_ALIVE = 'ALIVE'
    STATUS_SUCCESS = 'SUCCESS'
    STATUS_DIED = 'DIED'
    STATUS_ERROR = 'ERROR'

    __tablename__ = 'worker'
    uuid = Column(String(50), primary_key=True)
    startDate = Column(DateTime,  nullable=False)
    endDate = Column(DateTime)
    status = Column(Enum('ALIVE', 'SUCCESS', 'DIED', 'ERROR'))
    userId = Column(Integer, ForeignKey('user.userId'),  nullable=False)
    appId = Column(Integer, ForeignKey('app.appId'),  nullable=False)
