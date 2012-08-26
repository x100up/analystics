-- Скрипт сгенерирован Devart dbForge Studio for MySQL, Версия 5.0.97.1
-- Домашняя страница продукта: http://www.devart.com/ru/dbforge/mysql/studio
-- Дата скрипта: 26.08.2012 15:51:46
-- Версия сервера: 5.5.24-0ubuntu0.12.04.1
-- Версия клиента: 4.1

-- 
-- Отключение внешних ключей
-- 
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;

-- 
-- Установка кодировки, с использованием которой клиент будет посылать запросы на сервер
--
SET NAMES 'utf8';

-- 
-- Установка базы данных по умолчанию
--
USE analystic;

--
-- Описание для таблицы app
--
DROP TABLE IF EXISTS app;
CREATE TABLE app (
  appId INT(11) NOT NULL AUTO_INCREMENT,
  name VARCHAR(70) DEFAULT NULL,
  code VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (appId)
)
ENGINE = INNODB
AUTO_INCREMENT = 1
CHARACTER SET utf8
COLLATE utf8_general_ci;

--
-- Описание для таблицы user
--
DROP TABLE IF EXISTS user;
CREATE TABLE user (
  userId INT(11) NOT NULL AUTO_INCREMENT,
  login VARCHAR(50) DEFAULT NULL,
  fullname VARCHAR(50) DEFAULT NULL,
  `password` VARCHAR(50) DEFAULT NULL,
  role ENUM('user','admin') NOT NULL DEFAULT 'user',
  PRIMARY KEY (userId),
  UNIQUE INDEX login (login)
)
ENGINE = INNODB
AUTO_INCREMENT = 2
AVG_ROW_LENGTH = 16384
CHARACTER SET latin1
COLLATE latin1_swedish_ci;

--
-- Описание для таблицы userAppRule
--
DROP TABLE IF EXISTS userAppRule;
CREATE TABLE userAppRule (
  userId INT(11) NOT NULL,
  appId INT(11) NOT NULL,
  rule ENUM('ALLOW','DENY') NOT NULL DEFAULT 'ALLOW'
)
ENGINE = INNODB
CHARACTER SET utf8
COLLATE utf8_general_ci;

--
-- Описание для таблицы worker
--
DROP TABLE IF EXISTS worker;
CREATE TABLE worker (
  uuid VARCHAR(48) NOT NULL,
  startDate DATETIME NOT NULL,
  endDate DATETIME DEFAULT NULL,
  userId INT(11) NOT NULL,
  status ENUM('ALIVE','DIED','SUCCESS','ERROR') NOT NULL DEFAULT 'ALIVE',
  PRIMARY KEY (uuid),
  CONSTRAINT FK_worker_user_userId FOREIGN KEY (userId)
    REFERENCES user(userId) ON DELETE RESTRICT ON UPDATE RESTRICT
)
ENGINE = INNODB
CHARACTER SET latin1
COLLATE latin1_swedish_ci;

-- 
-- Вывод данных для таблицы app
--
-- Таблица analystic.app не содержит данных

-- 
-- Вывод данных для таблицы user
--
INSERT INTO user VALUES 
  (1, 'admin', NULL, '123123', 'admin');

-- 
-- Вывод данных для таблицы userAppRule
--
-- Таблица analystic.userAppRule не содержит данных

-- 
-- Вывод данных для таблицы worker
--
-- Таблица analystic.worker не содержит данных

-- 
-- Включение внешних ключей
-- 
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;