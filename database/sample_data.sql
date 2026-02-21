-- Script para insertar datos de ejemplo en FarmaControl
-- Ejecutar después de schema.sql

USE farmacia_db;

-- Usuarios de prueba
INSERT INTO usuarios (nombre, email, contrasena, rol, activo) VALUES
('Administrador del Sistema', 'admin@farmacia.com', 'f3253b0ede0d1d56eccc7c7c0c6e67d3a3f2d0b7e8c5a1f9d2a0e8c3b7f4d6', 'admin', TRUE),
('Vendedor Principal', 'vendedor@farmacia.com', '3a0e37a2c1d8d4f0c9b2a5e8f1d4c6b3a8e2f5d7c1a4b9e6f0d3c8b1a5e2f', 'vendedor', TRUE),
('Vendedor 2', 'vendedor2@farmacia.com', '3a0e37a2c1d8d4f0c9b2a5e8f1d4c6b3a8e2f5d7c1a4b9e6f0d3c8b1a5e2f', 'vendedor', TRUE);

-- Proveedores
INSERT INTO proveedores (nombre, contacto, email, direccion, ciudad, telefono, activo) VALUES
('Laboratorios Syntex', 'Juan García', 'info@syntex.com', 'Av. La Paz 123', 'Santo Domingo', '809-555-0001', TRUE),
('Distribuciones Farma', 'Maria López', 'ventas@farmadistr.com', 'Calle 1ero de Agosto 456', 'Santiago', '809-555-0002', TRUE),
('Farmacéuticos Unidos', 'Carlos Rodríguez', 'contacto@farmaunidos.com', 'Av. Independencia 789', 'La Romana', '809-555-0003', TRUE),
('Medicamentos del Caribe', 'Ana Martínez', 'pedidos@medcaribe.com', 'Zona Industrial 321', 'Santo Domingo', '809-555-0004', TRUE);

-- Productos - Analgésicos
INSERT INTO productos (codigo, nombre, descripcion, categoria_id, principio_activo, presentacion, unidad_base_id, precio_costo, precio_venta, stock_actual, stock_minimo, activo) VALUES
('PROD-001', 'Paracetamol 500mg', 'Analgésico y antitérmico', 1, 'Paracetamol', 'Pastilla', 2, 2.50, 5.00, 150, 20, TRUE),
('PROD-002', 'Ibuprofeno 200mg', 'Antiinflamatorio y analgésico', 1, 'Ibuprofeno', 'Pastilla', 2, 3.00, 6.50, 100, 20, TRUE),
('PROD-003', 'Aspirina 500mg', 'Analgésico y anticoagulante', 1, 'Ácido acetilsalicílico', 'Pastilla', 2, 1.50, 3.50, 80, 10, TRUE),
('PROD-004', 'Naproxeno 500mg', 'Antiinflamatorio potente', 1, 'Naproxeno', 'Pastilla', 2, 4.00, 8.00, 60, 15, TRUE);

-- Productos - Antibióticos
INSERT INTO productos (codigo, nombre, descripcion, categoria_id, principio_activo, presentacion, unidad_base_id, precio_costo, precio_venta, stock_actual, stock_minimo, activo) VALUES
('PROD-005', 'Amoxicilina 500mg', 'Antibiótico betalactámico', 2, 'Amoxicilina', 'Cápsula', 2, 5.00, 10.00, 120, 20, TRUE),
('PROD-006', 'Azitromicina 500mg', 'Antibiótico macrólido', 2, 'Azitromicina', 'Pastilla', 2, 8.00, 15.00, 75, 15, TRUE),
('PROD-007', 'Ciprofloxacino 500mg', 'Fluoroquinolona', 2, 'Ciprofloxacino', 'Pastilla', 2, 7.50, 14.00, 90, 20, TRUE);

-- Productos - Antiinflamatorios
INSERT INTO productos (codigo, nombre, descripcion, categoria_id, principio_activo, presentacion, unidad_base_id, precio_costo, precio_venta, stock_actual, stock_minimo, activo) VALUES
('PROD-008', 'Diclofenaco 50mg', 'Antiinflamatorio potente', 3, 'Diclofenaco', 'Ampolla', 7, 6.00, 12.00, 100, 20, TRUE),
('PROD-009', 'Meloxicam 15mg', 'Antiinflamatorio selectivo', 3, 'Meloxicam', 'Pastilla', 2, 5.50, 11.00, 85, 15, TRUE);

-- Productos - Antitérmicos
INSERT INTO productos (codigo, nombre, descripcion, categoria_id, principio_activo, presentacion, unidad_base_id, precio_costo, precio_venta, stock_actual, stock_minimo, activo) VALUES
('PROD-010', 'Dipirona 500mg', 'Antitérmico', 4, 'Dipirona', 'Pastilla', 2, 2.00, 4.50, 200, 30, TRUE);

-- Productos - Vitaminas
INSERT INTO productos (codigo, nombre, descripcion, categoria_id, principio_activo, presentacion, unidad_base_id, precio_costo, precio_venta, stock_actual, stock_minimo, activo) VALUES
('PROD-011', 'Vitamina C 1000mg', 'Vitamina C pura', 5, 'Ácido ascórbico', 'Pastilla efervescente', 2, 3.00, 7.00, 150, 20, TRUE),
('PROD-012', 'Complejo B', 'Complejo B12', 5, 'B12', 'Ampolla', 7, 4.50, 9.00, 80, 10, TRUE),
('PROD-013', 'Vitamina D3 1000 IU', 'Vitamina D3', 5, 'Colecalciferol', 'Pastilla', 2, 5.00, 10.00, 100, 15, TRUE);

-- Productos - Suero Fisiológico
INSERT INTO productos (codigo, nombre, descripcion, categoria_id, presentacion, unidad_base_id, precio_costo, precio_venta, stock_actual, stock_minimo, activo) VALUES
('PROD-014', 'Suero Fisiológico 500ml', 'Solución salina', 6, 'Botella de 500ml', 5, 15.00, 25.00, 50, 10, TRUE),
('PROD-015', 'Suero Fisiológico 1L', 'Solución salina', 6, 'Botella de 1L', 5, 25.00, 40.00, 30, 5, TRUE);

-- Variaciones de unidad para algunos productos
INSERT INTO variaciones_producto (producto_id, unidad_id, cantidad_equivalente, precio_venta, descripcion, activo) VALUES
(1, 3, 10, 45.00, 'Blister de 10 pastillas Paracetamol', TRUE),
(1, 4, 100, 400.00, 'Caja de 100 pastillas Paracetamol', TRUE),
(2, 3, 10, 60.00, 'Blister de 10 pastillas Ibuprofeno', TRUE),
(2, 4, 100, 550.00, 'Caja de 100 pastillas Ibuprofeno', TRUE);

-- Combos
INSERT INTO combos (nombre, descripcion, precio_combo, activo) VALUES
('Combo Gripe', 'Paracetamol + Vitamina C + Suero', 45.00, TRUE),
('Combo Dolor', 'Paracetamol + Ibuprofeno + Dipirona', 35.00, TRUE),
('Combo Antibiótico', 'Amoxicilina + Azitromicina', 80.00, TRUE);

-- Detalles de combos
INSERT INTO detalles_combo (combo_id, producto_id, cantidad, unidad_id) VALUES
(1, 1, 1, 2),  -- 1 Paracetamol pastilla
(1, 11, 1, 2), -- 1 Vitamina C pastilla
(1, 14, 1, 5), -- 1 Suero 500ml
(2, 1, 1, 2),  -- 1 Paracetamol
(2, 2, 1, 2),  -- 1 Ibuprofeno
(2, 10, 1, 2), -- 1 Dipirona
(3, 5, 1, 2),  -- 1 Amoxicilina
(3, 6, 1, 2);  -- 1 Azitromicina

-- Compras (Entradas de inventario)
INSERT INTO compras (numero_documento, proveedor_id, usuario_id, fecha_compra, numero_factura, total_costo, estado, observaciones) VALUES
('DOC-001', 1, 1, '2024-01-15', 'FACT-2024-001', 1500.00, 'completada', 'Primera compra'),
('DOC-002', 2, 1, '2024-01-20', 'FACT-2024-002', 2000.00, 'completada', 'Reabastecimiento'),
('DOC-003', 3, 1, '2024-01-25', 'FACT-2024-003', 1800.00, 'completada', 'Compra regular');

-- Detalles de compras
INSERT INTO detalles_compra (compra_id, producto_id, cantidad, unidad_id, precio_unitario, subtotal) VALUES
(1, 1, 100, 2, 2.50, 250.00),
(1, 2, 80, 2, 3.00, 240.00),
(1, 5, 60, 2, 5.00, 300.00),
(1, 11, 150, 2, 3.00, 450.00),
(1, 14, 40, 5, 15.00, 600.00),

(2, 3, 50, 2, 1.50, 75.00),
(2, 6, 75, 2, 8.00, 600.00),
(2, 8, 100, 7, 6.00, 600.00),
(2, 12, 60, 7, 4.50, 270.00),
(2, 13, 100, 2, 5.00, 500.00),

(3, 4, 50, 2, 4.00, 200.00),
(3, 7, 70, 2, 7.50, 525.00),
(3, 9, 60, 2, 5.50, 330.00),
(3, 15, 25, 5, 25.00, 625.00);

-- Actualizar stocks según compras (ya debe estar hecho por los triggers)
-- Los productos ya tienen stock_actual poblado desde el INSERT de productos

echo "Datos de ejemplo insertados exitosamente";
