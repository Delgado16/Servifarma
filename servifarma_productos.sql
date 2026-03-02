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
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `descripcion` text,
  `categoria_id` int NOT NULL,
  `principio_activo` varchar(150) DEFAULT NULL,
  `presentacion` varchar(100) DEFAULT NULL,
  `tipo_producto` enum('simple','jerarquico') DEFAULT 'simple',
  `unidad_base_id` int NOT NULL,
  `precio_costo` decimal(10,2) NOT NULL,
  `porcentaje_ganancia` decimal(5,2) DEFAULT '30.00',
  `precio_venta` decimal(10,2) NOT NULL,
  `stock_actual` int DEFAULT '0',
  `stock_minimo` int DEFAULT '5',
  `lote` varchar(50) DEFAULT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `unidad_base_id` (`unidad_base_id`),
  KEY `idx_producto_categoria` (`categoria_id`),
  KEY `idx_producto_codigo` (`codigo`),
  CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`),
  CONSTRAINT `productos_ibfk_2` FOREIGN KEY (`unidad_base_id`) REFERENCES `unidades_medida` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (1,'895412364M','DOLO NERVISE AMP SELECTPHARMA','primera prueba',1,'Tylenol, Tempra','Tabletas de 500mg','simple',1,20.00,30.00,5.50,121,20,'12387ML','2026-07-29',1,'2026-02-10 00:40:30'),(2,'7841256369CD','VITAMINAS C','yes mamey',5,'nitrogeno','27','simple',8,250.00,30.00,7.00,62,25,'123887423VC','2027-02-17',1,'2026-02-10 05:52:18');
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
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
