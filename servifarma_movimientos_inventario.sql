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
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos_inventario`
--

LOCK TABLES `movimientos_inventario` WRITE;
/*!40000 ALTER TABLE `movimientos_inventario` DISABLE KEYS */;
INSERT INTO `movimientos_inventario` VALUES (1,1,'entrada',20,100,120,'compra',1,2,'Compra #COMP-001','2026-02-12 01:49:13'),(2,2,'entrada',30,50,80,'compra',2,2,'Compra #COMP-002','2026-02-12 02:25:50'),(3,1,'entrada',10,120,130,'compra',3,2,'Compra #COMP-003','2026-02-12 02:26:42'),(4,2,'entrada',10,80,90,'compra',4,2,'Compra #COMP-004','2026-02-12 02:27:17'),(5,1,'salida',1,130,129,'venta',1,2,'Venta #1','2026-02-19 01:03:30'),(6,1,'salida',1,129,128,'venta',2,2,'Venta #2','2026-02-21 02:27:31'),(7,1,'salida',1,128,127,'venta',3,2,'Venta #3','2026-02-21 02:38:37'),(8,2,'salida',1,90,89,'venta',3,2,'Venta #3','2026-02-21 02:38:37'),(9,1,'salida',1,127,126,'venta',4,2,'Venta #4','2026-02-21 03:10:30'),(10,2,'salida',1,89,88,'venta',4,2,'Venta #4','2026-02-21 03:10:30'),(11,1,'salida',1,126,125,'venta',5,2,'Venta #5','2026-02-24 00:24:05'),(12,2,'salida',1,88,87,'venta',5,2,'Venta #5','2026-02-24 00:24:05'),(13,1,'salida',1,125,124,'venta',6,2,'Venta #6','2026-02-24 00:25:42'),(14,1,'salida',1,124,123,'venta',7,5,'Venta #7','2026-02-24 00:42:51'),(15,2,'salida',1,87,86,'venta',7,5,'Venta #7','2026-02-24 00:42:51'),(16,1,'salida',1,123,122,'venta',8,5,'Venta #8','2026-02-24 00:50:03'),(17,2,'salida',1,86,85,'venta',8,5,'Venta #8','2026-02-24 00:50:03'),(18,1,'salida',1,122,121,'venta',9,4,'Venta #9','2026-02-24 00:59:36'),(19,2,'salida',1,85,84,'venta',9,4,'Venta #9','2026-02-24 00:59:36'),(20,1,'salida',1,121,120,'venta',10,4,'Venta #10','2026-02-24 03:51:23'),(21,2,'salida',1,84,83,'venta',10,4,'Venta #10','2026-02-24 03:51:23'),(22,1,'salida',1,120,119,'venta',11,4,'Venta #11','2026-02-24 05:29:53'),(23,2,'salida',1,83,82,'venta',11,4,'Venta #11','2026-02-24 05:29:53'),(24,1,'salida',1,119,118,'venta',12,4,'Venta #12','2026-02-26 01:11:02'),(25,2,'salida',1,82,81,'venta',12,4,'Venta #12','2026-02-26 01:11:02'),(26,1,'salida',1,118,117,'venta',13,4,'Venta #13','2026-02-26 01:18:21'),(27,1,'salida',4,117,113,'venta',14,4,'Venta #14','2026-02-26 01:19:24'),(28,2,'salida',5,81,76,'venta',15,4,'Venta #15','2026-02-26 01:25:33'),(29,2,'salida',16,76,60,'venta',16,4,'Venta #16','2026-02-26 02:36:37'),(30,1,'salida',1,113,112,'venta',17,4,'Venta #17','2026-02-26 03:46:07'),(31,1,'salida',-1,112,111,'merma',0,2,'00','2026-02-27 02:15:09'),(32,2,'ajuste',1,60,61,'ajuste_manual',NULL,2,'Ajuste por conteo físico.','2026-02-27 02:26:19'),(33,1,'entrada',9,111,120,'manual',NULL,2,'n/a','2026-02-27 02:39:27'),(34,1,'entrada',1,120,121,'manual',NULL,2,'','2026-02-27 02:40:45'),(35,2,'ajuste',1,61,62,'ajuste_manual',NULL,2,'Ajuste por conteo físico.','2026-02-27 02:45:33');
/*!40000 ALTER TABLE `movimientos_inventario` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-01 15:49:08
