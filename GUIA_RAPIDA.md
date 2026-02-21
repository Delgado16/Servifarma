# 🚀 Guía Rápida - FarmaControl

## ⚡ Inicio Rápido (5 minutos)

### Windows
1. Descargar o clonar el proyecto
2. Hacer doble clic en `setup.bat`
3. Editar `.env` con credenciales MySQL
4. Ejecutar: `venv\Scripts\activate` y luego `python backend/app.py`

### Linux/Mac
1. Descargar o clonar el proyecto
2. Ejecutar: `chmod +x setup.sh && ./setup.sh`
3. Editar `.env` con credenciales MySQL
4. Ejecutar: `source venv/bin/activate` y luego `python backend/app.py`

## 🔧 Configuración Mínima

```bash
# 1. Instalar Python (si no está)
# Python 3.8 o superior

# 2. Instalar MySQL (si no está)
# MySQL Community Server

# 3. Crear base de datos
mysql -u root -p < database/schema.sql

# 4. Copiar archivo .env
cp .env.example .env

# 5. Editar .env con tus datos:
# MYSQL_USER=root
# MYSQL_PASSWORD=tu_contraseña
```

## 📚 Estructura de Carpetas

```
backend/
  ├── app.py            → Aplicación principal
  ├── config.py         → Configuración
  ├── routes_admin.py   → Rutas adicionales
  ├── static/           → CSS y JS
  └── templates/        → HTML

database/
  ├── schema.sql        → Estructura MySQL
  └── sample_data.sql   → Datos de ejemplo
```

## 🔑 Usuarios de Prueba

| Usuario | Email | Contraseña | Rol |
|---------|-------|-----------|-----|
| Admin | admin@farmacia.com | admin123 | Administrador |
| Vendedor | vendedor@farmacia.com | vendedor123 | Vendedor |

## 📋 Funcionalidades Principales

### 👨‍💼 Para Administrador

```
Dashboard
├── Ver estadísticas (productos, stock, inversión)
├── Productos bajo stock
└── Últimas ventas

Productos
├── Crear/editar/eliminar
├── Múltiples unidades de medida
├── Seguimiento de stock
└── Variaciones de presentación

Compras
├── Registrar entradas
├── Control de proveedores
└── Detalles por producto

Reportes
├── Ganancia vs Inversión
├── Movimientos de inventario
└── Análisis por período
```

### 💳 Para Vendedor

```
Punto de Venta
├── Agregar productos al carrito
├── Seleccionar variación (pastilla/blister/caja)
├── Aplicar servicios
├── Procesar pago
└── Generar comprobante

Servicios
├── Inyecciones
├── Canalizaciones
└── Consultas médicas
```

## 🎯 Casos de Uso

### 1. Vender un producto
```
1. Vendedor inicia sesión
2. Click en "Nueva Venta"
3. Buscar producto (Paracetamol)
4. Seleccionar cantidad y unidad (1 pastilla)
5. Agregar más productos si necesita
6. Procesar pago (efectivo, tarjeta, transferencia)
7. Sistema genera comprobante
```

### 2. Registrar compra a proveedor
```
1. Admin inicia sesión
2. Click en "Nueva Compra"
3. Seleccionar proveedor
4. Agregar productos y cantidades
5. Registrar compra
6. Stock se actualiza automáticamente
```

### 3. Crear un combo
```
1. Admin va a "Combos"
2. Click en "Nuevo Combo"
3. Nombre: "Combo Gripe"
4. Agregar: Paracetamol + Vitamina C + Suero
5. Precio del combo: RD$ 45.00
6. Guardar
```

### 4. Ver reportes
```
1. Admin va a "Reportes"
2. Seleccionar rango de fechas
3. Ver ganancia total vs inversión
4. Exportar a CSV si necesita
```

## ⚙️ Configuraciones Importantes

### Cambiar puerto
Editar `backend/app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)  # Cambiar puerto
```

### Cambiar moneda
Editar `backend/static/js/main.js`:
```javascript
function formatearDinero(cantidad) {
    return new Intl.NumberFormat('es-DO', {  // Cambiar locale
        style: 'currency',
        currency: 'DOP'  // Cambiar currency
    }).format(cantidad);
}
```

### Agregar más servicios
En MySQL:
```sql
INSERT INTO servicios (nombre, precio, tipo) 
VALUES ('Mi Servicio', 100.00, 'inyeccion');
```

## 🐛 Solucionar Problemas

### Error: "Connection refused"
```bash
# Verificar que MySQL está corriendo
mysql -u root -p -e "SELECT 1"

# Si está en Windows
net start MySQL57  # o tu versión
```

### Error: "No module named 'flask'"
```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstalar
pip install -r requirements.txt
```

### Stock no actualiza
- Verificar que la compra se guardó correctamente
- Revisar movimientos_inventario en la BD
- Comprobar que el usuario tiene rol admin

### Modal no abre
- Verificar que JavaScript esté habilitado
- Revisar consola del navegador (F12)
- Limpiar caché del navegador

## 📊 Base de Datos

### Tablas principales

| Tabla | Uso |
|-------|-----|
| usuarios | Almacena admin y vendedores |
| productos | Medicamentos y artículos |
| compras | Entradas de inventario |
| ventas | Registro de transacciones |
| servicios | Inyecciones, consultas, etc |
| combos | Paquetes de productos |
| proveedores | Información de distribuidores |

### Relaciones clave
```
Compras → Proveedores
Compras → Productos (detalles_compra)
Ventas → Usuarios
Ventas → Productos (detalles_venta)
Combos → Productos (detalles_combo)
```

## 🔒 Seguridad Básica

1. **Cambiar contraseña admin**
   - Editar .env
   - Reiniciar aplicación

2. **Backup de BD**
   ```bash
   mysqldump -u root -p farmacia_db > backup.sql
   ```

3. **Restaurar BD**
   ```bash
   mysql -u root -p farmacia_db < backup.sql
   ```

## 📝 Tips Útiles

- **Búsqueda de productos**: Buscar por código o nombre
- **Variaciones de unidad**: Un producto puede venderse de 3 formas diferentes
- **Stock mínimo**: Alerta cuando llega a este número
- **Combos**: Crear paquetes con descuento
- **Historial**: Ver todas las transacciones en reportes

## 🚀 Próximas Mejoras

Para agregar nuevas funcionalidades:
1. Agregar ruta en `app.py`
2. Crear template HTML en `templates/`
3. Agregar tabla SQL en `database/schema.sql`
4. Agregar JavaScript en `static/js/`

## 📞 Soporte

- Revisar logs en consola
- Verificar .env tiene credenciales correctas
- Revisar que MySQL esté activo
- Revisar que puerto 5000 está disponible

---

**¡Listo! Tu sistema farmacéutico está configurado y listo para usar.**
