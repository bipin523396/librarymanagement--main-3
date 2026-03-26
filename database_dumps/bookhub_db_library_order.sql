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
-- Table structure for table `library_order`
--

DROP TABLE IF EXISTS `library_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `library_order` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `order_id` varchar(20) NOT NULL,
  `order_type` varchar(50) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `completed_at` datetime(6) DEFAULT NULL,
  `assigned_rider_id` bigint DEFAULT NULL,
  `book_id` bigint NOT NULL,
  `customer_id` bigint NOT NULL,
  `branch_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_id` (`order_id`),
  KEY `library_order_assigned_rider_id_cdac7ab2_fk_library_d` (`assigned_rider_id`),
  KEY `library_order_book_id_6fc9df47_fk_library_book_id` (`book_id`),
  KEY `library_order_customer_id_4073446c_fk_library_userprofile_id` (`customer_id`),
  KEY `library_order_branch_id_5a5f0c84_fk_library_branch_id` (`branch_id`),
  CONSTRAINT `library_order_assigned_rider_id_cdac7ab2_fk_library_d` FOREIGN KEY (`assigned_rider_id`) REFERENCES `library_deliveryrider` (`id`),
  CONSTRAINT `library_order_book_id_6fc9df47_fk_library_book_id` FOREIGN KEY (`book_id`) REFERENCES `library_book` (`id`),
  CONSTRAINT `library_order_branch_id_5a5f0c84_fk_library_branch_id` FOREIGN KEY (`branch_id`) REFERENCES `library_branch` (`id`),
  CONSTRAINT `library_order_customer_id_4073446c_fk_library_userprofile_id` FOREIGN KEY (`customer_id`) REFERENCES `library_userprofile` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `library_order`
--

LOCK TABLES `library_order` WRITE;
/*!40000 ALTER TABLE `library_order` DISABLE KEYS */;
/*!40000 ALTER TABLE `library_order` ENABLE KEYS */;
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
