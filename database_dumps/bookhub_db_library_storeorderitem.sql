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
-- Table structure for table `library_storeorderitem`
--

DROP TABLE IF EXISTS `library_storeorderitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `library_storeorderitem` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `quantity` int unsigned NOT NULL,
  `price` decimal(6,2) NOT NULL,
  `book_id` bigint NOT NULL,
  `order_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `library_storeorderitem_book_id_8b7a12c6_fk_library_book_id` (`book_id`),
  KEY `library_storeorderit_order_id_d3a89d17_fk_library_s` (`order_id`),
  CONSTRAINT `library_storeorderit_order_id_d3a89d17_fk_library_s` FOREIGN KEY (`order_id`) REFERENCES `library_storeorder` (`id`),
  CONSTRAINT `library_storeorderitem_book_id_8b7a12c6_fk_library_book_id` FOREIGN KEY (`book_id`) REFERENCES `library_book` (`id`),
  CONSTRAINT `library_storeorderitem_chk_1` CHECK ((`quantity` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `library_storeorderitem`
--

LOCK TABLES `library_storeorderitem` WRITE;
/*!40000 ALTER TABLE `library_storeorderitem` DISABLE KEYS */;
INSERT INTO `library_storeorderitem` VALUES (1,1,99.99,1,1),(2,2,99.99,1,2),(32,1,10.00,15,12),(33,1,10.00,15,13),(34,1,99.99,1,13),(35,1,10.00,15,14),(36,1,99.99,1,14),(37,1,99.99,18,14),(47,2,99.99,18,17),(49,1,10.00,15,19),(50,1,30.00,16,20),(58,1,99.99,1,27),(63,1,99.99,19,32),(64,3,99.99,19,33),(65,1,99.99,18,33),(66,1,25.00,17,33),(67,1,99.99,20,34),(68,1,99.99,20,35),(69,1,99.99,20,36),(70,3,20.00,14,37),(71,1,99.99,19,37),(78,1,99.99,21,41),(79,3,99.99,21,42),(80,1,99.99,19,42),(81,2,99.99,18,42),(82,3,99.99,21,43),(83,1,99.99,19,43),(84,2,99.99,18,43),(85,3,99.99,21,44),(86,1,99.99,19,44),(87,2,99.99,18,44),(88,2,99.99,5,45),(89,1,99.99,19,45),(90,1,99.99,22,46),(91,1,99.99,21,47),(92,1,99.99,21,48),(93,1,99.99,22,48),(94,1,99.99,21,49);
/*!40000 ALTER TABLE `library_storeorderitem` ENABLE KEYS */;
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
