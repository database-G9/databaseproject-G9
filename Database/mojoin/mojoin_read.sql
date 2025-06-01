-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: mojoin
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `read`
--

DROP TABLE IF EXISTS `read`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `read` (
  `Account` char(20) NOT NULL,
  `nIndex` int NOT NULL,
  `History` int unsigned NOT NULL,
  PRIMARY KEY (`Account`,`nIndex`),
  CONSTRAINT `Account` FOREIGN KEY (`Account`) REFERENCES `user` (`Account`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `read`
--

LOCK TABLES `read` WRITE;
/*!40000 ALTER TABLE `read` DISABLE KEYS */;
INSERT INTO `read` VALUES ('aaa',30,2),('aaa',34,1),('aaa',76,1),('aaa',110,1),('aaa',165,4),('aaa',333,2),('aaa',922,3),('aaa',1213,1),('bbb',9,1),('bbb',757,1),('bbb',1111,2),('ccc',9,3),('ccc',110,0),('ccc',165,3),('ccc',333,1),('ccc',757,0),('ccc',922,4),('ccc',1111,1),('ccc',1213,2),('ddd',34,1),('ddd',76,1),('ddd',97,1),('ddd',98,1),('ddd',99,1),('ddd',101,1),('ddd',102,1),('ddd',104,1),('ddd',125,1),('ddd',167,1),('U002',590,1),('U002',622,1),('U002',730,1),('U002',910,1),('U002',922,1),('U003',964,1),('U003',987,1),('U003',988,1),('U003',1000,1),('U004',1032,1),('U004',1037,1),('U004',1038,1),('U004',1039,1),('U005',1047,1),('U005',1048,1),('U005',1052,1),('U005',1072,1),('U006',1076,1),('U006',1078,1),('U006',1079,1),('U006',1084,1),('U007',1090,1),('U007',1106,1),('U007',1115,1),('U007',1120,1),('U008',1121,1),('U008',1122,1),('U008',1123,1),('U008',1124,1),('U009',1127,1),('U009',1139,1),('U009',1148,1),('U009',1155,1),('U010',1157,1),('U010',1162,1),('U010',1167,1),('U010',1197,1);
/*!40000 ALTER TABLE `read` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-01 16:01:04
