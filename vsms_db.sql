-- MySQL dump 10.13  Distrib 8.0.28, for Win64 (x86_64)
--
-- Host: localhost    Database: motormates
-- ------------------------------------------------------
-- Server version	8.0.28

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
-- Table structure for table `mechanics`
--

DROP TABLE IF EXISTS `mechanics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mechanics` (
  `mechanic_id` int NOT NULL AUTO_INCREMENT,
  `mechanic_name` varchar(100) NOT NULL,
  `contact` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`mechanic_id`)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mechanics`
--

LOCK TABLES `mechanics` WRITE;
/*!40000 ALTER TABLE `mechanics` DISABLE KEYS */;
INSERT INTO `mechanics` VALUES (101,'Manoj Yadav','9895473409'),(102,'Uday Rai','7754902980');
/*!40000 ALTER TABLE `mechanics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service_types`
--

DROP TABLE IF EXISTS `service_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `service_types` (
  `service_type_id` int NOT NULL AUTO_INCREMENT,
  `service_name` varchar(100) NOT NULL,
  `price` int DEFAULT '0',
  `description` text,
  PRIMARY KEY (`service_type_id`),
  UNIQUE KEY `service_name` (`service_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service_types`
--

LOCK TABLES `service_types` WRITE;
/*!40000 ALTER TABLE `service_types` DISABLE KEYS */;
/*!40000 ALTER TABLE `service_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `services`
--

DROP TABLE IF EXISTS `services`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `services` (
  `service_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `vehicle_id` int NOT NULL,
  `service_types` json DEFAULT NULL,
  `description` text,
  `pickup_required` varchar(10) DEFAULT NULL,
  `pickup_address` varchar(250) DEFAULT NULL,
  `service_date` date DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Pending',
  `assigned_mechanic` int DEFAULT NULL,
  `payment_status` varchar(20) DEFAULT 'Pending',
  `base_cost` int DEFAULT '0',
  `extra_charges` int DEFAULT '0',
  `Paid` int DEFAULT '0',
  `charge_description` text,
  `work_done` text,
  `request_date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`service_id`),
  KEY `customer_id` (`customer_id`),
  KEY `vehicle_id` (`vehicle_id`),
  KEY `assigned_mechanic` (`assigned_mechanic`),
  CONSTRAINT `services_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `services_ibfk_2` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`) ON DELETE CASCADE,
  CONSTRAINT `services_ibfk_3` FOREIGN KEY (`assigned_mechanic`) REFERENCES `mechanics` (`mechanic_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `services`
--

LOCK TABLES `services` WRITE;
/*!40000 ALTER TABLE `services` DISABLE KEYS */;
INSERT INTO `services` VALUES (10,1,1,'[\"Engine Repair\"]','Empty','No',NULL,'2025-07-24','Completed',102,'Pending',3000,110,3105,'cleaning and management','ok','2025-07-28 12:29:52'),(11,1,5,'[\"AC Service\"]','Empty','No',NULL,'2025-07-31','Pending',NULL,'Done',1500,0,1500,'','','2025-07-28 15:18:14'),(12,5,9,'[\"General Maintenance\"]','meri gadi ke engine se aawaj aari he. meri g*nd phat rahi he ki gadi kharab na ho jaye.','Yes','shamshan ghat, 4 bangla, budhi aurat ke ghar ke piche.','2025-07-28','Cancelled',NULL,'Pending',1000,85,1080,'','me nhi karra tera kam. ja kahi aur jake apni g*nd marwa !','2025-07-28 17:09:15'),(13,6,11,'[\"Oil Change\"]','Empty good work','No',NULL,'2025-07-28','Pending',NULL,'Done',500,0,500,'','','2025-07-28 17:43:32'),(14,1,1,'[\"AC Service\", \"General Maintenance\"]','','No',NULL,'2025-07-28','Pending',NULL,'Done',2500,0,2500,'','','2025-07-28 18:48:23');
/*!40000 ALTER TABLE `services` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `password` varchar(100) NOT NULL,
  `user_type` varchar(20) NOT NULL DEFAULT 'Customer',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Vaibhav Gupta','gvaibhav046@gmail.com','7722969402','1!Vaibhav','Customer'),(2,'Atharv shukla','atharvshukla1@gmail.com','9406530214','2@Vaibhav','Admin'),(3,'Tarushee Gupta','tarusheegupta214@gmail.com','8839732191','3#Vaibhav','Customer'),(4,'Anshul Gupta','ganshul@gmail.com','9406530251','asdfA1!q','Customer'),(5,'Aaditya Kamlaskar','aaditya@gmail.com','8956564834','Aaditya@123','Customer'),(6,'Naivedyasingh','naivedyasingh23@gmail.com','8956564890','Abcd123@','Customer');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vehicles`
--

DROP TABLE IF EXISTS `vehicles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vehicles` (
  `vehicle_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `vehicle_type` varchar(20) DEFAULT NULL,
  `vehicle_brand` varchar(100) DEFAULT NULL,
  `vehicle_model` varchar(100) DEFAULT NULL,
  `vehicle_no` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`vehicle_id`),
  UNIQUE KEY `vehicle_no` (`vehicle_no`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `vehicles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vehicles`
--

LOCK TABLES `vehicles` WRITE;
/*!40000 ALTER TABLE `vehicles` DISABLE KEYS */;
INSERT INTO `vehicles` VALUES (1,1,'Car','Honda','Civic','MP09US8398'),(2,1,'Bike','Hero','HF Deluxe','MP39IT6789'),(3,3,'Bike','Hero','Splendor','MP08CS2130'),(4,4,'Car','Honda','City','MP81ER2342'),(5,1,'Car','Hyundai','Verna','MP09UI8790'),(6,1,'Bike','Hero','HF Deluxe','MP67UI7843'),(7,1,'Car','Toyota','Fortuner','MP08UR5638'),(8,1,'Car','Toyota','Corolla','MP78IO9087'),(9,5,'Bike','Yamaha','MT-15','MP09AK0000'),(11,6,'Bike','Yamaha','R15','MP08CS3189'),(21,1,'Car','Toyota','Corolla','MP09ZC4771'),(22,1,'Car','Toyota','Corolla','MP09ZC4774'),(23,1,'Car','Toyota','Corolla','MP09AS3439');
/*!40000 ALTER TABLE `vehicles` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-01 16:29:00
