# 💊 FarmaControl - Sistema de Gestión Farmacéutica

Sistema completo de gestión de inventario, ventas y servicios para farmacias.

## Características

### 👨‍💼 Administrador
- **Dashboard**: Vista general de estadísticas (productos, stock, inversión, ventas)
- **Gestión de Productos**: CRUD completo con códigos, categorías, presentaciones
- **Unidades de Medida**: Pastilla suelta, blister, caja (configurables)
- **Gestión de Compras**: Registro de entradas de inventario con proveedores
- **Control de Proveedores**: Base de datos de proveedores
- **Gestión de Combos**: Crear paquetes de productos
- **Reportes**: Ganancia vs inversión, movimientos de inventario
- **Gestión de Usuarios**: Crear vendedores

### 💳 Vendedor
- **Punto de Venta**: Interfaz intuitiva para realizar ventas
- **Carrito de Compras**: Agregar/eliminar productos
- **Servicios**: Inyecciones, canalizaciones, consultas médicas
- **Múltiples Formas de Pago**: Efectivo, tarjeta, transferencia
- **Historial de Ventas**: Ver ventas realizadas

### 📊 General
- Sistema de autenticación seguro
- Control de roles (admin/vendedor)
- Inventario en tiempo real
- Cálculo automático de ganancias e inversión
- Base de datos MySQL

## Requisitos

- Python 3.8+
- MySQL 5.7+
- pip (gestor de paquetes Python)

## Instalación

### 1. Clonar o descargar el proyecto

```bash
cd farmacia-control
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos

#### Opción A: MySQL (Recomendado)

1. Crear la base de datos:
```bash
mysql -u root -p < database/schema.sql
```

2. Copiar `.env.example` a `.env` y configurar:
```bash
cp .env.example .env
```

3. Editar `.env`:
```
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta-aqui
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=tu_contraseña
MYSQL_DB=farmacia_db
MYSQL_PORT=3306
```

### 5. Crear usuarios iniciales

Ejecutar script SQL adicional (opcional):
```sql
-- Usuario Admin
INSERT INTO usuarios (nombre, email, contrasena, rol) 
VALUES ('Administrador', 'admin@farmacia.com', SHA2('admin123', 256), 'admin');

-- Usuario Vendedor
INSERT INTO usuarios (nombre, email, contrasena, rol) 
VALUES ('Vendedor', 'vendedor@farmacia.com', SHA2('vendedor123', 256), 'vendedor');
```

> **Nota**: Las contraseñas se hashean con SHA256 en la base de datos

### 6. Ejecutar la aplicación

```bash
python backend/app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## Estructura del Proyecto

```
farmacia-control/
├── backend/
│   ├── app.py                 # Aplicación principal Flask
│   ├── config.py              # Configuración
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css    # Estilos CSS
│   │   └── js/
│   │       └── main.js       # JavaScript principal
│   └── templates/
│       ├── base.html         # Template base
│       ├── login.html        # Página de login
│       ├── admin/
│       │   ├── dashboard.html
│       │   ├── productos.html
│       │   ├── compras.html
│       │   └── proveedores.html
│       └── vendedor/
│           └── dashboard.html
├── database/
│   └── schema.sql            # Estructura MySQL
├── requirements.txt          # Dependencias Python
├── .env.example              # Variables de entorno (ejemplo)
└── README.md                 # Este archivo
```

## Rutas API

### Autenticación
- `POST /login` - Iniciar sesión
- `GET /logout` - Cerrar sesión

### Productos (Admin)
- `GET /api/productos` - Listar productos
- `POST /api/productos` - Crear producto
- `GET /api/productos/<id>` - Obtener producto
- `PUT /api/productos/<id>` - Actualizar producto
- `DELETE /api/productos/<id>` - Eliminar producto

### Compras (Admin)
- `GET /api/compras` - Listar compras
- `POST /api/compras` - Registrar compra

### Proveedores (Admin)
- `GET /api/proveedores` - Listar proveedores
- `POST /api/proveedores` - Crear proveedor

### Servicios
- `GET /api/servicios` - Listar servicios

### Ventas
- `GET /api/ventas` - Listar ventas
- `POST /api/ventas` - Registrar venta

### Combos (Admin)
- `GET /api/combos` - Listar combos
- `POST /api/combos` - Crear combo

### Reportes (Admin)
- `GET /api/reportes/ganancia` - Reporte de ganancias

## Credenciales de Prueba

Al ejecutar por primera vez, use:

- **Admin**
  - Email: `admin@farmacia.com`
  - Contraseña: `admin123`

- **Vendedor**
  - Email: `vendedor@farmacia.com`
  - Contraseña: `vendedor123`

## Características Implementadas

### Inventario
- ✅ Productos con múltiples unidades de medida
- ✅ Stock en tiempo real
- ✅ Movimientos de inventario
- ✅ Productos bajo stock

### Ventas
- ✅ Carrito de compras
- ✅ Múltiples formas de pago
- ✅ Registro de cliente (opcional)
- ✅ Historial de ventas

### Servicios
- ✅ Inyecciones (intramuscular, intravenosa)
- ✅ Canalizaciones
- ✅ Consultas médicas
- ✅ Combos (paquetes)

### Reportes
- ✅ Cálculo de inversión total
- ✅ Cálculo de ganancia
- ✅ Movimientos de inventario
- ✅ Ventas por período

### Seguridad
- ✅ Autenticación de usuarios
- ✅ Encriptación de contraseñas (SHA256)
- ✅ Sesiones seguras
- ✅ Control de roles

## Configuración Avanzada

### Cambiar Puerto

Editar `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Cambiar puerto aquí
```

### Modo Producción

1. Cambiar `FLASK_ENV` a `production` en `.env`
2. Cambiar `debug=False` en `app.py`
3. Configurar `SECRET_KEY` segura
4. Usar un servidor WSGI (Gunicorn, uWSGI)

### Base de Datos Remota

Configurar en `.env`:
```
MYSQL_HOST=servidor-remoto.com
MYSQL_USER=usuario_remoto
MYSQL_PASSWORD=contraseña_remota
```

## Troubleshooting

### Error: "Can't connect to MySQL"
- Verificar que MySQL esté corriendo
- Verificar credenciales en `.env`
- Verificar que la base de datos existe

### Error: "ModuleNotFoundError"
- Activar entorno virtual
- Reinstalar dependencias: `pip install -r requirements.txt`

### Error: "Template not found"
- Verificar estructura de carpetas
- Asegurar que los archivos `.html` están en `templates/`

## Mejoras Futuras

- [ ] Autenticación con 2FA
- [ ] Respaldos automáticos de BD
- [ ] Exportación de reportes a PDF
- [ ] Integración con métodos de pago
- [ ] App móvil
- [ ] Sincronización multi-sucursal
- [ ] Búsqueda avanzada de productos
- [ ] Gráficas interactivas
- [ ] Descuentos automáticos
- [ ] Facturación electrónica

## Licencia

Proyecto privado para uso farmacéutico.

## Soporte

Para reportar bugs o solicitar features, contactar al administrador del sistema.

---

**Desarrollado con Flask + MySQL + HTML/CSS/JavaScript**
