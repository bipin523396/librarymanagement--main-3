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
-- Table structure for table `library_storeorder`
--

DROP TABLE IF EXISTS `library_storeorder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `library_storeorder` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `total_amount` decimal(8,2) NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` int NOT NULL,
  `address` longtext,
  `assigned_rider_id` bigint DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `zip_code` varchar(20) DEFAULT NULL,
  `branch_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `library_storeorder_user_id_0e207194_fk_auth_user_id` (`user_id`),
  KEY `library_storeorder_assigned_rider_id_24980236_fk_library_d` (`assigned_rider_id`),
  KEY `library_storeorder_branch_id_6c05f348_fk_library_branch_id` (`branch_id`),
  CONSTRAINT `library_storeorder_assigned_rider_id_24980236_fk_library_d` FOREIGN KEY (`assigned_rider_id`) REFERENCES `library_deliveryrider` (`id`),
  CONSTRAINT `library_storeorder_branch_id_6c05f348_fk_library_branch_id` FOREIGN KEY (`branch_id`) REFERENCES `library_branch` (`id`),
  CONSTRAINT `library_storeorder_user_id_0e207194_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `library_storeorder`
--

LOCK TABLES `library_storeorder` WRITE;
/*!40000 ALTER TABLE `library_storeorder` DISABLE KEYS */;
INSERT INTO `library_storeorder` VALUES (1,99.99,'Pending','2026-03-25 09:35:14.524531',18,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(2,199.98,'Pending','2026-03-25 09:35:41.006713',18,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(12,10.00,'Pending','2026-03-25 11:24:04.028286',20,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(13,109.99,'Pending','2026-03-25 11:36:52.376425',20,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(14,209.98,'Pending','2026-03-25 11:37:14.140289',20,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(17,199.98,'Assigned','2026-03-25 11:56:14.149255',20,NULL,2,NULL,NULL,NULL,NULL,NULL,NULL),(19,10.00,'Assigned','2026-03-25 12:12:32.664632',8,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(20,30.00,'Pending','2026-03-25 12:18:36.846417',7,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(27,99.99,'Assigned','2026-03-25 16:21:03.492477',26,'Sona Nagar, Thiagarajar Polytechnic College Road, Suramangalam (P.O.)',9,'salem','bipi1@gmail.com','Rahulk','Tamil Nadu','636 005',NULL),(32,99.99,'Delivered','2026-03-25 17:26:00.489366',26,'Sona Nagar, Thiagarajar Polytechnic College Road, Suramangalam (P.O.)',NULL,'salem','bipinsagrmatha321@gmail.com','Bipin yaav','Tamil Nadu','636 005',NULL),(33,424.96,'Delivered','2026-03-25 17:59:26.298536',7,'Sona Nagar, Thiagarajar Polytechnic College Road, Suramangalam (P.O.)',NULL,'salem','bipinsaarmatha321@gmail.com','Bipin ya','Tamil Nadu','636 005',NULL),(34,99.99,'Assigned','2026-03-25 18:06:09.538073',37,'Sona Nagar, Thiagarajar Polytechnic College Road, Suramangalam (P.O.)',15,'salem','binsagarmatha321@gmail.com','Bipin yad','Tamil Nadu','636 005',NULL),(35,99.99,'Failed','2026-03-25 18:08:49.242997',37,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(36,99.99,'Delivered','2026-03-25 18:09:25.809483',37,'Sona Nagar, Thiagarajar Polytechnic College Road, Suramangalam (P.O.)',NULL,'salem','bipinsagarmath321@gmail.com','Bipin ydav','Tamil Nadu','636 005',NULL),(37,159.99,'Pending','2026-03-26 03:46:28.979876',8,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(41,99.99,'Pending','2026-03-26 04:44:07.000692',40,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(42,599.94,'Failed','2026-03-26 05:01:38.518774',8,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(43,599.94,'Failed','2026-03-26 05:02:30.122856',8,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(44,599.94,'Delivered','2026-03-26 05:03:22.935215',8,'Sona Nagar, Thiagarajar Polytechnic College Road, Suramangalam (P.O.)',7,'salem','bipinsagmatha321@gmail.com','Bipn yadav','Tamil Nadu','636 005',NULL),(45,299.97,'Delivered','2026-03-26 05:34:24.207783',26,'Sivathapuram',7,'salem','bipinsagarmatha321@gmail.com','Bipin yadav','Tamil Nadu','636 307',NULL),(46,99.99,'Pending','2026-03-26 08:28:16.221416',44,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(47,99.99,'Pending','2026-03-26 09:58:49.072137',42,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(48,199.98,'Assigned','2026-03-26 10:06:23.865328',42,'Sona Nagar, Thiagarajar Polytechnic College Road, Suramangalam (P.O.)',7,'salem','bipinsagarmatha321@gmail.com','Bipin yadav','Tamil Nadu','636 005',NULL),(49,99.99,'Assigned','2026-03-26 10:08:43.778642',42,'Sona Nagar, Thiagarajar Polytechnic College Road, Suramangalam (P.O.)',7,'salem','bipinsagarmatha321@gmail.com','Bipin yadav','Tamil Nadu','636 005',NULL);
/*!40000 ALTER TABLE `library_storeorder` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-26 19:37:09
