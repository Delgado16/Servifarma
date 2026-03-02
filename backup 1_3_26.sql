CREATE DATABASE  IF NOT EXISTS `avicola_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `avicola_db`;
-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: avicola_db
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
-- Table structure for table `bitacora`
--

DROP TABLE IF EXISTS `bitacora`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bitacora` (
  `id_bitacora` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `accion` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tabla_afectada` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `id_registro` int DEFAULT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_accion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_bitacora`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `bitacora_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bitacora`
--

LOCK TABLES `bitacora` WRITE;
/*!40000 ALTER TABLE `bitacora` DISABLE KEYS */;
INSERT INTO `bitacora` VALUES (1,1,'LOGIN',NULL,NULL,'Inicio de sesión exitoso',NULL,'2025-10-21 14:56:53'),(2,1,'LOGIN',NULL,NULL,'Inicio de sesión exitoso',NULL,'2025-10-21 15:25:31'),(3,1,'LOGIN',NULL,NULL,'Inicio de sesión exitoso',NULL,'2025-10-21 15:39:06'),(4,1,'LOGOUT',NULL,NULL,'Cierre de sesión',NULL,'2025-10-21 16:11:55'),(5,1,'LOGIN',NULL,NULL,'Inicio de sesión exitoso',NULL,'2025-10-21 16:12:22'),(6,1,'LOGOUT',NULL,NULL,'Cierre de sesión',NULL,'2025-10-21 17:30:24'),(7,1,'LOGIN',NULL,NULL,'Inicio de sesión exitoso',NULL,'2025-10-21 17:30:34'),(8,1,'LOGOUT',NULL,NULL,'Cierre de sesión',NULL,'2025-10-22 00:48:58'),(9,1,'LOGIN',NULL,NULL,'Inicio de sesión exitoso',NULL,'2025-10-22 00:49:06');
/*!40000 ALTER TABLE `bitacora` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bodegas`
--

DROP TABLE IF EXISTS `bodegas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bodegas` (
  `id_bodega` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ubicacion` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `capacidad_maxima` decimal(12,2) DEFAULT NULL,
  `id_encargado` int DEFAULT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_bodega`),
  KEY `id_encargado` (`id_encargado`),
  CONSTRAINT `bodegas_ibfk_1` FOREIGN KEY (`id_encargado`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bodegas`
--

LOCK TABLES `bodegas` WRITE;
/*!40000 ALTER TABLE `bodegas` DISABLE KEYS */;
/*!40000 ALTER TABLE `bodegas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalogo_movimientos`
--

DROP TABLE IF EXISTS `catalogo_movimientos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `catalogo_movimientos` (
  `id_tipo_movimiento` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tipo_operacion` enum('Entrada','Salida','Ajuste') COLLATE utf8mb4_unicode_ci NOT NULL,
  `categoria` enum('Produccion','Venta','Compra','Ajuste','Transferencia','Consumo','Merma') COLLATE utf8mb4_unicode_ci NOT NULL,
  `afecta_costo` tinyint(1) DEFAULT '0',
  `requiere_aproboacion` tinyint(1) DEFAULT '0',
  `activo` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_tipo_movimiento`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalogo_movimientos`
--

LOCK TABLES `catalogo_movimientos` WRITE;
/*!40000 ALTER TABLE `catalogo_movimientos` DISABLE KEYS */;
/*!40000 ALTER TABLE `catalogo_movimientos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
  `id_cliente` int NOT NULL AUTO_INCREMENT,
  `tipo_cliente` enum('Persona','Empresa') COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `identificacion` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telefono` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `direccion` text COLLATE utf8mb4_unicode_ci,
  `ciudad` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `limite_credito` decimal(12,2) DEFAULT '0.00',
  `activo` tinyint(1) DEFAULT '1',
  `fecha_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `identificacion` (`identificacion`),
  KEY `idx_clientes_identificacion` (`identificacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cuentas_por_cobrar`
--

DROP TABLE IF EXISTS `cuentas_por_cobrar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cuentas_por_cobrar` (
  `id_cuenta_cobrar` int NOT NULL AUTO_INCREMENT,
  `id_factura` int NOT NULL,
  `id_cliente` int NOT NULL,
  `monto_total` decimal(12,2) NOT NULL,
  `monto_pagado` decimal(12,2) DEFAULT '0.00',
  `saldo_pendiente` decimal(12,2) NOT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  `estado` enum('Pendiente','Pagada','Vencida') COLLATE utf8mb4_unicode_ci DEFAULT 'Pendiente',
  PRIMARY KEY (`id_cuenta_cobrar`),
  KEY `id_factura` (`id_factura`),
  KEY `id_cliente` (`id_cliente`),
  CONSTRAINT `cuentas_por_cobrar_ibfk_1` FOREIGN KEY (`id_factura`) REFERENCES `facturacion` (`id_factura`),
  CONSTRAINT `cuentas_por_cobrar_ibfk_2` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cuentas_por_cobrar`
--

LOCK TABLES `cuentas_por_cobrar` WRITE;
/*!40000 ALTER TABLE `cuentas_por_cobrar` DISABLE KEYS */;
/*!40000 ALTER TABLE `cuentas_por_cobrar` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cuentas_por_pagar`
--

DROP TABLE IF EXISTS `cuentas_por_pagar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cuentas_por_pagar` (
  `id_cuenta_pagar` int NOT NULL AUTO_INCREMENT,
  `id_gasto` int NOT NULL,
  `id_proveedor` int NOT NULL,
  `monto_total` decimal(12,2) NOT NULL,
  `monto_pagado` decimal(12,2) DEFAULT '0.00',
  `saldo_pendiente` decimal(12,2) NOT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  `estado` enum('Pendiente','Pagada','Vencida') COLLATE utf8mb4_unicode_ci DEFAULT 'Pendiente',
  PRIMARY KEY (`id_cuenta_pagar`),
  KEY `id_gasto` (`id_gasto`),
  KEY `id_proveedor` (`id_proveedor`),
  CONSTRAINT `cuentas_por_pagar_ibfk_1` FOREIGN KEY (`id_gasto`) REFERENCES `gastos` (`id_gasto`),
  CONSTRAINT `cuentas_por_pagar_ibfk_2` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cuentas_por_pagar`
--

LOCK TABLES `cuentas_por_pagar` WRITE;
/*!40000 ALTER TABLE `cuentas_por_pagar` DISABLE KEYS */;
/*!40000 ALTER TABLE `cuentas_por_pagar` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalle_facturacion`
--

DROP TABLE IF EXISTS `detalle_facturacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_facturacion` (
  `id_detalle` int NOT NULL AUTO_INCREMENT,
  `id_factura` int NOT NULL,
  `id_producto` int NOT NULL,
  `cantidad` decimal(12,2) NOT NULL,
  `precio_unitario` decimal(12,2) NOT NULL,
  `subtotal` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `id_factura` (`id_factura`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `detalle_facturacion_ibfk_1` FOREIGN KEY (`id_factura`) REFERENCES `facturacion` (`id_factura`) ON DELETE CASCADE,
  CONSTRAINT `detalle_facturacion_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_facturacion`
--

LOCK TABLES `detalle_facturacion` WRITE;
/*!40000 ALTER TABLE `detalle_facturacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `detalle_facturacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalle_movimiento_inventario`
--

DROP TABLE IF EXISTS `detalle_movimiento_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_movimiento_inventario` (
  `id_detalle` int NOT NULL AUTO_INCREMENT,
  `id_movimiento` int NOT NULL,
  `id_producto` int NOT NULL,
  `cantidad` decimal(12,2) NOT NULL,
  `costo_unitario` decimal(12,2) DEFAULT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `id_movimiento` (`id_movimiento`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `detalle_movimiento_inventario_ibfk_1` FOREIGN KEY (`id_movimiento`) REFERENCES `movimientos_inventario` (`id_movimiento`) ON DELETE CASCADE,
  CONSTRAINT `detalle_movimiento_inventario_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_movimiento_inventario`
--

LOCK TABLES `detalle_movimiento_inventario` WRITE;
/*!40000 ALTER TABLE `detalle_movimiento_inventario` DISABLE KEYS */;
/*!40000 ALTER TABLE `detalle_movimiento_inventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `facturacion`
--

DROP TABLE IF EXISTS `facturacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `facturacion` (
  `id_factura` int NOT NULL AUTO_INCREMENT,
  `numero_factura` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_cliente` int NOT NULL,
  `fecha_factura` date NOT NULL,
  `subtotal` decimal(12,2) NOT NULL,
  `total` decimal(12,2) NOT NULL,
  `estado` enum('Pendiente','Pagada','Anulada') COLLATE utf8mb4_unicode_ci DEFAULT 'Pendiente',
  `tipo_pago` enum('Contado','Credito') COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_usuario` int NOT NULL,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_factura`),
  UNIQUE KEY `numero_factura` (`numero_factura`),
  KEY `id_usuario` (`id_usuario`),
  KEY `idx_facturacion_fecha` (`fecha_factura`),
  KEY `idx_facturacion_cliente` (`id_cliente`),
  CONSTRAINT `facturacion_ibfk_1` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`),
  CONSTRAINT `facturacion_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facturacion`
--

LOCK TABLES `facturacion` WRITE;
/*!40000 ALTER TABLE `facturacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `facturacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gastos`
--

DROP TABLE IF EXISTS `gastos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gastos` (
  `id_gasto` int NOT NULL AUTO_INCREMENT,
  `tipo_gasto` enum('Compra','Mantenimiento','Reparacion','Servicios','Salarios','Otros') COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `monto` decimal(12,2) NOT NULL,
  `fecha_gasto` date NOT NULL,
  `id_proveedor` int DEFAULT NULL,
  `categoria` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado` enum('Pendiente','Pagado','Anulado') COLLATE utf8mb4_unicode_ci DEFAULT 'Pendiente',
  `id_usuario` int NOT NULL,
  `fecha_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_gasto`),
  KEY `id_proveedor` (`id_proveedor`),
  KEY `id_usuario` (`id_usuario`),
  KEY `idx_gastos_fecha` (`fecha_gasto`),
  CONSTRAINT `gastos_ibfk_1` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`),
  CONSTRAINT `gastos_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gastos`
--

LOCK TABLES `gastos` WRITE;
/*!40000 ALTER TABLE `gastos` DISABLE KEYS */;
/*!40000 ALTER TABLE `gastos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventario_bodega`
--

DROP TABLE IF EXISTS `inventario_bodega`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventario_bodega` (
  `id_inventario` int NOT NULL AUTO_INCREMENT,
  `id_producto` int NOT NULL,
  `id_bodega` int NOT NULL,
  `cantidad_actual` decimal(12,2) DEFAULT '0.00',
  `fecha_actualizacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_inventario`),
  UNIQUE KEY `unique_producto_bodega` (`id_producto`,`id_bodega`),
  KEY `id_bodega` (`id_bodega`),
  CONSTRAINT `inventario_bodega_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`),
  CONSTRAINT `inventario_bodega_ibfk_2` FOREIGN KEY (`id_bodega`) REFERENCES `bodegas` (`id_bodega`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario_bodega`
--

LOCK TABLES `inventario_bodega` WRITE;
/*!40000 ALTER TABLE `inventario_bodega` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventario_bodega` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimientos_inventario`
--

DROP TABLE IF EXISTS `movimientos_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientos_inventario` (
  `id_movimiento` int NOT NULL AUTO_INCREMENT,
  `id_tipo_movimiento` int DEFAULT NULL,
  `tipo_movimiento` enum('Entrada','Salida','Ajuste','Transferencia') COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_bodega_origen` int DEFAULT NULL,
  `id_bodega_destino` int DEFAULT NULL,
  `id_usuario` int NOT NULL,
  `fecha_movimiento` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  `referencia` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id_movimiento`),
  KEY `id_bodega_origen` (`id_bodega_origen`),
  KEY `id_bodega_destino` (`id_bodega_destino`),
  KEY `id_usuario` (`id_usuario`),
  KEY `idx_movimientos_fecha` (`fecha_movimiento`),
  KEY `id_tipo_movimiento` (`id_tipo_movimiento`),
  CONSTRAINT `movimientos_inventario_ibfk_1` FOREIGN KEY (`id_bodega_origen`) REFERENCES `bodegas` (`id_bodega`),
  CONSTRAINT `movimientos_inventario_ibfk_2` FOREIGN KEY (`id_bodega_destino`) REFERENCES `bodegas` (`id_bodega`),
  CONSTRAINT `movimientos_inventario_ibfk_3` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `movimientos_inventario_ibfk_4` FOREIGN KEY (`id_tipo_movimiento`) REFERENCES `catalogo_movimientos` (`id_tipo_movimiento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos_inventario`
--

LOCK TABLES `movimientos_inventario` WRITE;
/*!40000 ALTER TABLE `movimientos_inventario` DISABLE KEYS */;
/*!40000 ALTER TABLE `movimientos_inventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pagos_cuentascobrar`
--

DROP TABLE IF EXISTS `pagos_cuentascobrar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pagos_cuentascobrar` (
  `id_pago` int NOT NULL AUTO_INCREMENT,
  `id_cuenta_cobrar` int NOT NULL,
  `monto_pago` decimal(12,2) NOT NULL,
  `fecha_pago` date NOT NULL,
  `metodo_pago` enum('Efectivo','Transferencia','Cheque','Tarjeta') COLLATE utf8mb4_unicode_ci NOT NULL,
  `referencia` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  `id_usuario` int NOT NULL,
  `fecha_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pago`),
  KEY `id_cuenta_cobrar` (`id_cuenta_cobrar`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `pagos_cuentascobrar_ibfk_1` FOREIGN KEY (`id_cuenta_cobrar`) REFERENCES `cuentas_por_cobrar` (`id_cuenta_cobrar`),
  CONSTRAINT `pagos_cuentascobrar_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pagos_cuentascobrar`
--

LOCK TABLES `pagos_cuentascobrar` WRITE;
/*!40000 ALTER TABLE `pagos_cuentascobrar` DISABLE KEYS */;
/*!40000 ALTER TABLE `pagos_cuentascobrar` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pagos_cuentaspagar`
--

DROP TABLE IF EXISTS `pagos_cuentaspagar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pagos_cuentaspagar` (
  `id_pago` int NOT NULL AUTO_INCREMENT,
  `id_cuenta_pagar` int NOT NULL,
  `monto_pago` decimal(12,2) NOT NULL,
  `fecha_pago` date NOT NULL,
  `metodo_pago` enum('Efectivo','Transferencia','Cheque','Tarjeta') COLLATE utf8mb4_unicode_ci NOT NULL,
  `referencia` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  `id_usuario` int NOT NULL,
  `fecha_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pago`),
  KEY `id_cuenta_pagar` (`id_cuenta_pagar`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `pagos_cuentaspagar_ibfk_1` FOREIGN KEY (`id_cuenta_pagar`) REFERENCES `cuentas_por_pagar` (`id_cuenta_pagar`),
  CONSTRAINT `pagos_cuentaspagar_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pagos_cuentaspagar`
--

LOCK TABLES `pagos_cuentaspagar` WRITE;
/*!40000 ALTER TABLE `pagos_cuentaspagar` DISABLE KEYS */;
/*!40000 ALTER TABLE `pagos_cuentaspagar` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `produccion`
--

DROP TABLE IF EXISTS `produccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `produccion` (
  `id_produccion` int NOT NULL AUTO_INCREMENT,
  `fecha_produccion` date NOT NULL,
  `id_bodega` int NOT NULL,
  `cantidad_huevos` decimal(12,2) NOT NULL,
  `cantidad_aves_activas` int DEFAULT NULL,
  `porcentaje_postura` decimal(5,2) DEFAULT NULL,
  `huevos_rotos` int DEFAULT '0',
  `huevos_sucios` int DEFAULT '0',
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  `id_usuario_registro` int NOT NULL,
  `fecha_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_produccion`),
  KEY `id_bodega` (`id_bodega`),
  KEY `id_usuario_registro` (`id_usuario_registro`),
  KEY `idx_produccion_fecha` (`fecha_produccion`),
  CONSTRAINT `produccion_ibfk_1` FOREIGN KEY (`id_bodega`) REFERENCES `bodegas` (`id_bodega`),
  CONSTRAINT `produccion_ibfk_2` FOREIGN KEY (`id_usuario_registro`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `produccion`
--

LOCK TABLES `produccion` WRITE;
/*!40000 ALTER TABLE `produccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `produccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id_producto` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `categoria` enum('Huevos','Aves','Alimento','Medicamentos','Insumos','Otros') COLLATE utf8mb4_unicode_ci NOT NULL,
  `unidad_medida` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `precio_compra` decimal(12,2) DEFAULT NULL,
  `precio_venta` decimal(12,2) DEFAULT NULL,
  `stock_minimo` decimal(12,2) DEFAULT '0.00',
  `activo` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_producto`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `idx_productos_codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedores` (
  `id_proveedor` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `identificacion` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telefono` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `direccion` text COLLATE utf8mb4_unicode_ci,
  `ciudad` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tipo_proveedor` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `fecha_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_proveedor`),
  UNIQUE KEY `identificacion` (`identificacion`),
  KEY `idx_proveedores_identificacion` (`identificacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
/*!40000 ALTER TABLE `proveedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id_rol` int NOT NULL AUTO_INCREMENT,
  `nombre_rol` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `permisos` json DEFAULT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_rol`),
  UNIQUE KEY `nombre_rol` (`nombre_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Administrador','Acceso completo al sistema','{\"all\": true}',1,'2025-10-20 16:05:34'),(2,'Vendedor','Gestión de ventas y clientes','{\"ventas\": true, \"clientes\": true, \"inventario\": \"read\"}',1,'2025-10-20 16:05:34'),(3,'Encargado_Produccion','Control de producción e inventario','{\"inventario\": true, \"produccion\": true}',1,'2025-10-20 16:05:34'),(4,'Contador','Gestión contable y financiera','{\"cuentas\": true, \"reportes\": true, \"contabilidad\": true}',1,'2025-10-20 16:05:34'),(5,'Bodeguero','Gestión de inventario y bodegas','{\"inventario\": true, \"movimientos\": true}',1,'2025-10-20 16:05:34');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellido` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_rol` int NOT NULL,
  `telefono` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ultima_sesion` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email` (`email`),
  KEY `id_rol` (`id_rol`),
  KEY `idx_usuarios_email` (`email`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `roles` (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'Admin','Sistema','admin@avicola.com','scrypt:32768:8:1$TR3zNH2Afxw8vISP$ea5e513a53266f7d0d969a03d68c4794e97cc80caa6603957bfb892b5ffffae94a81e9bcb3df27083ccbfd73ee5d399046f986b6de9dea11a271a8bb7e62dd19',1,NULL,1,'2025-10-20 16:06:27','2025-10-22 00:49:05');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'avicola_db'
--

--
-- Dumping routines for database 'avicola_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-01 14:54:48
