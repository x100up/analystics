import ConfigParser

class Config():
    '''
    Struct for app settings
    '''

    CORE_LOG_PATH = 'core_log_path'
    CORE_APP_CONFIG_PATH = 'core_app_configs'
    CORE_RESULT_PATH = 'core_result_path'

    MYSQL_USER = 'mysql_user'
    MYSQL_HOST = 'mysql_host'
    MYSQL_PORT = 'mysql_port'
    MYSQL_DBNAME = 'mysql_dbname'
    MYSQL_PASSWORD = 'mysql_password'


    def __init__(self, values = None):
        self.values = {
            self.CORE_LOG_PATH: 'log',
            self.CORE_APP_CONFIG_PATH: 'app_configs',
            self.CORE_RESULT_PATH: 'result',

            self.MYSQL_HOST: 'localhost',

            'hive_prefix': 'stat_',
            'hive_port': '10000',
            'hive_host': 'localhost'
        }

        if values:
            self.values = dict(self.values.items() + values.items())


    def __getattr__(self, item):
        return self.get(item)

    def get(self, key):
        if self.values.has_key(key):
            return self.values[key]
        return None

    def getRawConfig(self):
        config = ConfigParser.RawConfigParser()
        config.add_section('core')
        config.add_section('mysql')
        config.add_section('hive')

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