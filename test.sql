-- --------------------------------------------------------
-- 호스트:                          192.168.110.114
-- 서버 버전:                        10.5.9-MariaDB - MariaDB Server
-- 서버 OS:                        Linux
-- HeidiSQL 버전:                  12.6.0.6765
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- test 데이터베이스 구조 내보내기
CREATE DATABASE IF NOT EXISTS `test` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
USE `test`;

-- 테이블 test.ETL_DW_HISTORY 구조 내보내기
CREATE TABLE IF NOT EXISTS `ETL_DW_HISTORY` (
  `dw_idx` int(11) NOT NULL AUTO_INCREMENT,
  `writer` varchar(50) DEFAULT NULL,
  `content` varchar(1000) DEFAULT NULL,
  `indate` datetime DEFAULT current_timestamp(),
  `download_yn` varchar(50) NOT NULL,
  PRIMARY KEY (`dw_idx`),
  KEY `writer` (`writer`),
  CONSTRAINT `ETL_DW_HISTORY_ibfk_1` FOREIGN KEY (`writer`) REFERENCES `TBL_USER` (`user_Id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

-- 테이블 데이터 test.ETL_DW_HISTORY:~0 rows (대략적) 내보내기

-- 테이블 test.ETL_UPLOAD_HISTORY 구조 내보내기
CREATE TABLE IF NOT EXISTS `ETL_UPLOAD_HISTORY` (
  `upload_idx` int(11) NOT NULL AUTO_INCREMENT,
  `file_idx` int(11) DEFAULT NULL,
  `writer` varchar(50) DEFAULT NULL,
  `indate` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`upload_idx`),
  KEY `file_idx` (`file_idx`),
  KEY `writer` (`writer`),
  CONSTRAINT `ETL_UPLOAD_HISTORY_ibfk_1` FOREIGN KEY (`file_idx`) REFERENCES `TBL_FILE` (`file_idx`),
  CONSTRAINT `ETL_UPLOAD_HISTORY_ibfk_2` FOREIGN KEY (`writer`) REFERENCES `TBL_USER` (`user_Id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

-- 테이블 데이터 test.ETL_UPLOAD_HISTORY:~0 rows (대략적) 내보내기

-- 테이블 test.TBL_BOARD 구조 내보내기
CREATE TABLE IF NOT EXISTS `TBL_BOARD` (
  `board_idx` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(300) DEFAULT NULL,
  `contents` varchar(4000) DEFAULT NULL,
  `count` int(11) DEFAULT NULL,
  `writer` varchar(50) DEFAULT NULL,
  `indate` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`board_idx`),
  KEY `writer` (`writer`),
  CONSTRAINT `TBL_BOARD_ibfk_1` FOREIGN KEY (`writer`) REFERENCES `TBL_USER` (`user_Id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

-- 테이블 데이터 test.TBL_BOARD:~4 rows (대략적) 내보내기
INSERT IGNORE INTO `TBL_BOARD` (`board_idx`, `title`, `contents`, `count`, `writer`, `indate`) VALUES
	(11, '공시지가_1990년_sample', NULL, NULL, 'admin', '2024-07-08 16:29:11'),
	(12, '공시지가_2024년', NULL, NULL, 'admin', '2024-07-08 16:29:18'),
	(13, '공시지가_2024년_sample', NULL, NULL, 'admin', '2024-07-08 16:29:24'),
	(14, '공시지가_1990년', NULL, NULL, 'admin', '2024-07-08 16:29:45');

-- 테이블 test.TBL_FILE 구조 내보내기
CREATE TABLE IF NOT EXISTS `TBL_FILE` (
  `file_idx` int(11) NOT NULL AUTO_INCREMENT,
  `file_name` varchar(255) NOT NULL,
  `board_idx` int(11) DEFAULT NULL,
  `writer` varchar(50) DEFAULT NULL,
  `indate` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`file_idx`),
  KEY `board_idx` (`board_idx`),
  KEY `writer` (`writer`),
  CONSTRAINT `TBL_FILE_ibfk_1` FOREIGN KEY (`board_idx`) REFERENCES `TBL_BOARD` (`board_idx`) ON DELETE CASCADE,
  CONSTRAINT `TBL_FILE_ibfk_2` FOREIGN KEY (`writer`) REFERENCES `TBL_USER` (`user_Id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

-- 테이블 데이터 test.TBL_FILE:~4 rows (대략적) 내보내기
INSERT IGNORE INTO `TBL_FILE` (`file_idx`, `file_name`, `board_idx`, `writer`, `indate`) VALUES
	(11, '공시지가_1990년_sample.csv', 11, 'admin', '2024-07-08 16:29:11'),
	(12, '공시지가_2024년.csv', 12, 'admin', '2024-07-08 16:29:18'),
	(13, '공시지가_2024년_sample.csv', 13, 'admin', '2024-07-08 16:29:24'),
	(14, '공시지가_1990년.csv', 14, 'admin', '2024-07-08 16:29:45');

-- 테이블 test.TBL_REPLY 구조 내보내기
CREATE TABLE IF NOT EXISTS `TBL_REPLY` (
  `reply_idx` int(11) NOT NULL AUTO_INCREMENT,
  `board_idx` int(11) NOT NULL,
  `seq` int(11) NOT NULL,
  `reply` varchar(1000) DEFAULT NULL,
  `writer` varchar(50) DEFAULT NULL,
  `indate` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`reply_idx`),
  KEY `board_idx` (`board_idx`),
  CONSTRAINT `TBL_REPLY_ibfk_1` FOREIGN KEY (`board_idx`) REFERENCES `TBL_BOARD` (`board_idx`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

-- 테이블 데이터 test.TBL_REPLY:~0 rows (대략적) 내보내기

-- 테이블 test.TBL_USER 구조 내보내기
CREATE TABLE IF NOT EXISTS `TBL_USER` (
  `user_Id` varchar(50) NOT NULL,
  `user_name` varchar(30) DEFAULT NULL,
  `password` varchar(20) DEFAULT NULL,
  `user_type` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`user_Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 테이블 데이터 test.TBL_USER:~2 rows (대략적) 내보내기
INSERT IGNORE INTO `TBL_USER` (`user_Id`, `user_name`, `password`, `user_type`) VALUES
	('admin', '관리자', '1234', 'admin'),
	('guest', '사용자', '1234', 'guest');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
