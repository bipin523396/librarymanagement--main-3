CREATE DATABASE  IF NOT EXISTS `bookhub_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `bookhub_db`;
-- MySQL dump 10.13  Distrib 8.0.43, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: bookhub_db
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `library_userprofile`
--

DROP TABLE IF EXISTS `library_userprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `library_userprofile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `phone` varchar(15) NOT NULL,
  `address` longtext NOT NULL,
  `pincode` varchar(10) NOT NULL,
  `membership_expiry` date DEFAULT NULL,
  `membership_id` bigint DEFAULT NULL,
  `user_id` int NOT NULL,
  `profile_picture` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `library_userprofile_membership_id_f72cf1f7_fk_library_m` (`membership_id`),
  CONSTRAINT `library_userprofile_membership_id_f72cf1f7_fk_library_m` FOREIGN KEY (`membership_id`) REFERENCES `library_membershipplan` (`id`),
  CONSTRAINT `library_userprofile_user_id_fad21699_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `library_userprofile`
--

LOCK TABLES `library_userprofile` WRITE;
/*!40000 ALTER TABLE `library_userprofile` DISABLE KEYS */;
INSERT INTO `library_userprofile` VALUES (10,'N/A','Address to be updated by member','000000','2026-04-24',1,24,NULL),(11,'N/A','Address to be updated by member','000000','2026-04-24',3,25,NULL),(12,'1234567890','Not provided yet','123455',NULL,NULL,35,NULL),(13,'N/A','Address to be updated by member','000000','2026-04-24',2,36,NULL),(14,'N/A','Sona Nagar, Thiagarajar Polytechnic College Road, Suramangalam (P.O.)','000000','2026-04-24',1,7,NULL),(15,'N/A','Address to be updated by member','000000','2026-04-24',2,38,NULL),(17,'N/A','Address to be updated by member','000000','2026-04-25',2,26,NULL),(18,'N/A','Admin','000000',NULL,NULL,41,NULL),(19,'N/A','Admin','000000',NULL,NULL,43,NULL),(20,'N/A','Admin','000000',NULL,NULL,44,NULL),(21,'N/A','Admin','000000',NULL,NULL,45,NULL);
/*!40000 ALTER TABLE `library_userprofile` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-26 19:37:10
