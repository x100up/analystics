import ConfigParser

class Config():
    """
    Struct for app settings
    """

    APP_HOST = 'app_host'
    APP_PORT = 'app_port'

    HIVE_HOST = 'hive_host'
    HIVE_PORT = 'hive_port'
    HIVE_PREFIX = 'hive_prefix'

    MYSQL_USER = 'mysql_user'
    MYSQL_HOST = 'mysql_host'
    MYSQL_PORT = 'mysql_port'
    MYSQL_DBNAME = 'mysql_dbname'
    MYSQL_PASSWORD = 'mysql_password'

    HDFS_HOST = 'hdfs_host'
    HDFS_PORT = 'hdfs_port'
    HDFS_USERNAME = 'hdfs_username'
    HDFS_STAT_ROOT = 'statistic_path'

    HADOOP_NAMENODE = 'hadoop_namenode'
    HADOOP_YARN_RESOURCEMANAGER = 'hadoop_yarn_resourcemanager'
    HADOOP_NODEMANAGER = 'hadoop_nodemanager'



    def __init__(self, values = None):
        # default settings
        self.values = {
            self.MYSQL_HOST: 'localhost',
            self.HIVE_PREFIX: 'stat_',
            self.HIVE_PORT: '10000',
            self.HIVE_HOST: 'localhost',
            self.HDFS_STAT_ROOT: '/statistics/'
        }

        if values:
            self.values = dict(self.values.items() + values.items())


    def __getattr__(self, item):
        return self.get(item)

    def get(self, key, default = None):
        if self.values.has_key(key):
            return self.values[key]
        return default

    def set(self, key, value):
        self.values[key] = value

    def getRawConfig(self):
        config = ConfigParser.RawConfigParser()
        config.add_section('app')
        config.add_section('mysql')
        config.add_section('hive')
        config.add_section('hdfs')
        config.add_section('hadoop')

        for key, value in self.values.items():
            section, key = key.split('_', 1)

            if config.has_section(section):
                config.set(section, key, value)

        return config

    def readConfigFile(self, configfile):
        configParser = ConfigParser.RawConfigParser()
        configParser.read([configfile])
        sections = configParser.sections()
        for section in sections:
            items = configParser.items(section)
            for k, v in items:
                self.values[section + '_' + k] = v