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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'Fared Delgado','fared@servifarma.com','admin123','vendedor',1,'2026-02-05 06:00:00'),(2,'Administrador del Sistema','admin@farmacia.com','scrypt:32768:8:1$kterdwwJCpfm2yq5$75a5005d1bdcc0bd3a356b1fb3573dd38648cb48c425113306e976fe8b8fe12a9998b4c7eca7bfcc5aab9db8a0c87c39d61d764dd6c7a22f217a3182ac6ee437','admin',1,'2026-02-06 01:41:46'),(3,'Yuri','vendedor@gmail.com','scrypt:32768:8:1$UrSSCWhkdXz5hnx0$4c13cbcd580a87be2aa8fddd50a391f7cc9bcc6d0b2eab2f2fe8db490f7734d114d0ad21046abae4724116204e1199b98d3797bf1e57aba47d550ebade4021d6','vendedor',1,'2026-02-12 05:39:22'),(4,'Sofia','sofia@servifarma.com','scrypt:32768:8:1$8EqE2ByPMY2vKogk$ec16d760232353b0b39929cd5c7c6407b31a809bb68e20973a3d25c231b05f78ec71ac108b70ef0aa05581dbd1e36cfd930ccf52add342acc91a2f44e13724d2','vendedor',1,'2026-02-13 00:40:49'),(5,'Jahir','jahir@servifarma.com','scrypt:32768:8:1$iIIl9tmkC83qcCIs$174230b96f35d244394060c0b41eb26ca33664b6dd4f67b3afd6a96d164d29df0ec82506d29b9d42394d087204dc1198f7f89cc57ae101c79530cb13904c209d','admin',1,'2026-02-13 00:41:20');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
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
