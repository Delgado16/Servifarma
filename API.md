# 📡 Documentación de API - FarmaControl

## BaseURL
```
http://localhost:5000
```

## Autenticación

Todas las rutas protegidas requieren una sesión activa.

### Login
```http
POST /login HTTP/1.1
Content-Type: application/x-www-form-urlencoded

email=admin@farmacia.com&contrasena=admin123
```

**Response (200)**
```json
{
  "redirect": "admin/dashboard"
}
```

### Logout
```http
GET /logout HTTP/1.1
```

---

## 📦 Productos

### Listar Productos
```http
GET /api/productos?buscar=paracetamol&categoria=1 HTTP/1.1
```

**Response**
```json
[
  {
    "id": 1,
    "codigo": "PROD-001",
    "nombre": "Paracetamol 500mg",
    "categoria_id": 1,
    "categoria_nombre": "Analgésicos",
    "precio_costo": 2.50,
    "precio_venta": 5.00,
    "stock_actual": 150,
    "stock_minimo": 20,
    "unidad_nombre": "Pastilla"
  }
]
```

### Crear Producto
```http
POST /api/productos HTTP/1.1
Content-Type: application/json

{
  "codigo": "PROD-100",
  "nombre": "Nuevo Medicamento",
  "categoria_id": 1,
  "principio_activo": "Sustancia activa",
  "presentacion": "Pastilla",
  "unidad_base_id": 2,
  "precio_costo": 3.50,
  "precio_venta": 7.00,
  "stock_minimo": 10,
  "descripcion": "Descripción del producto"
}
```

**Response (200)**
```json
{
  "success": true,
  "message": "Producto creado exitosamente"
}
```

### Obtener Producto
```http
GET /api/productos/1 HTTP/1.1
```

**Response**
```json
{
  "id": 1,
  "codigo": "PROD-001",
  "nombre": "Paracetamol 500mg",
  "precio_costo": 2.50,
  "precio_venta": 5.00,
  "stock_actual": 150,
  "variaciones": [
    {
      "id": 1,
      "unidad_nombre": "Blister",
      "cantidad_equivalente": 10,
      "precio_venta": 45.00
    }
  ]
}
```

### Actualizar Producto
```http
PUT /api/productos/1 HTTP/1.1
Content-Type: application/json

{
  "nombre": "Paracetamol 500mg - Nueva Versión",
  "precio_costo": 2.75,
  "precio_venta": 5.50,
  "stock_minimo": 25
}
```

### Eliminar Producto
```http
DELETE /api/productos/1 HTTP/1.1
```

---

## 🏢 Proveedores

### Listar Proveedores
```http
GET /api/proveedores HTTP/1.1
```

**Response**
```json
[
  {
    "id": 1,
    "nombre": "Laboratorios Syntex",
    "contacto": "Juan García",
    "email": "info@syntex.com",
    "telefono": "809-555-0001",
    "ciudad": "Santo Domingo",
    "direccion": "Av. La Paz 123"
  }
]
```

### Crear Proveedor
```http
POST /api/proveedores HTTP/1.1
Content-Type: application/json

{
  "nombre": "Nuevo Distribuidor",
  "contacto": "Persona Contacto",
  "email": "distribuidor@empresa.com",
  "telefono": "809-555-9999",
  "ciudad": "Santo Domingo",
  "direccion": "Calle Principal 100"
}
```

---

## 📋 Compras

### Listar Compras
```http
GET /api/compras HTTP/1.1
```

**Response**
```json
[
  {
    "id": 1,
    "numero_documento": "DOC-001",
    "proveedor_nombre": "Laboratorios Syntex",
    "usuario_nombre": "Administrador",
    "fecha_compra": "2024-01-15",
    "numero_factura": "FACT-2024-001",
    "total_costo": 1500.00,
    "estado": "completada"
  }
]
```

### Registrar Compra
```http
POST /api/compras HTTP/1.1
Content-Type: application/json

{
  "numero_documento": "DOC-100",
  "proveedor_id": 1,
  "fecha_compra": "2024-02-01",
  "numero_factura": "FACT-2024-100",
  "total_costo": 2500.00,
  "detalles": [
    {
      "producto_id": 1,
      "cantidad": 100,
      "unidad_id": 2,
      "precio_unitario": 2.50,
      "subtotal": 250.00
    },
    {
      "producto_id": 2,
      "cantidad": 80,
      "unidad_id": 2,
      "precio_unitario": 3.00,
      "subtotal": 240.00
    }
  ]
}
```

**Response (200)**
```json
{
  "success": true,
  "compra_id": 100
}
```

---

## 💳 Ventas

### Listar Ventas
```http
GET /api/ventas HTTP/1.1
```

**Response**
```json
[
  {
    "id": 1,
    "numero_comprobante": "VTA-1234567890",
    "usuario_nombre": "Vendedor Principal",
    "cliente_nombre": "Juan Pérez",
    "cliente_cedula": "123-4567890-1",
    "fecha_venta": "2024-02-01",
    "total_venta": 150.00,
    "efectivo": 150.00,
    "tarjeta": 0.00,
    "transferencia": 0.00
  }
]
```

### Registrar Venta
```http
POST /api/ventas HTTP/1.1
Content-Type: application/json

{
  "numero_comprobante": "VTA-123456",
  "cliente_nombre": "María García",
  "cliente_cedula": "987-6543210-1",
  "fecha_venta": "2024-02-01",
  "tipo_venta": "producto",
  "total_venta": 125.50,
  "efectivo": 125.50,
  "tarjeta": 0.00,
  "transferencia": 0.00,
  "observaciones": "Compra satisfacción del cliente",
  "detalles": [
    {
      "tipo": "producto",
      "id": 1,
      "cantidad": 2,
      "unidad_id": 2,
      "precio": 5.00,
      "subtotal": 10.00
    },
    {
      "tipo": "servicio",
      "id": 1,
      "cantidad": 1,
      "precio": 10.00,
      "subtotal": 10.00
    }
  ]
}
```

**Response (200)**
```json
{
  "success": true,
  "venta_id": 100
}
```

---

## 💉 Servicios

### Listar Servicios
```http
GET /api/servicios HTTP/1.1
```

**Response**
```json
[
  {
    "id": 1,
    "nombre": "Inyección Intramuscular",
    "descripcion": "Aplicación de inyección intramuscular",
    "precio": 5.00,
    "tipo": "inyeccion",
    "activo": true
  },
  {
    "id": 2,
    "nombre": "Consulta Médica",
    "descripcion": "Consulta con profesional de salud",
    "precio": 25.00,
    "tipo": "consulta",
    "activo": true
  }
]
```

---

## 🎁 Combos

### Listar Combos
```http
GET /api/combos HTTP/1.1
```

**Response**
```json
[
  {
    "id": 1,
    "nombre": "Combo Gripe",
    "descripcion": "Paracetamol + Vitamina C + Suero",
    "precio_combo": 45.00,
    "detalles": [
      {
        "producto_id": 1,
        "producto_nombre": "Paracetamol 500mg",
        "cantidad": 1,
        "unidad_nombre": "Pastilla"
      },
      {
        "producto_id": 11,
        "producto_nombre": "Vitamina C 1000mg",
        "cantidad": 1,
        "unidad_nombre": "Pastilla"
      }
    ]
  }
]
```

### Crear Combo
```http
POST /api/combos HTTP/1.1
Content-Type: application/json

{
  "nombre": "Combo Dolor",
  "descripcion": "Alivio de dolor muscular",
  "precio_combo": 35.00,
  "detalles": [
    {
      "producto_id": 1,
      "cantidad": 1,
      "unidad_id": 2
    },
    {
      "producto_id": 2,
      "cantidad": 1,
      "unidad_id": 2
    }
  ]
}
```

---

## 📊 Reportes

### Reporte de Ganancia
```http
GET /api/reportes/ganancia?fecha_inicio=2024-01-01&fecha_fin=2024-02-01 HTTP/1.1
```

**Response**
```json
{
  "ventas": [
    {
      "id": 1,
      "numero_comprobante": "VTA-123",
      "total_venta": 100.00,
      "costo_total": 45.00,
      "ganancia": 55.00
    }
  ],
  "ganancia_total": 2500.00,
  "inversion_total": 45000.00
}
```

---

## 📝 Movimientos

### Listar Movimientos
```http
GET /api/movimientos?fecha_inicio=2024-01-01&fecha_fin=2024-02-01 HTTP/1.1
```

**Response**
```json
[
  {
    "id": 1,
    "producto_nombre": "Paracetamol 500mg",
    "tipo_movimiento": "entrada",
    "cantidad": 100,
    "cantidad_anterior": 50,
    "cantidad_nueva": 150,
    "usuario_nombre": "Administrador",
    "fecha_movimiento": "2024-01-15T10:30:00"
  }
]
```

---

## 👥 Usuarios (Admin)

### Listar Usuarios
```http
GET /api/usuarios HTTP/1.1
```

**Response**
```json
[
  {
    "id": 1,
    "nombre": "Administrador",
    "email": "admin@farmacia.com",
    "rol": "admin",
    "activo": true
  }
]
```

### Crear Usuario
```http
POST /api/usuarios HTTP/1.1
Content-Type: application/json

{
  "nombre": "Nuevo Vendedor",
  "email": "vendedor_nuevo@farmacia.com",
  "contrasena": "password123",
  "rol": "vendedor"
}
```

### Actualizar Usuario
```http
PUT /api/usuarios/2 HTTP/1.1
Content-Type: application/json

{
  "nombre": "Nombre Actualizado",
  "rol": "vendedor",
  "contrasena": "nueva_contraseña"
}
```

### Eliminar Usuario
```http
DELETE /api/usuarios/2 HTTP/1.1
```

---

## 🔧 Unidades de Medida

### Listar Unidades
```http
GET /api/unidades HTTP/1.1
```

**Response**
```json
[
  {
    "id": 1,
    "nombre": "Unidad",
    "abreviatura": "u",
    "descripcion": "Una unidad"
  },
  {
    "id": 2,
    "nombre": "Pastilla",
    "abreviatura": "past",
    "descripcion": "Una pastilla"
  },
  {
    "id": 3,
    "nombre": "Blister",
    "abreviatura": "blis",
    "descripcion": "Blister de pastillas"
  }
]
```

---

## 📂 Categorías

### Listar Categorías
```http
GET /api/categorias HTTP/1.1
```

**Response**
```json
[
  {
    "id": 1,
    "nombre": "Analgésicos",
    "descripcion": "Medicamentos para el dolor"
  }
]
```

### Crear Categoría
```http
POST /api/categorias HTTP/1.1
Content-Type: application/json

{
  "nombre": "Mi Categoría",
  "descripcion": "Descripción de la categoría"
}
```

---

## ⚠️ Códigos de Error

| Código | Significado |
|--------|-------------|
| 200 | Éxito |
| 400 | Solicitud inválida |
| 401 | No autenticado |
| 403 | No autorizado (sin permisos) |
| 404 | Recurso no encontrado |
| 500 | Error del servidor |

---

## 📌 Notas Importantes

1. **Autenticación**: Las rutas protegidas requieren estar logueado
2. **Roles**: Admin accede a todo, Vendedor solo a ventas y servicios
3. **Stock**: Se actualiza automáticamente al registrar compras y ventas
4. **Movimientos**: Se registran automáticamente en cada operación
5. **Variaciones**: Un producto puede tener múltiples unidades de venta

---

**Documentación actualizada al 2024**
