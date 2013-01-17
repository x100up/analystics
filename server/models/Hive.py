from Base import Base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date, Boolean

class HiveTable(Base):
    __tablename__ = "hiveTable"
    hiveTableId = Column(Integer, primary_key=True)
    appId = Column(Integer, ForeignKey('app.appId'),  nullable=False, primary_key=True, autoincrement=False)
    eventCode = Column(String(255), name='keyCode')
    startFrom = Date(nullable = False)

class HiveTablePartition(Base):
    __tablename__ = "hiveTablePartition"
    hiveTablePartitionId = Column(Integer, primary_key=True)
    hiveTableId = Column(Integer, ForeignKey('hiveTable.hiveTableId'),  nullable=False, primary_key=True, autoincrement=False)
    partitionDate = Date(nullable = False),
    isCompact = Boolean()