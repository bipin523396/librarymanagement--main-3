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
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (7,'pbkdf2_sha256$600000$rPyRMzgqlG6pUF3KFXkjkN$KdcyAoRKe4XODoRGy138D/+ryzZqt9CxlvOWWe5dhNY=','2026-03-26 06:52:36.482009',1,'bipinsagarmatha123@gmail.com','Bipin adav','','bipinsagarmatha123@gmail.com',1,1,'2026-03-24 20:05:59.674248'),(8,'!FsZU263qLsolAbyHfwUfd95uOZx9s0zr6ugFrA0t','2026-03-26 06:48:56.112776',0,'bipinsagarmatha213@gmail.com','FILMNOVA NEXUS','','bipinsagarmatha213@gmail.com',0,1,'2026-03-24 21:10:25.812223'),(9,'!9ecjykQnPw7Qf9ZkcG8snJXef5qj2p0ipHOA4P0D','2026-03-25 17:53:46.502684',0,'jeromejohnitty@gmail.com','Jerome','','jeromejohnitty@gmail.com',0,1,'2026-03-24 21:26:53.048891'),(11,'!btsiueQIoKQUzl1McYPseW1teGdrWI6PwSJMOQvS','2026-03-25 04:18:26.003174',0,'thenameis848@gmail.com','Nono','','thenameis848@gmail.com',0,1,'2026-03-25 04:18:07.907644'),(12,'pbkdf2_sha256$600000$VpfxsuXqdERdEw2uFKem94$1tzR46Mhlc31DfqJw6r3K/Kg/mOkZB5qHmmWbwx/ZCM=',NULL,0,'rahul','rahul k ','','',0,1,'2026-03-25 04:28:18.860987'),(13,'pbkdf2_sha256$600000$GI22HZWiBSKCjUurbPbZSB$+AcWm+uf3NM6cS0LatL7C9AgM0OvuXpAlA6YoORkE9w=',NULL,0,'kjhgf','hgfd','','',0,1,'2026-03-25 04:32:57.903952'),(15,'pbkdf2_sha256$600000$wx8vxTiPemW2fZ7WchtwX3$wbjcFL4sXRoHM+MUzowQbFr8MQahCiYdDQ99n0P5tRA=',NULL,0,'fdsa','dsfds','','',0,1,'2026-03-25 04:40:03.075559'),(18,'pbkdf2_sha256$600000$tcFOqjsjypx8YEUfbK3xUB$7i7kTPR393lxSJqY9GDVRBwe8I+rwqTlH+7pIb/4+J4=','2026-03-26 06:49:14.660000',0,'yogesh','yogesh','','',0,1,'2026-03-25 06:15:30.940870'),(20,'pbkdf2_sha256$600000$AfSLPBY1y3vO7ueYTio6Zn$wDbffyPMHPFsFiJFh88PTVBMYb/oBWRWvuOq2ypbJXc=','2026-03-25 11:17:40.345801',1,'testuser','','','test@example.com',1,1,'2026-03-25 10:17:08.837562'),(24,'pbkdf2_sha256$600000$A9M3kox0o13bRzyAgW53RA$HjjZEA8o2oX/U40C2w0ilN5OnVUzF7k2Gz+hta6VZ1I=',NULL,0,'jonas@gmail.com','jonas','','jonas@gmail.com',0,1,'2026-03-25 15:57:07.172647'),(25,'pbkdf2_sha256$600000$rNB3Q4osuXXv8rxdpqPbDy$NTf9V64Pq9vW0FMvpaMJJVvbNa17eTUE7goiNIgquDg=',NULL,0,'bipy@gmail.com','rahulk','','bipy@gmail.com',0,1,'2026-03-25 16:07:07.271873'),(26,'!oJuryDKCIQCuEsasQsZ8i4G4aaRj45kopMJ9j1d8','2026-03-26 09:38:52.364039',0,'bipinsagarmatha321@gmail.com','nirm','Yadav','bipinsagarmatha321@gmail.com',0,1,'2026-03-25 16:19:31.272230'),(27,'pbkdf2_sha256$600000$mgL0YND6lD8KfNgg1yCOMK$zJyaSiX+aMf+r6TpLBKrAvtITGeUoVXrlbwV/0ar1lQ=',NULL,0,'testrider1','Test Rider 1','','',0,1,'2026-03-25 17:02:41.630907'),(28,'pbkdf2_sha256$600000$4eNDmFCqqNptClDWluDAa6$WdvPTf+KE0h3njLeR+oja5j8lwc9S7760is7AK5Lquo=','2026-03-25 17:08:45.984970',0,'binay','binay','','',0,1,'2026-03-25 17:07:41.957374'),(35,'pbkdf2_sha256$600000$wtT37lVG4PXkwiMaOvOTuB$kTrAqW4r9eKPLjrflnyEIMhZjJu2nObeYze1ZCIQSfk=','2026-03-25 17:53:23.256245',0,'jer@gmail.com','jer','john','jer@gmail.com',0,1,'2026-03-25 17:53:00.714133'),(36,'pbkdf2_sha256$600000$24dfV8QYHcr7PMtXZjCMev$0ZucouFpDIMEdvEJG4ACSQgsmsXPJ1DItzNJhmuaSpw=',NULL,0,'jeromejohn@gmail.com','jeromejohn','','jeromejohn@gmail.com',0,1,'2026-03-25 17:56:35.468456'),(37,'pbkdf2_sha256$600000$EgbCBq0JGnI6CooHmWMKJX$AkQwMxqoCHaBCMO3zCDKCttaDhiyZybKs3RUgQKVhq4=','2026-03-25 18:05:44.482310',0,'aashish','rambilas sah','','',0,1,'2026-03-25 18:05:15.015188'),(38,'pbkdf2_sha256$600000$b2aplhWRqLvrTQKtUQnlNU$F3f8Fvywa/ipxPuM9xTEAU6xTjdWfDyZ7HjwsElonwU=',NULL,0,'bhgc@gmail.com','ramansh','','bhgc@gmail.com',0,1,'2026-03-25 18:46:29.567795'),(40,'!shwPlpMw9DYf94gsbCmZUpEZildCqB8Xp3AdmTwQ','2026-03-26 04:41:12.636194',0,'rahulsbgmct@gmail.com','ZEIO','','rahulsbgmct@gmail.com',0,1,'2026-03-26 04:41:12.606474'),(41,'pbkdf2_sha256$600000$OQIjnG0HhvnF2KUR02KVGY$uihAXTBECwWkP+W/qPj3r/WGS72xlQzMBbzDyXT56KI=','2026-03-26 07:04:30.583938',1,'jerome@gmail.com','jerome','','jerome@gmail.com',1,1,'2026-03-26 07:03:49.497277'),(42,'pbkdf2_sha256$600000$3HbJ4ZeMfz41yEeIVVLaOg$ySnVqaWFIUYkbvbUZyXtILKNgeK5wl4/UF12UyYEjOQ=','2026-03-26 10:09:40.763417',1,'admin','','','admin@bookhub.local',1,1,'2026-03-26 07:08:07.191374'),(43,'pbkdf2_sha256$600000$K3RK5Kv5GRJHLdpswoRhmx$gGtVePtOtOkd1NDTBO//DwKvlmzOVNbfI3jFGMxyjzI=','2026-03-26 07:10:52.207975',1,'rahul@gmail.com','rahul','','rahul@gmail.com',1,1,'2026-03-26 07:08:48.717882'),(44,'pbkdf2_sha256$600000$nHZ3Oal34rrtKS6UvWjV56$Flvnn3jSiecSvdmPKnzH/ZA0oM3l7YASG2WFuiUklhk=','2026-03-26 08:32:59.621271',1,'yogesh@gmail.com','yogesh','','yogesh@gmail.com',1,1,'2026-03-26 07:12:25.677135'),(45,'pbkdf2_sha256$600000$oSitFTMuFHx67HZ3PBnTyo$0FQGoDNsWBR2GKpXcBSmUIu/apUHv3igpqVrIGfWUQw=','2026-03-26 09:27:21.973164',1,'sugu@gmail.com','sugu','','sugu@gmail.com',1,1,'2026-03-26 09:26:57.194507');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
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
