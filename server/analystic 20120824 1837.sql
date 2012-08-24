-- Скрипт сгенерирован Devart dbForge Studio for MySQL, Версия 5.0.97.1
-- Домашняя страница продукта: http://www.devart.com/ru/dbforge/mysql/studio
-- Дата скрипта: 24.08.2012 18:37:23
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
-- Описание для таблицы user
--
DROP TABLE IF EXISTS user;
CREATE TABLE user (
  userId INT(11) NOT NULL AUTO_INCREMENT,
  login VARCHAR(50) DEFAULT NULL,
  fullname VARCHAR(50) DEFAULT NULL,
  `password` VARCHAR(50) DEFAULT NULL,
  role ENUM('user','admin') NOT NULL DEFAULT 'user',
  PRIMARY KEY (userId)
)
ENGINE = INNODB
AUTO_INCREMENT = 2
AVG_ROW_LENGTH = 16384
CHARACTER SET latin1
COLLATE latin1_swedish_ci;

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
AVG_ROW_LENGTH = 585
CHARACTER SET latin1
COLLATE latin1_swedish_ci;

-- 
-- Вывод данных для таблицы user
--
INSERT INTO user VALUES 
  (1, 'x100up', NULL, '123123', 'admin');

-- 
-- Вывод данных для таблицы worker
--
INSERT INTO worker VALUES 
  ('009a58df-3780-46d1-a6be-6a9df18e765d', '2012-08-23 17:06:15', NULL, 1, 'DIED'),
  ('03a02875-7321-4586-b08d-68dde6d7b092', '2012-08-23 17:59:08', '2012-08-23 18:12:17', 1, 'ERROR'),
  ('0fdcc162-30dd-404d-bcb7-1bfda63b7ef5', '2012-08-23 17:59:09', '2012-08-23 18:12:16', 1, 'ERROR'),
  ('22ffdb0c-4484-45d3-9323-5a68ceb936c2', '2012-08-23 17:19:50', NULL, 1, 'DIED'),
  ('23d87e5b-71f6-4822-aa6f-9ec5716be317', '2012-08-23 17:59:08', '2012-08-23 18:12:17', 1, 'ERROR'),
  ('2dc81c14-4e49-4679-b3e0-e5efb1080b2c', '2012-08-23 17:22:41', NULL, 1, 'DIED'),
  ('323a6531-971f-4183-b256-730274051409', '2012-08-23 17:11:13', NULL, 1, 'DIED'),
  ('36749458-b879-4d89-acbd-f229122db249', '2012-08-23 17:59:06', '2012-08-23 18:12:16', 1, 'ERROR'),
  ('5b88c7c7-0d62-47f2-a0d8-e9d997869d50', '2012-08-24 10:36:23', '2012-08-24 10:36:24', 1, 'ERROR'),
  ('65f68e22-9137-49cb-bd1b-b8d453c45a60', '2012-08-23 18:12:58', '2012-08-23 18:12:58', 1, 'ERROR'),
  ('66f8dcbf-6327-4022-b4f6-9071bd916eb5', '2012-08-23 17:33:28', NULL, 1, 'DIED'),
  ('68db144e-6337-42ab-b3ba-bd3e38a3da3f', '2012-08-23 16:57:15', NULL, 1, 'ALIVE'),
  ('6a24214e-64df-47d0-ab72-39569454bb48', '2012-08-23 17:59:08', '2012-08-23 18:12:16', 1, 'ERROR'),
  ('7487d2b6-a0c1-4d7f-b4ee-75785235c3a1', '2012-08-23 17:01:49', NULL, 1, 'ALIVE'),
  ('74ef50e8-d39a-49e1-a3be-e36f9568354c', '2012-08-23 17:59:07', '2012-08-23 18:12:17', 1, 'ERROR'),
  ('7bf310ea-947e-4793-a39c-fb46102f0d03', '2012-08-23 17:59:07', '2012-08-23 18:12:17', 1, 'ERROR'),
  ('8456f636-e378-4861-975a-9133d29fe19c', '2012-08-23 17:34:08', '2012-08-23 17:34:08', 1, 'DIED'),
  ('9e15a914-6e09-4d0c-b018-f444b622ed61', '2012-08-23 17:59:09', '2012-08-23 18:12:16', 1, 'ERROR'),
  ('b0529a2c-242e-4906-a9ba-ef76127a200d', '2012-08-23 17:58:33', '2012-08-23 18:00:03', 1, 'SUCCESS'),
  ('b892964a-30ad-4539-99e3-ed17104938b2', '2012-08-24 10:37:48', NULL, 1, 'DIED'),
  ('be58591e-6c06-4923-92a4-878141d6daf4', '2012-08-23 17:04:04', NULL, 1, 'DIED'),
  ('c3121ddd-12d0-42af-906a-c51bb8359620', '2012-08-23 17:33:10', NULL, 1, 'DIED'),
  ('c6f1f49b-4575-4120-b214-07d0f079a1c9', '2012-08-23 17:58:48', '2012-08-23 18:12:17', 1, 'ERROR'),
  ('cb9ca0c4-03e3-445b-ab28-d3502cf95078', '2012-08-23 17:17:12', NULL, 1, 'DIED'),
  ('ea3c60ae-b7ac-4def-bb6d-2125dfa88b97', '2012-08-24 10:36:40', NULL, 1, 'DIED'),
  ('ec9e8717-8231-4c5a-b4d1-dc35c94077f3', '2012-08-23 17:56:01', '2012-08-23 17:56:40', 1, 'DIED'),
  ('f6567236-e4f9-4eda-9fb0-db12720f1364', '2012-08-23 17:34:47', '2012-08-23 17:35:27', 1, 'DIED'),
  ('f825dc47-07f6-401c-abdb-1be5072d3f02', '2012-08-23 18:13:17', '2012-08-23 18:17:31', 1, 'ERROR');

-- 
-- Включение внешних ключей
-- 
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;