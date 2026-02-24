try:
    import pymysql
    pymysql.install_as_MySQLdb()
    print("PyMySQL configurado correctamente")
except ImportError:
    print("PyMySQL no está instalado. Ejecuta: pip install pymysql")

from decimal import Decimal
import MySQLdb
from flask import Flask, flash, json, render_template, request, jsonify, session, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
# CORREGIR EL IMPORT:
from MySQLdb.cursors import DictCursor  # Import específico
from functools import wraps
import hashlib
import os
import traceback
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)

# ========================
# CONFIGURACIÓN CORRECTA
# ========================

# Cargar configuración desde config.py
app.config.from_object('config.DevelopmentConfig')

# INICIALIZAR MySQL ANTES de agregar configuraciones adicionales
mysql = MySQL(app)

# Ahora agregar configuraciones adicionales que NO estén en config.py
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)


# ========================
# DECORADORES
# ========================

def login_required(f):
    """Verifica que el usuario esté autenticado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Verifica que el usuario sea administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        
        # CORREGIDO: Usar DictCursor directamente
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute('SELECT rol FROM usuarios WHERE id = %s', (session['usuario_id'],))
        user = cursor.fetchone()
        cursor.close()
        
        if not user or user['rol'] != 'admin':
            return jsonify({'error': 'No tienes permisos de administrador'}), 403
        return f(*args, **kwargs)
    return decorated_function

def roles_required(roles_permitidos):
    """Verifica que el usuario tenga uno de los roles permitidos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'usuario_id' not in session:
                return redirect(url_for('login'))
            
            cursor = mysql.connection.cursor(DictCursor)
            cursor.execute('SELECT rol FROM usuarios WHERE id = %s', (session['usuario_id'],))
            user = cursor.fetchone()
            cursor.close()
            
            if not user or user['rol'] not in roles_permitidos:
                return jsonify({'error': f'No tienes permisos. Roles permitidos: {", ".join(roles_permitidos)}'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Uso:
@roles_required(['admin', 'vendedor'])
def mi_vista():
    return "Acceso permitido para admin y vendedor"


# ========================
# RUTAS DE AUTENTICACIÓN
# ========================

@app.route('/')
def index():
    if 'usuario_id' in session:
        cursor = mysql.connection.cursor(DictCursor)  # CORREGIDO
        cursor.execute('SELECT rol FROM usuarios WHERE id = %s', (session['usuario_id'],))
        user = cursor.fetchone()
        cursor.close()
        
        if user['rol'] == 'admin':
            return redirect(url_for('dashboard_admin'))
        else:
            return redirect(url_for('dashboard_vendedor'))
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        contrasena = request.form.get('contrasena')
        
        # DEBUG: Mostrar datos recibidos
        print(f"DEBUG - Email recibido: {email}")
        print(f"DEBUG - Contraseña recibida: {contrasena}")
        
        if not email or not contrasena:
            return render_template('login.html', error='Email y contraseña son requeridos')
        
        try:
            cursor = mysql.connection.cursor(DictCursor)
            print("DEBUG - Conexión a MySQL establecida")
            
            # Verificar si la tabla usuarios existe
            cursor.execute("SHOW TABLES LIKE 'usuarios'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print("DEBUG - Tabla 'usuarios' no existe")
                cursor.close()
                return render_template('login.html', error='Base de datos no configurada correctamente')
            
            # Buscar usuario SOLO por email
            cursor.execute('''
                SELECT * FROM usuarios 
                WHERE email = %s AND activo = TRUE
            ''', (email,))
            
            user = cursor.fetchone()
            cursor.close()
            
            print(f"DEBUG - Usuario encontrado: {user}")
            
            if user:
                print(f"DEBUG - Hash en BD: {user['contrasena']}")
                print(f"DEBUG - Verificando con check_password_hash...")
                
                # ✅ CORREGIDO: Usar check_password_hash en lugar de verify_password
                if check_password_hash(user['contrasena'], contrasena):
                    session.permanent = True
                    session['usuario_id'] = user['id']
                    session['usuario_nombre'] = user['nombre']
                    session['usuario_rol'] = user['rol']
                    
                    print(f"DEBUG - Sesión creada: usuario_id={session['usuario_id']}, rol={session['usuario_rol']}")
                    
                    if user['rol'] == 'admin':
                        return redirect(url_for('dashboard_admin'))
                    else:
                        return redirect(url_for('dashboard_vendedor'))
                else:
                    print("DEBUG - Contraseña incorrecta")
                    return render_template('login.html', error='Contraseña incorrecta')
            else:
                print("DEBUG - Usuario no encontrado")
                return render_template('login.html', error='Usuario no encontrado')
                    
        except Exception as e:
            print(f"DEBUG - Error en login: {str(e)}")
            traceback.print_exc()
            return render_template('login.html', error=f'Error de conexión a la base de datos: {str(e)}')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ========================
# DASHBOARD ADMINISTRADOR
# ========================

@app.route('/admin/dashboard')
@admin_required
def dashboard_admin():
    cursor = mysql.connection.cursor(DictCursor)
    
    # Estadísticas generales
    cursor.execute('''
        SELECT 
            COUNT(*) as total_productos,
            SUM(stock_actual) as stock_total,
            SUM(stock_actual * precio_costo) as inversion_total
        FROM productos WHERE activo = TRUE
    ''')
    stats = cursor.fetchone()
    
    cursor.execute('''
        SELECT 
            SUM(total_venta) as ganancia_total,
            COUNT(*) as total_ventas
        FROM ventas WHERE DATE(fecha_venta) >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    ''')
    ventas_stats = cursor.fetchone()
    
    cursor.close()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         ventas_stats=ventas_stats)

# ========================
# GESTIÓN DE PRODUCTOS
# ========================

@app.route('/productos', methods=['GET', 'POST'])
@app.route('/productos/nuevo', methods=['GET', 'POST'])
@admin_required
def productos():
    cursor = mysql.connection.cursor(DictCursor)
    
    # Obtener datos para filtros y formulario
    cursor.execute('SELECT id, nombre FROM categorias WHERE activo = TRUE ORDER BY nombre')
    categorias = cursor.fetchall()
    
    cursor.execute('SELECT id, nombre FROM unidades_medida WHERE activo = TRUE ORDER BY nombre')
    unidades = cursor.fetchall()
    
    if request.method == 'POST':
        # Este POST maneja la creación desde el modal
        data = request.form
        
        try:
            # Validaciones
            if not data.get('codigo') or not data.get('nombre'):
                flash('Código y nombre son requeridos', 'error')
                return redirect(url_for('productos'))
            
            # Verificar si el código ya existe
            cursor.execute('SELECT id FROM productos WHERE codigo = %s', (data['codigo'].strip(),))
            if cursor.fetchone():
                flash('El código ya está registrado', 'error')
                return redirect(url_for('productos'))
            
            # Convertir valores
            fecha_vencimiento = None
            if data.get('fecha_vencimiento'):
                fecha_vencimiento = datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d').date()
            
            # Insertar producto
            cursor.execute('''
                INSERT INTO productos (
                    codigo, nombre, descripcion, categoria_id, 
                    principio_activo, presentacion, unidad_base_id,
                    precio_costo, precio_venta, stock_actual, stock_minimo,
                    lote, fecha_vencimiento, activo
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            ''', (
                data['codigo'].strip(),
                data['nombre'].strip(),
                data.get('descripcion', '').strip(),
                data.get('categoria_id'),
                data.get('principio_activo', '').strip(),
                data.get('presentacion', '').strip(),
                data.get('unidad_base_id'),
                float(data.get('precio_costo', 0)),
                float(data.get('precio_venta', 0)),
                int(data.get('stock_actual', 0)),
                int(data.get('stock_minimo', 5)),
                data.get('lote', '').strip(),
                fecha_vencimiento
            ))
            
            mysql.connection.commit()
            flash('Producto creado exitosamente', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al crear producto: {str(e)}', 'error')
        finally:
            cursor.close()
        
        return redirect(url_for('productos'))
    
    # Método GET - Mostrar lista
    buscar = request.args.get('buscar', '')
    categoria = request.args.get('categoria', '')
    mostrar_inactivos = request.args.get('mostrar_inactivos', '0') == '1'
    
    query = '''
        SELECT p.*, c.nombre as categoria_nombre, u.nombre as unidad_nombre,
               CASE 
                   WHEN p.stock_actual <= p.stock_minimo THEN 'bajo'
                   WHEN p.fecha_vencimiento IS NOT NULL AND p.fecha_vencimiento <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 'vencimiento'
                   ELSE 'normal'
               END as estado_stock
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
        WHERE 1=1
    '''
    params = []
    
    if not mostrar_inactivos:
        query += ' AND p.activo = TRUE'
    
    if buscar:
        query += ' AND (p.nombre LIKE %s OR p.codigo LIKE %s OR p.lote LIKE %s)'
        params.extend([f'%{buscar}%', f'%{buscar}%', f'%{buscar}%'])
    
    if categoria:
        query += ' AND p.categoria_id = %s'
        params.append(categoria)
    
    query += ' ORDER BY p.nombre'
    
    cursor.execute(query, params)
    productos_lista = cursor.fetchall()
    cursor.close()
    
    return render_template('admin/productos.html',
                         productos=productos_lista,
                         categorias=categorias,
                         unidades=unidades,
                         buscar=buscar,
                         categoria_seleccionada=categoria,
                         mostrar_inactivos=mostrar_inactivos)

@app.route('/productos/<int:producto_id>/editar', methods=['POST'])
@admin_required
def editar_producto(producto_id):
    """Maneja la edición de productos desde modal"""
    cursor = mysql.connection.cursor(DictCursor)
    
    try:
        data = request.form
        
        # Verificar si el producto existe
        cursor.execute('SELECT * FROM productos WHERE id = %s', (producto_id,))
        producto = cursor.fetchone()
        
        if not producto:
            flash('Producto no encontrado', 'error')
            return redirect(url_for('productos'))
        
        # Convertir fecha de vencimiento
        fecha_vencimiento = None
        if data.get('fecha_vencimiento'):
            fecha_vencimiento = datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d').date()
        
        # Actualizar producto
        cursor.execute('''
            UPDATE productos SET
                codigo = %s,
                nombre = %s,
                descripcion = %s,
                categoria_id = %s,
                principio_activo = %s,
                presentacion = %s,
                unidad_base_id = %s,
                precio_costo = %s,
                precio_venta = %s,
                stock_actual = %s,
                stock_minimo = %s,
                lote = %s,
                fecha_vencimiento = %s,
                activo = %s
            WHERE id = %s
        ''', (
            data['codigo'].strip(),
            data['nombre'].strip(),
            data.get('descripcion', '').strip(),
            data.get('categoria_id'),
            data.get('principio_activo', '').strip(),
            data.get('presentacion', '').strip(),
            data.get('unidad_base_id'),
            float(data.get('precio_costo', 0)),
            float(data.get('precio_venta', 0)),
            int(data.get('stock_actual', 0)),
            int(data.get('stock_minimo', 5)),
            data.get('lote', '').strip(),
            fecha_vencimiento,
            data.get('activo') == 'on',
            producto_id
        ))
        
        mysql.connection.commit()
        flash('Producto actualizado exitosamente', 'success')
        
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al actualizar producto: {str(e)}', 'error')
    finally:
        cursor.close()
    
    return redirect(url_for('productos'))

@app.route('/productos/<int:producto_id>/eliminar', methods=['POST'])
@admin_required
def eliminar_producto(producto_id):
    cursor = mysql.connection.cursor(DictCursor)
    
    try:
        # Verificar si el producto existe
        cursor.execute('SELECT * FROM productos WHERE id = %s', (producto_id,))
        producto = cursor.fetchone()
        
        if not producto:
            flash('Producto no encontrado', 'error')
            return redirect(url_for('productos'))
        
        # Marcar como inactivo en lugar de eliminar
        cursor.execute('UPDATE productos SET activo = FALSE WHERE id = %s', (producto_id,))
        
        mysql.connection.commit()
        flash('Producto marcado como inactivo', 'success')
        
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar producto: {str(e)}', 'error')
    finally:
        cursor.close()
    
    return redirect(url_for('productos'))

@app.route('/productos/exportar', methods=['GET'])
@admin_required
def exportar_productos():
    """Exportar productos a Excel"""
    cursor = mysql.connection.cursor(DictCursor)
    
    cursor.execute('''
        SELECT p.codigo, p.nombre, c.nombre as categoria,
               p.principio_activo, p.presentacion,
               u.nombre as unidad, p.stock_actual,
               p.precio_costo, p.precio_venta,
               p.lote, p.fecha_vencimiento
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
        WHERE p.activo = TRUE
        ORDER BY p.nombre
    ''')
    
    productos = cursor.fetchall()
    cursor.close()
    
    # Aquí puedes implementar la generación de Excel
    # Por ahora solo devuelve JSON
    return jsonify(productos)

# ========================
# GESTIÓN DE COMPRAS
# ========================
@app.route('/compras')
@admin_required
def compras():
    cursor = mysql.connection.cursor(DictCursor)
    
    # Cargar datos para el formulario
    cursor.execute('SELECT id, nombre FROM proveedores WHERE activo = 1 ORDER BY nombre')
    proveedores = cursor.fetchall()
    
    cursor.execute('SELECT id, nombre, precio_costo, stock_actual FROM productos WHERE activo = 1 ORDER BY nombre')
    productos = cursor.fetchall()
    
    # Cargar compras para la tabla
    cursor.execute('''
        SELECT c.*, p.nombre as proveedor_nombre, u.nombre as usuario_nombre
        FROM compras c
        LEFT JOIN proveedores p ON c.proveedor_id = p.id
        LEFT JOIN usuarios u ON c.usuario_id = u.id
        ORDER BY c.fecha_creacion DESC LIMIT 100
    ''')
    compras_lista = cursor.fetchall()
    
    cursor.close()
    
    return render_template('admin/compras.html', 
                         proveedores=proveedores,
                         productos=productos,
                         compras=compras_lista,
                         today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/compras/registrar', methods=['POST'])
@admin_required
def registrar_compra():
    try:
        # Obtener datos del formulario
        numero_documento = request.form.get('numero_documento')
        proveedor_id = request.form.get('proveedor_id')
        fecha_compra = request.form.get('fecha_compra')
        numero_factura = request.form.get('numero_factura', '')
        
        # Validaciones básicas
        if not all([numero_documento, proveedor_id, fecha_compra]):
            flash('Complete todos los campos requeridos', 'danger')
            return redirect('/compras')
        
        cursor = mysql.connection.cursor(DictCursor)
        
        # Calcular total basado en los detalles
        producto_ids = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')
        precios = request.form.getlist('precio_unitario[]')
        
        total_costo = 0
        detalles_validos = []
        
        # Procesar y validar detalles
        for i in range(len(producto_ids)):
            if producto_ids[i] and cantidades[i] and precios[i]:
                try:
                    cantidad = int(cantidades[i])
                    precio = float(precios[i])
                    
                    if cantidad > 0 and precio > 0:
                        subtotal = cantidad * precio
                        total_costo += subtotal
                        
                        detalles_validos.append({
                            'producto_id': producto_ids[i],
                            'cantidad': cantidad,
                            'precio': precio,
                            'subtotal': subtotal
                        })
                except (ValueError, TypeError):
                    continue
        
        if not detalles_validos:
            flash('Debe agregar al menos un producto válido', 'danger')
            return redirect(url_for('compras'))
        
        # Insertar compra
        cursor.execute('''
            INSERT INTO compras (numero_documento, proveedor_id, usuario_id, 
                                fecha_compra, numero_factura, total_costo, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            numero_documento,
            proveedor_id,
            session['usuario_id'],
            fecha_compra,
            numero_factura,
            total_costo,
            'completada'
        ))
        
        compra_id = cursor.lastrowid
        
        # Insertar detalles y actualizar stock
        for detalle in detalles_validos:
            # Insertar detalle de compra
            cursor.execute('''
                INSERT INTO detalles_compra (compra_id, producto_id, cantidad, 
                                            unidad_id, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                compra_id,
                detalle['producto_id'],
                detalle['cantidad'],
                1,  # unidad_id por defecto
                detalle['precio'],
                detalle['subtotal']
            ))
            
            # Obtener stock actual
            cursor.execute('SELECT stock_actual FROM productos WHERE id = %s', (detalle['producto_id'],))
            result = cursor.fetchone()
            
            if result:
                stock_anterior = result['stock_actual']
                stock_nuevo = stock_anterior + detalle['cantidad']
                
                # Actualizar stock
                cursor.execute('''
                    UPDATE productos 
                    SET stock_actual = %s 
                    WHERE id = %s
                ''', (stock_nuevo, detalle['producto_id']))
                
                # Registrar movimiento
                cursor.execute('''
                    INSERT INTO movimientos_inventario (
                        producto_id, tipo_movimiento, 
                        cantidad, cantidad_anterior, 
                        cantidad_nueva, referencia_tipo, 
                        referencia_id, usuario_id, observaciones
                    ) VALUES (%s, 'entrada', %s, %s, %s, 'compra', %s, %s, %s)
                ''', (
                    detalle['producto_id'],
                    detalle['cantidad'],
                    stock_anterior,
                    stock_nuevo,
                    compra_id,
                    session['usuario_id'],
                    f"Compra #{numero_documento}"
                ))
        
        mysql.connection.commit()
        cursor.close()
        
        flash(f'✅ Compra #{numero_documento} registrada exitosamente!', 'success')
        return redirect(url_for('compras'))
        
    except Exception as e:
        mysql.connection.rollback()
        flash(f'❌ Error al registrar la compra: {str(e)}', 'danger')
        return redirect(url_for('compras'))

# ========================
# GESTIÓN DE PROVEEDORES
# ========================

@app.route('/proveedores', methods=['GET'])
@admin_required
def proveedores():
    cursor = mysql.connection.cursor(DictCursor)
    
    try:
        # Parámetros de filtrado
        incluir_inactivos = request.args.get('incluir_inactivos', 'false').lower() == 'true'
        buscar = request.args.get('buscar', '')
        ciudad = request.args.get('ciudad', '')
        
        # Construir query básica - SIN DATE_FORMAT
        query = 'SELECT * FROM proveedores WHERE 1=1'
        params = []
        
        if not incluir_inactivos:
            query += ' AND activo = TRUE'
        
        if buscar:
            query += ' AND (nombre LIKE %s OR contacto LIKE %s OR email LIKE %s)'
            like_param = f'%{buscar}%'
            params.extend([like_param, like_param, like_param])
        
        if ciudad:
            query += ' AND ciudad = %s'
            params.append(ciudad)
        
        query += ' ORDER BY nombre'
        
        cursor.execute(query, params)
        proveedores = cursor.fetchall()
        
        # Obtener ciudades únicas para el filtro
        cursor.execute('SELECT DISTINCT ciudad FROM proveedores WHERE ciudad IS NOT NULL ORDER BY ciudad')
        ciudades = [row['ciudad'] for row in cursor.fetchall()]
        
        cursor.close()
        
        return render_template(
            'admin/proveedores.html',
            proveedores=proveedores,
            ciudades=ciudades,
            incluir_inactivos=incluir_inactivos,
            buscar=buscar,
            ciudad_filtro=ciudad
        )
    
    except Exception as e:
        cursor.close()
        flash(f'Error al cargar proveedores: {str(e)}', 'danger')
        return render_template('admin/proveedores.html', proveedores=[], ciudades=[])

@app.route('/proveedores/crear', methods=['POST'])
@admin_required
def crear_proveedor():
    cursor = mysql.connection.cursor(DictCursor)
    
    try:
        nombre = request.form.get('nombre', '').strip()
        contacto = request.form.get('contacto', '').strip()
        email = request.form.get('email', '').strip()
        direccion = request.form.get('direccion', '').strip()
        ciudad = request.form.get('ciudad', '').strip()
        telefono = request.form.get('telefono', '').strip()
        
        # Validaciones básicas
        if not nombre or len(nombre) < 2:
            flash('El nombre del proveedor es requerido (mínimo 2 caracteres)', 'danger')
            return redirect(url_for('proveedores'))
        
        # Insertar en base de datos
        cursor.execute('''
            INSERT INTO proveedores (nombre, contacto, email, direccion, ciudad, telefono)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (nombre, contacto, email, direccion, ciudad, telefono))
        
        mysql.connection.commit()
        cursor.close()
        
        flash('Proveedor creado exitosamente', 'success')
        return redirect(url_for('proveedores'))
    
    except Exception as e:
        cursor.close()
        flash(f'Error al crear el proveedor: {str(e)}', 'danger')
        return redirect(url_for('proveedores'))

@app.route('/proveedores/editar/<int:id>', methods=['POST'])
@admin_required
def editar_proveedor(id):
    cursor = mysql.connection.cursor(DictCursor)
    
    try:
        nombre = request.form.get('nombre', '').strip()
        contacto = request.form.get('contacto', '').strip()
        email = request.form.get('email', '').strip()
        direccion = request.form.get('direccion', '').strip()
        ciudad = request.form.get('ciudad', '').strip()
        telefono = request.form.get('telefono', '').strip()
        activo = request.form.get('activo', 'true') == 'true'
        
        # Validaciones básicas
        if not nombre or len(nombre) < 2:
            flash('El nombre del proveedor es requerido (mínimo 2 caracteres)', 'danger')
            return redirect(url_for('proveedores'))
        
        # Actualizar proveedor
        cursor.execute('''
            UPDATE proveedores 
            SET nombre = %s, contacto = %s, email = %s, direccion = %s, 
                ciudad = %s, telefono = %s, activo = %s
            WHERE id = %s
        ''', (nombre, contacto, email, direccion, ciudad, telefono, activo, id))
        
        mysql.connection.commit()
        cursor.close()
        
        flash('Proveedor actualizado exitosamente', 'success')
        return redirect(url_for('proveedores'))
    
    except Exception as e:
        cursor.close()
        flash(f'Error al editar el proveedor: {str(e)}', 'danger')
        return redirect(url_for('proveedores'))

@app.route('/proveedores/desactivar/<int:id>', methods=['POST'])
@admin_required
def desactivar_proveedor(id):
    cursor = mysql.connection.cursor()
    
    try:
        cursor.execute('UPDATE proveedores SET activo = FALSE WHERE id = %s', (id,))
        mysql.connection.commit()
        cursor.close()
        
        flash('Proveedor desactivado exitosamente', 'warning')
        return redirect(url_for('proveedores'))
    
    except Exception as e:
        cursor.close()
        flash(f'Error al desactivar el proveedor: {str(e)}', 'danger')
        return redirect(url_for('proveedores'))

@app.route('/proveedores/activar/<int:id>', methods=['POST'])
@admin_required
def activar_proveedor(id):
    cursor = mysql.connection.cursor()
    
    try:
        cursor.execute('UPDATE proveedores SET activo = TRUE WHERE id = %s', (id,))
        mysql.connection.commit()
        cursor.close()
        
        flash('Proveedor activado exitosamente', 'success')
        return redirect(url_for('proveedores'))
    
    except Exception as e:
        cursor.close()
        flash(f'Error al activar el proveedor: {str(e)}', 'danger')
        return redirect(url_for('proveedores'))

@app.route('/proveedores/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_proveedor(id):
    cursor = mysql.connection.cursor()
    
    try:
        cursor.execute('DELETE FROM proveedores WHERE id = %s', (id,))
        mysql.connection.commit()
        cursor.close()
        
        flash('Proveedor eliminado exitosamente', 'danger')
        return redirect(url_for('proveedores'))
    
    except Exception as e:
        cursor.close()
        flash(f'Error al eliminar el proveedor: {str(e)}', 'danger')
        return redirect(url_for('proveedores'))

# ========================
# DASHBOARD VENDEDOR
# ========================
@app.route('/vendedor/dashboard')
@login_required
def dashboard_vendedor():
    cursor = mysql.connection.cursor(DictCursor)
    usuario_id = session['usuario_id']
    
    # Obtener nombre del vendedor
    cursor.execute("SELECT nombre FROM usuarios WHERE id = %s", (usuario_id,))
    usuario = cursor.fetchone()
    nombre_vendedor = usuario['nombre'] if usuario else 'Vendedor'
    
    # 1. Ventas del vendedor hoy
    cursor.execute("""
        SELECT 
            COUNT(*) as total_ventas_hoy,
            COALESCE(SUM(total_venta), 0) as monto_total_hoy
        FROM ventas 
        WHERE usuario_id = %s 
        AND DATE(fecha_venta) = CURDATE()
    """, (usuario_id,))
    ventas_hoy = cursor.fetchone()
    
    # 2. Ventas del vendedor esta semana
    cursor.execute("""
        SELECT 
            COUNT(*) as total_ventas_semana,
            COALESCE(SUM(total_venta), 0) as monto_total_semana
        FROM ventas 
        WHERE usuario_id = %s 
        AND YEARWEEK(fecha_venta) = YEARWEEK(CURDATE())
    """, (usuario_id,))
    ventas_semana = cursor.fetchone()
    
    # 3. Ventas del vendedor este mes
    cursor.execute("""
        SELECT 
            COUNT(*) as total_ventas_mes,
            COALESCE(SUM(total_venta), 0) as monto_total_mes
        FROM ventas 
        WHERE usuario_id = %s 
        AND MONTH(fecha_venta) = MONTH(CURDATE()) 
        AND YEAR(fecha_venta) = YEAR(CURDATE())
    """, (usuario_id,))
    ventas_mes = cursor.fetchone()
    
    # 4. Últimas 10 ventas del vendedor
    cursor.execute("""
        SELECT v.*, 
               DATE_FORMAT(v.fecha_venta, '%%d/%%m/%%Y') as fecha_formateada,
               DATE_FORMAT(v.fecha_creacion, '%%H:%%i:%%s') as hora
        FROM ventas v
        WHERE v.usuario_id = %s
        ORDER BY v.fecha_creacion DESC
        LIMIT 10
    """, (usuario_id,))
    ultimas_ventas = cursor.fetchall()
    
    # 5. Productos con bajo stock
    cursor.execute("""
        SELECT p.*, 
               c.nombre as categoria_nombre,
               u.abreviatura as unidad
        FROM productos p
        INNER JOIN categorias c ON p.categoria_id = c.id
        INNER JOIN unidades_medida u ON p.unidad_base_id = u.id
        WHERE p.stock_actual <= p.stock_minimo 
        AND p.activo = 1
        ORDER BY p.stock_actual ASC
        LIMIT 10
    """)
    productos_bajo_stock = cursor.fetchall()
    
    # 6. Productos menos vendidos POR ESTE VENDEDOR
    cursor.execute("""
        SELECT 
            p.id,
            p.codigo,
            p.nombre as producto_nombre,
            p.stock_actual,
            p.stock_minimo,
            c.nombre as categoria_nombre,
            COALESCE(SUM(dv.cantidad), 0) as total_vendido
        FROM productos p
        INNER JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN detalles_venta dv ON p.id = dv.referencia_id AND dv.tipo_detalle = 'producto'
        LEFT JOIN ventas v ON dv.venta_id = v.id AND v.usuario_id = %s AND v.fecha_venta >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        WHERE p.activo = 1
        GROUP BY p.id, p.codigo, p.nombre, p.stock_actual, p.stock_minimo, c.nombre
        HAVING total_vendido > 0
        ORDER BY total_vendido ASC
        LIMIT 10
    """, (usuario_id,))
    productos_menos_vendidos = cursor.fetchall()
    
    # 7. Productos más vendidos POR ESTE VENDEDOR
    cursor.execute("""
        SELECT 
            p.id,
            p.codigo,
            p.nombre as producto_nombre,
            p.stock_actual,
            c.nombre as categoria_nombre,
            COALESCE(SUM(dv.cantidad), 0) as total_vendido,
            COALESCE(SUM(dv.subtotal), 0) as total_ingresos
        FROM productos p
        INNER JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN detalles_venta dv ON p.id = dv.referencia_id AND dv.tipo_detalle = 'producto'
        LEFT JOIN ventas v ON dv.venta_id = v.id AND v.usuario_id = %s AND v.fecha_venta >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        WHERE p.activo = 1
        GROUP BY p.id, p.codigo, p.nombre, p.stock_actual, c.nombre
        HAVING total_vendido > 0
        ORDER BY total_vendido DESC
        LIMIT 10
    """, (usuario_id,))
    productos_mas_vendidos = cursor.fetchall()
    
    # 8. Ventas por día (SIN GROUP BY problemático)
    cursor.execute("""
        SELECT 
            DATE(v.fecha_venta) as fecha,
            COUNT(*) as cantidad_ventas,
            COALESCE(SUM(v.total_venta), 0) as total_ventas
        FROM ventas v
        WHERE v.usuario_id = %s
        AND v.fecha_venta >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY DATE(v.fecha_venta)
        ORDER BY fecha DESC
    """, (usuario_id,))
    ventas_por_dia = cursor.fetchall()
    
    # Agregar día de semana en Python
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    for venta in ventas_por_dia:
        from datetime import datetime
        fecha_obj = datetime.strptime(str(venta['fecha']), '%Y-%m-%d')
        venta['dia_semana'] = dias_semana[fecha_obj.weekday()]
    
    # 9. Productos próximos a vencer
    cursor.execute("""
        SELECT 
            p.id,
            p.codigo,
            p.nombre,
            p.lote,
            p.stock_actual,
            p.fecha_vencimiento,
            c.nombre as categoria_nombre,
            DATEDIFF(p.fecha_vencimiento, CURDATE()) as dias_para_vencer
        FROM productos p
        INNER JOIN categorias c ON p.categoria_id = c.id
        WHERE p.fecha_vencimiento IS NOT NULL
        AND p.fecha_vencimiento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
        AND p.activo = 1
        ORDER BY p.fecha_vencimiento ASC
        LIMIT 10
    """)
    productos_por_vencer = cursor.fetchall()
    
    # 10. Resumen de ventas por tipo
    cursor.execute("""
        SELECT 
            dv.tipo_detalle,
            COUNT(DISTINCT dv.venta_id) as num_ventas,
            COUNT(*) as total_items,
            SUM(dv.subtotal) as total_ingresos
        FROM detalles_venta dv
        INNER JOIN ventas v ON dv.venta_id = v.id
        WHERE v.usuario_id = %s
        AND v.fecha_venta >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY dv.tipo_detalle
    """, (usuario_id,))
    resumen_tipos = cursor.fetchall()
    
    cursor.close()
    
    return render_template('vendedor/dashboard.html',
                          nombre_vendedor=nombre_vendedor,
                          ventas_hoy=ventas_hoy,
                          ventas_semana=ventas_semana,
                          ventas_mes=ventas_mes,
                          ultimas_ventas=ultimas_ventas,
                          productos_bajo_stock=productos_bajo_stock,
                          productos_menos_vendidos=productos_menos_vendidos,
                          productos_mas_vendidos=productos_mas_vendidos,
                          ventas_por_dia=ventas_por_dia,
                          productos_por_vencer=productos_por_vencer,
                          resumen_tipos=resumen_tipos)
    

@app.route('/vendedor/buscar-productos', methods=['GET'])
@login_required
def buscar_productos():
    cursor = mysql.connection.cursor(DictCursor)
    
    # Obtener parámetros de búsqueda
    buscar = request.args.get('buscar', '').strip()
    categoria = request.args.get('categoria', '')
    incluir_sin_stock = request.args.get('incluir_sin_stock', '').lower() == 'true'
    
    # Query base
    query = '''
        SELECT 
            p.id, 
            p.codigo, 
            p.nombre, 
            p.descripcion,
            p.presentacion,
            p.principio_activo,
            p.precio_venta, 
            p.stock_actual,
            p.stock_minimo,
            p.lote,
            p.fecha_vencimiento,
            c.nombre as categoria_nombre,
            um.nombre as unidad_medida,
            um.abreviatura as unidad_abreviatura
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN unidades_medida um ON p.unidad_base_id = um.id
        WHERE p.activo = TRUE
    '''
    params = []
    
    # Filtros
    if not incluir_sin_stock:
        query += ' AND p.stock_actual > 0'
    
    if buscar:
        query += ' AND (p.nombre LIKE %s OR p.codigo LIKE %s OR p.principio_activo LIKE %s)'
        like_param = f'%{buscar}%'
        params.extend([like_param, like_param, like_param])
    
    if categoria and categoria.isdigit():
        query += ' AND p.categoria_id = %s'
        params.append(int(categoria))
    
    query += ' ORDER BY p.nombre LIMIT 50'
    
    try:
        cursor.execute(query, params)
        productos = cursor.fetchall()
    except Exception as e:
        print(f"Error en la consulta: {e}")
        productos = []
    
    # Procesar productos
    productos_procesados = []
    for producto in productos:
        producto_dict = dict(producto)
        
        # Formatear fecha
        if producto_dict.get('fecha_vencimiento'):
            producto_dict['fecha_vencimiento'] = producto_dict['fecha_vencimiento'].strftime('%Y-%m-%d')
        
        # Estado del stock
        if producto_dict['stock_actual'] <= 0:
            producto_dict['estado_stock'] = 'agotado'
        elif producto_dict['stock_actual'] <= producto_dict['stock_minimo']:
            producto_dict['estado_stock'] = 'bajo'
        else:
            producto_dict['estado_stock'] = 'normal'
        
        # Presentación completa
        presentacion_parts = []
        if producto_dict.get('presentacion'):
            presentacion_parts.append(producto_dict['presentacion'])
        if producto_dict.get('unidad_medida'):
            presentacion_parts.append(f"({producto_dict['unidad_medida']})")
        
        producto_dict['presentacion_completa'] = ' '.join(presentacion_parts) if presentacion_parts else 'Sin presentación'
        producto_dict['precio_venta'] = float(producto_dict['precio_venta']) if producto_dict.get('precio_venta') else 0
        
        productos_procesados.append(producto_dict)
    
    cursor.close()
    
    # Si es petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'productos': productos_procesados,
            'total': len(productos_procesados),
            'filtros': {
                'buscar': buscar,
                'categoria': categoria,
                'incluir_sin_stock': incluir_sin_stock
            }
        })
    
    # Si es petición normal, obtener categorías y renderizar template
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute('SELECT id, nombre FROM categorias WHERE activo = TRUE ORDER BY nombre')
    categorias = cursor.fetchall()
    cursor.close()
    
    return render_template('vendedor/buscar_productos.html',
                         productos=productos_procesados,
                         categorias=categorias,
                         total=len(productos_procesados),
                         filtros={
                             'buscar': buscar,
                             'categoria': categoria,
                             'incluir_sin_stock': incluir_sin_stock
                         })


@app.route('/api/categorias', methods=['GET'])
@login_required
def api_categorias():
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute('SELECT id, nombre FROM categorias WHERE activo = TRUE ORDER BY nombre')
    categorias = cursor.fetchall()
    cursor.close()
    return jsonify(categorias)

# ========================
# GESTIÓN DE VENTAS
# ========================

@app.context_processor
def utility_processor():
    return dict(now=datetime.now)

@app.route('/ventas/visualizar', methods=['GET'])
@admin_required
def visualizar_ventas():
    cursor = mysql.connection.cursor(DictCursor)
    
    try:
        # Obtener parámetros de filtro
        filtro = request.args.get('filtro', 'dia')
        fecha_inicio = request.args.get('fecha_inicio', '')
        fecha_fin = request.args.get('fecha_fin', '')
        
        # ============================================
        # VALIDACIÓN PARA FILTRO PERSONALIZADO
        # ============================================
        if filtro == 'personalizado':
            if not fecha_inicio or not fecha_fin:
                flash('Debe proporcionar fecha inicio y fecha fin para el filtro personalizado', 'warning')
                return redirect(url_for('visualizar_ventas', filtro='dia'))
        
        # ============================================
        # 1. CONSTRUIR CONSULTA DE VENTAS - CORREGIDA
        # ============================================
        # IMPORTANTE: Eliminado v.tipo_venta que no existe en la tabla
        query_ventas = '''
            SELECT v.*, u.nombre as usuario_nombre
            FROM ventas v
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            WHERE 1=1
        '''
        params_ventas = []
        
        # Aplicar filtros de fecha
        if filtro == 'dia':
            query_ventas += " AND DATE(v.fecha_venta) = CURDATE()"
        elif filtro == 'semana':
            query_ventas += " AND YEARWEEK(v.fecha_venta) = YEARWEEK(CURDATE())"
        elif filtro == 'mes':
            query_ventas += " AND MONTH(v.fecha_venta) = MONTH(CURDATE()) AND YEAR(v.fecha_venta) = YEAR(CURDATE())"
        elif filtro == 'personalizado' and fecha_inicio and fecha_fin:
            query_ventas += " AND DATE(v.fecha_venta) BETWEEN %s AND %s"
            params_ventas.extend([fecha_inicio, fecha_fin])
        
        query_ventas += " ORDER BY v.fecha_venta DESC, v.fecha_creacion DESC"
        
        # Ejecutar consulta de ventas
        cursor.execute(query_ventas, params_ventas)
        ventas = cursor.fetchall()
        
        # ============================================
        # 2. CONSTRUIR WHERE CLAUSE PARA TOTALES
        # ============================================
        where_totales = ""
        params_totales = []
        
        if filtro == 'dia':
            where_totales = " WHERE DATE(fecha_venta) = CURDATE()"
        elif filtro == 'semana':
            where_totales = " WHERE YEARWEEK(fecha_venta) = YEARWEEK(CURDATE())"
        elif filtro == 'mes':
            where_totales = " WHERE MONTH(fecha_venta) = MONTH(CURDATE()) AND YEAR(fecha_venta) = YEAR(CURDATE())"
        elif filtro == 'personalizado' and fecha_inicio and fecha_fin:
            where_totales = " WHERE DATE(fecha_venta) BETWEEN %s AND %s"
            params_totales = [fecha_inicio, fecha_fin]
        
        # ============================================
        # 3. CALCULAR TOTALES DEL PERÍODO
        # ============================================
        query_totales = f'''
            SELECT 
                COUNT(*) as total_ventas,
                IFNULL(SUM(total_venta), 0) as suma_total,
                IFNULL(SUM(efectivo), 0) as suma_efectivo,
                IFNULL(AVG(total_venta), 0) as promedio_venta,
                IFNULL(SUM(cambio), 0) as total_cambio
            FROM ventas v
            {where_totales}
        '''
        
        if params_totales:
            cursor.execute(query_totales, params_totales)
        else:
            cursor.execute(query_totales)
        
        resumen = cursor.fetchone()
        
        # Si no hay resultados, crear diccionario con valores por defecto
        if not resumen:
            resumen = {
                'total_ventas': 0,
                'suma_total': 0,
                'suma_efectivo': 0,
                'promedio_venta': 0,
                'total_cambio': 0
            }
        
        # ============================================
        # 4. OBTENER PRODUCTOS MÁS VENDIDOS
        # ============================================
        query_productos = '''
            SELECT 
                p.nombre, 
                IFNULL(SUM(dv.cantidad), 0) as total_vendido, 
                IFNULL(SUM(dv.subtotal), 0) as total_recaudado,
                COUNT(DISTINCT v.id) as ventas_incluidas
            FROM detalles_venta dv
            INNER JOIN ventas v ON dv.venta_id = v.id
            INNER JOIN productos p ON dv.referencia_id = p.id
            WHERE dv.tipo_detalle = 'producto'
        '''
        
        params_productos = []
        
        # Agregar condiciones de fecha
        if filtro == 'dia':
            query_productos += " AND DATE(v.fecha_venta) = CURDATE()"
        elif filtro == 'semana':
            query_productos += " AND YEARWEEK(v.fecha_venta) = YEARWEEK(CURDATE())"
        elif filtro == 'mes':
            query_productos += " AND MONTH(v.fecha_venta) = MONTH(CURDATE()) AND YEAR(v.fecha_venta) = YEAR(CURDATE())"
        elif filtro == 'personalizado' and fecha_inicio and fecha_fin:
            query_productos += " AND DATE(v.fecha_venta) BETWEEN %s AND %s"
            params_productos = [fecha_inicio, fecha_fin]
        
        query_productos += '''
            GROUP BY p.id, p.nombre
            ORDER BY total_vendido DESC
            LIMIT 10
        '''
        
        # Ejecutar consulta de productos
        cursor.execute(query_productos, params_productos)
        productos_vendidos = cursor.fetchall()
        
        cursor.close()
        
        return render_template('admin/visualizar_ventas.html', 
                             ventas=ventas,
                             resumen=resumen,
                             productos_vendidos=productos_vendidos,
                             filtro_actual=filtro,
                             fecha_inicio=fecha_inicio,
                             fecha_fin=fecha_fin)
    
    except Exception as e:
        cursor.close()
        flash(f'Error al visualizar ventas: {str(e)}', 'danger')
        return render_template('admin/visualizar_ventas.html', 
                             ventas=[],
                             resumen={
                                 'total_ventas': 0,
                                 'suma_total': 0,
                                 'suma_efectivo': 0,
                                 'promedio_venta': 0,
                                 'total_cambio': 0
                             },
                             productos_vendidos=[],
                             filtro_actual=filtro,
                             fecha_inicio=fecha_inicio,
                             fecha_fin=fecha_fin)

@app.route('/ventas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_venta():
    cursor = mysql.connection.cursor(DictCursor)
    
    if request.method == 'POST':
        try:
            # Iniciar transacción
            cursor.execute("START TRANSACTION")
            
            # Obtener datos de la venta
            items = json.loads(request.form.get('items', '[]'))
            efectivo = float(request.form.get('efectivo', 0))
            total_venta = float(request.form.get('total_venta', 0))
            
            # Validaciones básicas
            if not items:
                raise ValueError("No hay items en la venta")
            
            if efectivo < total_venta:
                raise ValueError("El efectivo es insuficiente")
            
            # Calcular cambio
            cambio = efectivo - total_venta
            
            # ============================================
            # CORREGIDO: Eliminado tipo_venta del INSERT
            # ============================================
            cursor.execute('''
                INSERT INTO ventas (usuario_id, fecha_venta, total_venta, efectivo, cambio)
                VALUES (%s, CURDATE(), %s, %s, %s)
            ''', (session['usuario_id'], total_venta, efectivo, cambio))
            
            venta_id = cursor.lastrowid
            
            # Procesar cada item
            for item in items:
                # Insertar detalle de venta
                cursor.execute('''
                    INSERT INTO detalles_venta 
                    (venta_id, tipo_detalle, referencia_id, cantidad, unidad_id, precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (
                    venta_id,
                    item['tipo_detalle'],
                    item['referencia_id'],
                    item.get('cantidad', 1),
                    item.get('unidad_id'),
                    item['precio_unitario'],
                    item['subtotal']
                ))
                
                # Si es producto, actualizar stock
                if item['tipo_detalle'] == 'producto':
                    # Verificar stock actual
                    cursor.execute('SELECT stock_actual, nombre FROM productos WHERE id = %s', 
                                 (item['referencia_id'],))
                    producto = cursor.fetchone()
                    
                    if not producto:
                        raise ValueError(f"Producto no encontrado")
                    
                    if producto['stock_actual'] < item['cantidad']:
                        raise ValueError(f"Stock insuficiente para {producto['nombre']}. Disponible: {producto['stock_actual']}")
                    
                    # Actualizar stock
                    nuevo_stock = producto['stock_actual'] - item['cantidad']
                    cursor.execute('''
                        UPDATE productos 
                        SET stock_actual = %s 
                        WHERE id = %s
                    ''', (nuevo_stock, item['referencia_id']))
                    
                    # Registrar movimiento de inventario
                    cursor.execute('''
                        INSERT INTO movimientos_inventario 
                        (producto_id, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, 
                         referencia_tipo, referencia_id, usuario_id, observaciones)
                        VALUES (%s, 'salida', %s, %s, %s, 'venta', %s, %s, %s)
                    ''', (
                        item['referencia_id'],
                        item['cantidad'],
                        producto['stock_actual'],
                        nuevo_stock,
                        venta_id,
                        session['usuario_id'],
                        f"Venta #{venta_id}"
                    ))
            
            # Confirmar transacción
            mysql.connection.commit()
            
            return jsonify({
                'success': True,
                'message': 'Venta registrada exitosamente',
                'venta_id': venta_id,
                'cambio': cambio
                # Eliminado 'tipo_venta' del JSON response
            })
            
        except ValueError as e:
            mysql.connection.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({'success': False, 'message': f'Error al procesar la venta: {str(e)}'}), 500
        finally:
            cursor.close()
    
    # GET: Mostrar formulario de venta
    try:
        # Obtener productos activos con stock
        cursor.execute('''
            SELECT p.*, c.nombre as categoria_nombre, u.abreviatura as unidad_abrev
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
            WHERE p.activo = 1 AND p.stock_actual > 0
            ORDER BY p.nombre
        ''')
        productos = cursor.fetchall()
        
        # Obtener variaciones de productos
        for producto in productos:
            cursor.execute('''
                SELECT v.*, u.abreviatura as unidad_abrev, u.nombre as unidad_nombre
                FROM variaciones_producto v
                JOIN unidades_medida u ON v.unidad_id = u.id
                WHERE v.producto_id = %s AND v.activo = 1
            ''', (producto['id'],))
            producto['variaciones'] = cursor.fetchall()
        
        # Obtener servicios activos
        cursor.execute('''
            SELECT s.*, t.nombre as tipo_nombre
            FROM servicios s
            INNER JOIN tipos_servicio t ON s.tipo_servicio_id = t.id
            WHERE s.activo = 1 
            ORDER BY t.nombre, s.nombre
        ''')
        servicios = cursor.fetchall()
        
        # Obtener combos activos
        cursor.execute('''
            SELECT c.*, 
                   (SELECT COUNT(*) FROM detalles_combo WHERE combo_id = c.id) as total_productos
            FROM combos c
            WHERE c.activo = 1
            ORDER BY c.nombre
        ''')
        combos = cursor.fetchall()
        
        cursor.close()
        
        return render_template('admin/punto_venta.html',
                             productos=productos,
                             servicios=servicios,
                             combos=combos)
    
    except Exception as e:
        cursor.close()
        flash(f'Error al cargar datos: {str(e)}', 'error')
        return render_template('admin/punto_venta.html',
                             productos=[],
                             servicios=[],
                             combos=[])

@app.route('/ventas/<int:venta_id>', methods=['GET'])
@login_required
def detalle_venta(venta_id):
    cursor = mysql.connection.cursor(DictCursor)
    
    try:
        # ============================================
        # 1. OBTENER INFORMACIÓN DE LA VENTA - CORREGIDO
        # ============================================
        cursor.execute('''
            SELECT v.*, u.nombre as usuario_nombre, u.email as usuario_email, u.rol as usuario_rol
            FROM ventas v
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            WHERE v.id = %s
        ''', (venta_id,))
        
        venta = cursor.fetchone()
        
        if not venta:
            cursor.close()
            flash('Venta no encontrada', 'danger')
            return redirect(url_for('visualizar_ventas'))
        
        # ============================================
        # 2. OBTENER DETALLES DE LA VENTA
        # ============================================
        cursor.execute('''
            SELECT 
                dv.*,
                -- Nombre del item según su tipo
                CASE 
                    WHEN dv.tipo_detalle = 'producto' THEN p.nombre
                    WHEN dv.tipo_detalle = 'servicio' THEN s.nombre
                    WHEN dv.tipo_detalle = 'combo' THEN c.nombre
                    ELSE 'Desconocido'
                END as nombre_item,
                -- Presentación solo para productos
                CASE 
                    WHEN dv.tipo_detalle = 'producto' THEN p.presentacion
                    ELSE NULL
                END as presentacion,
                -- Unidad de medida
                u.abreviatura as unidad_abrev,
                u.nombre as unidad_nombre,
                -- Información adicional
                dv.tipo_detalle as tipo_item,
                CASE
                    WHEN dv.tipo_detalle = 'producto' THEN p.id
                    WHEN dv.tipo_detalle = 'servicio' THEN s.id
                    WHEN dv.tipo_detalle = 'combo' THEN c.id
                END as item_id,
                -- Estado del item
                CASE
                    WHEN dv.tipo_detalle = 'producto' AND p.id IS NULL THEN 'Producto no disponible'
                    WHEN dv.tipo_detalle = 'servicio' AND s.id IS NULL THEN 'Servicio no disponible'
                    WHEN dv.tipo_detalle = 'combo' AND c.id IS NULL THEN 'Combo no disponible'
                    ELSE 'Disponible'
                END as estado_item,
                -- Precio unitario formateado para la vista
                FORMAT(dv.precio_unitario, 2) as precio_unitario_formato,
                -- Subtotal formateado para la vista
                FORMAT(dv.subtotal, 2) as subtotal_formato
            FROM detalles_venta dv
            LEFT JOIN productos p ON dv.tipo_detalle = 'producto' AND dv.referencia_id = p.id
            LEFT JOIN servicios s ON dv.tipo_detalle = 'servicio' AND dv.referencia_id = s.id
            LEFT JOIN combos c ON dv.tipo_detalle = 'combo' AND dv.referencia_id = c.id
            LEFT JOIN unidades_medida u ON dv.unidad_id = u.id
            WHERE dv.venta_id = %s
            ORDER BY 
                CASE dv.tipo_detalle
                    WHEN 'producto' THEN 1
                    WHEN 'servicio' THEN 2
                    WHEN 'combo' THEN 3
                    ELSE 4
                END,
                dv.id
        ''', (venta_id,))
        
        detalles = cursor.fetchall()
        
        # ============================================
        # 3. CALCULAR RESUMEN DE LA VENTA
        # ============================================
        resumen_detalle = {
            'total_items': len(detalles),
            'total_productos': sum(1 for d in detalles if d['tipo_detalle'] == 'producto'),
            'total_servicios': sum(1 for d in detalles if d['tipo_detalle'] == 'servicio'),
            'total_combos': sum(1 for d in detalles if d['tipo_detalle'] == 'combo'),
            'subtotal': sum(float(d['subtotal']) for d in detalles),
            'items_no_disponibles': sum(1 for d in detalles if 'no disponible' in d['estado_item'].lower())
        }
        
        # ============================================
        # 4. VERIFICAR CONSISTENCIA DE TOTALES
        # ============================================
        if abs(float(resumen_detalle['subtotal']) - float(venta['total_venta'])) > 0.01:
            # Registrar inconsistencia (opcional)
            print(f"ADVERTENCIA: Venta {venta_id} - Total calculado ({resumen_detalle['subtotal']}) != Total registrado ({venta['total_venta']})")
            
            # Ajustar el subtotal para que coincida con el total de la venta
            resumen_detalle['subtotal'] = float(venta['total_venta'])
        
        cursor.close()
        
        return render_template('admin/detalle_venta.html', 
                             venta=venta, 
                             detalles=detalles,
                             resumen_detalle=resumen_detalle)
    
    except Exception as e:
        cursor.close()
        print(f"Error en detalle_venta ({venta_id}): {str(e)}")
        flash('Error al cargar el detalle de la venta', 'danger')
        return redirect(url_for('visualizar_ventas'))

@app.route('/api/productos/disponibles', methods=['GET'])
@login_required
def api_productos_disponibles():
    """API para obtener productos disponibles para la venta"""
    cursor = mysql.connection.cursor(DictCursor)
    try:
        cursor.execute('''
            SELECT p.id, p.codigo, p.nombre, p.descripcion, 
                   p.precio_venta, p.stock_actual,
                   p.presentacion, p.lote, p.fecha_vencimiento,
                   c.nombre as categoria_nombre,
                   u.id as unidad_id, u.nombre as unidad_nombre, 
                   u.abreviatura as unidad_abrev
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
            WHERE p.activo = 1 AND p.stock_actual > 0
            ORDER BY p.nombre
        ''')
        productos = cursor.fetchall()
        
        # Obtener variaciones para cada producto
        for producto in productos:
            cursor.execute('''
                SELECT v.*, u.nombre as unidad_nombre, u.abreviatura as unidad_abrev
                FROM variaciones_producto v
                JOIN unidades_medida u ON v.unidad_id = u.id
                WHERE v.producto_id = %s AND v.activo = 1
            ''', (producto['id'],))
            producto['variaciones'] = cursor.fetchall()
        
        return jsonify(productos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/api/combos/disponibles', methods=['GET'])
@login_required
def api_combos_disponibles():
    """API para obtener combos disponibles"""
    cursor = mysql.connection.cursor(DictCursor)
    try:
        cursor.execute('''
            SELECT c.*, 
                   COUNT(dc.id) as total_productos,
                   CASE 
                       WHEN EXISTS (
                           SELECT 1 FROM detalles_combo dc2 
                           JOIN productos p ON dc2.producto_id = p.id 
                           WHERE dc2.combo_id = c.id AND p.stock_actual < dc2.cantidad
                       ) THEN 0
                       ELSE 1
                   END as disponible
            FROM combos c
            LEFT JOIN detalles_combo dc ON c.id = dc.combo_id
            WHERE c.activo = 1
            GROUP BY c.id
            ORDER BY c.nombre
        ''')
        combos = cursor.fetchall()
        return jsonify(combos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/api/servicios/disponibles', methods=['GET'])
@login_required
def api_servicios_disponibles():
    """API para obtener servicios disponibles"""
    cursor = mysql.connection.cursor(DictCursor)
    try:
        cursor.execute('''
            SELECT 
                s.id, 
                s.nombre, 
                s.descripcion, 
                s.precio,
                s.tipo_servicio_id,
                t.nombre as tipo_nombre
            FROM servicios s
            INNER JOIN tipos_servicio t ON s.tipo_servicio_id = t.id
            WHERE s.activo = 1 
            ORDER BY t.nombre, s.nombre
        ''')
        servicios = cursor.fetchall()
        
        # Convertir Decimal a float para JSON
        for servicio in servicios:
            if 'precio' in servicio and servicio['precio'] is not None:
                servicio['precio'] = float(servicio['precio'])
        
        return jsonify(servicios)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

# ========================
# GESTIÓN DE SERVICIOS
# ========================

@app.route('/tipos-servicio')
@login_required
def ver_tipos_servicio():
    """Vista para gestionar tipos de servicio"""
    cursor = mysql.connection.cursor(DictCursor)
    try:
        # Verificar si debemos mostrar inactivos
        mostrar_inactivos = request.args.get('mostrar_inactivos', False)
        
        if mostrar_inactivos:
            cursor.execute('''
                SELECT id, nombre, descripcion, activo 
                FROM tipos_servicio 
                ORDER BY activo DESC, nombre
            ''')
        else:
            cursor.execute('''
                SELECT id, nombre, descripcion, activo 
                FROM tipos_servicio 
                WHERE activo = 1
                ORDER BY nombre
            ''')
        
        tipos = cursor.fetchall()
        
        return render_template('admin/tipos_servicio.html', 
                             tipos=tipos,
                             mostrando_inactivos=mostrar_inactivos)
    except Exception as e:
        flash(f'Error al cargar tipos de servicio: {str(e)}', 'error')
        return render_template('admin/tipos_servicio.html', tipos=[])
    finally:
        cursor.close()

@app.route('/servicios')
@login_required
def ver_servicios():
    """Vista para gestionar servicios"""
    cursor = mysql.connection.cursor(DictCursor)
    try:
        # Obtener tipos activos para el filtro y selects
        cursor.execute('''
            SELECT id, nombre, descripcion, activo
            FROM tipos_servicio 
            WHERE activo = 1 
            ORDER BY nombre
        ''')
        tipos_activos = cursor.fetchall()
        
        # Obtener servicios (con filtro opcional)
        tipo_filtro = request.args.get('tipo', type=int)
        mostrar_inactivos = request.args.get('mostrar_inactivos', False)
        
        query = '''
            SELECT s.id, s.nombre, s.descripcion, s.precio, s.activo, 
                   s.tipo_servicio_id, t.nombre as tipo_nombre,
                   t.descripcion as tipo_descripcion, t.activo as tipo_activo
            FROM servicios s
            INNER JOIN tipos_servicio t ON s.tipo_servicio_id = t.id
            WHERE 1=1
        '''
        params = []
        
        if tipo_filtro:
            query += ' AND s.tipo_servicio_id = %s'
            params.append(tipo_filtro)
        
        if not mostrar_inactivos:
            query += ' AND s.activo = 1'
        
        query += ' ORDER BY t.nombre, s.nombre'
        
        cursor.execute(query, params)
        servicios = cursor.fetchall()
        
        # Obtener tipos para el modal de creación/edición
        cursor.execute('''
            SELECT id, nombre, descripcion, activo
            FROM tipos_servicio 
            WHERE activo = 1 
            ORDER BY nombre
        ''')
        tipos_para_modal = cursor.fetchall()
        
        return render_template('admin/servicios.html', 
                             servicios=servicios, 
                             tipos_activos=tipos_activos,
                             tipos_para_modal=tipos_para_modal,
                             tipo_seleccionado=tipo_filtro,
                             mostrando_inactivos=mostrar_inactivos)
    except Exception as e:
        flash(f'Error al cargar servicios: {str(e)}', 'error')
        return render_template('admin/servicios.html', 
                             servicios=[], 
                             tipos_activos=[],
                             tipos_para_modal=[])
    finally:
        cursor.close()


# ============================================
# RUTAS API EXISTENTES (TIPOS DE SERVICIO)
# ============================================

@app.route('/api/tipos-servicio', methods=['GET'])
@login_required
def api_listar_tipos_servicio():
    """Obtener todos los tipos de servicio"""
    cursor = mysql.connection.cursor(DictCursor)
    try:
        cursor.execute('''
            SELECT id, nombre, descripcion, activo 
            FROM tipos_servicio 
            ORDER BY nombre
        ''')
        tipos = cursor.fetchall()
        return jsonify(tipos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/api/tipos-servicio/activos', methods=['GET'])
@login_required
def api_tipos_servicio_activos():
    """Obtener solo tipos de servicio activos"""
    cursor = mysql.connection.cursor(DictCursor)
    try:
        cursor.execute('''
            SELECT id, nombre, descripcion 
            FROM tipos_servicio 
            WHERE activo = 1 
            ORDER BY nombre
        ''')
        tipos = cursor.fetchall()
        return jsonify(tipos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/api/tipos-servicio', methods=['POST'])
@login_required
def api_crear_tipo_servicio():
    """Crear un nuevo tipo de servicio"""
    data = request.get_json()
    
    if not data or not data.get('nombre'):
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    cursor = mysql.connection.cursor(DictCursor)
    try:
        cursor.execute('''
            INSERT INTO tipos_servicio (nombre, descripcion)
            VALUES (%s, %s)
        ''', (data['nombre'], data.get('descripcion')))
        mysql.connection.commit()
        
        return jsonify({
            'mensaje': 'Tipo de servicio creado exitosamente',
            'id': cursor.lastrowid
        }), 201
    except MySQLdb.IntegrityError:
        return jsonify({'error': 'Ya existe un tipo de servicio con ese nombre'}), 400
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/api/tipos-servicio/<int:id>', methods=['PUT'])
@login_required
def api_editar_tipo_servicio(id):
    """Editar un tipo de servicio existente"""
    data = request.get_json()
    
    if not data or not data.get('nombre'):
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    cursor = mysql.connection.cursor(DictCursor)
    try:
        cursor.execute('''
            UPDATE tipos_servicio 
            SET nombre = %s, descripcion = %s
            WHERE id = %s
        ''', (data['nombre'], data.get('descripcion'), id))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Tipo de servicio no encontrado'}), 404
            
        mysql.connection.commit()
        return jsonify({'mensaje': 'Tipo de servicio actualizado exitosamente'})
    except MySQLdb.IntegrityError:
        return jsonify({'error': 'Ya existe un tipo de servicio con ese nombre'}), 400
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/api/tipos-servicio/<int:id>/estado', methods=['PUT'])
@login_required
def api_cambiar_estado_tipo_servicio(id):
    """Activar o desactivar un tipo de servicio"""
    data = request.get_json()
    
    if 'activo' not in data:
        return jsonify({'error': 'El campo activo es requerido'}), 400
    
    cursor = mysql.connection.cursor(DictCursor)
    try:
        # Verificar si hay servicios asociados antes de desactivar
        if data['activo'] == 0:
            cursor.execute('''
                SELECT COUNT(*) as total 
                FROM servicios 
                WHERE tipo_servicio_id = %s AND activo = 1
            ''', (id,))
            resultado = cursor.fetchone()
            
            if resultado['total'] > 0:
                return jsonify({
                    'error': 'No se puede desactivar el tipo porque tiene servicios activos asociados'
                }), 400
        
        cursor.execute('''
            UPDATE tipos_servicio 
            SET activo = %s
            WHERE id = %s
        ''', (data['activo'], id))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Tipo de servicio no encontrado'}), 404
            
        mysql.connection.commit()
        estado = "activado" if data['activo'] == 1 else "desactivado"
        return jsonify({'mensaje': f'Tipo de servicio {estado} exitosamente'})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

# ============================================
# RUTAS API (SERVICIOS)
# ============================================

@app.route('/api/servicios', methods=['GET'])
@login_required
def api_listar_servicios():
    """Obtener todos los servicios con información del tipo"""
    cursor = mysql.connection.cursor(DictCursor)
    try:
        cursor.execute('''
            SELECT s.id, s.nombre, s.descripcion, s.precio, s.activo, 
                   s.tipo_servicio_id, t.nombre as tipo_nombre
            FROM servicios s
            INNER JOIN tipos_servicio t ON s.tipo_servicio_id = t.id
            ORDER BY t.nombre, s.nombre
        ''')
        servicios = cursor.fetchall()
        return jsonify(servicios)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/api/servicios/activos', methods=['GET'])
@login_required
def api_servicios_activos():
    """Obtener servicios activos (tu ruta original mejorada)"""
    cursor = mysql.connection.cursor(DictCursor)
    try:
        cursor.execute('''
            SELECT s.id, s.nombre, s.descripcion, s.precio, 
                   t.nombre as tipo, s.tipo_servicio_id
            FROM servicios s
            INNER JOIN tipos_servicio t ON s.tipo_servicio_id = t.id
            WHERE s.activo = 1 AND t.activo = 1
            ORDER BY t.nombre, s.nombre
        ''')
        servicios = cursor.fetchall()
        return jsonify(servicios)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/api/servicios/tipo/<int:tipo_id>', methods=['GET'])
@login_required
def api_servicios_por_tipo(tipo_id):
    """Obtener servicios por tipo de servicio"""
    cursor = mysql.connection.cursor(DictCursor)
    try:
        cursor.execute('''
            SELECT id, nombre, descripcion, precio, activo
            FROM servicios 
            WHERE tipo_servicio_id = %s
            ORDER BY nombre
        ''', (tipo_id,))
        servicios = cursor.fetchall()
        return jsonify(servicios)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/api/servicios', methods=['POST'])
@login_required
def api_crear_servicio():
    """Crear un nuevo servicio"""
    data = request.get_json()
    
    # Validaciones
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400
    
    campos_requeridos = ['nombre', 'precio', 'tipo_servicio_id']
    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({'error': f'El campo {campo} es requerido'}), 400
    
    try:
        precio = float(data['precio'])
        if precio < 0:
            return jsonify({'error': 'El precio no puede ser negativo'}), 400
    except ValueError:
        return jsonify({'error': 'El precio debe ser un número válido'}), 400
    
    cursor = mysql.connection.cursor(DictCursor)
    try:
        # Verificar que el tipo de servicio existe y está activo
        cursor.execute('SELECT activo FROM tipos_servicio WHERE id = %s', (data['tipo_servicio_id'],))
        tipo = cursor.fetchone()
        
        if not tipo:
            return jsonify({'error': 'El tipo de servicio no existe'}), 400
        if not tipo['activo']:
            return jsonify({'error': 'No se puede crear un servicio en un tipo de servicio inactivo'}), 400
        
        cursor.execute('''
            INSERT INTO servicios (nombre, descripcion, precio, tipo_servicio_id)
            VALUES (%s, %s, %s, %s)
        ''', (data['nombre'], data.get('descripcion'), precio, data['tipo_servicio_id']))
        mysql.connection.commit()
        
        return jsonify({
            'mensaje': 'Servicio creado exitosamente',
            'id': cursor.lastrowid
        }), 201
    except MySQLdb.IntegrityError:
        return jsonify({'error': 'Ya existe un servicio con ese nombre'}), 400
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/api/servicios/<int:id>', methods=['PUT'])
@login_required
def api_editar_servicio(id):
    """Editar un servicio existente"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400
    
    campos_requeridos = ['nombre', 'precio', 'tipo_servicio_id']
    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({'error': f'El campo {campo} es requerido'}), 400
    
    try:
        precio = float(data['precio'])
        if precio < 0:
            return jsonify({'error': 'El precio no puede ser negativo'}), 400
    except ValueError:
        return jsonify({'error': 'El precio debe ser un número válido'}), 400
    
    cursor = mysql.connection.cursor(DictCursor)
    try:
        # Verificar que el tipo de servicio existe y está activo
        cursor.execute('SELECT activo FROM tipos_servicio WHERE id = %s', (data['tipo_servicio_id'],))
        tipo = cursor.fetchone()
        
        if not tipo:
            return jsonify({'error': 'El tipo de servicio no existe'}), 400
        if not tipo['activo']:
            return jsonify({'error': 'No se puede asignar un servicio a un tipo de servicio inactivo'}), 400
        
        cursor.execute('''
            UPDATE servicios 
            SET nombre = %s, descripcion = %s, precio = %s, tipo_servicio_id = %s
            WHERE id = %s
        ''', (data['nombre'], data.get('descripcion'), precio, data['tipo_servicio_id'], id))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Servicio no encontrado'}), 404
            
        mysql.connection.commit()
        return jsonify({'mensaje': 'Servicio actualizado exitosamente'})
    except MySQLdb.IntegrityError:
        return jsonify({'error': 'Ya existe un servicio con ese nombre'}), 400
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/api/servicios/<int:id>/estado', methods=['PUT'])
@login_required
def api_cambiar_estado_servicio(id):
    """Activar o desactivar un servicio"""
    data = request.get_json()
    
    if 'activo' not in data:
        return jsonify({'error': 'El campo activo es requerido'}), 400
    
    cursor = mysql.connection.cursor(DictCursor)
    try:
        cursor.execute('''
            UPDATE servicios 
            SET activo = %s
            WHERE id = %s
        ''', (data['activo'], id))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Servicio no encontrado'}), 404
            
        mysql.connection.commit()
        estado = "activado" if data['activo'] == 1 else "desactivado"
        return jsonify({'mensaje': f'Servicio {estado} exitosamente'})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

# ========================
# GESTIÓN DE COMBOS
# ========================
@app.route('/combos')
@admin_required
def listado_combos():
    """Vista para listar todos los combos activos"""
    cursor = mysql.connection.cursor(DictCursor)
    
    cursor.execute('''
        SELECT c.*, 
               COUNT(dc.id) as total_productos,
               COALESCE(SUM(p.precio_costo * dc.cantidad), 0) as costo_total
        FROM combos c
        LEFT JOIN detalles_combo dc ON c.id = dc.combo_id
        LEFT JOIN productos p ON dc.producto_id = p.id
        WHERE c.activo = 1
        GROUP BY c.id
        ORDER BY c.nombre
    ''')
    combos = cursor.fetchall()
    
    # Calcular márgenes
    for combo in combos:
        combo['margen'] = float(combo['precio_combo']) - float(combo['costo_total'])
        combo['porcentaje_margen'] = (combo['margen'] / float(combo['precio_combo']) * 100) if float(combo['precio_combo']) > 0 else 0
    
    cursor.close()
    
    return render_template('admin/combos.html', combos=combos)


@app.route('/combos/nuevo', methods=['GET', 'POST'])
@admin_required
def combo_nuevo():
    """Vista para crear un nuevo combo"""
    cursor = mysql.connection.cursor(DictCursor)
    
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion', '')
            precio_combo = request.form.get('precio_combo')
            
            # Validaciones básicas
            if not nombre or not precio_combo:
                flash('Nombre y precio son requeridos', 'error')
                return redirect(url_for('combo_nuevo'))
            
            # Insertar combo
            cursor.execute('''
                INSERT INTO combos (nombre, descripcion, precio_combo)
                VALUES (%s, %s, %s)
            ''', (nombre, descripcion, precio_combo))
            
            combo_id = cursor.lastrowid
            
            # Procesar productos
            productos_ids = request.form.getlist('productos[]')
            cantidades = request.form.getlist('cantidades[]')
            unidades_ids = request.form.getlist('unidades[]')
            
            stock_insuficiente = False
            productos_sin_stock = []
            
            for i in range(len(productos_ids)):
                if productos_ids[i] and cantidades[i] and unidades_ids[i]:
                    # Verificar stock
                    cursor.execute('SELECT stock_actual, nombre FROM productos WHERE id = %s', (productos_ids[i],))
                    producto = cursor.fetchone()
                    
                    if producto:
                        cantidad_requerida = float(cantidades[i])
                        if cantidad_requerida > float(producto['stock_actual']):
                            stock_insuficiente = True
                            productos_sin_stock.append(producto['nombre'])
                    
                    # Insertar detalle
                    cursor.execute('''
                        INSERT INTO detalles_combo (combo_id, producto_id, cantidad, unidad_id)
                        VALUES (%s, %s, %s, %s)
                    ''', (combo_id, productos_ids[i], cantidades[i], unidades_ids[i]))
            
            mysql.connection.commit()
            
            if stock_insuficiente:
                productos_str = ', '.join(productos_sin_stock)
                flash(f'Combo creado pero hay stock insuficiente para: {productos_str}', 'warning')
            else:
                flash('Combo creado exitosamente', 'success')
                
            return redirect(url_for('listado_combos'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al crear el combo: {str(e)}', 'error')
            return redirect(url_for('combo_nuevo'))
        finally:
            cursor.close()
    
    # GET - mostrar formulario
    cursor.execute('''
        SELECT p.id, p.codigo, p.nombre, p.descripcion,
               p.precio_costo, p.precio_venta, p.stock_actual,
               p.unidad_base_id, p.activo,
               u.nombre as unidad_nombre, u.abreviatura as unidad_abreviatura
        FROM productos p
        LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
        WHERE p.activo = 1
        ORDER BY p.nombre
    ''')
    productos = cursor.fetchall()
    
    cursor.execute('SELECT id, nombre, abreviatura FROM unidades_medida ORDER BY nombre')
    unidades_medida = cursor.fetchall()
    
    cursor.close()
    
    return render_template('admin/combos.html', 
                         productos=productos, 
                         unidades_medida=unidades_medida,
                         combo=None)


@app.route('/combos/<int:combo_id>/editar', methods=['GET', 'POST'])
@admin_required
def combo_editar(combo_id):
    """Vista para editar un combo existente"""
    cursor = mysql.connection.cursor(DictCursor)
    
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion', '')
            precio_combo = request.form.get('precio_combo')
            
            if not nombre or not precio_combo:
                flash('Nombre y precio son requeridos', 'error')
                return redirect(url_for('combo_editar', combo_id=combo_id))
            
            # Actualizar combo
            cursor.execute('''
                UPDATE combos 
                SET nombre = %s, descripcion = %s, precio_combo = %s
                WHERE id = %s AND activo = 1
            ''', (nombre, descripcion, precio_combo, combo_id))
            
            # Eliminar detalles antiguos
            cursor.execute('DELETE FROM detalles_combo WHERE combo_id = %s', (combo_id,))
            
            # Insertar nuevos detalles
            productos_ids = request.form.getlist('productos[]')
            cantidades = request.form.getlist('cantidades[]')
            unidades_ids = request.form.getlist('unidades[]')
            
            stock_insuficiente = False
            productos_sin_stock = []
            
            for i in range(len(productos_ids)):
                if productos_ids[i] and cantidades[i] and unidades_ids[i]:
                    # Verificar stock
                    cursor.execute('SELECT stock_actual, nombre FROM productos WHERE id = %s', (productos_ids[i],))
                    producto = cursor.fetchone()
                    
                    if producto:
                        cantidad_requerida = float(cantidades[i])
                        if cantidad_requerida > float(producto['stock_actual']):
                            stock_insuficiente = True
                            productos_sin_stock.append(producto['nombre'])
                    
                    # Insertar detalle
                    cursor.execute('''
                        INSERT INTO detalles_combo (combo_id, producto_id, cantidad, unidad_id)
                        VALUES (%s, %s, %s, %s)
                    ''', (combo_id, productos_ids[i], cantidades[i], unidades_ids[i]))
            
            mysql.connection.commit()
            
            if stock_insuficiente:
                productos_str = ', '.join(productos_sin_stock)
                flash(f'Combo actualizado pero hay stock insuficiente para: {productos_str}', 'warning')
            else:
                flash('Combo actualizado exitosamente', 'success')
                
            return redirect(url_for('listado_combos'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al actualizar el combo: {str(e)}', 'error')
            return redirect(url_for('combo_editar', combo_id=combo_id))
        finally:
            cursor.close()
    
    # GET - mostrar formulario con datos
    cursor.execute('SELECT * FROM combos WHERE id = %s AND activo = 1', (combo_id,))
    combo = cursor.fetchone()
    
    if not combo:
        cursor.close()
        flash('Combo no encontrado', 'error')
        return redirect(url_for('listado_combos'))
    
    # Obtener detalles del combo con precios actuales
    cursor.execute('''
        SELECT dc.*, p.nombre as producto_nombre, p.codigo,
               p.precio_costo, p.precio_venta, p.stock_actual,
               u.nombre as unidad_nombre, u.abreviatura as unidad_abreviatura
        FROM detalles_combo dc
        JOIN productos p ON dc.producto_id = p.id
        LEFT JOIN unidades_medida u ON dc.unidad_id = u.id
        WHERE dc.combo_id = %s
    ''', (combo_id,))
    combo['detalles'] = cursor.fetchall()
    
    # Productos activos para el select
    cursor.execute('''
        SELECT p.id, p.codigo, p.nombre, p.descripcion,
               p.precio_costo, p.precio_venta, p.stock_actual,
               p.unidad_base_id, p.activo,
               u.nombre as unidad_nombre, u.abreviatura as unidad_abreviatura
        FROM productos p
        LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
        WHERE p.activo = 1
        ORDER BY p.nombre
    ''')
    productos = cursor.fetchall()
    
    # Unidades de medida
    cursor.execute('SELECT id, nombre, abreviatura FROM unidades_medida ORDER BY nombre')
    unidades_medida = cursor.fetchall()
    
    cursor.close()
    
    return render_template('admin/combos.html', 
                         combo=combo,
                         productos=productos, 
                         unidades_medida=unidades_medida)


@app.route('/combos/<int:combo_id>/eliminar', methods=['POST'])
@admin_required
def combo_eliminar(combo_id):
    """Ruta para desactivar un combo"""
    cursor = mysql.connection.cursor(DictCursor)
    
    try:
        cursor.execute('UPDATE combos SET activo = 0 WHERE id = %s', (combo_id,))
        mysql.connection.commit()
        flash('Combo desactivado correctamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al desactivar el combo: {str(e)}', 'error')
    finally:
        cursor.close()
    
    return redirect(url_for('listado_combos'))

# ============================================
# API RUTAS (SOLO LAS ESENCIALES)
# ============================================

@app.route('/api/combos', methods=['GET', 'POST'])
@admin_required
def api_combos():
    """API para listar y crear combos"""
    cursor = mysql.connection.cursor(DictCursor)
    
    if request.method == 'GET':
        cursor.execute('SELECT * FROM combos WHERE activo = 1 ORDER BY nombre')
        combos = cursor.fetchall()
        
        for combo in combos:
            cursor.execute('''
                SELECT dc.*, p.nombre as producto_nombre, p.precio_costo,
                       u.nombre as unidad_nombre, u.abreviatura
                FROM detalles_combo dc
                LEFT JOIN productos p ON dc.producto_id = p.id
                LEFT JOIN unidades_medida u ON dc.unidad_id = u.id
                WHERE dc.combo_id = %s
            ''', (combo['id'],))
            combo['detalles'] = cursor.fetchall()
            
            # Calcular costo total
            costo_total = 0
            for detalle in combo['detalles']:
                if detalle.get('precio_costo'):
                    costo_total += float(detalle['precio_costo']) * float(detalle['cantidad'])
            combo['costo_total'] = round(costo_total, 2)
        
        cursor.close()
        return jsonify(combos)
    
    elif request.method == 'POST':
        data = request.get_json()
        
        try:
            if not data.get('nombre') or not data.get('precio_combo'):
                return jsonify({'error': 'Nombre y precio son requeridos'}), 400
            
            if not data.get('detalles') or len(data['detalles']) == 0:
                return jsonify({'error': 'El combo debe tener al menos un producto'}), 400
            
            cursor.execute('''
                INSERT INTO combos (nombre, descripcion, precio_combo, activo)
                VALUES (%s, %s, %s, 1)
            ''', (
                data['nombre'],
                data.get('descripcion', ''),
                data['precio_combo']
            ))
            
            combo_id = cursor.lastrowid
            
            for detalle in data['detalles']:
                cursor.execute('SELECT id FROM productos WHERE id = %s', (detalle['producto_id'],))
                if not cursor.fetchone():
                    raise Exception(f"Producto ID {detalle['producto_id']} no existe")
                
                cursor.execute('''
                    INSERT INTO detalles_combo (combo_id, producto_id, cantidad, unidad_id)
                    VALUES (%s, %s, %s, %s)
                ''', (
                    combo_id,
                    detalle['producto_id'],
                    detalle['cantidad'],
                    detalle['unidad_id']
                ))
            
            mysql.connection.commit()
            cursor.close()
            
            return jsonify({'success': True, 'combo_id': combo_id})
            
        except Exception as e:
            mysql.connection.rollback()
            cursor.close()
            return jsonify({'error': str(e)}), 500


@app.route('/api/combos/<int:combo_id>', methods=['GET', 'PUT'])
@admin_required
def api_combo_detail(combo_id):
    """API para obtener o actualizar un combo específico"""
    cursor = mysql.connection.cursor(DictCursor)
    
    cursor.execute('SELECT * FROM combos WHERE id = %s', (combo_id,))
    combo = cursor.fetchone()
    
    if not combo:
        cursor.close()
        return jsonify({'error': 'Combo no encontrado'}), 404
    
    if request.method == 'GET':
        cursor.execute('''
            SELECT dc.*, p.nombre as producto_nombre, p.codigo, p.precio_costo,
                   u.nombre as unidad_nombre, u.abreviatura
            FROM detalles_combo dc
            LEFT JOIN productos p ON dc.producto_id = p.id
            LEFT JOIN unidades_medida u ON dc.unidad_id = u.id
            WHERE dc.combo_id = %s
        ''', (combo_id,))
        combo['detalles'] = cursor.fetchall()
        
        costo_total = 0
        for detalle in combo['detalles']:
            if detalle.get('precio_costo'):
                costo_total += float(detalle['precio_costo']) * float(detalle['cantidad'])
        combo['costo_total'] = round(costo_total, 2)
        
        cursor.close()
        return jsonify(combo)
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        try:
            if not data.get('nombre') or not data.get('precio_combo'):
                return jsonify({'error': 'Nombre y precio son requeridos'}), 400
            
            if not data.get('detalles') or len(data['detalles']) == 0:
                return jsonify({'error': 'El combo debe tener al menos un producto'}), 400
            
            cursor.execute('''
                UPDATE combos 
                SET nombre = %s, descripcion = %s, precio_combo = %s
                WHERE id = %s
            ''', (
                data['nombre'],
                data.get('descripcion', ''),
                data['precio_combo'],
                combo_id
            ))
            
            cursor.execute('DELETE FROM detalles_combo WHERE combo_id = %s', (combo_id,))
            
            for detalle in data['detalles']:
                cursor.execute('SELECT id FROM productos WHERE id = %s', (detalle['producto_id'],))
                if not cursor.fetchone():
                    raise Exception(f"Producto ID {detalle['producto_id']} no existe")
                
                cursor.execute('''
                    INSERT INTO detalles_combo (combo_id, producto_id, cantidad, unidad_id)
                    VALUES (%s, %s, %s, %s)
                ''', (
                    combo_id,
                    detalle['producto_id'],
                    detalle['cantidad'],
                    detalle['unidad_id']
                ))
            
            mysql.connection.commit()
            cursor.close()
            
            return jsonify({'success': True, 'message': 'Combo actualizado correctamente'})
            
        except Exception as e:
            mysql.connection.rollback()
            cursor.close()
            return jsonify({'error': str(e)}), 500


@app.route('/api/combos/productos/disponibles', methods=['GET'])
@admin_required
def api_combos_productos_disponibles():
    """API para obtener productos disponibles para combos"""
    cursor = mysql.connection.cursor(DictCursor)
    
    cursor.execute('''
        SELECT p.id, p.nombre, p.codigo, 
               p.precio_costo, p.precio_venta,
               p.stock_actual, 
               p.unidad_base_id,
               u.nombre as unidad_nombre,
               u.id as unidad_id,
               u.abreviatura as unidad_abreviatura
        FROM productos p
        LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
        WHERE p.activo = 1 AND p.stock_actual > 0
        ORDER BY p.nombre
    ''')
    
    productos = cursor.fetchall()
    
    for producto in productos:
        producto['precio_costo'] = float(producto['precio_costo'])
        producto['precio_venta'] = float(producto['precio_venta'])
    
    cursor.close()
    return jsonify(productos)


@app.route('/api/combos/calcular-costo', methods=['POST'])
@admin_required
def api_calcular_costo():
    """API para calcular costo total de productos seleccionados"""
    data = request.get_json()
    detalles = data.get('detalles', [])
    
    if not detalles:
        return jsonify({'costo_total': 0})
    
    cursor = mysql.connection.cursor(DictCursor)
    costo_total = 0
    
    for detalle in detalles:
        cursor.execute('SELECT precio_costo FROM productos WHERE id = %s', (detalle['producto_id'],))
        producto = cursor.fetchone()
        if producto:
            costo_total += float(producto['precio_costo']) * float(detalle['cantidad'])
    
    cursor.close()
    return jsonify({'costo_total': round(costo_total, 2)})

# ===========================
# MOVIMIENTOS DE INVENTARIOS
# ===========================






# ========================
# REPORTES
# ========================

@app.route('/api/reportes/ganancia', methods=['GET'])
@admin_required
def reporte_ganancia():
    cursor = mysql.connection.cursor(DictCursor)
    
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    
    query = '''
        SELECT 
            v.id,
            v.numero_comprobante,
            v.total_venta,
            SUM(dc.cantidad * p.precio_costo) as costo_total,
            (v.total_venta - SUM(dc.cantidad * p.precio_costo)) as ganancia
        FROM ventas v
        LEFT JOIN detalles_venta dv ON v.id = dv.venta_id
        LEFT JOIN productos p ON dv.referencia_id = p.id
        WHERE 1=1
    '''
    params = []
    
    if fecha_inicio:
        query += ' AND DATE(v.fecha_venta) >= %s'
        params.append(fecha_inicio)
    
    if fecha_fin:
        query += ' AND DATE(v.fecha_venta) <= %s'
        params.append(fecha_fin)
    
    query += ' GROUP BY v.id ORDER BY v.fecha_venta DESC'
    
    cursor.execute(query, params)
    ventas = cursor.fetchall()
    
    cursor.execute('''
        SELECT 
            SUM(stock_actual * precio_costo) as inversion_total
        FROM productos WHERE activo = TRUE
    ''')
    inversion = cursor.fetchone()
    
    cursor.close()
    
    ganancia_total = sum([v['ganancia'] if v['ganancia'] else 0 for v in ventas])
    
    return jsonify({
        'ventas': ventas,
        'ganancia_total': ganancia_total,
        'inversion_total': inversion['inversion_total']
    })

# ========================
# Usuarios
# ========================

@app.route('/usuarios', methods=['GET'])
@admin_required
def ver_usuarios():
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute('SELECT * FROM usuarios ORDER BY nombre')
    usuarios = cursor.fetchall()
    cursor.close()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@app.route('/usuarios/crear', methods=['POST'])
@admin_required
def crear_usuario():
    cursor = mysql.connection.cursor(DictCursor)
    
    nombre = request.form['nombre']
    email = request.form['email']
    contrasena = generate_password_hash(request.form['contrasena'])
    rol = request.form['rol']
    
    try:
        cursor.execute(
            'INSERT INTO usuarios (nombre, email, contrasena, rol) VALUES (%s, %s, %s, %s)',
            (nombre, email, contrasena, rol)
        )
        mysql.connection.commit()
        flash('Usuario creado exitosamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash('Error: El email ya está registrado', 'error')
    finally:
        cursor.close()
    
    return redirect(url_for('ver_usuarios'))

@app.route('/usuarios/editar', methods=['POST'])
@admin_required
def editar_usuario():
    cursor = mysql.connection.cursor(DictCursor)
    
    usuario_id = request.form['usuario_id']
    nombre = request.form['nombre']
    email = request.form['email']
    rol = request.form['rol']
    contrasena = request.form.get('contrasena', '')
    
    try:
        if contrasena:
            contrasena_hash = generate_password_hash(contrasena)
            cursor.execute(
                'UPDATE usuarios SET nombre = %s, email = %s, contrasena = %s, rol = %s WHERE id = %s',
                (nombre, email, contrasena_hash, rol, usuario_id)
            )
        else:
            cursor.execute(
                'UPDATE usuarios SET nombre = %s, email = %s, rol = %s WHERE id = %s',
                (nombre, email, rol, usuario_id)
            )
        
        mysql.connection.commit()
        flash('Usuario actualizado exitosamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash('Error: El email ya está registrado por otro usuario', 'error')
    finally:
        cursor.close()
    
    return redirect(url_for('ver_usuarios'))

@app.route('/usuarios/toggle-estado', methods=['POST'])
@admin_required
def toggle_estado_usuario():
    cursor = mysql.connection.cursor(DictCursor)
    
    usuario_id = request.form['usuario_id']
    
    # Evitar que un admin se desactive a sí mismo
    if int(usuario_id) == session['usuario_id']:
        flash('No puedes cambiar el estado de tu propio usuario', 'error')
        cursor.close()
        return redirect(url_for('ver_usuarios'))
    
    cursor.execute('SELECT activo, nombre FROM usuarios WHERE id = %s', (usuario_id,))
    usuario = cursor.fetchone()
    
    if usuario:
        nuevo_estado = not usuario['activo']
        cursor.execute('UPDATE usuarios SET activo = %s WHERE id = %s', (nuevo_estado, usuario_id))
        mysql.connection.commit()
        
        estado = 'activado' if nuevo_estado else 'desactivado'
        flash(f'Usuario {usuario["nombre"]} {estado} exitosamente', 'success')
    else:
        flash('Usuario no encontrado', 'error')
    
    cursor.close()
    return redirect(url_for('ver_usuarios'))

@app.route('/favicon.ico')
def favicon():
    return '', 204

# Manejo de errores
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
