# coding=utf-8
from sqlalchemy.exc import OperationalError
from controllers.BaseController import InstallController
from models.Config import Config
from sqlalchemy import create_engine
from utils.dbloader import migrate
from models.User import User
import hashlib
import os
import time

class InstallAction(InstallController):

    def prepare(self):
        super(InstallAction, self).prepare()
        self.errors = []

    def post(self):

        self.config = Config( dict([(key, value.pop()) for key, value in self.request.arguments.items()]) )

        # file and folder configuration

        if not self.request.arguments.has_key(Config.CORE_LOG_PATH):
            self.errors.append(u'Вы должны определить директорию для логов')
        else:
            try:
                path = self.createFolder(self.config.get(Config.CORE_LOG_PATH))
            except BaseException as exception:
                self.errors.append(u'Ошибка при создании директории логов: ' + exception.message)


        if not self.request.arguments.has_key(Config.CORE_APP_CONFIG_PATH):
            self.errors.append(u'Вы должны определить директорию конфигураций приложений')
        else:
            try:
                path = self.createFolder(self.config.get(Config.CORE_APP_CONFIG_PATH))
            except BaseException as exception:
                self.errors.append(u'Ошибка при создании директории конфигураций приложений: ' + exception.message)


        if not self.request.arguments.has_key(Config.CORE_RESULT_PATH):
            self.errors.append(u'Вы должны определить директорию результатов вычислений')
        else:
            try:
                path = self.createFolder(self.config.get(Config.CORE_RESULT_PATH))
            except BaseException as exception:
                self.errors.append(u'Ошибка при создании директории результатов вычислений: ' + exception.message)

        # mysql settings
        if not self.request.arguments.has_key(Config.MYSQL_HOST):
            self.errors.append(u'Вы должны определить хост для MySQL')
        elif not self.request.arguments.has_key(Config.MYSQL_DBNAME):
            self.errors.append(u'Вы должны определить имя базы данных')
        else:
            conn_str = 'mysql://'
            if self.config.get(Config.MYSQL_USER):
                conn_str += self.config.get(Config.MYSQL_USER)
                if self.config.get(Config.MYSQL_PASSWORD):
                    conn_str += ':' + self.config.get(Config.MYSQL_PASSWORD)

                conn_str += '@'

            conn_str += self.config.get(Config.MYSQL_HOST)
            print conn_str
            engine = create_engine(conn_str + '/?init_command=set%20names%20%22utf8%22', encoding='utf8', convert_unicode=True)
            try:
                connection = engine.connect()
            except OperationalError as op_error:
                self.errors.append(u'Ошибка соединения с MySQL: ' + op_error.message)
            except BaseException as ex:
                self.errors.append(u'Исключение SQLALCHEMY: ' + ex.message)
            else:

                try:
                    connection.execute('CREATE DATABASE IF NOT EXISTS `{0}` CHARACTER SET utf8 COLLATE utf8_general_ci'.
                        format(self.config.get(Config.MYSQL_DBNAME)))
                except BaseException as ex:
                    self.errors.append(u'Исключение при создании БД: ' + ex.message)
                finally:
                    connection.close()

        if not self.errors:
            # save config file
            raw_config = self.config.getRawConfig()
            try:
                configfile = open('server.cfg', 'wb')
            except BaseException as exception:
                self.errors.append(u'Ошибка при записи файла конфигурации: ' + exception.message)
            else:
                raw_config.write(configfile)
                configfile.close()
                self.redirect('/install/final')
                return

        print self.errors
        self.run()


    def get(self, *args, **kwargs):
        self.config = Config()
        self.run()


    def run(self):
        self.render('install/install.jinja2', {'config': self.config, 'curdir': os.path.abspath(os.curdir),
                                               'errors':self.errors})

    def createFolder(self, folder):
        path = os.path.abspath(folder)
        if not os.path.exists(path):
            os.makedirs(path, mode=0644)
        return path

class FinalInstallAction(InstallController):

    def get(self, *args, **kwargs):
        self.errors = []

        # перезагружаем конфигурацию приложения
        self.application.loadConfiguration()

        self.invalidateDBSessions()
        # миграция БД
        password = None
        try:
            connection = self.getDBSession()
            migrate(connection = connection)
        except BaseException as exception:
            self.errors.append(u'Ошибка при миграции БД: ' + exception.message)
        else:
            # create admin user
            password = hashlib.sha256(str(time.time())).hexdigest()[5:11]
            user = User()
            user.fullname = 'Admin'
            user.login = 'admin'
            user.password = hashlib.sha256(password).hexdigest()
            user.role = User.ROLE_ADMIN
            try:
                connection.merge(user)
                connection.commit()
            except BaseException as exception:
                self.errors.append(u'Ошибка при создани пользователя: ' + exception.message)
            else:
                self.application.isInstalled = True

        self.render('install/end.jinja2', {'errors': self.errors, 'admin_pass': password})