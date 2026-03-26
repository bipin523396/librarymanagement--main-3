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
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-03-23 16:08:06.726778'),(2,'auth','0001_initial','2026-03-23 16:08:06.876331'),(3,'admin','0001_initial','2026-03-23 16:08:06.912289'),(4,'admin','0002_logentry_remove_auto_add','2026-03-23 16:08:06.918449'),(5,'admin','0003_logentry_add_action_flag_choices','2026-03-23 16:08:06.930073'),(6,'contenttypes','0002_remove_content_type_name','2026-03-23 16:08:06.951279'),(7,'auth','0002_alter_permission_name_max_length','2026-03-23 16:08:06.962752'),(8,'auth','0003_alter_user_email_max_length','2026-03-23 16:08:06.970336'),(9,'auth','0004_alter_user_username_opts','2026-03-23 16:08:06.972995'),(10,'auth','0005_alter_user_last_login_null','2026-03-23 16:08:06.983893'),(11,'auth','0006_require_contenttypes_0002','2026-03-23 16:08:06.984398'),(12,'auth','0007_alter_validators_add_error_messages','2026-03-23 16:08:06.986695'),(13,'auth','0008_alter_user_username_max_length','2026-03-23 16:08:07.000752'),(14,'auth','0009_alter_user_last_name_max_length','2026-03-23 16:08:07.014613'),(15,'auth','0010_alter_group_name_max_length','2026-03-23 16:08:07.020301'),(16,'auth','0011_update_proxy_permissions','2026-03-23 16:08:07.023516'),(17,'auth','0012_alter_user_first_name_max_length','2026-03-23 16:08:07.034505'),(18,'library','0001_initial','2026-03-23 16:08:07.118759'),(19,'sessions','0001_initial','2026-03-23 16:08:07.126343'),(20,'library','0002_book_image','2026-03-24 12:56:39.063836'),(21,'account','0001_initial','2026-03-24 16:56:29.520412'),(22,'account','0002_email_max_length','2026-03-24 16:56:29.551266'),(23,'account','0003_alter_emailaddress_create_unique_verified_email','2026-03-24 16:56:29.570723'),(24,'account','0004_alter_emailaddress_drop_unique_email','2026-03-24 16:56:29.592890'),(25,'account','0005_emailaddress_idx_upper_email','2026-03-24 16:56:29.600502'),(26,'account','0006_emailaddress_lower','2026-03-24 16:56:29.607107'),(27,'account','0007_emailaddress_idx_email','2026-03-24 16:56:29.625055'),(28,'account','0008_emailaddress_unique_primary_email_fixup','2026-03-24 16:56:29.632111'),(29,'account','0009_emailaddress_unique_primary_email','2026-03-24 16:56:29.636163'),(30,'sites','0001_initial','2026-03-24 16:56:29.640456'),(31,'sites','0002_alter_domain_unique','2026-03-24 16:56:29.647770'),(32,'socialaccount','0001_initial','2026-03-24 16:56:29.732237'),(33,'socialaccount','0002_token_max_lengths','2026-03-24 16:56:29.750965'),(34,'socialaccount','0003_extra_data_default_dict','2026-03-24 16:56:29.755839'),(35,'socialaccount','0004_app_provider_id_settings','2026-03-24 16:56:29.788373'),(36,'socialaccount','0005_socialtoken_nullable_app','2026-03-24 16:56:29.816068'),(37,'socialaccount','0006_alter_socialaccount_extra_data','2026-03-24 16:56:29.828815'),(38,'library','0003_usersettings','2026-03-24 21:24:37.809667'),(39,'library','0003_storeorder_book_price_storeorderitem_cart','2026-03-25 09:28:55.062635'),(40,'library','0004_merge_20260325_0928','2026-03-25 09:28:55.064986'),(41,'library','0005_storeorder_address_storeorder_assigned_rider_and_more','2026-03-25 12:31:02.662284'),(42,'library','0006_alter_storeorder_status','2026-03-25 12:34:41.594957'),(43,'library','0007_complaint','2026-03-25 15:53:50.114581'),(44,'library','0008_branch_book_branch_order_branch_storeorder_branch','2026-03-25 19:26:17.955877'),(45,'library','0009_deliveryrider_profile_picture_and_more','2026-03-26 09:45:45.982251');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
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
