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
-- Table structure for table `detalles_compra`
--

DROP TABLE IF EXISTS `detalles_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalles_compra` (
  `id` int NOT NULL AUTO_INCREMENT,
  `compra_id` int NOT NULL,
  `producto_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `unidad_id` int NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(15,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `compra_id` (`compra_id`),
  KEY `producto_id` (`producto_id`),
  KEY `unidad_id` (`unidad_id`),
  CONSTRAINT `detalles_compra_ibfk_1` FOREIGN KEY (`compra_id`) REFERENCES `compras` (`id`) ON DELETE CASCADE,
  CONSTRAINT `detalles_compra_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`),
  CONSTRAINT `detalles_compra_ibfk_3` FOREIGN KEY (`unidad_id`) REFERENCES `unidades_medida` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalles_compra`
--

LOCK TABLES `detalles_compra` WRITE;
/*!40000 ALTER TABLE `detalles_compra` DISABLE KEYS */;
INSERT INTO `detalles_compra` VALUES (1,1,1,20,1,20.00,400.00),(2,2,2,30,1,30.00,900.00),(3,3,1,10,1,15.00,150.00),(4,4,2,10,1,12.00,120.00);
/*!40000 ALTER TABLE `detalles_compra` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-01 15:49:09
