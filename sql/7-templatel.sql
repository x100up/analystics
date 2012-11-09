﻿CREATE TABLE taskTemplate(
  taskTemplateId BIGINT(20) NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) DEFAULT NULL,
  userId INT(11) NOT NULL,
  appId INT(11) NOT NULL,
  shared ENUM('YES', 'NO') DEFAULT 'NO',
  PRIMARY KEY (taskTemplateId),
  CONSTRAINT FK_taskTemplate_app_appId FOREIGN KEY (`appId`)
  REFERENCES `app` (appId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT FK_taskTemplate_user_userId FOREIGN KEY (`userId`)
  REFERENCES `user` (userId) ON DELETE CASCADE ON UPDATE CASCADE
)
ENGINE = INNODB
AUTO_INCREMENT = 1
CHARACTER SET utf8
COLLATE utf8_general_ci;