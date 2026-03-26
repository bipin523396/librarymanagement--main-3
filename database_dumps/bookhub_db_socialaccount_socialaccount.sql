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
-- Table structure for table `socialaccount_socialaccount`
--

DROP TABLE IF EXISTS `socialaccount_socialaccount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `socialaccount_socialaccount` (
  `id` int NOT NULL AUTO_INCREMENT,
  `provider` varchar(200) NOT NULL,
  `uid` varchar(191) NOT NULL,
  `last_login` datetime(6) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `extra_data` json NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `socialaccount_socialaccount_provider_uid_fc810c6e_uniq` (`provider`,`uid`),
  KEY `socialaccount_socialaccount_user_id_8146e70c_fk_auth_user_id` (`user_id`),
  CONSTRAINT `socialaccount_socialaccount_user_id_8146e70c_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialaccount`
--

LOCK TABLES `socialaccount_socialaccount` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialaccount` DISABLE KEYS */;
INSERT INTO `socialaccount_socialaccount` VALUES (2,'google','105064871834027554614','2026-03-25 17:54:10.745685','2026-03-24 21:09:59.732260','{\"aud\": \"37499849662-79ob4citrf0vhkr541bmmhbapmdmaab5.apps.googleusercontent.com\", \"azp\": \"37499849662-79ob4citrf0vhkr541bmmhbapmdmaab5.apps.googleusercontent.com\", \"exp\": 1774464850, \"iat\": 1774461250, \"iss\": \"https://accounts.google.com\", \"sub\": \"105064871834027554614\", \"name\": \"Bipin Yadav\", \"email\": \"bipinsagarmatha123@gmail.com\", \"at_hash\": \"BHpMM1EW1gHPJtGC4fFNgg\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocI71RI_RD5B-k7VSJWAn01-aMJJqtLTenOnmJDUjcOotLOOwgM=s96-c\", \"given_name\": \"Bipin\", \"family_name\": \"Yadav\", \"email_verified\": true}',7),(3,'google','117471383032591424991','2026-03-26 06:48:56.101633','2026-03-24 21:10:25.825893','{\"aud\": \"37499849662-79ob4citrf0vhkr541bmmhbapmdmaab5.apps.googleusercontent.com\", \"azp\": \"37499849662-79ob4citrf0vhkr541bmmhbapmdmaab5.apps.googleusercontent.com\", \"exp\": 1774511336, \"iat\": 1774507736, \"iss\": \"https://accounts.google.com\", \"sub\": \"117471383032591424991\", \"name\": \"FILMNOVA NEXUS\", \"email\": \"bipinsagarmatha213@gmail.com\", \"at_hash\": \"rfJ1lUbxVqhQ5U5xI9E9mQ\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocINJsV3STPYSEa6F_XazCIthbzkrTXW4ZUggQ5Vu8Q2gNRrz9U=s96-c\", \"given_name\": \"FILMNOVA NEXUS\", \"email_verified\": true}',8),(4,'google','111151374748205467320','2026-03-25 17:53:46.492367','2026-03-24 21:26:53.065455','{\"aud\": \"37499849662-79ob4citrf0vhkr541bmmhbapmdmaab5.apps.googleusercontent.com\", \"azp\": \"37499849662-79ob4citrf0vhkr541bmmhbapmdmaab5.apps.googleusercontent.com\", \"exp\": 1774464826, \"iat\": 1774461226, \"iss\": \"https://accounts.google.com\", \"sub\": \"111151374748205467320\", \"name\": \"Jerome\", \"email\": \"jeromejohnitty@gmail.com\", \"at_hash\": \"yfo5-JPSJCIeitCk0LhFTg\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocIUUNXfDkqlV3zF-UCK6b9hhtobVbS-OdpglZ6oR1e6RkO5Hg=s96-c\", \"given_name\": \"Jerome\", \"email_verified\": true}',9),(5,'google','110207988986108223552','2026-03-25 04:18:25.992783','2026-03-25 04:18:07.925793','{\"aud\": \"37499849662-79ob4citrf0vhkr541bmmhbapmdmaab5.apps.googleusercontent.com\", \"azp\": \"37499849662-79ob4citrf0vhkr541bmmhbapmdmaab5.apps.googleusercontent.com\", \"exp\": 1774415906, \"iat\": 1774412306, \"iss\": \"https://accounts.google.com\", \"sub\": \"110207988986108223552\", \"name\": \"Nono\", \"email\": \"thenameis848@gmail.com\", \"at_hash\": \"ht-bwb6HbuMElEcom-emAg\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocL6glAcULXYmmFTFtWYVpMJvzqRi7HtoLweiy-JM6qRpfmB9w=s96-c\", \"given_name\": \"Nono\", \"email_verified\": true}',11),(6,'google','106568491035551410166','2026-03-26 09:38:52.348476','2026-03-25 16:19:31.293873','{\"aud\": \"37499849662-79ob4citrf0vhkr541bmmhbapmdmaab5.apps.googleusercontent.com\", \"azp\": \"37499849662-79ob4citrf0vhkr541bmmhbapmdmaab5.apps.googleusercontent.com\", \"exp\": 1774521532, \"iat\": 1774517932, \"iss\": \"https://accounts.google.com\", \"sub\": \"106568491035551410166\", \"name\": \"Bipin Yadav\", \"email\": \"bipinsagarmatha321@gmail.com\", \"at_hash\": \"c_La2Psnik6j0mFHgwUdoQ\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocLRvGNmbFFR1Beo43WPmkMgZoNHevVszrfGfgX4s4gFiIOVlivf=s96-c\", \"given_name\": \"Bipin\", \"family_name\": \"Yadav\", \"email_verified\": true}',26),(7,'google','106720176706095182787','2026-03-26 04:41:12.622978','2026-03-26 04:41:12.623066','{\"aud\": \"37499849662-79ob4citrf0vhkr541bmmhbapmdmaab5.apps.googleusercontent.com\", \"azp\": \"37499849662-79ob4citrf0vhkr541bmmhbapmdmaab5.apps.googleusercontent.com\", \"exp\": 1774503672, \"iat\": 1774500072, \"iss\": \"https://accounts.google.com\", \"sub\": \"106720176706095182787\", \"name\": \"ZEIO\", \"email\": \"rahulsbgmct@gmail.com\", \"at_hash\": \"Qq6yfGMy4DotVRrCmntW0w\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocLyj7J9tR-Gwe7NlgwBvbON-URqWjuNyNBD_DX9luNd5e6NMTSX=s96-c\", \"given_name\": \"ZEIO\", \"email_verified\": true}',40);
/*!40000 ALTER TABLE `socialaccount_socialaccount` ENABLE KEYS */;
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
