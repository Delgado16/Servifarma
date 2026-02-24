-- Database: farmacia_db
CREATE DATABASE IF NOT EXISTS farmacia_db;
USE farmacia_db;

-- Tabla de usuarios (Admin y Vendedor)
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'vendedor') NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY email_unique (email)
);
INSERT INTO usuarios (nombre, email, contrasena, rol, activo) VALUES
('Administrador del Sistema', 'admin@farmacia.com', 'f3253b0ede0d1d56eccc7c7c0c6e67d3a3f2d0b7e8c5a1f9d2a0e8c3b7f4d6', 'admin', TRUE);
insert into usuarios values (1, 'Fared Delgado','fared@servifarma.com','admin123','admin',TRUE,'2026-02-05');


-- Tabla de proveedores
CREATE TABLE proveedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    ciudad VARCHAR(100),
    telefono VARCHAR(20),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla de unidades de medida
CREATE TABLE unidades_medida (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    abreviatura VARCHAR(10) NOT NULL UNIQUE,
    descripcion TEXT
);

-- Tabla de categorías de productos
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de productos (medicamentos)
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    categoria_id INT NOT NULL,
    principio_activo VARCHAR(150),
    presentacion VARCHAR(100),
    unidad_base_id INT NOT NULL,
    precio_costo DECIMAL(10, 2) NOT NULL,
    precio_venta DECIMAL(10, 2) NOT NULL,
    stock_actual INT DEFAULT 0,
    stock_minimo INT DEFAULT 5,
    lote VARCHAR(50),
    fecha_vencimiento DATE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id),
    FOREIGN KEY (unidad_base_id) REFERENCES unidades_medida(id)
);

-- Tabla de variaciones de unidad para un producto
-- (permite vender pastillas sueltas, blister o caja)
CREATE TABLE variaciones_producto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    unidad_id INT NOT NULL,
    cantidad_equivalente INT NOT NULL,
    precio_venta DECIMAL(10, 2),
    descripcion VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
    FOREIGN KEY (unidad_id) REFERENCES unidades_medida(id),
    UNIQUE KEY producto_unidad (producto_id, unidad_id)
);

-- Tabla de compras (Entradas de inventario)
CREATE TABLE compras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_documento VARCHAR(50) UNIQUE,
    proveedor_id INT NOT NULL,
    usuario_id INT NOT NULL,
    fecha_compra DATE NOT NULL,
    numero_factura VARCHAR(50),
    total_costo DECIMAL(15, 2) NOT NULL,
    estado ENUM('pendiente', 'completada', 'cancelada') DEFAULT 'pendiente',
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla de detalles de compra
CREATE TABLE detalles_compra (
    id INT AUTO_INCREMENT PRIMARY KEY,
    compra_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    unidad_id INT NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(15, 2) NOT NULL,
    FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (unidad_id) REFERENCES unidades_medida(id)
);

-- Tabla de combos
CREATE TABLE combos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    precio_combo DECIMAL(10, 2) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de detalles de combos
CREATE TABLE detalles_combo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    combo_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    unidad_id INT NOT NULL,
    FOREIGN KEY (combo_id) REFERENCES combos(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (unidad_id) REFERENCES unidades_medida(id)
);

CREATE TABLE tipos_servicio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT NULL,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla de servicios (inyecciones, canalizaciones, consultas)
CREATE TABLE servicios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    precio DECIMAL(10, 2) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    tipo_servicio_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tipo_servicio_id) REFERENCES tipos_servicio(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

drop table servicios;

-- Tabla de ventas
CREATE TABLE ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    fecha_venta DATE NOT NULL,
    total_venta DECIMAL(15, 2) NOT NULL,
    efectivo DECIMAL(15, 2) DEFAULT 0,
    cambio DECIMAL(15, 2) DEFAULT 0,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);



-- Tabla de detalles de ventas
CREATE TABLE detalles_venta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    tipo_detalle ENUM('producto', 'servicio', 'combo') NOT NULL,
    referencia_id INT,
    cantidad INT DEFAULT 1,
    unidad_id INT,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(15, 2) NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
    FOREIGN KEY (unidad_id) REFERENCES unidades_medida(id)
);

-- Tabla de movimientos de inventario
CREATE TABLE movimientos_inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    tipo_movimiento ENUM('entrada', 'salida', 'ajuste') NOT NULL,
    cantidad INT NOT NULL,
    cantidad_anterior INT NOT NULL,
    cantidad_nueva INT NOT NULL,
    referencia_tipo VARCHAR(50),
    referencia_id INT,
    usuario_id INT NOT NULL,
    observaciones TEXT,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Índices para mejorar consultas
CREATE INDEX idx_usuario_rol ON usuarios(rol);
CREATE INDEX idx_producto_categoria ON productos(categoria_id);
CREATE INDEX idx_producto_codigo ON productos(codigo);
CREATE INDEX idx_venta_usuario ON ventas(usuario_id);
CREATE INDEX idx_venta_fecha ON ventas(fecha_venta);
CREATE INDEX idx_compra_proveedor ON compras(proveedor_id);
CREATE INDEX idx_compra_fecha ON compras(fecha_compra);
CREATE INDEX idx_movimiento_producto ON movimientos_inventario(producto_id);
CREATE INDEX idx_movimiento_fecha ON movimientos_inventario(fecha_movimiento);

-- Insertar unidades de medida base
INSERT INTO unidades_medida (nombre, abreviatura, descripcion) VALUES
('Unidad', 'u', 'Una unidad'),
('Pastilla', 'past', 'Una pastilla'),
('Blister', 'blis', 'Blister de pastillas'),
('Caja', 'cja', 'Caja de producto'),
('Mililitro', 'ml', 'Mililitro'),
('Litro', 'l', 'Litro'),
('Ampolla', 'amp', 'Ampolla'),
('Sobre', 'sob', 'Sobre de polvo');

-- Insertar categorías
INSERT INTO categorias (nombre, descripcion) VALUES
('Analgésicos', 'Medicamentos para el dolor'),
('Antibióticos', 'Medicamentos para infecciones'),
('Antiinflamatorios', 'Medicamentos antiinflamatorios'),
('Antitérmicos', 'Medicamentos para la fiebre'),
('Vitaminas', 'Suplementos vitamínicos'),
('Suero Fisiológico', 'Soluciones de suero'),
('Desinfectantes', 'Productos desinfectantes');

-- Insertar servicios
INSERT INTO servicios (nombre, descripcion, precio, tipo, activo) VALUES
('Inyección Intramuscular', 'Aplicación de inyección intramuscular', 5.00, 'inyeccion', TRUE),
('Inyección Intravenosa', 'Aplicación de inyección intravenosa', 10.00, 'inyeccion', TRUE),
('Canalización', 'Instalación de catéter intravenoso', 15.00, 'canalizacion', TRUE),
('Consulta Médica', 'Consulta con profesional de salud', 25.00, 'consulta', TRUE),
('Consulta + Inyección', 'Paquete consulta e inyección', 30.00, 'consulta', TRUE);

ALTER TABLE ventas ADD COLUMN cambio DECIMAL(15, 2) DEFAULT 0;