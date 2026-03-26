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
-- Table structure for table `library_book`
--

DROP TABLE IF EXISTS `library_book`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `library_book` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `author` varchar(100) NOT NULL,
  `category` varchar(50) NOT NULL,
  `isbn` varchar(20) NOT NULL,
  `copies_total` int NOT NULL,
  `copies_available` int NOT NULL,
  `status` varchar(20) NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `price` decimal(6,2) NOT NULL,
  `branch_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `isbn` (`isbn`),
  KEY `library_book_branch_id_cacf1f9a_fk_library_branch_id` (`branch_id`),
  CONSTRAINT `library_book_branch_id_cacf1f9a_fk_library_branch_id` FOREIGN KEY (`branch_id`) REFERENCES `library_branch` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `library_book`
--

LOCK TABLES `library_book` WRITE;
/*!40000 ALTER TABLE `library_book` DISABLE KEYS */;
INSERT INTO `library_book` VALUES (1,'harry potter','harry','Fiction','1',1,1,'Available','book_images/Screenshot_2026-03-25_at_3.53.56PM.png',99.99,1),(5,'MONALISA','MONA','Fiction','2',5,5,'Available','book_images/Screenshot_2026-03-25_at_3.51.02PM.png',99.99,1),(6,'einstein','albert','Fiction','1244',123,123,'Available','book_images/Screenshot_2026-03-25_at_3.52.51PM.png',99.99,1),(10,'Business Fundamentals','B. Guru','Business','B001',1,10,'Available','book_images/Screenshot_2026-03-26_at_8.39.00AM.png',25.00,1),(11,'Academic Excellence','Professor X','Academic','A001',1,5,'Available','book_images/Screenshot_2026-03-26_at_8.36.59AM.png',40.00,1),(12,'Mind Over Matter','Psych Guru','Self-Help','S001',1,20,'Available','book_images/Screenshot_2026-03-26_at_8.36.02AM.png',15.00,1),(13,'Python Mastery','Guido','Academic','P001',1,5,'Available','book_images/Screenshot_2026-03-26_at_8.35.18AM.png',50.00,1),(14,'Success Habits','Covey','Self-Help','S002',1,15,'Available','book_images/Screenshot_2026-03-26_at_8.34.26AM.png',20.00,1),(15,'Ancient Myths','Unknown','Fiction','F004',1,8,'Available','book_images/Screenshot_2026-03-26_at_8.33.47AM.png',10.00,1),(16,'The Mystery of the Manor','Agatha','Mystery','M001',1,3,'Available','book_images/Screenshot_2026-03-26_at_8.32.49AM.png',30.00,1),(17,'Horror Nights','Stephen King','Horror','H001',1,7,'Available','book_images/Screenshot_2026-03-26_at_8.31.06AM.png',25.00,1),(18,'super30','akshay kumar','Academic','1324',1,1,'Available','book_images/Screenshot_2026-03-26_at_8.32.08AM.png',99.99,1),(19,'invisibleman ','harry','Fiction','14235',11,11,'Available','book_images/Screenshot_2026-03-26_at_8.19.40AM.png',99.99,1),(20,'oliver twist','jonathan hills','Self Help','234567',109,109,'Available','book_images/Screenshot_2026-03-26_at_8.18.42AM.png',99.99,1),(21,'my story ','yogesh','Fiction','12324',1,1,'Available','book_images/PHOTO-2026-02-27-23-02-56_6nAbv69.jpg',99.99,NULL),(22,'sdf','asdfg','Toddlers','12',13,13,'Available','book_images/PHOTO-2026-02-27-23-02-56.jpg',99.99,NULL);
/*!40000 ALTER TABLE `library_book` ENABLE KEYS */;
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
