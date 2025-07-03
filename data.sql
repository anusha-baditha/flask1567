-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: ecommy
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin_details`
--

DROP TABLE IF EXISTS `admin_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_details` (
  `admin_username` varchar(30) NOT NULL,
  `admin_email` varchar(50) NOT NULL,
  `admin_password` varbinary(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `address` text,
  PRIMARY KEY (`admin_email`),
  UNIQUE KEY `admin_email` (`admin_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_details`
--

LOCK TABLES `admin_details` WRITE;
/*!40000 ALTER TABLE `admin_details` DISABLE KEYS */;
INSERT INTO `admin_details` VALUES ('anusha','anusha@codegnan.com',_binary '$2b$12$tD71yWRkhs/F2z8X2v8N4OQnft9ei4IcGsQFJETb55whNLNtJ..zy','2025-06-13 14:46:04','Vijayawada p b siddhartha college');
/*!40000 ALTER TABLE `admin_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `items` (
  `itemid` binary(16) NOT NULL,
  `item_name` mediumtext NOT NULL,
  `description` longtext NOT NULL,
  `item_cost` decimal(20,4) NOT NULL,
  `item_quantity` mediumint unsigned DEFAULT NULL,
  `item_category` enum('Home appliances','Electronics','Sports','Fashion','Grocery') DEFAULT NULL,
  `added_by` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `imgname` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`itemid`),
  KEY `items_addedby` (`added_by`),
  CONSTRAINT `items_addedby` FOREIGN KEY (`added_by`) REFERENCES `admin_details` (`admin_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `items`
--

LOCK TABLES `items` WRITE;
/*!40000 ALTER TABLE `items` DISABLE KEYS */;
INSERT INTO `items` VALUES (_binary 'i\“\√Jã\∑[¿>∫Ωöç','ACcc','Brand	DAIKIN\r\nCapacity	1.5 Tons\r\nCooling Power	17100 British Thermal Units\r\nSpecial Feature	High Ambient Operation upto 52¬∞C, 3D Airflow, Dew Clean Technology, Triple Display, PM 2.5 Filter\r\nProduct Dimensions	22.9D x 88.5W x 29.8H Centimeters\r\n',37898.0000,23,'Home appliances','anusha@codegnan.com','2025-06-16 13:55:08','Fo5Af3.jfif');
/*!40000 ALTER TABLE `items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `order_id` int unsigned NOT NULL AUTO_INCREMENT,
  `order_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `item_id` binary(16) NOT NULL,
  `item_name` varchar(255) NOT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  `payment_by` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`order_id`),
  KEY `payment_by` (`payment_by`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`payment_by`) REFERENCES `users` (`useremail`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`itemid`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,'2025-06-25 15:20:36',_binary 'i\“\√Jã\∑[¿>∫Ωöç','ACcc',3789800.00,'anusha@codegnan.com'),(2,'2025-06-26 14:35:43',_binary 'i\“\√Jã\∑[¿>∫Ωöç','ACcc',3789800.00,'anusha@codegnan.com'),(3,'2025-06-26 14:36:47',_binary 'i\“\√Jã\∑[¿>∫Ωöç','ACcc',3789800.00,'anusha@codegnan.com');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `r_id` int unsigned NOT NULL AUTO_INCREMENT,
  `review_text` text,
  `create_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `itemid` binary(16) DEFAULT NULL,
  `added_by` varchar(30) DEFAULT NULL,
  `rating` enum('1','2','3','4','5') DEFAULT NULL,
  PRIMARY KEY (`r_id`),
  KEY `itemis` (`itemid`),
  KEY `added_by` (`added_by`),
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`itemid`) REFERENCES `items` (`itemid`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`added_by`) REFERENCES `users` (`useremail`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
INSERT INTO `reviews` VALUES (1,'good','2025-06-27 15:04:14',_binary 'i\“\√Jã\∑[¿>∫Ωöç','anusha@codegnan.com','4');
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `useremail` varchar(30) NOT NULL,
  `username` varchar(30) NOT NULL,
  `password` varbinary(255) DEFAULT NULL,
  `address` text NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `gender` enum('Male','Female','Other') DEFAULT NULL,
  PRIMARY KEY (`useremail`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('anusha@codegnan.com','anusha',_binary '$2b$12$qydd0JKbnQJxU8lJNc4rE.jVsuaBnsUQjZdB/pfCqJYThgEkol5WG','Vijayawada p b siddhartha college','2025-06-20 13:56:46','Female');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-03 14:50:47
