-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: servifarma
-- ------------------------------------------------------
-- Server version	9.4.0

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
-- Table structure for table `detalles_venta`
--

DROP TABLE IF EXISTS `detalles_venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalles_venta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `venta_id` int NOT NULL,
  `tipo_detalle` enum('producto','servicio','combo') NOT NULL,
  `referencia_id` int DEFAULT NULL,
  `cantidad` int DEFAULT '1',
  `unidad_id` int DEFAULT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(15,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `venta_id` (`venta_id`),
  KEY `unidad_id` (`unidad_id`),
  CONSTRAINT `detalles_venta_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `detalles_venta_ibfk_2` FOREIGN KEY (`unidad_id`) REFERENCES `unidades_medida` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalles_venta`
--

LOCK TABLES `detalles_venta` WRITE;
/*!40000 ALTER TABLE `detalles_venta` DISABLE KEYS */;
INSERT INTO `detalles_venta` VALUES (1,1,'producto',1,1,1,5.50,5.50),(2,2,'producto',1,1,1,5.50,5.50),(3,2,'servicio',1,1,NULL,500.00,500.00),(4,3,'producto',1,1,1,5.50,5.50),(5,3,'producto',2,1,8,7.00,7.00),(6,3,'servicio',1,1,NULL,500.00,500.00),(7,4,'servicio',2,1,NULL,30.00,30.00),(8,4,'servicio',1,1,NULL,500.00,500.00),(9,4,'producto',1,1,1,5.50,5.50),(10,4,'producto',2,1,8,7.00,7.00),(11,5,'producto',1,1,1,5.50,5.50),(12,5,'producto',2,1,8,7.00,7.00),(13,6,'servicio',2,1,NULL,30.00,30.00),(14,6,'producto',1,1,1,5.50,5.50),(15,7,'producto',1,1,1,5.50,5.50),(16,7,'producto',2,1,8,7.00,7.00),(17,7,'servicio',1,1,NULL,500.00,500.00),(18,8,'producto',1,1,1,5.50,5.50),(19,8,'producto',2,1,8,7.00,7.00),(20,8,'servicio',1,1,NULL,500.00,500.00),(21,9,'producto',1,1,1,5.50,5.50),(22,9,'producto',2,1,8,7.00,7.00),(23,9,'servicio',1,1,NULL,500.00,500.00),(24,9,'servicio',2,1,NULL,30.00,30.00),(25,10,'producto',1,1,1,5.50,5.50),(26,10,'producto',2,1,8,7.00,7.00),(27,10,'servicio',1,1,NULL,500.00,500.00),(28,10,'servicio',2,1,NULL,30.00,30.00),(29,11,'producto',1,1,1,5.50,5.50),(30,11,'producto',2,1,8,7.00,7.00),(31,11,'servicio',1,8,NULL,500.00,4000.00),(32,11,'servicio',2,6,NULL,30.00,180.00),(33,12,'producto',1,1,1,5.50,5.50),(34,12,'producto',2,1,8,7.00,7.00),(35,13,'producto',1,1,1,5.50,5.50),(36,14,'servicio',1,1,NULL,500.00,500.00),(37,14,'servicio',2,1,NULL,30.00,30.00),(38,14,'producto',1,4,1,5.50,22.00),(39,15,'producto',2,5,8,7.00,35.00),(40,16,'producto',2,16,8,7.00,112.00),(41,17,'producto',1,1,1,5.50,5.50),(42,17,'servicio',1,1,NULL,500.00,500.00),(43,17,'servicio',2,7,NULL,30.00,210.00);
/*!40000 ALTER TABLE `detalles_venta` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-01 15:49:10
