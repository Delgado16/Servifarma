
CREATE TABLE `categorias` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `combos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `descripcion` text,
  `precio_combo` decimal(10,2) NOT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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

CREATE TABLE `tipos_servicio` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `descripcion` text,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;