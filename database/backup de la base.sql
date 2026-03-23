CREATE DATABASE  IF NOT EXISTS `servifarma` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `servifarma`;
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
-- Table structure for table `categorias`
--

DROP TABLE IF EXISTS `categorias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias`
--

LOCK TABLES `categorias` WRITE;
/*!40000 ALTER TABLE `categorias` DISABLE KEYS */;
INSERT INTO `categorias` VALUES (1,'Analgésicos','Medicamentos para el dolor','2026-02-06 03:12:35',1),(2,'Antibióticos','Medicamentos para infecciones','2026-02-06 03:12:35',1),(3,'Antiinflamatorios','Medicamentos antiinflamatorios','2026-02-06 03:12:35',1),(4,'Antitérmicos','Medicamentos para la fiebre','2026-02-06 03:12:35',1),(5,'Vitaminas','Suplementos vitamínicos','2026-02-06 03:12:35',1),(6,'Suero Fisiológico','Soluciones de suero','2026-02-06 03:12:35',1),(7,'Desinfectantes','Productos desinfectantes','2026-02-06 03:12:35',1);
/*!40000 ALTER TABLE `categorias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `combos`
--

DROP TABLE IF EXISTS `combos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `combos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `descripcion` text,
  `precio_combo` decimal(10,2) NOT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `combos`
--

LOCK TABLES `combos` WRITE;
/*!40000 ALTER TABLE `combos` DISABLE KEYS */;
/*!40000 ALTER TABLE `combos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compras`
--

DROP TABLE IF EXISTS `compras`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compras` (
  `id` int NOT NULL AUTO_INCREMENT,
  `numero_documento` varchar(50) DEFAULT NULL,
  `proveedor_id` int NOT NULL,
  `usuario_id` int NOT NULL,
  `fecha_compra` date NOT NULL,
  `numero_factura` varchar(50) DEFAULT NULL,
  `total_costo` decimal(15,2) NOT NULL,
  `estado` enum('pendiente','completada','cancelada') DEFAULT 'pendiente',
  `observaciones` text,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero_documento` (`numero_documento`),
  KEY `usuario_id` (`usuario_id`),
  KEY `idx_compra_proveedor` (`proveedor_id`),
  KEY `idx_compra_fecha` (`fecha_compra`),
  CONSTRAINT `compras_ibfk_1` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id`),
  CONSTRAINT `compras_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compras`
--

LOCK TABLES `compras` WRITE;
/*!40000 ALTER TABLE `compras` DISABLE KEYS */;
INSERT INTO `compras` VALUES (1,'COMP-001',1,2,'2026-02-11','',400.00,'completada',NULL,'2026-02-12 01:49:12'),(2,'COMP-002',1,2,'2026-02-11','VITSMINAC/895632',900.00,'completada',NULL,'2026-02-12 02:25:50'),(3,'COMP-003',1,2,'2026-02-11','/895632',150.00,'completada',NULL,'2026-02-12 02:26:42'),(4,'COMP-004',2,2,'2026-02-11','VITSMINAC/895632',120.00,'completada',NULL,'2026-02-12 02:27:17'),(5,'COMP-005',1,2,'2026-03-08','/895632',20.00,'completada',NULL,'2026-03-09 00:06:06'),(6,'COMP-006',1,2,'2026-03-09','',5250.00,'completada',NULL,'2026-03-10 01:27:10'),(7,'COMP-007',2,2,'2026-03-09','',1050.00,'completada',NULL,'2026-03-10 03:25:49'),(8,'COMP-008',2,2,'2026-03-19','Factura',300.00,'completada',NULL,'2026-03-20 02:05:17'),(9,'COMP-009',1,2,'2026-03-20','primers compra',500.00,'completada',NULL,'2026-03-21 01:34:16');
/*!40000 ALTER TABLE `compras` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalles_combo`
--

DROP TABLE IF EXISTS `detalles_combo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalles_combo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `combo_id` int NOT NULL,
  `producto_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `unidad_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `combo_id` (`combo_id`),
  KEY `producto_id` (`producto_id`),
  KEY `unidad_id` (`unidad_id`),
  CONSTRAINT `detalles_combo_ibfk_1` FOREIGN KEY (`combo_id`) REFERENCES `combos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `detalles_combo_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`),
  CONSTRAINT `detalles_combo_ibfk_3` FOREIGN KEY (`unidad_id`) REFERENCES `unidades_medida` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalles_combo`
--

LOCK TABLES `detalles_combo` WRITE;
/*!40000 ALTER TABLE `detalles_combo` DISABLE KEYS */;
/*!40000 ALTER TABLE `detalles_combo` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalles_compra`
--

LOCK TABLES `detalles_compra` WRITE;
/*!40000 ALTER TABLE `detalles_compra` DISABLE KEYS */;
INSERT INTO `detalles_compra` VALUES (1,1,1,20,1,20.00,400.00),(2,2,2,30,1,30.00,900.00),(3,3,1,10,1,15.00,150.00),(4,4,2,10,1,12.00,120.00),(5,5,1,1,1,20.00,20.00),(6,6,3,150,1,30.00,4500.00),(7,6,2,3,1,250.00,750.00),(8,7,1,6,1,20.00,120.00),(9,7,3,6,1,30.00,180.00),(10,7,2,3,1,250.00,750.00),(11,8,3,100,2,3.00,300.00),(12,9,2,2,4,250.00,500.00);
/*!40000 ALTER TABLE `detalles_compra` ENABLE KEYS */;
UNLOCK TABLES;

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
  `variacion_id` int DEFAULT NULL,
  `cantidad` int DEFAULT '1',
  `unidad_id` int DEFAULT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(15,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `venta_id` (`venta_id`),
  KEY `unidad_id` (`unidad_id`),
  KEY `idx_variacion_id` (`variacion_id`),
  CONSTRAINT `detalles_venta_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `detalles_venta_ibfk_2` FOREIGN KEY (`unidad_id`) REFERENCES `unidades_medida` (`id`),
  CONSTRAINT `fk_detalles_venta_variacion` FOREIGN KEY (`variacion_id`) REFERENCES `variaciones_producto` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalles_venta`
--

LOCK TABLES `detalles_venta` WRITE;
/*!40000 ALTER TABLE `detalles_venta` DISABLE KEYS */;
INSERT INTO `detalles_venta` VALUES (1,1,'producto',1,NULL,1,1,5.50,5.50),(2,2,'producto',1,NULL,1,1,5.50,5.50),(3,2,'servicio',1,NULL,1,NULL,500.00,500.00),(4,3,'producto',1,NULL,1,1,5.50,5.50),(5,3,'producto',2,NULL,1,8,7.00,7.00),(6,3,'servicio',1,NULL,1,NULL,500.00,500.00),(7,4,'servicio',2,NULL,1,NULL,30.00,30.00),(8,4,'servicio',1,NULL,1,NULL,500.00,500.00),(9,4,'producto',1,NULL,1,1,5.50,5.50),(10,4,'producto',2,NULL,1,8,7.00,7.00),(11,5,'producto',1,NULL,1,1,5.50,5.50),(12,5,'producto',2,NULL,1,8,7.00,7.00),(13,6,'servicio',2,NULL,1,NULL,30.00,30.00),(14,6,'producto',1,NULL,1,1,5.50,5.50),(15,7,'producto',1,NULL,1,1,5.50,5.50),(16,7,'producto',2,NULL,1,8,7.00,7.00),(17,7,'servicio',1,NULL,1,NULL,500.00,500.00),(18,8,'producto',1,NULL,1,1,5.50,5.50),(19,8,'producto',2,NULL,1,8,7.00,7.00),(20,8,'servicio',1,NULL,1,NULL,500.00,500.00),(21,9,'producto',1,NULL,1,1,5.50,5.50),(22,9,'producto',2,NULL,1,8,7.00,7.00),(23,9,'servicio',1,NULL,1,NULL,500.00,500.00),(24,9,'servicio',2,NULL,1,NULL,30.00,30.00),(25,10,'producto',1,NULL,1,1,5.50,5.50),(26,10,'producto',2,NULL,1,8,7.00,7.00),(27,10,'servicio',1,NULL,1,NULL,500.00,500.00),(28,10,'servicio',2,NULL,1,NULL,30.00,30.00),(29,11,'producto',1,NULL,1,1,5.50,5.50),(30,11,'producto',2,NULL,1,8,7.00,7.00),(31,11,'servicio',1,NULL,8,NULL,500.00,4000.00),(32,11,'servicio',2,NULL,6,NULL,30.00,180.00),(33,12,'producto',1,NULL,1,1,5.50,5.50),(34,12,'producto',2,NULL,1,8,7.00,7.00),(35,13,'producto',1,NULL,1,1,5.50,5.50),(36,14,'servicio',1,NULL,1,NULL,500.00,500.00),(37,14,'servicio',2,NULL,1,NULL,30.00,30.00),(38,14,'producto',1,NULL,4,1,5.50,22.00),(39,15,'producto',2,NULL,5,8,7.00,35.00),(40,16,'producto',2,NULL,16,8,7.00,112.00),(41,17,'producto',1,NULL,1,1,5.50,5.50),(42,17,'servicio',1,NULL,1,NULL,500.00,500.00),(43,17,'servicio',2,NULL,7,NULL,30.00,210.00),(44,18,'servicio',1,NULL,1,NULL,500.00,500.00),(45,19,'servicio',2,NULL,1,NULL,30.00,30.00),(46,19,'servicio',1,NULL,1,NULL,500.00,500.00),(47,20,'servicio',1,NULL,1,NULL,500.00,500.00),(48,21,'producto',4,NULL,2,2,5.00,10.00),(49,21,'producto',1,NULL,1,1,26.00,26.00),(50,21,'producto',2,NULL,1,8,7.00,7.00);
/*!40000 ALTER TABLE `detalles_venta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimientos_inventario`
--

DROP TABLE IF EXISTS `movimientos_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientos_inventario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `producto_id` int NOT NULL,
  `tipo_movimiento` enum('entrada','salida','ajuste') NOT NULL,
  `cantidad` int NOT NULL,
  `cantidad_anterior` int NOT NULL,
  `cantidad_nueva` int NOT NULL,
  `referencia_tipo` varchar(50) DEFAULT NULL,
  `referencia_id` int DEFAULT NULL,
  `usuario_id` int NOT NULL,
  `observaciones` text,
  `fecha_movimiento` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  KEY `idx_movimiento_producto` (`producto_id`),
  KEY `idx_movimiento_fecha` (`fecha_movimiento`),
  CONSTRAINT `movimientos_inventario_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`),
  CONSTRAINT `movimientos_inventario_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos_inventario`
--

LOCK TABLES `movimientos_inventario` WRITE;
/*!40000 ALTER TABLE `movimientos_inventario` DISABLE KEYS */;
INSERT INTO `movimientos_inventario` VALUES (1,1,'entrada',20,100,120,'compra',1,2,'Compra #COMP-001','2026-02-12 01:49:13'),(2,2,'entrada',30,50,80,'compra',2,2,'Compra #COMP-002','2026-02-12 02:25:50'),(3,1,'entrada',10,120,130,'compra',3,2,'Compra #COMP-003','2026-02-12 02:26:42'),(4,2,'entrada',10,80,90,'compra',4,2,'Compra #COMP-004','2026-02-12 02:27:17'),(5,1,'salida',1,130,129,'venta',1,2,'Venta #1','2026-02-19 01:03:30'),(6,1,'salida',1,129,128,'venta',2,2,'Venta #2','2026-02-21 02:27:31'),(7,1,'salida',1,128,127,'venta',3,2,'Venta #3','2026-02-21 02:38:37'),(8,2,'salida',1,90,89,'venta',3,2,'Venta #3','2026-02-21 02:38:37'),(9,1,'salida',1,127,126,'venta',4,2,'Venta #4','2026-02-21 03:10:30'),(10,2,'salida',1,89,88,'venta',4,2,'Venta #4','2026-02-21 03:10:30'),(11,1,'salida',1,126,125,'venta',5,2,'Venta #5','2026-02-24 00:24:05'),(12,2,'salida',1,88,87,'venta',5,2,'Venta #5','2026-02-24 00:24:05'),(13,1,'salida',1,125,124,'venta',6,2,'Venta #6','2026-02-24 00:25:42'),(14,1,'salida',1,124,123,'venta',7,5,'Venta #7','2026-02-24 00:42:51'),(15,2,'salida',1,87,86,'venta',7,5,'Venta #7','2026-02-24 00:42:51'),(16,1,'salida',1,123,122,'venta',8,5,'Venta #8','2026-02-24 00:50:03'),(17,2,'salida',1,86,85,'venta',8,5,'Venta #8','2026-02-24 00:50:03'),(18,1,'salida',1,122,121,'venta',9,4,'Venta #9','2026-02-24 00:59:36'),(19,2,'salida',1,85,84,'venta',9,4,'Venta #9','2026-02-24 00:59:36'),(20,1,'salida',1,121,120,'venta',10,4,'Venta #10','2026-02-24 03:51:23'),(21,2,'salida',1,84,83,'venta',10,4,'Venta #10','2026-02-24 03:51:23'),(22,1,'salida',1,120,119,'venta',11,4,'Venta #11','2026-02-24 05:29:53'),(23,2,'salida',1,83,82,'venta',11,4,'Venta #11','2026-02-24 05:29:53'),(24,1,'salida',1,119,118,'venta',12,4,'Venta #12','2026-02-26 01:11:02'),(25,2,'salida',1,82,81,'venta',12,4,'Venta #12','2026-02-26 01:11:02'),(26,1,'salida',1,118,117,'venta',13,4,'Venta #13','2026-02-26 01:18:21'),(27,1,'salida',4,117,113,'venta',14,4,'Venta #14','2026-02-26 01:19:24'),(28,2,'salida',5,81,76,'venta',15,4,'Venta #15','2026-02-26 01:25:33'),(29,2,'salida',16,76,60,'venta',16,4,'Venta #16','2026-02-26 02:36:37'),(30,1,'salida',1,113,112,'venta',17,4,'Venta #17','2026-02-26 03:46:07'),(31,1,'salida',-1,112,111,'merma',0,2,'00','2026-02-27 02:15:09'),(32,2,'ajuste',1,60,61,'ajuste_manual',NULL,2,'Ajuste por conteo físico.','2026-02-27 02:26:19'),(33,1,'entrada',9,111,120,'manual',NULL,2,'n/a','2026-02-27 02:39:27'),(34,1,'entrada',1,120,121,'manual',NULL,2,'','2026-02-27 02:40:45'),(35,2,'ajuste',1,61,62,'ajuste_manual',NULL,2,'Ajuste por conteo físico.','2026-02-27 02:45:33'),(36,1,'entrada',1,121,122,'compra',5,2,'Compra #COMP-005','2026-03-09 00:06:09'),(37,3,'entrada',150,20,170,'compra',6,2,'Compra #COMP-006','2026-03-10 01:27:10'),(38,2,'entrada',3,62,65,'compra',6,2,'Compra #COMP-006','2026-03-10 01:27:11'),(39,1,'entrada',6,122,128,'compra',7,2,'Compra #COMP-007','2026-03-10 03:25:49'),(40,3,'entrada',6,170,176,'compra',7,2,'Compra #COMP-007','2026-03-10 03:25:49'),(41,2,'entrada',3,65,68,'compra',7,2,'Compra #COMP-007','2026-03-10 03:25:49'),(42,3,'entrada',100,176,276,'compra',8,2,'Compra #COMP-008 - 100 unidades','2026-03-20 02:05:17'),(43,2,'entrada',2,68,70,'compra',9,2,'Compra #COMP-009 - 2 unidades','2026-03-21 01:34:16'),(44,3,'entrada',250,276,526,'manual',NULL,2,'registro actual','2026-03-22 02:41:55'),(45,2,'entrada',10,70,80,'manual',NULL,2,'yes yes','2026-03-22 02:42:49'),(46,2,'ajuste',1,80,81,'ajuste_manual',NULL,2,'Ajuste por conteo físico.','2026-03-22 02:58:36'),(47,4,'salida',2,150,148,'venta',21,2,'Venta #21','2026-03-22 08:58:07'),(48,1,'salida',1,128,127,'venta',21,2,'Venta #21','2026-03-22 08:58:07'),(49,2,'salida',1,81,80,'venta',21,2,'Venta #21','2026-03-22 08:58:07');
/*!40000 ALTER TABLE `movimientos_inventario` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (1,'895412364MM2','DOLO NERVISE AMP SELECTPHARMA','primera prueba',1,'Tylenol, Tempra','Tabletas de 500mg','simple',1,20.00,30.00,26.00,127,20,'12387ML','2026-07-29',1,'2026-02-10 00:40:30'),(2,'7841256369CD','VITAMINAS C','yes mamey',5,'nitrogeno','27','simple',8,125.00,30.00,7.00,80,25,'123887423VC','2027-02-17',1,'2026-02-10 05:52:18'),(3,'896631478ERS','NOLVAGINA',NULL,1,'mmm','100 mg','simple',2,0.03,30.00,0.04,526,15,'1238700ML','2026-03-02',1,'2026-03-01 22:06:28'),(4,'8965223AS','LORATADINA',NULL,3,'prueba','100 mg','simple',2,1.00,1.00,5.00,148,100,'123887423VCAA','2026-10-30',1,'2026-03-22 08:57:21');
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `contacto` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `direccion` text,
  `ciudad` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
INSERT INTO `proveedores` VALUES (1,'AMP SELECTPHARMA','Henry Alvarado','amp@selec.com','Ticuantepe, carretera san benito','Managua','78963251','2026-02-10 05:36:50',1),(2,'DIDELSA','Lorena Martinez','didelsa@gmail.com','frente a galerias santo domingo','Managua','25639874','2026-02-10 05:53:36',1);
/*!40000 ALTER TABLE `proveedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servicios`
--

DROP TABLE IF EXISTS `servicios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servicios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `precio` decimal(10,2) NOT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `tipo_servicio_id` int NOT NULL,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `tipo_servicio_id` (`tipo_servicio_id`),
  CONSTRAINT `servicios_ibfk_1` FOREIGN KEY (`tipo_servicio_id`) REFERENCES `tipos_servicio` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servicios`
--

LOCK TABLES `servicios` WRITE;
/*!40000 ALTER TABLE `servicios` DISABLE KEYS */;
INSERT INTO `servicios` VALUES (1,'Consultas','Consulta Médica con el doctor de turno',500.00,1,1,'2026-02-19 05:55:48'),(2,'Curacion de Heridas','Curacion',30.00,1,2,'2026-02-21 03:03:22');
/*!40000 ALTER TABLE `servicios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipos_servicio`
--

DROP TABLE IF EXISTS `tipos_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipos_servicio` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `descripcion` text,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipos_servicio`
--

LOCK TABLES `tipos_servicio` WRITE;
/*!40000 ALTER TABLE `tipos_servicio` DISABLE KEYS */;
INSERT INTO `tipos_servicio` VALUES (1,'Consulta Medica','Consulta médica con el doctor de turno',1),(2,'Curacion','Curacion de cualquier tipo',1);
/*!40000 ALTER TABLE `tipos_servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unidades_medida`
--

DROP TABLE IF EXISTS `unidades_medida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `unidades_medida` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `abreviatura` varchar(10) NOT NULL,
  `descripcion` text,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`),
  UNIQUE KEY `abreviatura` (`abreviatura`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unidades_medida`
--

LOCK TABLES `unidades_medida` WRITE;
/*!40000 ALTER TABLE `unidades_medida` DISABLE KEYS */;
INSERT INTO `unidades_medida` VALUES (1,'Unidad','u','Una unidad','2026-02-10 00:13:46',1),(2,'Pastilla','past','Una pastilla','2026-02-10 00:13:46',1),(3,'Blister','blis','Blister de pastillas','2026-02-10 00:13:46',1),(4,'Caja','cja','Caja de producto','2026-02-10 00:13:46',1),(5,'Mililitro','ml','Mililitro','2026-02-10 00:13:46',1),(6,'Litro','l','Litro','2026-02-10 00:13:46',1),(7,'Ampolla','amp','Ampolla','2026-02-10 00:13:46',1),(8,'Sobre','sob','Sobre de polvo','2026-02-10 00:13:46',1);
/*!40000 ALTER TABLE `unidades_medida` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `rol` enum('admin','vendedor') NOT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `email_unique` (`email`),
  KEY `idx_usuario_rol` (`rol`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'Fared Delgado','fared@servifarma.com','admin123','vendedor',1,'2026-02-05 06:00:00'),(2,'Administrador del Sistema','admin@farmacia.com','scrypt:32768:8:1$kterdwwJCpfm2yq5$75a5005d1bdcc0bd3a356b1fb3573dd38648cb48c425113306e976fe8b8fe12a9998b4c7eca7bfcc5aab9db8a0c87c39d61d764dd6c7a22f217a3182ac6ee437','admin',1,'2026-02-06 01:41:46'),(3,'Yuri','vendedor@gmail.com','scrypt:32768:8:1$UrSSCWhkdXz5hnx0$4c13cbcd580a87be2aa8fddd50a391f7cc9bcc6d0b2eab2f2fe8db490f7734d114d0ad21046abae4724116204e1199b98d3797bf1e57aba47d550ebade4021d6','vendedor',1,'2026-02-12 05:39:22'),(4,'Sofia','sofia@servifarma.com','scrypt:32768:8:1$8EqE2ByPMY2vKogk$ec16d760232353b0b39929cd5c7c6407b31a809bb68e20973a3d25c231b05f78ec71ac108b70ef0aa05581dbd1e36cfd930ccf52add342acc91a2f44e13724d2','vendedor',1,'2026-02-13 00:40:49'),(5,'Jahir','jahir@servifarma.com','scrypt:32768:8:1$iIIl9tmkC83qcCIs$174230b96f35d244394060c0b41eb26ca33664b6dd4f67b3afd6a96d164d29df0ec82506d29b9d42394d087204dc1198f7f89cc57ae101c79530cb13904c209d','admin',1,'2026-02-13 00:41:20'),(6,'Tereza','tereza@servifarma.com','scrypt:32768:8:1$xaToLFrpl1qizXV6$ae6f7b69397459c1e2a3318b78322ee7bca4358190183b72aae01053c6deb888827fd3ebaf7761ba0db63695a6a7228548e2a479c5a1f7257e8a91343c2d6cc9','admin',1,'2026-03-02 01:40:41'),(7,'Elias Barrios','elias@servifarma.com','scrypt:32768:8:1$3c7rIVbWswQ785LC$3c91a7b0d099720975b563cbe5b26ce8cfc04eaa4177baa49e60df36317396098347ff5c3d39349be4c11e4fa93fb9838aa46847ab313c7b193f7181b2b8ee5f','admin',1,'2026-03-12 01:15:03');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `variaciones_producto`
--

DROP TABLE IF EXISTS `variaciones_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `variaciones_producto` (
  `id` int NOT NULL AUTO_INCREMENT,
  `producto_id` int NOT NULL,
  `presentacion_padre_id` int DEFAULT NULL,
  `nivel` int DEFAULT '1',
  `unidad_id` int NOT NULL,
  `cantidad_equivalente` int NOT NULL,
  `precio_costo_equivalente` decimal(10,2) DEFAULT NULL,
  `porcentaje_ganancia` decimal(5,2) DEFAULT NULL,
  `cantidad_por_padre` int DEFAULT NULL,
  `precio_venta` decimal(10,2) DEFAULT NULL,
  `descripcion` varchar(100) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `producto_unidad` (`producto_id`,`unidad_id`),
  KEY `unidad_id` (`unidad_id`),
  KEY `presentacion_padre_id` (`presentacion_padre_id`),
  CONSTRAINT `variaciones_producto_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `variaciones_producto_ibfk_2` FOREIGN KEY (`unidad_id`) REFERENCES `unidades_medida` (`id`),
  CONSTRAINT `variaciones_producto_ibfk_3` FOREIGN KEY (`presentacion_padre_id`) REFERENCES `variaciones_producto` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `variaciones_producto`
--

LOCK TABLES `variaciones_producto` WRITE;
/*!40000 ALTER TABLE `variaciones_producto` DISABLE KEYS */;
INSERT INTO `variaciones_producto` VALUES (1,3,NULL,1,2,1,NULL,NULL,NULL,6.00,'Venta por unidad base',1),(2,2,NULL,1,4,1,NULL,NULL,NULL,NULL,NULL,1),(3,4,NULL,4,2,1,1.00,1.00,NULL,5.00,'Venta por unidad base',1);
/*!40000 ALTER TABLE `variaciones_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `fecha_venta` date NOT NULL,
  `total_venta` decimal(15,2) NOT NULL,
  `efectivo` decimal(15,2) DEFAULT '0.00',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `cambio` decimal(15,2) DEFAULT '0.00',
  PRIMARY KEY (`id`),
  KEY `idx_venta_usuario` (`usuario_id`),
  KEY `idx_venta_fecha` (`fecha_venta`),
  CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
INSERT INTO `ventas` VALUES (1,2,'2026-02-18',5.50,10.00,'2026-02-19 01:03:30',4.50),(2,2,'2026-02-20',505.50,510.00,'2026-02-21 02:27:31',4.50),(3,2,'2026-02-20',512.50,513.00,'2026-02-21 02:38:37',0.50),(4,2,'2026-02-20',542.50,550.00,'2026-02-21 03:10:30',7.50),(5,2,'2026-02-23',12.50,20.00,'2026-02-24 00:24:05',7.50),(6,2,'2026-02-23',35.50,40.00,'2026-02-24 00:25:42',4.50),(7,5,'2026-02-23',512.50,520.00,'2026-02-24 00:42:50',7.50),(8,5,'2026-02-23',512.50,520.00,'2026-02-24 00:50:03',7.50),(9,4,'2026-02-23',542.50,550.00,'2026-02-24 00:59:36',7.50),(10,4,'2026-02-23',542.50,550.00,'2026-02-24 03:51:23',7.50),(11,4,'2026-02-23',4192.50,5000.00,'2026-02-24 05:29:53',807.50),(12,4,'2026-02-25',12.50,30.00,'2026-02-26 01:11:02',17.50),(13,4,'2026-02-25',5.50,6.00,'2026-02-26 01:18:21',0.50),(14,4,'2026-02-25',552.00,600.00,'2026-02-26 01:19:24',48.00),(15,4,'2026-02-25',35.00,40.00,'2026-02-26 01:25:32',5.00),(16,4,'2026-02-25',112.00,120.00,'2026-02-26 02:36:37',8.00),(17,4,'2026-02-25',715.50,800.00,'2026-02-26 03:46:07',84.50),(18,2,'2026-03-01',500.00,600.00,'2026-03-02 01:26:44',100.00),(19,6,'2026-03-01',530.00,600.00,'2026-03-02 01:42:32',70.00),(20,2,'2026-03-19',500.00,500.00,'2026-03-20 02:03:19',0.00),(21,2,'2026-03-22',43.00,50.00,'2026-03-22 08:58:07',7.00);
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'servifarma'
--

--
-- Dumping routines for database 'servifarma'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-22  7:56:48
