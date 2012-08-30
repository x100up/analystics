Flume

http://archive.cloudera.com/cdh/3/flume-ng-1.1.0-cdh3u4/FlumeUserGuide.html

source - источник данных, которые обрабаотыват Flume.

Мы используем org.apache.flume.source.thriftLegacy.ThriftLegacySource 

sink - место, куда складываются данные, полученные от источника.
hdfs.rollInterval 30 Количество секунд до на начала записи следующего файла
hdfs.rollSize 1024 - макс размер одного файла 
hdfs.rollCount 10 -  количество событий которое будет записан в фаил
hdfs.batchSize -  количсевто событий которое будет записано в фаил, перед тем как он зафлушится в хдфс

channel - канал (буффер), по которому дынные от источника попадают в sink.

Наиболее целесобразно использовать org.apache.flume.channel.recoverable.memory.RecoverableMemoryChannel
wal.dataDir (${user.home}/.flume/recoverable-memory-channel
wal.rollSize (0x04000000) Максимальный размер одного файла в байтах перед прокруткой 
wal.minRetentionPeriod 300000 Минимальное количество времени в милиссекундах, перед записью в лог
wal.workerInterval 60000 Как часто будут проверятся старые лог
wal.maxLogsSize (0x20000000) макс размер всех логов. не включая текущий лог
