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
-- Table structure for table `library_complaint`
--

DROP TABLE IF EXISTS `library_complaint`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `library_complaint` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(254) NOT NULL,
  `subject` varchar(200) NOT NULL,
  `message` longtext NOT NULL,
  `is_resolved` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `library_complaint_user_id_0e6cbb8f_fk_auth_user_id` (`user_id`),
  CONSTRAINT `library_complaint_user_id_0e6cbb8f_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `library_complaint`
--

LOCK TABLES `library_complaint` WRITE;
/*!40000 ALTER TABLE `library_complaint` DISABLE KEYS */;
INSERT INTO `library_complaint` VALUES (1,'Bipin yadav','bipinsagarmatha321@gmail.com','money not transfer','problem with payment ',0,'2026-03-25 16:41:36.516882',NULL),(2,'Bipin ','bipinsagarmatha321@gmail.com','money not transfer','transfer it to me',1,'2026-03-25 16:43:34.002325',NULL),(3,'Bipin yadav','bipinsagarha321@gmail.com','my wesite is not working ','plz fix it as soon as possible',0,'2026-03-25 17:39:49.764408',NULL),(4,'Bipin yadav','bipinsagarha321@gmail.com','my wesite is not working ','plz fix it as soon as possible',1,'2026-03-25 17:40:08.441530',NULL),(5,'Bipin yadav','bipinsagarmatha321@gmail.com','need refund ','book not recieved need refund immediately\r\n',1,'2026-03-25 17:54:52.223612',7),(6,'Bipin yadav','bipinsagarmatha321@gmail.com','money not transfer','did\'t receive the mail of receipt',1,'2026-03-26 04:01:50.580423',NULL),(7,'sugu','bipinsagarmat@gmail.com','need refund ','i cancelled no refund',0,'2026-03-26 05:19:10.351469',18),(8,'Bipin yada','bipinsagarmath@gmail.com','money not transfer','money is not transfered',1,'2026-03-26 05:38:00.371497',NULL),(9,'Bipin yadav','bipinsagarmatha321@gmail.com','my wesite is not working ','aghfg',1,'2026-03-26 09:58:26.549056',42);
/*!40000 ALTER TABLE `library_complaint` ENABLE KEYS */;
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
