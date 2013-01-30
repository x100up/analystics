__author__ = 'x100up'
from models.Hive import HiveTable, HiveTablePartition


class HiveMetaService():

    def __init__(self, dbSession):
        self.dbSession = dbSession

    def getOrCreateHiveTable(self, appId, eventCode):
        hiveTable = self.dbSession.query(HiveTable).filter_by(appId = appId, eventCode = eventCode).first()
        if not hiveTable:
            hiveTable = HiveTable()
            hiveTable.appId = appId
            hiveTable.eventCode = eventCode
            self.dbSession.add(hiveTable)
            self.dbSession.commit()

        return hiveTable

    def getOrCreateHiveTablePartition(self, hiveTableId, partitionDate):
        hiveTablePartition = self.dbSession.query(HiveTablePartition).filter_by(hiveTableId = hiveTableId, partitionDate = partitionDate).first()
        if not hiveTablePartition:
            hiveTablePartition = HiveTablePartition()
            hiveTablePartition.hiveTableId = hiveTableId
            hiveTablePartition.partitionDate = partitionDate
            hiveTablePartition.isCompact = 0
            self.dbSession.add(hiveTablePartition)
            self.dbSession.commit()

        return hiveTablePartition

    def getMinDateForEvent(self, appId, eventCode):
        hiveTable = self.dbSession.query(HiveTable).filter_by(appId = appId, eventCode = eventCode).first()
        if hiveTable:
            return hiveTable.startFrom
        else:
            return None