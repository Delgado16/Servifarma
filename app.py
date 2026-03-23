try:
    import pymysql
    pymysql.install_as_MySQLdb()
    print("PyMySQL configurado correctamente")
except ImportError:
    print("PyMySQL no está instalado. Ejecuta: pip install pymysql")

from decimal import Decimal
import MySQLdb
from flask import Flask, flash, json, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
from MySQLdb.cursors import DictCursor
from functools import wraps
import hashlib
import os
import traceback
from dotenv import load_dotenv
from datetime import date, datetime
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
    # Importar datetime y timedelta al inicio de la función
    from datetime import datetime, timedelta
    
    cursor = mysql.connection.cursor(DictCursor)
    
    # ============================================
    # ESTADÍSTICAS GENERALES DE PRODUCTOS
    # ============================================
    cursor.execute('''
        SELECT 
            COUNT(*) as total_productos,
            IFNULL(SUM(stock_actual), 0) as stock_total,
            IFNULL(SUM(stock_actual * precio_costo), 0) as inversion_total,
            COUNT(CASE WHEN stock_actual <= stock_minimo THEN 1 END) as productos_bajo_stock,
            IFNULL(SUM(precio_venta * stock_actual), 0) as valor_venta_total
        FROM productos 
        WHERE activo = TRUE
    ''')
    stats = cursor.fetchone()
    
    # ============================================
    # VENTAS DEL DÍA ACTUAL
    # ============================================
    cursor.execute('''
        SELECT 
            COUNT(*) as ventas_hoy,
            IFNULL(SUM(total_venta), 0) as total_hoy,
            IFNULL(AVG(total_venta), 0) as ticket_promedio_hoy
        FROM ventas 
        WHERE DATE(fecha_venta) = CURDATE()
    ''')
    ventas_hoy = cursor.fetchone()
    
    # ============================================
    # VENTAS ÚLTIMOS 30 DÍAS
    # ============================================
    cursor.execute('''
        SELECT 
            COUNT(*) as total_ventas,
            IFNULL(SUM(total_venta), 0) as ganancia_total,
            IFNULL(AVG(total_venta), 0) as ticket_promedio
        FROM ventas 
        WHERE DATE(fecha_venta) >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    ''')
    ventas_stats = cursor.fetchone()
    
    # ============================================
    # TOP 5 PRODUCTOS MÁS VENDIDOS - SIN GROUP BY
    # ============================================
    cursor.execute('''
        SELECT DISTINCT
            p.id,
            p.nombre,
            p.codigo,
            p.stock_actual,
            c.nombre as categoria,
            (SELECT IFNULL(SUM(dv.cantidad), 0) 
             FROM detalles_venta dv 
             INNER JOIN ventas v ON dv.venta_id = v.id
             WHERE dv.referencia_id = p.id 
             AND dv.tipo_detalle = 'producto'
             AND v.fecha_venta >= DATE_SUB(NOW(), INTERVAL 30 DAY)) as total_vendido,
            (SELECT IFNULL(SUM(dv.subtotal), 0) 
             FROM detalles_venta dv 
             INNER JOIN ventas v ON dv.venta_id = v.id
             WHERE dv.referencia_id = p.id 
             AND dv.tipo_detalle = 'producto'
             AND v.fecha_venta >= DATE_SUB(NOW(), INTERVAL 30 DAY)) as total_ingresos
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = TRUE
        HAVING total_vendido > 0
        ORDER BY total_vendido DESC
        LIMIT 5
    ''')
    top_productos = cursor.fetchall()
    
    # ============================================
    # VENTAS POR DÍA (ÚLTIMOS 7 DÍAS) - CONSULTA SIMPLE
    # ============================================
    ventas_diarias = []
    for i in range(7):
        fecha = datetime.now() - timedelta(days=i)
        fecha_str = fecha.strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT 
                COUNT(*) as num_ventas,
                IFNULL(SUM(total_venta), 0) as total
            FROM ventas 
            WHERE DATE(fecha_venta) = %s
        ''', (fecha_str,))
        
        resultado = cursor.fetchone()
        ventas_diarias.append({
            'fecha': fecha_str,
            'fecha_corta': fecha.strftime('%d/%m'),
            'num_ventas': resultado['num_ventas'],
            'total': resultado['total']
        })
    
    # Ordenar por fecha ascendente para el gráfico
    ventas_diarias.reverse()
    
    # ============================================
    # VENTAS POR CATEGORÍA
    # ============================================
    cursor.execute('''
        SELECT 
            c.nombre as categoria,
            COUNT(DISTINCT v.id) as num_ventas,
            IFNULL(SUM(dv.subtotal), 0) as total
        FROM categorias c
        LEFT JOIN productos p ON c.id = p.categoria_id AND p.activo = TRUE
        LEFT JOIN detalles_venta dv ON p.id = dv.referencia_id AND dv.tipo_detalle = 'producto'
        LEFT JOIN ventas v ON dv.venta_id = v.id AND v.fecha_venta >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        WHERE c.activo = TRUE
        GROUP BY c.id, c.nombre
        HAVING total > 0
        ORDER BY total DESC
    ''')
    ventas_categorias = cursor.fetchall()
    
    # ============================================
    # PRODUCTOS CON BAJO STOCK
    # ============================================
    cursor.execute('''
        SELECT 
            p.nombre,
            p.codigo,
            p.stock_actual,
            p.stock_minimo,
            c.nombre as categoria,
            p.fecha_vencimiento,
            DATEDIFF(p.fecha_vencimiento, CURDATE()) as dias_para_vencer
        FROM productos p
        INNER JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = TRUE 
        AND p.stock_actual <= p.stock_minimo
        ORDER BY (p.stock_actual / p.stock_minimo) ASC, p.stock_actual ASC
        LIMIT 10
    ''')
    bajo_stock = cursor.fetchall()
    
    # ============================================
    # ÚLTIMOS MOVIMIENTOS DE INVENTARIO
    # ============================================
    cursor.execute('''
        SELECT 
            mi.tipo_movimiento,
            mi.cantidad,
            p.nombre as producto,
            p.codigo as codigo_producto,
            u.nombre as usuario,
            mi.fecha_movimiento,
            mi.observaciones
        FROM movimientos_inventario mi
        INNER JOIN productos p ON mi.producto_id = p.id
        INNER JOIN usuarios u ON mi.usuario_id = u.id
        ORDER BY mi.fecha_movimiento DESC
        LIMIT 10
    ''')
    ultimos_movimientos_raw = cursor.fetchall()
    
    # Procesar fechas en Python
    ultimos_movimientos = []
    for mov in ultimos_movimientos_raw:
        ultimos_movimientos.append({
            'tipo_movimiento': mov['tipo_movimiento'],
            'cantidad': mov['cantidad'],
            'producto': mov['producto'],
            'codigo_producto': mov['codigo_producto'],
            'usuario': mov['usuario'],
            'fecha': mov['fecha_movimiento'].strftime('%d/%m/%Y %H:%M') if mov['fecha_movimiento'] else '',
            'observaciones': mov['observaciones']
        })
    
    # ============================================
    # ESTADÍSTICAS DE USUARIOS
    # ============================================
    cursor.execute('''
        SELECT 
            COUNT(*) as total_usuarios,
            SUM(CASE WHEN rol = 'admin' THEN 1 ELSE 0 END) as admins,
            SUM(CASE WHEN rol = 'vendedor' THEN 1 ELSE 0 END) as vendedores,
            SUM(CASE WHEN DATE(fecha_creacion) = CURDATE() THEN 1 ELSE 0 END) as usuarios_nuevos_hoy
        FROM usuarios 
        WHERE activo = TRUE
    ''')
    usuarios_stats = cursor.fetchone()
    
    # ============================================
    # PRODUCTOS PRÓXIMOS A VENCERSE
    # ============================================
    cursor.execute('''
        SELECT 
            p.nombre,
            p.codigo,
            p.lote,
            p.fecha_vencimiento,
            p.stock_actual,
            c.nombre as categoria,
            DATEDIFF(p.fecha_vencimiento, CURDATE()) as dias_para_vencer
        FROM productos p
        INNER JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = TRUE 
        AND p.fecha_vencimiento IS NOT NULL
        AND p.fecha_vencimiento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 60 DAY)
        AND p.stock_actual > 0
        ORDER BY p.fecha_vencimiento ASC
    ''')
    proximos_vencer_raw = cursor.fetchall()
    
    # Procesar nivel de urgencia en Python
    proximos_vencer = []
    for prod in proximos_vencer_raw:
        dias = prod['dias_para_vencer']
        if dias <= 15:
            nivel = 'critico'
        elif dias <= 30:
            nivel = 'alerta'
        else:
            nivel = 'normal'
        
        proximos_vencer.append({
            'nombre': prod['nombre'],
            'codigo': prod['codigo'],
            'lote': prod['lote'],
            'fecha_vencimiento': prod['fecha_vencimiento'],
            'stock_actual': prod['stock_actual'],
            'categoria': prod['categoria'],
            'dias_para_vencer': dias,
            'nivel_urgencia': nivel
        })
    
    # ============================================
    # PRODUCTOS VENCIDOS
    # ============================================
    cursor.execute('''
        SELECT 
            p.nombre,
            p.codigo,
            p.lote,
            p.fecha_vencimiento,
            p.stock_actual,
            c.nombre as categoria,
            DATEDIFF(CURDATE(), p.fecha_vencimiento) as dias_vencido
        FROM productos p
        INNER JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = TRUE 
        AND p.fecha_vencimiento < CURDATE()
        AND p.stock_actual > 0
        ORDER BY p.fecha_vencimiento ASC
    ''')
    productos_vencidos = cursor.fetchall()
    
    # ============================================
    # ÚLTIMAS 5 VENTAS
    # ============================================
    cursor.execute('''
        SELECT 
            v.id,
            v.fecha_venta,
            v.total_venta,
            u.nombre as vendedor
        FROM ventas v
        INNER JOIN usuarios u ON v.usuario_id = u.id
        ORDER BY v.fecha_venta DESC
        LIMIT 5
    ''')
    ultimas_ventas_raw = cursor.fetchall()
    
    # Procesar fechas y contar items en Python
    ultimas_ventas = []
    for venta in ultimas_ventas_raw:
        # Contar items de la venta
        cursor.execute('''
            SELECT COUNT(*) as total 
            FROM detalles_venta 
            WHERE venta_id = %s
        ''', (venta['id'],))
        items_count = cursor.fetchone()['total']
        
        ultimas_ventas.append({
            'id': venta['id'],
            'fecha_venta': venta['fecha_venta'],
            'total_venta': venta['total_venta'],
            'vendedor': venta['vendedor'],
            'fecha_formateada': venta['fecha_venta'].strftime('%d/%m/%Y %H:%M') if venta['fecha_venta'] else '',
            'items_vendidos': items_count
        })
    
    # ============================================
    # RESUMEN DE HOY
    # ============================================
    cursor.execute('''
        SELECT 
            COUNT(DISTINCT v.id) as total_ventas_hoy,
            IFNULL(SUM(v.total_venta), 0) as total_ingresos_hoy,
            COUNT(DISTINCT v.usuario_id) as vendedores_activos_hoy
        FROM ventas v
        WHERE DATE(v.fecha_venta) = CURDATE()
    ''')
    resumen_hoy = cursor.fetchone()
    
    # Contar productos vendidos hoy por separado
    cursor.execute('''
        SELECT COUNT(DISTINCT dv.referencia_id) as total
        FROM detalles_venta dv
        INNER JOIN ventas v ON dv.venta_id = v.id
        WHERE DATE(v.fecha_venta) = CURDATE()
        AND dv.tipo_detalle = 'producto'
    ''')
    productos_hoy = cursor.fetchone()
    resumen_hoy['productos_vendidos_hoy'] = productos_hoy['total'] if productos_hoy else 0
    
    cursor.close()
    
    return render_template('admin/dashboard.html', 
                         # Estadísticas generales
                         stats=stats,
                         ventas_hoy=ventas_hoy,
                         ventas_stats=ventas_stats,
                         resumen_hoy=resumen_hoy,
                         
                         # Productos y ventas
                         top_productos=top_productos,
                         ventas_diarias=ventas_diarias,
                         ventas_categorias=ventas_categorias,
                         
                         # Alertas y seguimiento
                         bajo_stock=bajo_stock,
                         proximos_vencer=proximos_vencer,
                         productos_vencidos=productos_vencidos,
                         
                         # Actividad reciente
                         ultimos_movimientos=ultimos_movimientos,
                         ultimas_ventas=ultimas_ventas,
                         
                         # Usuarios
                         usuarios_stats=usuarios_stats,
                         
                         # Fecha actual para el template
                         fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M'))
    
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
    
    cursor.execute('''
        SELECT id, nombre, abreviatura, 
               CASE 
                   WHEN abreviatura IN ('PST', 'TAB', 'CAP', 'ML', 'G', 'UND', 'UN') THEN 'base'
                   ELSE 'derivada'
               END as tipo
        FROM unidades_medida 
        WHERE activo = TRUE 
        ORDER BY tipo, nombre
    ''')
    unidades = cursor.fetchall()
    
    if request.method == 'POST':
        data = request.form
        tipo_producto = data.get('tipo_producto', 'simple')
        
        try:
            # Validaciones básicas
            if not data.get('codigo') or not data.get('nombre'):
                flash('Código y nombre son requeridos', 'error')
                return redirect(url_for('productos'))
            
            # Verificar si el código ya existe
            cursor.execute('SELECT id FROM productos WHERE codigo = %s', (data['codigo'].strip(),))
            if cursor.fetchone():
                flash('El código ya está registrado', 'error')
                return redirect(url_for('productos'))
            
            fecha_vencimiento = None
            if data.get('fecha_vencimiento'):
                fecha_vencimiento = datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d').date()
            
            # ===== PRODUCTO SIMPLE =====
            if tipo_producto == 'simple':
                # Validar campos requeridos con manejo correcto de valores vacíos
                required_fields = ['unidad_base_id', 'precio_costo', 'precio_venta']
                missing_fields = []
                
                for field in required_fields:
                    value = data.get(field, '').strip()
                    if not value:
                        missing_fields.append(field)
                
                if missing_fields:
                    flash(f'Campos requeridos faltantes: {", ".join(missing_fields)}', 'error')
                    return redirect(url_for('productos'))
                
                # Validar que sean números positivos
                try:
                    precio_costo = float(data.get('precio_costo', 0))
                    precio_venta = float(data.get('precio_venta', 0))
                    
                    if precio_costo <= 0:
                        flash('El precio de costo debe ser mayor a 0', 'error')
                        return redirect(url_for('productos'))
                    
                    if precio_venta <= 0:
                        flash('El precio de venta debe ser mayor a 0', 'error')
                        return redirect(url_for('productos'))
                        
                except ValueError:
                    flash('Los precios deben ser números válidos', 'error')
                    return redirect(url_for('productos'))
                
                # Verificar que la unidad base exista (sin restricción de abreviaturas)
                cursor.execute('SELECT id FROM unidades_medida WHERE id = %s', (data.get('unidad_base_id'),))
                if not cursor.fetchone():
                    flash('La unidad base seleccionada no es válida', 'error')
                    return redirect(url_for('productos'))
                
                # Insertar producto
                cursor.execute('''
                    INSERT INTO productos (
                        codigo, nombre, descripcion, categoria_id, 
                        principio_activo, presentacion, tipo_producto, unidad_base_id,
                        precio_costo, porcentaje_ganancia, precio_venta, 
                        stock_actual, stock_minimo, lote, fecha_vencimiento, activo,
                        fecha_creacion
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, NOW())
                ''', (
                    data['codigo'].strip(),
                    data['nombre'].strip(),
                    data.get('descripcion', '').strip() or None,
                    data.get('categoria_id') or None,
                    data.get('principio_activo', '').strip() or None,
                    data.get('presentacion', '').strip() or None,
                    'simple',
                    data.get('unidad_base_id'),
                    float(data.get('precio_costo', 0)),
                    float(data.get('porcentaje_ganancia', 30)) if data.get('porcentaje_ganancia') else 30.00,
                    float(data.get('precio_venta', 0)),
                    int(data.get('stock_actual', 0)) if data.get('stock_actual') else 0,
                    int(data.get('stock_minimo', 5)) if data.get('stock_minimo') else 5,
                    data.get('lote', '').strip() or None,
                    fecha_vencimiento
                ))
                
                producto_id = cursor.lastrowid
                
                # Crear variación para la unidad base
                cursor.execute('''
                    INSERT INTO variaciones_producto 
                    (producto_id, unidad_id, cantidad_equivalente, precio_venta, 
                     precio_costo_equivalente, porcentaje_ganancia, descripcion, 
                     nivel, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                ''', (
                    producto_id, 
                    data.get('unidad_base_id'), 
                    1,  # cantidad_equivalente
                    float(data.get('precio_venta', 0)),
                    float(data.get('precio_costo', 0)),
                    float(data.get('porcentaje_ganancia', 30)) if data.get('porcentaje_ganancia') else 30.00,
                    'Venta por unidad base',
                    4  # nivel 4 para unidad base
                ))
                
                # Si también se configuraron presentaciones adicionales
                presentaciones_unidad = request.form.getlist('presentacion_unidad[]')
                presentaciones_cantidad = request.form.getlist('presentacion_cantidad[]')
                presentaciones_precio = request.form.getlist('presentacion_precio[]')
                presentaciones_desc = request.form.getlist('presentacion_desc[]')
                
                for i in range(len(presentaciones_unidad)):
                    if (presentaciones_unidad[i] and presentaciones_cantidad[i] and 
                        presentaciones_precio[i]):
                        
                        try:
                            cantidad = int(presentaciones_cantidad[i])
                            if cantidad <= 0:
                                continue
                                
                            precio = float(presentaciones_precio[i])
                            unidad_id = int(presentaciones_unidad[i])
                            
                            # Verificar que la unidad exista
                            cursor.execute('SELECT id FROM unidades_medida WHERE id = %s', (unidad_id,))
                            if not cursor.fetchone():
                                continue
                            
                            # Calcular costo equivalente
                            costo_unitario_base = float(data.get('precio_costo', 0))
                            costo_equivalente = costo_unitario_base * cantidad
                            
                            cursor.execute('''
                                INSERT INTO variaciones_producto 
                                (producto_id, unidad_id, cantidad_equivalente, precio_venta,
                                 precio_costo_equivalente, porcentaje_ganancia, descripcion, 
                                 nivel, activo)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                            ''', (
                                producto_id, unidad_id, cantidad, precio,
                                costo_equivalente, 
                                float(data.get('porcentaje_ganancia', 30)) if data.get('porcentaje_ganancia') else 30.00,
                                presentaciones_desc[i] if presentaciones_desc and presentaciones_desc[i] else f'Presentación de {cantidad} unidades',
                                3  # nivel inferior a la unidad base
                            ))
                        except (ValueError, TypeError) as e:
                            print(f"Error en presentación {i}: {e}")
                            continue
            
            # ===== PRODUCTO JERÁRQUICO =====
            else:  # tipo_producto == 'jerarquico'
                # Validar campos requeridos
                required_fields = {
                    'costo_caja': 'Costo de la caja',
                    'sobres_por_caja': 'Cantidad de sobres por caja',
                    'blister_por_sobre': 'Cantidad de blisteres por sobre',
                    'pastillas_por_blister': 'Cantidad de pastillas por blister',
                    'porcentaje_ganancia': 'Porcentaje de ganancia',
                    'stock_inicial_cajas': 'Stock inicial en cajas'
                }
                
                for field, label in required_fields.items():
                    if not data.get(field) or float(data.get(field, 0)) <= 0:
                        flash(f'El campo {label} debe ser mayor a 0', 'error')
                        return redirect(url_for('productos'))
                
                # Obtener IDs de unidades por abreviatura
                cursor.execute('''
                    SELECT 
                        (SELECT id FROM unidades_medida WHERE abreviatura = 'PST') as pastilla_id,
                        (SELECT id FROM unidades_medida WHERE abreviatura = 'BLI') as blister_id,
                        (SELECT id FROM unidades_medida WHERE abreviatura = 'SBR') as sobre_id,
                        (SELECT id FROM unidades_medida WHERE abreviatura = 'CJA') as caja_id
                ''')
                unidades_ids = cursor.fetchone()
                
                if not all(unidades_ids.values()):
                    flash('Error: No están configuradas todas las unidades de medida necesarias', 'error')
                    return redirect(url_for('productos'))
                
                # Calcular total de pastillas por caja
                sobres_por_caja = int(data.get('sobres_por_caja', 0))
                blister_por_sobre = int(data.get('blister_por_sobre', 0))
                pastillas_por_blister = int(data.get('pastillas_por_blister', 0))
                total_pastillas_por_caja = sobres_por_caja * blister_por_sobre * pastillas_por_blister
                
                # Convertir stock de cajas a pastillas (unidad base)
                stock_en_cajas = int(data.get('stock_inicial_cajas', 0))
                stock_en_pastillas = stock_en_cajas * total_pastillas_por_caja
                
                # Calcular costos unitarios
                costo_caja = float(data.get('costo_caja', 0))
                costo_por_pastilla = costo_caja / total_pastillas_por_caja
                costo_por_blister = costo_por_pastilla * pastillas_por_blister
                costo_por_sobre = costo_por_blister * blister_por_sobre
                
                porcentaje = float(data.get('porcentaje_ganancia', 30))
                
                # Calcular precios de venta
                precio_pastilla = costo_por_pastilla * (1 + porcentaje/100)
                precio_blister = costo_por_blister * (1 + porcentaje/100)
                precio_sobre = costo_por_sobre * (1 + porcentaje/100)
                precio_caja = costo_caja * (1 + porcentaje/100)
                
                # Insertar producto (unidad base = PASTILLA)
                cursor.execute('''
                    INSERT INTO productos (
                        codigo, nombre, descripcion, categoria_id, 
                        principio_activo, presentacion, tipo_producto, unidad_base_id,
                        precio_costo, porcentaje_ganancia, precio_venta, 
                        stock_actual, stock_minimo, lote, fecha_vencimiento, activo,
                        fecha_creacion
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, NOW())
                ''', (
                    data['codigo'].strip(),
                    data['nombre'].strip(),
                    data.get('descripcion', '').strip() or None,
                    data.get('categoria_id') or None,
                    data.get('principio_activo', '').strip() or None,
                    data.get('presentacion', '').strip() or None,
                    'jerarquico',
                    unidades_ids['pastilla_id'],
                    costo_por_pastilla,
                    porcentaje,
                    precio_pastilla,
                    stock_en_pastillas,
                    int(data.get('stock_minimo', 5)) * total_pastillas_por_caja,
                    data.get('lote', '').strip() or None,
                    fecha_vencimiento
                ))
                
                producto_id = cursor.lastrowid
                
                # Insertar todas las variaciones (presentaciones)
                # Nivel 4: Pastilla (unidad base)
                cursor.execute('''
                    INSERT INTO variaciones_producto 
                    (producto_id, unidad_id, nivel, cantidad_equivalente, 
                     precio_costo_equivalente, porcentaje_ganancia, precio_venta, 
                     descripcion, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                ''', (
                    producto_id, unidades_ids['pastilla_id'], 4, 1,
                    costo_por_pastilla, porcentaje, precio_pastilla,
                    'Unidad base - Pastilla'
                ))
                
                # Nivel 3: Blister
                cursor.execute('''
                    INSERT INTO variaciones_producto 
                    (producto_id, unidad_id, nivel, cantidad_equivalente,
                     precio_costo_equivalente, porcentaje_ganancia, precio_venta,
                     descripcion, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                ''', (
                    producto_id, unidades_ids['blister_id'], 3,
                    pastillas_por_blister, costo_por_blister, porcentaje, precio_blister,
                    f'Blister de {pastillas_por_blister} pastillas'
                ))
                
                # Nivel 2: Sobre
                cursor.execute('''
                    INSERT INTO variaciones_producto 
                    (producto_id, unidad_id, nivel, cantidad_equivalente,
                     precio_costo_equivalente, porcentaje_ganancia, precio_venta,
                     descripcion, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                ''', (
                    producto_id, unidades_ids['sobre_id'], 2,
                    pastillas_por_blister * blister_por_sobre, 
                    costo_por_sobre, porcentaje, precio_sobre,
                    f'Sobre de {blister_por_sobre} blisteres'
                ))
                
                # Nivel 1: Caja
                cursor.execute('''
                    INSERT INTO variaciones_producto 
                    (producto_id, unidad_id, nivel, cantidad_equivalente,
                     precio_costo_equivalente, porcentaje_ganancia, precio_venta,
                     descripcion, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                ''', (
                    producto_id, unidades_ids['caja_id'], 1,
                    total_pastillas_por_caja, costo_caja, porcentaje, precio_caja,
                    f'Caja de {sobres_por_caja} sobres'
                ))
            
            mysql.connection.commit()
            flash('✅ Producto creado exitosamente', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'❌ Error al crear producto: {str(e)}', 'error')
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            cursor.close()
        
        return redirect(url_for('productos'))
    
    # Método GET - Mostrar lista
    buscar = request.args.get('buscar', '')
    categoria = request.args.get('categoria', '')
    tipo = request.args.get('tipo', '')
    mostrar_inactivos = request.args.get('mostrar_inactivos', '0') == '1'
    
    query = '''
        SELECT 
            p.*, 
            c.nombre as categoria_nombre, 
            u.nombre as unidad_nombre, 
            u.abreviatura,
            -- Estado del stock
            CASE 
                WHEN p.stock_actual <= p.stock_minimo THEN 'bajo'
                WHEN p.fecha_vencimiento IS NOT NULL AND p.fecha_vencimiento <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 'vencimiento'
                ELSE 'normal'
            END as estado_stock,
            -- Total de variaciones
            (SELECT COUNT(*) FROM variaciones_producto WHERE producto_id = p.id) as total_variaciones,
            -- Stock formateado según el tipo de producto
            CASE 
                WHEN p.tipo_producto = 'jerarquico' THEN
                    CONCAT(
                        FLOOR(p.stock_actual / NULLIF((
                            SELECT cantidad_equivalente 
                            FROM variaciones_producto 
                            WHERE producto_id = p.id AND nivel = 1
                            LIMIT 1
                        ), 0)), ' cajas (', p.stock_actual, ' pastillas)'
                    )
                ELSE
                    CONCAT(p.stock_actual, ' ', u.abreviatura)
            END as stock_formateado,
            -- Precios por presentación (para mostrar en tooltip)
            (
                SELECT GROUP_CONCAT(
                    CONCAT(u2.abreviatura, ': C$', v.precio_venta)
                    SEPARATOR ' | '
                )
                FROM variaciones_producto v
                JOIN unidades_medida u2 ON v.unidad_id = u2.id
                WHERE v.producto_id = p.id AND v.activo = TRUE
            ) as precios_presentaciones
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
    
    if tipo:
        query += ' AND p.tipo_producto = %s'
        params.append(tipo)
    
    query += ' ORDER BY p.nombre'
    
    cursor.execute(query, params)
    productos_lista = cursor.fetchall()
    now = datetime.now().date()
    cursor.close()
    
    return render_template('admin/productos.html',
                         productos=productos_lista,
                         categorias=categorias,
                         unidades=unidades,
                         buscar=buscar,
                         categoria_seleccionada=categoria,
                         tipo_seleccionado=tipo,
                         mostrar_inactivos=mostrar_inactivos,
                         now=now)

# ========================
# RUTAS PARA EDICIÓN DE PRODUCTOS
# ========================

@app.route('/productos/<int:producto_id>/editar', methods=['GET'])
@admin_required
def editar_producto_form(producto_id):
    """Muestra el formulario de edición de producto"""
    cursor = mysql.connection.cursor(DictCursor)
    
    try:
        # Obtener el producto
        cursor.execute('''
            SELECT p.*, c.nombre as categoria_nombre, u.nombre as unidad_nombre 
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
            WHERE p.id = %s
        ''', (producto_id,))
        producto = cursor.fetchone()
        
        if not producto:
            flash('Producto no encontrado', 'error')
            return redirect(url_for('productos'))
        
        # Obtener categorías para el formulario
        cursor.execute('SELECT id, nombre FROM categorias WHERE activo = TRUE ORDER BY nombre')
        categorias = cursor.fetchall()
        
        # Obtener unidades de medida
        cursor.execute('''
            SELECT id, nombre, abreviatura 
            FROM unidades_medida 
            WHERE activo = TRUE 
            ORDER BY nombre
        ''')
        unidades = cursor.fetchall()
        
        # Obtener variaciones del producto
        cursor.execute('''
            SELECT v.*, u.nombre as unidad_nombre, u.abreviatura
            FROM variaciones_producto v
            JOIN unidades_medida u ON v.unidad_id = u.id
            WHERE v.producto_id = %s AND v.activo = TRUE
            ORDER BY v.nivel DESC, v.cantidad_equivalente ASC
        ''', (producto_id,))
        variaciones = cursor.fetchall()
        
        cursor.close()
        
        # Convertir valores Decimal a float para la plantilla con manejo de None
        for key in ['precio_costo', 'precio_venta', 'porcentaje_ganancia']:
            if producto.get(key) is not None:
                try:
                    producto[key] = float(producto[key])
                except (TypeError, ValueError):
                    producto[key] = 0.0
            else:
                producto[key] = 0.0
        
        # Inicializar valores jerárquicos con valores por defecto
        producto['costo_caja'] = 0.0
        producto['sobres_por_caja'] = 0
        producto['blister_por_sobre'] = 0
        producto['pastillas_por_blister'] = 0
        
        # Si es jerárquico, extraer datos de estructura
        if producto['tipo_producto'] == 'jerarquico' and variaciones:
            # Buscar variaciones por nivel
            caja_var = next((v for v in variaciones if v['nivel'] == 1), None)
            sobre_var = next((v for v in variaciones if v['nivel'] == 2), None)
            blister_var = next((v for v in variaciones if v['nivel'] == 3), None)
            
            # Procesar caja (nivel 1)
            if caja_var:
                # Convertir precio_costo_equivalente a float
                if caja_var.get('precio_costo_equivalente') is not None:
                    try:
                        producto['costo_caja'] = float(caja_var['precio_costo_equivalente'])
                    except (TypeError, ValueError):
                        producto['costo_caja'] = 0.0
                else:
                    producto['costo_caja'] = 0.0
                
                # Calcular sobres por caja
                if sobre_var and sobre_var.get('cantidad_equivalente'):
                    try:
                        if caja_var.get('cantidad_equivalente') and sobre_var['cantidad_equivalente']:
                            producto['sobres_por_caja'] = int(caja_var['cantidad_equivalente'] / sobre_var['cantidad_equivalente'])
                        else:
                            producto['sobres_por_caja'] = 1
                    except (TypeError, ValueError, ZeroDivisionError):
                        producto['sobres_por_caja'] = 1
                else:
                    producto['sobres_por_caja'] = 1
            
            # Procesar sobre y blister (niveles 2 y 3)
            if sobre_var and blister_var:
                # Calcular blister por sobre
                if blister_var.get('cantidad_equivalente'):
                    try:
                        if sobre_var.get('cantidad_equivalente') and blister_var['cantidad_equivalente']:
                            producto['blister_por_sobre'] = int(sobre_var['cantidad_equivalente'] / blister_var['cantidad_equivalente'])
                        else:
                            producto['blister_por_sobre'] = 1
                    except (TypeError, ValueError, ZeroDivisionError):
                        producto['blister_por_sobre'] = 1
                else:
                    producto['blister_por_sobre'] = 1
            
            # Procesar blister (nivel 3)
            if blister_var:
                if blister_var.get('cantidad_equivalente') is not None:
                    try:
                        producto['pastillas_por_blister'] = int(blister_var['cantidad_equivalente'])
                    except (TypeError, ValueError):
                        producto['pastillas_por_blister'] = 1
                else:
                    producto['pastillas_por_blister'] = 1
        
        # Convertir valores de variaciones a float con manejo de None
        for variacion in variaciones:
            for key in ['precio_costo_equivalente', 'precio_venta', 'porcentaje_ganancia']:
                if variacion.get(key) is not None:
                    try:
                        variacion[key] = float(variacion[key])
                    except (TypeError, ValueError):
                        variacion[key] = 0.0
                else:
                    variacion[key] = 0.0
        
        # Debug: imprimir valores para verificar
        print(f"Editando producto ID: {producto_id}, Tipo: {producto['tipo_producto']}")
        print(f"precio_costo: {producto.get('precio_costo')}")
        print(f"precio_venta: {producto.get('precio_venta')}")
        print(f"porcentaje_ganancia: {producto.get('porcentaje_ganancia')}")
        print(f"costo_caja: {producto.get('costo_caja')}")
        print(f"sobres_por_caja: {producto.get('sobres_por_caja')}")
        print(f"blister_por_sobre: {producto.get('blister_por_sobre')}")
        print(f"pastillas_por_blister: {producto.get('pastillas_por_blister')}")
        
        return render_template('admin/editar_producto.html',
                             producto=producto,
                             categorias=categorias,
                             unidades=unidades,
                             variaciones=variaciones,
                             now=datetime.now().date())
        
    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        flash(f'Error al cargar el producto: {str(e)}', 'error')
        print(f"Error en editar_producto_form: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('productos'))

@app.route('/productos/<int:producto_id>/actualizar', methods=['POST'])
@admin_required
def actualizar_producto(producto_id):
    """Procesa la actualización del producto"""
    cursor = mysql.connection.cursor(DictCursor)
    
    try:
        data = request.form
        
        # Validar campos básicos
        if not data.get('codigo') or not data.get('nombre'):
            flash('Código y nombre son requeridos', 'error')
            return redirect(url_for('editar_producto_form', producto_id=producto_id))
        
        # Verificar si el código ya existe (excluyendo el producto actual)
        cursor.execute('SELECT id FROM productos WHERE codigo = %s AND id != %s', 
                      (data['codigo'].strip(), producto_id))
        if cursor.fetchone():
            flash('El código ya está registrado para otro producto', 'error')
            return redirect(url_for('editar_producto_form', producto_id=producto_id))
        
        # Procesar fecha de vencimiento
        fecha_vencimiento = None
        if data.get('fecha_vencimiento'):
            try:
                fecha_vencimiento = datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d').date()
            except ValueError:
                flash('Formato de fecha inválido', 'error')
                return redirect(url_for('editar_producto_form', producto_id=producto_id))
        
        tipo_producto = data.get('tipo_producto', 'simple')
        activo = 1 if data.get('activo') == 'on' else 0
        
        # ===== ACTUALIZACIÓN PRODUCTO SIMPLE =====
        if tipo_producto == 'simple':
            # Validar campos requeridos
            if not data.get('unidad_base_id'):
                flash('Unidad base requerida', 'error')
                return redirect(url_for('editar_producto_form', producto_id=producto_id))
            
            try:
                precio_costo = float(data.get('precio_costo', 0))
                precio_venta = float(data.get('precio_venta', 0))
                porcentaje = float(data.get('porcentaje_ganancia', 30))
                
                if precio_costo <= 0:
                    flash('El precio de costo debe ser mayor a 0', 'error')
                    return redirect(url_for('editar_producto_form', producto_id=producto_id))
                
                if precio_venta <= 0:
                    flash('El precio de venta debe ser mayor a 0', 'error')
                    return redirect(url_for('editar_producto_form', producto_id=producto_id))
                    
            except ValueError:
                flash('Los precios deben ser números válidos', 'error')
                return redirect(url_for('editar_producto_form', producto_id=producto_id))
            
            # Actualizar producto simple (NO modificar stock_actual)
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
                    porcentaje_ganancia = %s,
                    precio_venta = %s,
                    stock_minimo = %s,
                    lote = %s,
                    fecha_vencimiento = %s,
                    activo = %s
                WHERE id = %s
            ''', (
                data['codigo'].strip(),
                data['nombre'].strip(),
                data.get('descripcion', '').strip() or None,
                data.get('categoria_id') or None,
                data.get('principio_activo', '').strip() or None,
                data.get('presentacion', '').strip() or None,
                data.get('unidad_base_id'),
                precio_costo,
                porcentaje,
                precio_venta,
                int(data.get('stock_minimo', 5)) if data.get('stock_minimo') else 5,
                data.get('lote', '').strip() or None,
                fecha_vencimiento,
                activo,
                producto_id
            ))
            
            # Actualizar variación base (nivel 4)
            cursor.execute('''
                UPDATE variaciones_producto SET
                    precio_venta = %s,
                    precio_costo_equivalente = %s,
                    porcentaje_ganancia = %s
                WHERE producto_id = %s AND nivel = 4
            ''', (
                precio_venta,
                precio_costo,
                porcentaje,
                producto_id
            ))
        
        # ===== ACTUALIZACIÓN PRODUCTO JERÁRQUICO =====
        else:
            try:
                costo_caja = float(data.get('costo_caja', 0))
                porcentaje = float(data.get('porcentaje_ganancia_jer', 30))
                
                if costo_caja <= 0:
                    flash('El costo de la caja debe ser mayor a 0', 'error')
                    return redirect(url_for('editar_producto_form', producto_id=producto_id))
                    
            except ValueError:
                flash('Valores numéricos inválidos', 'error')
                return redirect(url_for('editar_producto_form', producto_id=producto_id))
            
            # Obtener la estructura actual del producto desde variaciones
            cursor.execute('''
                SELECT 
                    (SELECT cantidad_equivalente FROM variaciones_producto 
                     WHERE producto_id = %s AND nivel = 1) as sobres_por_caja,
                    (SELECT cantidad_equivalente / pastillas_por_blister FROM (
                        SELECT cantidad_equivalente as pastillas_por_blister 
                        FROM variaciones_producto 
                        WHERE producto_id = %s AND nivel = 3
                    ) as sub) as blister_por_sobre,
                    (SELECT cantidad_equivalente FROM variaciones_producto 
                     WHERE producto_id = %s AND nivel = 3) as pastillas_por_blister
            ''', (producto_id, producto_id, producto_id))
            
            estructura = cursor.fetchone()
            
            if estructura and estructura['sobres_por_caja'] and estructura['blister_por_sobre'] and estructura['pastillas_por_blister']:
                sobres_por_caja = estructura['sobres_por_caja']
                blister_por_sobre = estructura['blister_por_sobre']
                pastillas_por_blister = estructura['pastillas_por_blister']
            else:
                # Si no se encuentra estructura, usar valores por defecto
                sobres_por_caja = 1
                blister_por_sobre = 1
                pastillas_por_blister = 1
            
            # Obtener IDs de unidades
            cursor.execute('''
                SELECT 
                    (SELECT id FROM unidades_medida WHERE abreviatura = 'PST') as pastilla_id,
                    (SELECT id FROM unidades_medida WHERE abreviatura = 'BLI') as blister_id,
                    (SELECT id FROM unidades_medida WHERE abreviatura = 'SBR') as sobre_id,
                    (SELECT id FROM unidades_medida WHERE abreviatura = 'CJA') as caja_id
            ''')
            unidades_ids = cursor.fetchone()
            
            if not all(unidades_ids.values()):
                flash('Error: No están configuradas todas las unidades de medida necesarias', 'error')
                return redirect(url_for('editar_producto_form', producto_id=producto_id))
            
            # Calcular total de pastillas por caja
            total_pastillas_por_caja = sobres_por_caja * blister_por_sobre * pastillas_por_blister
            
            # Calcular costos
            costo_por_pastilla = costo_caja / total_pastillas_por_caja
            costo_por_blister = costo_por_pastilla * pastillas_por_blister
            costo_por_sobre = costo_por_blister * blister_por_sobre
            
            # Calcular precios
            precio_pastilla = costo_por_pastilla * (1 + porcentaje/100)
            precio_blister = costo_por_blister * (1 + porcentaje/100)
            precio_sobre = costo_por_sobre * (1 + porcentaje/100)
            precio_caja = costo_caja * (1 + porcentaje/100)
            
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
                    porcentaje_ganancia = %s,
                    precio_venta = %s,
                    stock_minimo = %s,
                    lote = %s,
                    fecha_vencimiento = %s,
                    activo = %s
                WHERE id = %s
            ''', (
                data['codigo'].strip(),
                data['nombre'].strip(),
                data.get('descripcion', '').strip() or None,
                data.get('categoria_id') or None,
                data.get('principio_activo', '').strip() or None,
                data.get('presentacion', '').strip() or None,
                unidades_ids['pastilla_id'],
                costo_por_pastilla,
                porcentaje,
                precio_pastilla,
                int(data.get('stock_minimo', 5)) * total_pastillas_por_caja,
                data.get('lote', '').strip() or None,
                fecha_vencimiento,
                activo,
                producto_id
            ))
            
            # Actualizar variaciones
            variaciones_config = [
                {'nivel': 4, 'unidad_id': unidades_ids['pastilla_id'], 
                 'cantidad': 1, 'costo': costo_por_pastilla, 'precio': precio_pastilla,
                 'desc': 'Unidad base - Pastilla'},
                {'nivel': 3, 'unidad_id': unidades_ids['blister_id'], 
                 'cantidad': pastillas_por_blister, 'costo': costo_por_blister, 
                 'precio': precio_blister, 'desc': f'Blister de {pastillas_por_blister} pastillas'},
                {'nivel': 2, 'unidad_id': unidades_ids['sobre_id'], 
                 'cantidad': pastillas_por_blister * blister_por_sobre, 
                 'costo': costo_por_sobre, 'precio': precio_sobre,
                 'desc': f'Sobre de {blister_por_sobre} blisteres'},
                {'nivel': 1, 'unidad_id': unidades_ids['caja_id'], 
                 'cantidad': total_pastillas_por_caja, 'costo': costo_caja, 
                 'precio': precio_caja, 'desc': f'Caja de {sobres_por_caja} sobres'}
            ]
            
            for variacion in variaciones_config:
                cursor.execute('''
                    INSERT INTO variaciones_producto 
                    (producto_id, unidad_id, nivel, cantidad_equivalente,
                     precio_costo_equivalente, porcentaje_ganancia, precio_venta,
                     descripcion, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                    ON DUPLICATE KEY UPDATE
                        nivel = VALUES(nivel),
                        cantidad_equivalente = VALUES(cantidad_equivalente),
                        precio_costo_equivalente = VALUES(precio_costo_equivalente),
                        porcentaje_ganancia = VALUES(porcentaje_ganancia),
                        precio_venta = VALUES(precio_venta),
                        descripcion = VALUES(descripcion),
                        activo = TRUE
                ''', (
                    producto_id, variacion['unidad_id'], variacion['nivel'],
                    variacion['cantidad'], variacion['costo'], porcentaje,
                    variacion['precio'], variacion['desc']
                ))
        
        mysql.connection.commit()
        flash('✅ Producto actualizado exitosamente', 'success')
        return redirect(url_for('productos'))
        
    except Exception as e:
        mysql.connection.rollback()
        flash(f'❌ Error al actualizar el producto: {str(e)}', 'error')
        print(f"Error en actualizar_producto: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('editar_producto_form', producto_id=producto_id))
    finally:
        cursor.close()

# ===== RUTAS PARA CONSULTAR VARIACIONES (MEJORADAS) =====

@app.route('/productos/<int:producto_id>/variaciones', methods=['GET'])
@admin_required
def obtener_variaciones_producto(producto_id):
    """Obtiene todas las variaciones de un producto para usarlas en ventas"""
    cursor = mysql.connection.cursor(DictCursor)
    
    cursor.execute('''
        SELECT 
            v.id,
            v.producto_id,
            v.unidad_id,
            u.nombre as unidad_nombre,
            u.abreviatura,
            v.cantidad_equivalente,
            v.precio_venta,
            v.precio_costo_equivalente,
            v.descripcion,
            v.nivel,
            p.nombre as producto_nombre,
            p.tipo_producto,
            p.stock_actual as stock_base,
            -- Stock disponible en esta presentación
            FLOOR(p.stock_actual / v.cantidad_equivalente) as stock_disponible
        FROM variaciones_producto v
        JOIN unidades_medida u ON v.unidad_id = u.id
        JOIN productos p ON v.producto_id = p.id
        WHERE v.producto_id = %s AND v.activo = TRUE
        ORDER BY v.cantidad_equivalente ASC
    ''', (producto_id,))
    
    variaciones = cursor.fetchall()
    cursor.close()
    
    return jsonify(variaciones)


@app.route('/productos/<int:producto_id>/precios-detalle', methods=['GET'])
@admin_required
def detalle_precios_producto(producto_id):
    """Muestra el detalle de precios de todas las presentaciones"""
    cursor = mysql.connection.cursor(DictCursor)
    
    cursor.execute('''
        SELECT 
            p.nombre as producto,
            p.tipo_producto,
            p.precio_costo as costo_base,
            p.porcentaje_ganancia,
            v.id as variacion_id,
            u.nombre as unidad,
            u.abreviatura,
            v.cantidad_equivalente,
            v.precio_costo_equivalente as costo_unitario,
            v.precio_venta,
            v.precio_venta - v.precio_costo_equivalente as ganancia,
            ROUND(((v.precio_venta - v.precio_costo_equivalente) / NULLIF(v.precio_costo_equivalente, 0) * 100), 2) as margen,
            v.descripcion,
            v.nivel,
            -- Stock en esta presentación
            FLOOR(p.stock_actual / v.cantidad_equivalente) as stock_presentacion
        FROM productos p
        LEFT JOIN variaciones_producto v ON p.id = v.producto_id
        LEFT JOIN unidades_medida u ON v.unidad_id = u.id
        WHERE p.id = %s AND (v.activo = TRUE OR v.activo IS NULL)
        ORDER BY v.cantidad_equivalente ASC
    ''', (producto_id,))
    
    precios = cursor.fetchall()
    cursor.close()
    
    return render_template('admin/detalle_precios.html', precios=precios, producto_id=producto_id)


# ===== NUEVA RUTA: Obtener unidades para presentaciones =====
@app.route('/unidades/presentaciones', methods=['GET'])
@admin_required
def obtener_unidades_presentacion():
    """Obtiene las unidades disponibles para presentaciones (excluye bases)"""
    cursor = mysql.connection.cursor(DictCursor)
    
    cursor.execute('''
        SELECT id, nombre, abreviatura 
        FROM unidades_medida 
        WHERE activo = TRUE 
        AND abreviatura NOT IN ('PST', 'TAB', 'CAP', 'ML', 'G')
        ORDER BY nombre
    ''')
    
    unidades = cursor.fetchall()
    cursor.close()
    
    return jsonify(unidades)


# ===== NUEVA RUTA: Agregar presentación a producto existente =====
@app.route('/productos/<int:producto_id>/agregar-presentacion', methods=['POST'])
@admin_required
def agregar_presentacion_producto(producto_id):
    """Agrega una nueva presentación a un producto existente"""
    cursor = mysql.connection.cursor(DictCursor)
    
    try:
        data = request.json
        
        unidad_id = data.get('unidad_id')
        cantidad = int(data.get('cantidad', 0))
        precio_venta = float(data.get('precio_venta', 0))
        descripcion = data.get('descripcion', '')
        
        if not all([unidad_id, cantidad > 0, precio_venta > 0]):
            return jsonify({'success': False, 'error': 'Datos incompletos'})
        
        # Verificar que no exista ya esta presentación
        cursor.execute('''
            SELECT id FROM variaciones_producto 
            WHERE producto_id = %s AND unidad_id = %s
        ''', (producto_id, unidad_id))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Esta presentación ya existe'})
        
        # Obtener costo base del producto
        cursor.execute('SELECT precio_costo FROM productos WHERE id = %s', (producto_id,))
        producto = cursor.fetchone()
        
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'})
        
        costo_equivalente = producto['precio_costo'] * cantidad
        
        # Insertar nueva presentación
        cursor.execute('''
            INSERT INTO variaciones_producto 
            (producto_id, unidad_id, cantidad_equivalente, precio_venta,
             precio_costo_equivalente, descripcion, activo)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        ''', (producto_id, unidad_id, cantidad, precio_venta, 
              costo_equivalente, descripcion))
        
        mysql.connection.commit()
        return jsonify({'success': True, 'message': 'Presentación agregada'})
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()

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
    
    # Cargar productos con sus presentaciones
    cursor.execute('''
        SELECT 
            p.id, 
            p.nombre,
            p.codigo,
            p.precio_costo,
            p.stock_actual,
            u.abreviatura as unidad_base,
            COUNT(v.id) as num_presentaciones
        FROM productos p
        JOIN unidades_medida u ON p.unidad_base_id = u.id
        LEFT JOIN variaciones_producto v ON p.id = v.producto_id
        WHERE p.activo = 1
        GROUP BY p.id
        ORDER BY p.nombre
    ''')
    productos = cursor.fetchall()
    
    # También cargar unidades de medida para el selector
    cursor.execute('SELECT id, nombre, abreviatura FROM unidades_medida WHERE activo = 1')
    unidades = cursor.fetchall()
    
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
                         unidades=unidades,
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
        
        # Obtener arrays del formulario
        producto_ids = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')
        unidad_ids = request.form.getlist('unidad_id[]')  # ¡NUEVO! Unidad en que se compra
        precios = request.form.getlist('precio_unitario[]')
        
        total_costo = 0
        detalles_validos = []
        
        # Procesar y validar detalles
        for i in range(len(producto_ids)):
            if producto_ids[i] and cantidades[i] and unidad_ids[i] and precios[i]:
                try:
                    cantidad = int(cantidades[i])
                    unidad_id = int(unidad_ids[i])
                    precio = float(precios[i])
                    
                    if cantidad > 0 and precio > 0:
                        subtotal = cantidad * precio
                        total_costo += subtotal
                        
                        # Buscar la equivalencia de esta unidad en el producto
                        cursor.execute('''
                            SELECT cantidad_equivalente 
                            FROM variaciones_producto 
                            WHERE producto_id = %s AND unidad_id = %s AND activo = 1
                        ''', (producto_ids[i], unidad_id))
                        
                        equivalencia = cursor.fetchone()
                        
                        if equivalencia:
                            # Si existe la presentación, calcular unidades base
                            unidades_base_por_unidad = equivalencia['cantidad_equivalente']
                        else:
                            # Si no existe, asumir que es la unidad base (1:1)
                            # Pero deberías crearla automáticamente
                            cursor.execute('''
                                INSERT INTO variaciones_producto 
                                (producto_id, unidad_id, cantidad_equivalente, activo)
                                VALUES (%s, %s, 1, 1)
                            ''', (producto_ids[i], unidad_id))
                            unidades_base_por_unidad = 1
                        
                        unidades_base_recibidas = cantidad * unidades_base_por_unidad
                        
                        detalles_validos.append({
                            'producto_id': producto_ids[i],
                            'cantidad': cantidad,
                            'unidad_id': unidad_id,
                            'precio': precio,
                            'subtotal': subtotal,
                            'unidades_base_recibidas': unidades_base_recibidas
                        })
                except (ValueError, TypeError) as e:
                    print(f"Error en detalle {i}: {e}")
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
            # Insertar detalle de compra (AHORA CON LA UNIDAD CORRECTA)
            cursor.execute('''
                INSERT INTO detalles_compra (
                    compra_id, producto_id, cantidad, 
                    unidad_id, precio_unitario, subtotal
                ) VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                compra_id,
                detalle['producto_id'],
                detalle['cantidad'],
                detalle['unidad_id'],  # ¡YA NO ES 1 FIJO!
                detalle['precio'],
                detalle['subtotal']
            ))
            
            # Obtener stock actual (en unidad base)
            cursor.execute('SELECT stock_actual FROM productos WHERE id = %s', (detalle['producto_id'],))
            result = cursor.fetchone()
            
            if result:
                stock_anterior = result['stock_actual']
                # Actualizar stock con las unidades base recibidas
                stock_nuevo = stock_anterior + detalle['unidades_base_recibidas']
                
                # Actualizar stock
                cursor.execute('''
                    UPDATE productos 
                    SET stock_actual = %s,
                        precio_costo = %s  -- Actualizar costo promedio
                    WHERE id = %s
                ''', (
                    stock_nuevo,
                    detalle['precio'] / detalle['unidades_base_recibidas'],  # Costo por unidad base
                    detalle['producto_id']
                ))
                
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
                    detalle['unidades_base_recibidas'],  # Cantidad en unidad base
                    stock_anterior,
                    stock_nuevo,
                    compra_id,
                    session['usuario_id'],
                    f"Compra #{numero_documento} - {detalle['cantidad']} unidades"
                ))
        
        mysql.connection.commit()
        cursor.close()
        
        flash(f'✅ Compra #{numero_documento} registrada exitosamente!', 'success')
        return redirect(url_for('compras'))
        
    except Exception as e:
        mysql.connection.rollback()
        flash(f'❌ Error al registrar la compra: {str(e)}', 'danger')
        print(f"Error en compra: {str(e)}")  # Para debug
        return redirect(url_for('compras'))

@app.route('/compras/<int:compra_id>/detalle')
@admin_required
def detalle_compra(compra_id):
    cursor = mysql.connection.cursor(DictCursor)
    
    try:
        # Obtener datos de la compra
        cursor.execute('''
            SELECT 
                c.*,
                p.nombre as proveedor_nombre,
                p.telefono as proveedor_telefono,
                p.email as proveedor_email,
                p.direccion as proveedor_direccion,
                u.nombre as usuario_nombre,
                u.email as usuario_email
            FROM compras c
            LEFT JOIN proveedores p ON c.proveedor_id = p.id
            LEFT JOIN usuarios u ON c.usuario_id = u.id
            WHERE c.id = %s
        ''', (compra_id,))
        
        compra = cursor.fetchone()
        
        if not compra:
            flash('Compra no encontrada', 'danger')
            return redirect(url_for('compras'))
        
        # Obtener detalles de la compra con información completa
        cursor.execute('''
            SELECT 
                dc.*,
                pr.codigo as producto_codigo,
                pr.nombre as producto_nombre,
                pr.descripcion as producto_descripcion,
                pr.unidad_base_id,
                ub.nombre as unidad_base_nombre,
                ub.abreviatura as unidad_base_abrev,
                um.nombre as unidad_nombre,
                um.abreviatura as unidad_abreviatura,
                v.cantidad_equivalente
            FROM detalles_compra dc
            JOIN productos pr ON dc.producto_id = pr.id
            LEFT JOIN unidades_medida ub ON pr.unidad_base_id = ub.id
            LEFT JOIN unidades_medida um ON dc.unidad_id = um.id
            LEFT JOIN variaciones_producto v ON v.producto_id = pr.id AND v.unidad_id = dc.unidad_id
            WHERE dc.compra_id = %s
            ORDER BY dc.id ASC
        ''', (compra_id,))
        
        detalles = cursor.fetchall()
        
        # Calcular estadísticas
        subtotal = sum(detalle['subtotal'] for detalle in detalles)
        
        # Calcular total de unidades base recibidas
        total_unidades_base = 0
        for detalle in detalles:
            if detalle['cantidad_equivalente']:
                total_unidades_base += detalle['cantidad'] * detalle['cantidad_equivalente']
        
        cursor.close()
        
        return render_template('admin/detalle_compra.html',
                             compra=compra,
                             detalles=detalles,
                             subtotal=subtotal,
                             total_unidades_base=total_unidades_base,
                             now=datetime.now())
                             
    except Exception as e:
        cursor.close()
        flash(f'Error al cargar el detalle: {str(e)}', 'danger')
        return redirect(url_for('compras'))

# NUEVA RUTA: Obtener presentaciones de un producto
@app.route('/productos/<int:producto_id>/presentaciones')
@admin_required
def obtener_presentaciones_producto(producto_id):
    """Devuelve las presentaciones disponibles para un producto"""
    cursor = mysql.connection.cursor(DictCursor)
    
    # Obtener todas las unidades de medida disponibles
    cursor.execute('SELECT id, nombre, abreviatura FROM unidades_medida ORDER BY nombre')
    todas_unidades = cursor.fetchall()
    
    # Obtener las variaciones del producto
    cursor.execute('''
        SELECT 
            v.id,
            v.unidad_id,
            u.nombre as unidad_nombre,
            u.abreviatura,
            v.cantidad_equivalente,
            v.descripcion,
            p.unidad_base_id
        FROM variaciones_producto v
        JOIN unidades_medida u ON v.unidad_id = u.id
        JOIN productos p ON v.producto_id = p.id
        WHERE v.producto_id = %s AND v.activo = 1
        ORDER BY v.cantidad_equivalente ASC
    ''', (producto_id,))
    
    presentaciones = cursor.fetchall()
    
    # Si no hay presentaciones configuradas, devolver todas las unidades
    # para que el usuario pueda seleccionar (esto ayuda a configurar)
    if not presentaciones:
        cursor.execute('SELECT unidad_base_id FROM productos WHERE id = %s', (producto_id,))
        producto = cursor.fetchone()
        
        # Crear presentaciones por defecto con las unidades más comunes
        presentaciones = []
        for unidad in todas_unidades[:5]:  # Solo las primeras 5 como ejemplo
            presentaciones.append({
                'id': None,
                'unidad_id': unidad['id'],
                'unidad_nombre': unidad['nombre'],
                'abreviatura': unidad['abreviatura'],
                'cantidad_equivalente': 1,
                'descripcion': f'Compra en {unidad["nombre"]}',
                'unidad_base_id': producto['unidad_base_id'] if producto else None
            })
    
    cursor.close()
    return jsonify(presentaciones)

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

@app.route('/vendedor/mis-ventas', methods=['GET'])
@login_required
def mis_ventas():
    # IMPRIMIR TODO EL CONTENIDO DE LA SESIÓN PARA DEBUG
    print("="*50)
    print("CONTENIDO COMPLETO DE LA SESIÓN:")
    for key, value in session.items():
        print(f"  {key}: {value}")
    print("="*50)
    
    # VERIFICAR USUARIO EN SESIÓN - USANDO 'usuario_id' EN LUGAR DE 'user_id'
    if 'usuario_id' not in session:
        print("❌ NO HAY 'usuario_id' EN LA SESIÓN")
        print(f"Claves disponibles en sesión: {list(session.keys())}")
        flash('Debe iniciar sesión primero', 'danger')
        return redirect(url_for('login'))
    
    usuario_id = session['usuario_id']
    usuario_nombre = session.get('usuario_nombre', 'Desconocido')
    usuario_rol = session.get('usuario_rol', '')
    
    print(f"✅ USUARIO EN SESIÓN: ID={usuario_id}, Nombre={usuario_nombre}, Rol={usuario_rol}")
    
    cursor = mysql.connection.cursor(DictCursor)
    
    try:
        # VERIFICAR QUE EL USUARIO EXISTE EN LA BD
        cursor.execute("""
            SELECT id, nombre, email, rol, activo 
            FROM usuarios 
            WHERE id = %s AND activo = 1
        """, (usuario_id,))
        
        usuario = cursor.fetchone()
        
        if not usuario:
            print(f"❌ USUARIO ID {usuario_id} NO ENCONTRADO EN BD")
            # Limpiar sesión inválida
            session.clear()
            flash('Usuario no encontrado. Por favor inicie sesión nuevamente.', 'danger')
            return redirect(url_for('login'))
        
        print(f"✅ USUARIO VERIFICADO EN BD: {usuario}")
        
        # OPCIONAL: Verificar rol (si quieres que solo vendedores accedan)
        if usuario_rol != 'vendedor' and usuario_rol != 'admin':
            print(f"❌ ROL NO AUTORIZADO: {usuario_rol}")
            flash('Acceso no autorizado', 'danger')
            return redirect(url_for('login'))
        
        # ============================================
        # OBTENER FILTRO DE LA URL
        # ============================================
        filtro = request.args.get('filtro', 'todo')
        print(f"Filtro seleccionado: {filtro}")
        
        # ============================================
        # CONSULTA DE VENTAS CON FILTROS
        # ============================================
        query_ventas = """
            SELECT v.*, u.nombre as nombre_vendedor
            FROM ventas v
            INNER JOIN usuarios u ON v.usuario_id = u.id
            WHERE v.usuario_id = %s
        """
        
        params_ventas = [usuario_id]
        
        # Aplicar filtros de fecha
        if filtro == 'dia':
            query_ventas += " AND DATE(v.fecha_venta) = CURDATE()"
        elif filtro == 'semana':
            query_ventas += " AND YEARWEEK(v.fecha_venta) = YEARWEEK(CURDATE())"
        elif filtro == 'mes':
            query_ventas += " AND MONTH(v.fecha_venta) = MONTH(CURDATE()) AND YEAR(v.fecha_venta) = YEAR(CURDATE())"
        # 'todo' no necesita filtro adicional
        
        query_ventas += " ORDER BY v.fecha_venta DESC, v.fecha_creacion DESC"
        
        print(f"Query ventas: {query_ventas}")
        print(f"Params ventas: {params_ventas}")
        
        cursor.execute(query_ventas, params_ventas)
        ventas = cursor.fetchall()
        
        print(f"Ventas encontradas: {len(ventas)}")
        
        # ============================================
        # CALCULAR TOTALES CON FILTROS
        # ============================================
        query_totales = """
            SELECT 
                COUNT(*) as total_ventas,
                IFNULL(SUM(total_venta), 0) as suma_total,
                IFNULL(SUM(efectivo), 0) as suma_efectivo
            FROM ventas 
            WHERE usuario_id = %s
        """
        
        params_totales = [usuario_id]
        
        # Aplicar mismos filtros a totales
        if filtro == 'dia':
            query_totales += " AND DATE(fecha_venta) = CURDATE()"
        elif filtro == 'semana':
            query_totales += " AND YEARWEEK(fecha_venta) = YEARWEEK(CURDATE())"
        elif filtro == 'mes':
            query_totales += " AND MONTH(fecha_venta) = MONTH(CURDATE()) AND YEAR(fecha_venta) = YEAR(CURDATE())"
        
        cursor.execute(query_totales, params_totales)
        totales = cursor.fetchone()
        
        print(f"Totales: {totales}")
        
        # ============================================
        # OPCIONAL: OBTENER PRODUCTOS MÁS VENDIDOS
        # ============================================
        query_productos = """
            SELECT 
                p.nombre, 
                IFNULL(SUM(dv.cantidad), 0) as total_vendido,
                IFNULL(SUM(dv.subtotal), 0) as total_recaudado
            FROM detalles_venta dv
            INNER JOIN ventas v ON dv.venta_id = v.id
            INNER JOIN productos p ON dv.referencia_id = p.id
            WHERE v.usuario_id = %s
            GROUP BY p.id, p.nombre
            ORDER BY total_vendido DESC
            LIMIT 5
        """
        
        params_productos = [usuario_id]
        
        # Aplicar filtros de fecha a productos
        if filtro == 'dia':
            query_productos = query_productos.replace("WHERE v.usuario_id = %s", 
                                                      "WHERE v.usuario_id = %s AND DATE(v.fecha_venta) = CURDATE()")
        elif filtro == 'semana':
            query_productos = query_productos.replace("WHERE v.usuario_id = %s", 
                                                      "WHERE v.usuario_id = %s AND YEARWEEK(v.fecha_venta) = YEARWEEK(CURDATE())")
        elif filtro == 'mes':
            query_productos = query_productos.replace("WHERE v.usuario_id = %s", 
                                                      "WHERE v.usuario_id = %s AND MONTH(v.fecha_venta) = MONTH(CURDATE()) AND YEAR(v.fecha_venta) = YEAR(CURDATE())")
        
        cursor.execute(query_productos, params_productos)
        productos_vendidos = cursor.fetchall()
        
        cursor.close()
        
        # Renderizar template
        return render_template('vendedor/mis_ventas.html', 
                             ventas=ventas,
                             totales=totales,
                             productos_vendidos=productos_vendidos,
                             usuario=usuario,
                             filtro_actual=filtro)
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        cursor.close()
        flash(f'Error al cargar ventas: {str(e)}', 'danger')
        return render_template('vendedor/mis_ventas.html', 
                             ventas=[],
                             totales={'total_ventas': 0, 'suma_total': 0, 'suma_efectivo': 0},
                             productos_vendidos=[],
                             usuario={'nombre': usuario_nombre, 'id': usuario_id, 'rol': usuario_rol} if 'usuario_id' in session else None,
                             filtro_actual=filtro)

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
#
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
            
            # Verificar que existe una caja activa para el usuario
            cursor.execute("""
                SELECT id, total_ventas, total_efectivo, monto_apertura 
                FROM caja 
                WHERE usuario_id = %s AND estado = 'abierta'
            """, (session['usuario_id'],))
            
            caja_activa = cursor.fetchone()
            
            if not caja_activa:
                raise ValueError("No tienes una caja aperturada. Debes aperturar caja primero.")
            
            # Convertir valores Decimal a float
            total_ventas_actual = float(caja_activa['total_ventas']) if caja_activa['total_ventas'] else 0.0
            total_efectivo_actual = float(caja_activa['total_efectivo']) if caja_activa['total_efectivo'] else 0.0
            
            # Calcular cambio
            cambio = efectivo - total_venta
            
            # Insertar cabecera de venta con referencia a la caja
            cursor.execute('''
                INSERT INTO ventas (usuario_id, caja_id, fecha_venta, total_venta, efectivo, cambio)
                VALUES (%s, %s, CURDATE(), %s, %s, %s)
            ''', (session['usuario_id'], caja_activa['id'], total_venta, efectivo, cambio))
            
            venta_id = cursor.lastrowid
            
            # Procesar cada item (tu código existente)
            for item in items:
                tipo_detalle = item['tipo_detalle']
                referencia_id = item['referencia_id']
                cantidad = float(item.get('cantidad', 1))
                precio_unitario = float(item['precio_unitario'])
                subtotal = float(item['subtotal'])
                variacion_id = item.get('variacion_id')
                
                if tipo_detalle == 'producto':
                    if variacion_id:
                        # Es una variación de producto
                        cursor.execute('''
                            SELECT 
                                v.*,
                                p.stock_actual as stock_producto_base,
                                p.nombre as producto_nombre,
                                u.abreviatura as unidad_abrev,
                                u2.abreviatura as unidad_base_abrev,
                                v.cantidad_equivalente
                            FROM variaciones_producto v
                            JOIN productos p ON v.producto_id = p.id
                            JOIN unidades_medida u ON v.unidad_id = u.id
                            JOIN unidades_medida u2 ON p.unidad_base_id = u2.id
                            WHERE v.id = %s AND v.activo = 1
                        ''', (variacion_id,))
                        
                        variacion = cursor.fetchone()
                        
                        if not variacion:
                            raise ValueError(f"Variación de producto no encontrada")
                        
                        # Convertir valores Decimal a float
                        stock_producto_base = float(variacion['stock_producto_base']) if variacion['stock_producto_base'] else 0.0
                        cantidad_equivalente = float(variacion['cantidad_equivalente']) if variacion['cantidad_equivalente'] else 1.0
                        
                        # Calcular cantidad en unidades base (para actualizar stock)
                        cantidad_base = cantidad * cantidad_equivalente
                        
                        # Verificar stock
                        if stock_producto_base < cantidad_base:
                            stock_disponible_presentacion = int(stock_producto_base / cantidad_equivalente)
                            raise ValueError(
                                f"Stock insuficiente para {variacion['producto_nombre']} "
                                f"en presentación {variacion['unidad_abrev']}. "
                                f"Disponible: {stock_disponible_presentacion} "
                                f"{variacion['unidad_abrev']}"
                            )
                        
                        # Insertar detalle de venta con variación
                        cursor.execute('''
                            INSERT INTO detalles_venta 
                            (venta_id, tipo_detalle, referencia_id, variacion_id, 
                             cantidad, unidad_id, precio_unitario, subtotal, observaciones)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            venta_id,
                            tipo_detalle,
                            referencia_id,
                            variacion_id,
                            cantidad,
                            variacion['unidad_id'],
                            precio_unitario,
                            subtotal,
                            f"Presentación: {variacion['unidad_abrev']} - {variacion.get('descripcion', 'Sin descripción')}"
                        ))
                        
                        # Actualizar stock del producto base (restando la cantidad base)
                        nuevo_stock = stock_producto_base - cantidad_base
                        cursor.execute('''
                            UPDATE productos 
                            SET stock_actual = %s 
                            WHERE id = %s
                        ''', (nuevo_stock, referencia_id))
                        
                        # Registrar movimiento de inventario
                        observacion_movimiento = (
                            f"Venta #{venta_id} - "
                            f"Presentación: {variacion['unidad_abrev']} - "
                            f"Cantidad vendida: {cantidad} {variacion['unidad_abrev']} "
                            f"(Equivalente a {cantidad_base} {variacion['unidad_base_abrev']})"
                        )
                        
                        cursor.execute('''
                            INSERT INTO movimientos_inventario 
                            (producto_id, tipo_movimiento, cantidad, cantidad_anterior, 
                             cantidad_nueva, referencia_tipo, referencia_id, usuario_id, observaciones)
                            VALUES (%s, 'salida', %s, %s, %s, 'venta', %s, %s, %s)
                        ''', (
                            referencia_id,
                            cantidad_base,
                            stock_producto_base,
                            nuevo_stock,
                            venta_id,
                            session['usuario_id'],
                            observacion_movimiento
                        ))
                    
                    else:
                        # Producto simple sin variación
                        cursor.execute('''
                            SELECT stock_actual, nombre, unidad_base_id 
                            FROM productos 
                            WHERE id = %s
                        ''', (referencia_id,))
                        producto = cursor.fetchone()
                        
                        if not producto:
                            raise ValueError(f"Producto no encontrado")
                        
                        stock_actual = float(producto['stock_actual']) if producto['stock_actual'] else 0.0
                        
                        if stock_actual < cantidad:
                            raise ValueError(
                                f"Stock insuficiente para {producto['nombre']}. "
                                f"Disponible: {stock_actual}"
                            )
                        
                        # Insertar detalle de venta
                        cursor.execute('''
                            INSERT INTO detalles_venta 
                            (venta_id, tipo_detalle, referencia_id, cantidad, 
                             unidad_id, precio_unitario, subtotal)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            venta_id,
                            tipo_detalle,
                            referencia_id,
                            cantidad,
                            producto['unidad_base_id'],
                            precio_unitario,
                            subtotal
                        ))
                        
                        # Actualizar stock
                        nuevo_stock = stock_actual - cantidad
                        cursor.execute('''
                            UPDATE productos 
                            SET stock_actual = %s 
                            WHERE id = %s
                        ''', (nuevo_stock, referencia_id))
                        
                        # Registrar movimiento de inventario
                        cursor.execute('''
                            INSERT INTO movimientos_inventario 
                            (producto_id, tipo_movimiento, cantidad, cantidad_anterior, 
                             cantidad_nueva, referencia_tipo, referencia_id, usuario_id, observaciones)
                            VALUES (%s, 'salida', %s, %s, %s, 'venta', %s, %s, %s)
                        ''', (
                            referencia_id,
                            cantidad,
                            stock_actual,
                            nuevo_stock,
                            venta_id,
                            session['usuario_id'],
                            f"Venta #{venta_id}"
                        ))
                
                elif tipo_detalle == 'servicio':
                    # Servicios
                    cursor.execute('''
                        INSERT INTO detalles_venta 
                        (venta_id, tipo_detalle, referencia_id, cantidad, precio_unitario, subtotal)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (
                        venta_id,
                        tipo_detalle,
                        referencia_id,
                        cantidad,
                        precio_unitario,
                        subtotal
                    ))
                
                elif tipo_detalle == 'combo':
                    # Combos
                    cursor.execute('''
                        INSERT INTO detalles_venta 
                        (venta_id, tipo_detalle, referencia_id, cantidad, precio_unitario, subtotal)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (
                        venta_id,
                        tipo_detalle,
                        referencia_id,
                        cantidad,
                        precio_unitario,
                        subtotal
                    ))
            
            # ACTUALIZAR CAJA: Incrementar total_ventas y total_efectivo
            # Ya convertimos estos valores al inicio
            nuevo_total_ventas = total_ventas_actual + total_venta
            nuevo_total_efectivo = total_efectivo_actual + total_venta
            
            cursor.execute("""
                UPDATE caja 
                SET total_ventas = %s, total_efectivo = %s
                WHERE id = %s
            """, (nuevo_total_ventas, nuevo_total_efectivo, caja_activa['id']))
            
            # Confirmar transacción
            mysql.connection.commit()
            
            return jsonify({
                'success': True,
                'message': 'Venta registrada exitosamente',
                'venta_id': venta_id,
                'cambio': cambio,
                'caja_actual': {
                    'total_ventas': nuevo_total_ventas,
                    'total_efectivo': nuevo_total_efectivo
                }
            })
            
        except ValueError as e:
            mysql.connection.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error en nueva_venta: {str(e)}")
            return jsonify({'success': False, 'message': f'Error al procesar la venta: {str(e)}'}), 500
        finally:
            cursor.close()
    
    # GET: Mostrar formulario de venta
    try:
        # Primero verificar si el usuario tiene caja activa
        cursor.execute("""
            SELECT id, monto_apertura, total_ventas, total_efectivo 
            FROM caja 
            WHERE usuario_id = %s AND estado = 'abierta'
        """, (session['usuario_id'],))
        
        caja_activa = cursor.fetchone()
        
        if not caja_activa:
            flash('No tienes una caja aperturada. Debes aperturar caja antes de realizar ventas.', 'warning')
            return redirect(url_for('caja_movimiento'))
        
        # Convertir valores Decimal a float para la vista
        if caja_activa['total_ventas']:
            caja_activa['total_ventas'] = float(caja_activa['total_ventas'])
        if caja_activa['total_efectivo']:
            caja_activa['total_efectivo'] = float(caja_activa['total_efectivo'])
        if caja_activa['monto_apertura']:
            caja_activa['monto_apertura'] = float(caja_activa['monto_apertura'])
        
        # Obtener productos activos
        cursor.execute('''
            SELECT 
                p.*,
                c.nombre as categoria_nombre,
                u.abreviatura as unidad_abrev,
                u.nombre as unidad_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
            WHERE p.activo = 1
            ORDER BY p.nombre
        ''')
        productos = cursor.fetchall()
        
        # Convertir valores Decimal a float para cada producto
        for producto in productos:
            if producto.get('stock_actual'):
                producto['stock_actual'] = float(producto['stock_actual'])
            if producto.get('precio_base'):
                producto['precio_base'] = float(producto['precio_base'])
            if producto.get('precio_compra'):
                producto['precio_compra'] = float(producto['precio_compra'])
        
        # Obtener variaciones para cada producto jerárquico
        for producto in productos:
            if producto['tipo_producto'] == 'jerarquico':
                cursor.execute('''
                    SELECT 
                        v.*,
                        u.nombre as unidad_nombre,
                        u.abreviatura as unidad_abrev,
                        -- Calcular stock disponible
                        FLOOR(p.stock_actual / v.cantidad_equivalente) as stock_disponible
                    FROM variaciones_producto v
                    JOIN unidades_medida u ON v.unidad_id = u.id
                    JOIN productos p ON v.producto_id = p.id
                    WHERE v.producto_id = %s AND v.activo = 1
                    ORDER BY v.nivel, v.cantidad_equivalente
                ''', (producto['id'],))
                producto['variaciones'] = cursor.fetchall()
                
                # Convertir valores Decimal a float para cada variación
                for variacion in producto['variaciones']:
                    if variacion.get('precio_venta'):
                        variacion['precio_venta'] = float(variacion['precio_venta'])
                    if variacion.get('cantidad_equivalente'):
                        variacion['cantidad_equivalente'] = float(variacion['cantidad_equivalente'])
                    if variacion.get('stock_disponible'):
                        variacion['stock_disponible'] = int(variacion['stock_disponible'])
            else:
                producto['variaciones'] = []
        
        # Obtener servicios activos
        cursor.execute('''
            SELECT s.*, t.nombre as tipo_nombre
            FROM servicios s
            INNER JOIN tipos_servicio t ON s.tipo_servicio_id = t.id
            WHERE s.activo = 1 
            ORDER BY t.nombre, s.nombre
        ''')
        servicios = cursor.fetchall()
        
        # Convertir valores Decimal a float para cada servicio
        for servicio in servicios:
            if servicio.get('precio'):
                servicio['precio'] = float(servicio['precio'])
        
        # Obtener combos activos
        cursor.execute('''
            SELECT c.*, 
                   (SELECT COUNT(*) FROM detalles_combo WHERE combo_id = c.id) as total_productos
            FROM combos c
            WHERE c.activo = 1
            ORDER BY c.nombre
        ''')
        combos = cursor.fetchall()
        
        # Convertir valores Decimal a float para cada combo
        for combo in combos:
            if combo.get('precio_combo'):
                combo['precio_combo'] = float(combo['precio_combo'])
        
        cursor.close()
        
        return render_template('admin/punto_venta.html',
                             productos=productos,
                             servicios=servicios,
                             combos=combos,
                             caja_activa=caja_activa)
    
    except Exception as e:
        cursor.close()
        print(f"Error al cargar datos: {str(e)}")
        flash(f'Error al cargar datos: {str(e)}', 'error')
        return render_template('admin/punto_venta.html',
                             productos=[],
                             servicios=[],
                             combos=[],
                             caja_activa=None)
#
@app.route('/ventas/<int:venta_id>', methods=['GET'])
@login_required
def detalle_venta(venta_id):
    cursor = mysql.connection.cursor(DictCursor)
    
    print(f"=== Accediendo a detalle_venta con ID: {venta_id} ===")
    
    try:
        # Obtener información de la venta
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
        
        # Obtener detalles de la venta con información de variaciones
        cursor.execute('''
            SELECT 
                dv.*,
                -- Nombre del item según su tipo
                CASE 
                    WHEN dv.tipo_detalle = 'producto' THEN 
                        CONCAT(
                            p.nombre,
                            IF(dv.variacion_id IS NOT NULL, 
                            CONCAT(' (', u.abreviatura, ')'), 
                            IF(p.tipo_producto = 'simple', 
                                CONCAT(' (', ub.abreviatura, ')'), 
                                ''))
                        )
                    WHEN dv.tipo_detalle = 'servicio' THEN s.nombre
                    WHEN dv.tipo_detalle = 'combo' THEN c.nombre
                    ELSE 'Desconocido'
                END as nombre_item,
                -- Información de variación
                vp.unidad_id as variacion_unidad_id,
                u.abreviatura as variacion_unidad,
                vp.cantidad_equivalente,
                vp.descripcion as variacion_descripcion,
                -- Presentación
                p.presentacion as presentacion,
                -- Unidad de medida
                COALESCE(u.abreviatura, ub.abreviatura) as unidad_abrev,
                COALESCE(u.nombre, ub.nombre) as unidad_nombre,
                -- Información adicional
                dv.tipo_detalle as tipo_item,
                p.tipo_producto as producto_tipo,
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
                -- Valores formateados
                FORMAT(dv.precio_unitario, 2) as precio_unitario_formato,
                FORMAT(dv.subtotal, 2) as subtotal_formato
                -- ELIMINA ESTA LÍNEA: dv.observaciones
            FROM detalles_venta dv
            LEFT JOIN productos p ON dv.tipo_detalle = 'producto' AND dv.referencia_id = p.id
            LEFT JOIN servicios s ON dv.tipo_detalle = 'servicio' AND dv.referencia_id = s.id
            LEFT JOIN combos c ON dv.tipo_detalle = 'combo' AND dv.referencia_id = c.id
            LEFT JOIN unidades_medida ub ON p.unidad_base_id = ub.id
            LEFT JOIN variaciones_producto vp ON dv.variacion_id = vp.id
            LEFT JOIN unidades_medida u ON vp.unidad_id = u.id
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
        
        # Calcular resumen
        resumen_detalle = {
            'total_items': len(detalles),
            'total_productos': sum(1 for d in detalles if d['tipo_detalle'] == 'producto'),
            'total_servicios': sum(1 for d in detalles if d['tipo_detalle'] == 'servicio'),
            'total_combos': sum(1 for d in detalles if d['tipo_detalle'] == 'combo'),
            'subtotal': sum(float(d['subtotal']) for d in detalles),
            'items_no_disponibles': sum(1 for d in detalles if 'no disponible' in d['estado_item'].lower())
        }
        
        # Verificar consistencia de totales
        if abs(float(resumen_detalle['subtotal']) - float(venta['total_venta'])) > 0.01:
            print(f"ADVERTENCIA: Venta {venta_id} - Total calculado ({resumen_detalle['subtotal']}) != Total registrado ({venta['total_venta']})")
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
#
@app.route('/api/productos/disponibles', methods=['GET'])
@login_required
def api_productos_disponibles():
    """API para obtener productos disponibles con sus variaciones jerárquicas"""
    cursor = mysql.connection.cursor(DictCursor)
    try:
        # Obtener todos los productos activos
        cursor.execute('''
            SELECT 
                p.id, 
                p.codigo, 
                p.nombre, 
                p.descripcion, 
                p.tipo_producto,
                p.precio_venta as precio_base,
                p.stock_actual as stock_base,
                p.presentacion,
                p.lote, 
                p.fecha_vencimiento,
                p.principio_activo,
                c.nombre as categoria_nombre,
                u.id as unidad_base_id, 
                u.nombre as unidad_base_nombre, 
                u.abreviatura as unidad_base_abrev
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
            WHERE p.activo = 1
            ORDER BY p.nombre
        ''')
        productos = cursor.fetchall()
        
        # Para cada producto, obtener sus variaciones
        for producto in productos:
            if producto['tipo_producto'] == 'jerarquico':
                cursor.execute('''
                    SELECT 
                        v.id,
                        v.producto_id,
                        v.presentacion_padre_id,
                        v.nivel,
                        v.unidad_id,
                        v.cantidad_equivalente,
                        v.cantidad_por_padre,
                        v.precio_venta,
                        v.porcentaje_ganancia,
                        v.descripcion,
                        v.activo,
                        u.nombre as unidad_nombre,
                        u.abreviatura as unidad_abrev,
                        -- Calcular stock disponible basado en el producto base
                        FLOOR(p.stock_actual / v.cantidad_equivalente) as stock_disponible,
                        -- Información de la presentación padre
                        vp.unidad_id as padre_unidad_id,
                        up.nombre as padre_unidad_nombre,
                        up.abreviatura as padre_unidad_abrev
                    FROM variaciones_producto v
                    JOIN unidades_medida u ON v.unidad_id = u.id
                    JOIN productos p ON v.producto_id = p.id
                    LEFT JOIN variaciones_producto vp ON v.presentacion_padre_id = vp.id
                    LEFT JOIN unidades_medida up ON vp.unidad_id = up.id
                    WHERE v.producto_id = %s AND v.activo = 1
                    ORDER BY v.nivel, v.cantidad_equivalente
                ''', (producto['id'],))
                
                variaciones = cursor.fetchall()
                
                # Convertir valores Decimal a float para JSON
                for variacion in variaciones:
                    if variacion.get('precio_venta'):
                        variacion['precio_venta'] = float(variacion['precio_venta'])
                    if variacion.get('porcentaje_ganancia'):
                        variacion['porcentaje_ganancia'] = float(variacion['porcentaje_ganancia'])
                    if variacion.get('stock_disponible'):
                        variacion['stock_disponible'] = int(variacion['stock_disponible'])
                    
                    # Construir nombre de presentación completo
                    presentacion_nombre = variacion['unidad_abrev']
                    if variacion.get('padre_unidad_abrev'):
                        presentacion_nombre = f"{variacion['padre_unidad_abrev']} → {presentacion_nombre}"
                    
                    variacion['presentacion_completa'] = presentacion_nombre
                
                producto['variaciones'] = variaciones
            else:
                producto['variaciones'] = []
            
            # Convertir valores numéricos a float
            if producto.get('precio_base'):
                producto['precio_base'] = float(producto['precio_base'])
            if producto.get('stock_base'):
                producto['stock_base'] = int(producto['stock_base'])
        
        return jsonify(productos)
        
    except Exception as e:
        print(f"Error en api_productos_disponibles: {str(e)}")
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
# CAJA DE EFECTIVO
# ========================
@app.route('/caja')
@login_required
def caja_index():
    """Página principal de caja con información del día actual"""
    from datetime import datetime
    import calendar
    import locale
    
    # Configurar locale para nombres de meses en español
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except:
        pass
    
    cursor = mysql.connection.cursor(DictCursor)
    
    # Obtener caja activa del usuario actual
    cursor.execute("""
        SELECT c.*, u.nombre as usuario_nombre
        FROM caja c
        INNER JOIN usuarios u ON c.usuario_id = u.id
        WHERE c.usuario_id = %s AND c.estado = 'abierta'
        ORDER BY c.fecha_apertura DESC LIMIT 1
    """, (session['usuario_id'],))
    
    caja_activa = cursor.fetchone()
    
    # Variables para el modal de cierre
    resumen_ventas = None
    monto_esperado = 0
    
    # Si hay caja activa, obtener las ventas del día de esta caja
    ventas_hoy = []
    total_ventas_hoy = 0
    
    if caja_activa:
        cursor.execute("""
            SELECT v.*, 
                   COUNT(dv.id) as total_items
            FROM ventas v
            LEFT JOIN detalles_venta dv ON v.id = dv.venta_id
            WHERE v.caja_id = %s AND DATE(v.fecha_venta) = CURDATE()
            GROUP BY v.id
            ORDER BY v.fecha_venta DESC
        """, (caja_activa['id'],))
        
        ventas_hoy = cursor.fetchall()
        
        # Calcular total de ventas del día
        cursor.execute("""
            SELECT COALESCE(SUM(total_venta), 0) as total
            FROM ventas
            WHERE caja_id = %s AND DATE(fecha_venta) = CURDATE()
        """, (caja_activa['id'],))
        
        total_ventas_hoy = cursor.fetchone()['total']
        
        # Obtener resumen de ventas para el modal de cierre
        cursor.execute("""
            SELECT 
                COUNT(*) as total_ventas_dia,
                COALESCE(SUM(total_venta), 0) as monto_total_ventas,
                MIN(fecha_venta) as primera_venta,
                MAX(fecha_venta) as ultima_venta
            FROM ventas
            WHERE caja_id = %s AND DATE(fecha_venta) = CURDATE()
        """, (caja_activa['id'],))
        
        resumen_ventas = cursor.fetchone()
        
        # Calcular monto esperado en caja
        monto_esperado = float(caja_activa['monto_apertura']) + float(resumen_ventas['monto_total_ventas'] if resumen_ventas['monto_total_ventas'] else 0)
    
    # Obtener historial de cierres del mes actual para este usuario
    cursor.execute("""
        SELECT 
            c.*,
            u.nombre as usuario_nombre,
            DATE(c.fecha_apertura) as fecha,
            TIME(c.fecha_apertura) as hora_apertura,
            TIME(c.fecha_cierre) as hora_cierre,
            TIMEDIFF(c.fecha_cierre, c.fecha_apertura) as tiempo_trabajado
        FROM caja c
        INNER JOIN usuarios u ON c.usuario_id = u.id
        WHERE c.usuario_id = %s 
            AND c.estado = 'cerrada'
            AND MONTH(c.fecha_apertura) = MONTH(CURDATE())
            AND YEAR(c.fecha_apertura) = YEAR(CURDATE())
        ORDER BY c.fecha_apertura DESC
    """, (session['usuario_id'],))
    
    historial_mes = cursor.fetchall()
    
    # Calcular resumen del mes
    resumen_mes = {
        'total_aperturas': len(historial_mes),
        'total_ventas_mes': sum(float(c['total_ventas']) for c in historial_mes),
        'total_efectivo_mes': sum(float(c['total_efectivo']) for c in historial_mes),
        'diferencia_total': sum(float(c['diferencia'] or 0) for c in historial_mes)
    }
    
    cursor.close()
    
    # Obtener nombre del mes actual
    now = datetime.now()
    nombre_mes = calendar.month_name[now.month]
    
    return render_template('admin/caja/caja_efectivo.html',
                         caja_activa=caja_activa,
                         ventas_hoy=ventas_hoy,
                         total_ventas_hoy=total_ventas_hoy,
                         historial_mes=historial_mes,
                         resumen_mes=resumen_mes,
                         resumen_ventas=resumen_ventas,
                         monto_esperado=monto_esperado,
                         now=now,
                         nombre_mes=nombre_mes)

@app.route('/caja/apertura', methods=['GET', 'POST'])
@login_required
def caja_apertura():
    """Aperturar nueva caja"""
    if request.method == 'POST':
        try:
            monto_apertura = request.form.get('monto_apertura', 0, type=float)
            observaciones = request.form.get('observaciones', '')
            
            cursor = mysql.connection.cursor(DictCursor)
            
            # Verificar si ya tiene una caja abierta
            cursor.execute("""
                SELECT id, estado FROM caja 
                WHERE usuario_id = %s AND estado = 'abierta'
            """, (session['usuario_id'],))
            
            caja_existente = cursor.fetchone()
            
            if caja_existente:
                flash('Ya tienes una caja abierta. Debes cerrarla antes de abrir una nueva.', 'warning')
                return redirect(url_for('caja_index'))
            
            # Verificar si ya aperturó caja hoy
            cursor.execute("""
                SELECT id FROM caja 
                WHERE usuario_id = %s 
                    AND DATE(fecha_apertura) = CURDATE()
                    AND estado = 'cerrada'
            """, (session['usuario_id'],))
            
            caja_hoy = cursor.fetchone()
            
            if caja_hoy:
                flash('Ya realizaste una apertura de caja hoy. Solo puedes aperturar una caja por día.', 'warning')
                return redirect(url_for('caja_index'))
            
            # Crear nueva caja
            cursor.execute("""
                INSERT INTO caja (usuario_id, fecha_apertura, monto_apertura, estado, observaciones)
                VALUES (%s, NOW(), %s, 'abierta', %s)
            """, (
                session['usuario_id'],
                monto_apertura,
                observaciones
            ))
            
            mysql.connection.commit()
            
            flash(f'✅ Caja aperturada exitosamente con saldo inicial de C$ {monto_apertura:,.2f}', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'❌ Error al aperturar caja: {str(e)}', 'danger')
            print(f"Error: {e}")
        
        finally:
            cursor.close()
        
        return redirect(url_for('caja_index'))
    
    # GET - Mostrar formulario de apertura
    return render_template('admin/caja/apertura.html')

@app.route('/caja/cierre', methods=['GET', 'POST'])
@login_required
def caja_cierre():
    """Cerrar caja actual con verificación de efectivo físico"""
    cursor = mysql.connection.cursor(DictCursor)
    
    # Obtener caja activa
    cursor.execute("""
        SELECT c.*, u.nombre as usuario_nombre
        FROM caja c
        INNER JOIN usuarios u ON c.usuario_id = u.id
        WHERE c.usuario_id = %s AND c.estado = 'abierta'
    """, (session['usuario_id'],))
    
    caja_activa = cursor.fetchone()
    
    if not caja_activa:
        flash('No tienes una caja abierta para cerrar', 'warning')
        return redirect(url_for('caja_index'))
    
    # Obtener ventas del día para esta caja
    cursor.execute("""
        SELECT 
            COUNT(*) as total_ventas_dia,
            COALESCE(SUM(total_venta), 0) as monto_total_ventas,
            MIN(fecha_venta) as primera_venta,
            MAX(fecha_venta) as ultima_venta
        FROM ventas
        WHERE caja_id = %s AND DATE(fecha_venta) = CURDATE()
    """, (caja_activa['id'],))
    
    resumen_ventas = cursor.fetchone()
    
    # Calcular monto esperado
    monto_esperado = float(caja_activa['monto_apertura']) + float(resumen_ventas['monto_total_ventas'])
    
    if request.method == 'POST':
        try:
            monto_fisico = request.form.get('monto_fisico', type=float)
            observaciones_cierre = request.form.get('observaciones_cierre', '')
            
            if not monto_fisico:
                flash('Debes ingresar el monto físico verificado', 'danger')
                return redirect(url_for('caja_cierre'))
            
            # Calcular diferencias
            diferencia = monto_fisico - monto_esperado
            
            # Actualizar observaciones existentes
            observaciones_completas = caja_activa['observaciones'] or ''
            if observaciones_completas:
                observaciones_completas += f" | Cierre: {observaciones_cierre}"
            else:
                observaciones_completas = f"Cierre: {observaciones_cierre}"
            
            # Cerrar la caja
            cursor.execute("""
                UPDATE caja 
                SET fecha_cierre = NOW(),
                    monto_cierre = %s,
                    diferencia = %s,
                    estado = 'cerrada',
                    observaciones = %s
                WHERE id = %s
            """, (
                monto_fisico,
                diferencia,
                observaciones_completas,
                caja_activa['id']
            ))
            
            mysql.connection.commit()
            
            if diferencia == 0:
                flash(f'✅ Caja cerrada exitosamente. El efectivo coincide perfectamente.', 'success')
            else:
                flash(f'⚠️ Caja cerrada exitosamente. Diferencia: C$ {diferencia:,.2f}', 'info')
            
            return redirect(url_for('caja_index'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'❌ Error al cerrar caja: {str(e)}', 'danger')
            print(f"Error: {e}")
            return redirect(url_for('caja_cierre'))
        
        finally:
            cursor.close()
    
    # GET - Mostrar formulario de cierre
    return render_template('admin/caja/cierre.html',
                         caja_activa=caja_activa,
                         resumen_ventas=resumen_ventas,
                         monto_esperado=monto_esperado)


@app.route('/caja/historial')
@login_required
def caja_historial():
    """Historial de cajas con filtro por fecha (día del mes)"""
    cursor = mysql.connection.cursor(DictCursor)
    
    # Obtener parámetros de filtro
    mes = request.args.get('mes', type=int, default=datetime.now().month)
    año = request.args.get('año', type=int, default=datetime.now().year)
    dia = request.args.get('dia', type=int)
    usuario_id = request.args.get('usuario_id', type=int)
    
    # Construir query base
    query = """
        SELECT 
            c.*,
            u.nombre as usuario_nombre,
            DATE(c.fecha_apertura) as fecha_apertura_date,
            TIME(c.fecha_apertura) as hora_apertura,
            TIME(c.fecha_cierre) as hora_cierre,
            TIMEDIFF(c.fecha_cierre, c.fecha_apertura) as tiempo_trabajado,
            (SELECT COUNT(*) FROM ventas WHERE caja_id = c.id) as total_ventas_realizadas,
            (SELECT COALESCE(SUM(total_venta), 0) FROM ventas WHERE caja_id = c.id) as monto_ventas_total
        FROM caja c
        INNER JOIN usuarios u ON c.usuario_id = u.id
        WHERE c.estado = 'cerrada'
            AND MONTH(c.fecha_apertura) = %s
            AND YEAR(c.fecha_apertura) = %s
    """
    params = [mes, año]
    
    if dia:
        query += " AND DAY(c.fecha_apertura) = %s"
        params.append(dia)
    
    if usuario_id:
        query += " AND c.usuario_id = %s"
        params.append(usuario_id)
    
    query += " ORDER BY c.fecha_apertura DESC"
    
    cursor.execute(query, params)
    historial = cursor.fetchall()
    
    # Calcular resumen del período
    resumen = {
        'total_cajas': len(historial),
        'total_ventas_acumulado': sum(float(c['total_ventas']) for c in historial),
        'total_efectivo_acumulado': sum(float(c['total_efectivo']) for c in historial),
        'diferencia_total': sum(float(c['diferencia'] or 0) for c in historial),
        'promedio_ventas_dia': sum(float(c['total_ventas']) for c in historial) / len(historial) if historial else 0
    }
    
    # Obtener lista de usuarios para filtro
    cursor.execute("""
        SELECT DISTINCT u.id, u.nombre 
        FROM usuarios u
        INNER JOIN caja c ON u.id = c.usuario_id
        ORDER BY u.nombre
    """)
    usuarios = cursor.fetchall()
    
    cursor.close()
    
    return render_template('admin/caja/historial.html',
                         historial=historial,
                         resumen=resumen,
                         usuarios=usuarios,
                         mes_actual=mes,
                         año_actual=año,
                         dia_actual=dia,
                         usuario_filtro=usuario_id,
                         meses=[(1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
                                (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
                                (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')],
                         años=range(2020, datetime.now().year + 1),
                         dias=range(1, 32))


@app.route('/caja/detalle/<int:caja_id>')
@login_required
def caja_detalle(caja_id):
    """Ver detalle completo de una caja específica"""
    cursor = mysql.connection.cursor(DictCursor)
    
    # Obtener información de la caja
    cursor.execute("""
        SELECT 
            c.*,
            u.nombre as usuario_nombre,
            DATE(c.fecha_apertura) as fecha_apertura_date,
            TIME(c.fecha_apertura) as hora_apertura,
            TIME(c.fecha_cierre) as hora_cierre,
            TIMEDIFF(c.fecha_cierre, c.fecha_apertura) as tiempo_trabajado,
            DATEDIFF(c.fecha_cierre, c.fecha_apertura) as dias_trabajados
        FROM caja c
        INNER JOIN usuarios u ON c.usuario_id = u.id
        WHERE c.id = %s
    """, (caja_id,))
    
    caja = cursor.fetchone()
    
    if not caja:
        flash('Caja no encontrada', 'danger')
        return redirect(url_for('caja_historial'))
    
    # Obtener todas las ventas de esta caja
    cursor.execute("""
        SELECT 
            v.*,
            COUNT(dv.id) as total_items,
            GROUP_CONCAT(DISTINCT 
                CASE 
                    WHEN dv.tipo_detalle = 'producto' THEN 
                        CONCAT(p.nombre, ' (x', dv.cantidad, ')')
                    WHEN dv.tipo_detalle = 'servicio' THEN 
                        CONCAT(s.nombre, ' (x', dv.cantidad, ')')
                    WHEN dv.tipo_detalle = 'combo' THEN 
                        CONCAT(cm.nombre, ' (x', dv.cantidad, ')')
                END
            ) as items_resumen
        FROM ventas v
        LEFT JOIN detalles_venta dv ON v.id = dv.venta_id
        LEFT JOIN productos p ON dv.tipo_detalle = 'producto' AND dv.referencia_id = p.id
        LEFT JOIN servicios s ON dv.tipo_detalle = 'servicio' AND dv.referencia_id = s.id
        LEFT JOIN combos cm ON dv.tipo_detalle = 'combo' AND dv.referencia_id = cm.id
        WHERE v.caja_id = %s
        GROUP BY v.id
        ORDER BY v.fecha_venta DESC
    """, (caja_id,))
    
    ventas = cursor.fetchall()
    
    # Calcular resumen de ventas
    resumen_ventas = {
        'total_ventas': len(ventas),
        'monto_total': sum(float(v['total_venta']) for v in ventas),
        'efectivo_recibido': sum(float(v['efectivo']) for v in ventas),
        'total_cambio': sum(float(v['cambio']) for v in ventas),
        'venta_promedio': sum(float(v['total_venta']) for v in ventas) / len(ventas) if ventas else 0
    }
    
    cursor.close()
    
    return render_template('admin/caja/detalle.html',
                         caja=caja,
                         ventas=ventas,
                         resumen_ventas=resumen_ventas)


@app.route('/caja/resumen_dia')
@login_required
def caja_resumen_dia():
    """Resumen de todas las cajas del día actual"""
    cursor = mysql.connection.cursor(DictCursor)
    
    # Obtener todas las cajas cerradas hoy
    cursor.execute("""
        SELECT 
            c.*,
            u.nombre as usuario_nombre,
            (SELECT COUNT(*) FROM ventas WHERE caja_id = c.id) as total_ventas_realizadas,
            (SELECT COALESCE(SUM(total_venta), 0) FROM ventas WHERE caja_id = c.id) as monto_ventas_total
        FROM caja c
        INNER JOIN usuarios u ON c.usuario_id = u.id
        WHERE DATE(c.fecha_apertura) = CURDATE()
        ORDER BY c.fecha_apertura DESC
    """)
    
    cajas_dia = cursor.fetchall()
    
    # Obtener cajas abiertas actualmente
    cursor.execute("""
        SELECT 
            c.*,
            u.nombre as usuario_nombre,
            (SELECT COUNT(*) FROM ventas WHERE caja_id = c.id AND DATE(fecha_venta) = CURDATE()) as ventas_hoy
        FROM caja c
        INNER JOIN usuarios u ON c.usuario_id = u.id
        WHERE c.estado = 'abierta'
        ORDER BY c.fecha_apertura
    """)
    
    cajas_abiertas = cursor.fetchall()
    
    # Calcular resumen del día
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT c.id) as total_cajas,
            SUM(c.total_ventas) as total_ventas_dia,
            SUM(c.total_efectivo) as total_efectivo_dia,
            SUM(c.diferencia) as diferencia_total_dia,
            COUNT(DISTINCT c.usuario_id) as total_vendedores
        FROM caja c
        WHERE DATE(c.fecha_apertura) = CURDATE() AND c.estado = 'cerrada'
    """)
    
    resumen_dia = cursor.fetchone()
    
    cursor.close()
    
    return render_template('admin/caja/resumen_dia.html',
                         cajas_dia=cajas_dia,
                         cajas_abiertas=cajas_abiertas,
                         resumen_dia=resumen_dia)


@app.route('/caja/verificar_estado')
@login_required
def caja_verificar_estado():
    """API para verificar estado de caja (para AJAX)"""
    cursor = mysql.connection.cursor(DictCursor)
    
    cursor.execute("""
        SELECT 
            c.id,
            c.monto_apertura,
            c.total_ventas,
            c.total_efectivo,
            c.fecha_apertura,
            (c.monto_apertura + c.total_efectivo) as total_disponible,
            (SELECT COUNT(*) FROM ventas WHERE caja_id = c.id AND DATE(fecha_venta) = CURDATE()) as ventas_hoy
        FROM caja c
        WHERE c.usuario_id = %s AND c.estado = 'abierta'
    """, (session['usuario_id'],))
    
    caja_activa = cursor.fetchone()
    cursor.close()
    
    if caja_activa:
        return jsonify({
            'success': True,
            'tiene_caja_activa': True,
            'caja': {
                'id': caja_activa['id'],
                'monto_apertura': float(caja_activa['monto_apertura']),
                'total_ventas': float(caja_activa['total_ventas']),
                'total_efectivo': float(caja_activa['total_efectivo']),
                'total_disponible': float(caja_activa['total_disponible']),
                'ventas_hoy': caja_activa['ventas_hoy'],
                'fecha_apertura': caja_activa['fecha_apertura'].strftime('%d/%m/%Y %H:%M')
            }
        })
    else:
        return jsonify({
            'success': True,
            'tiene_caja_activa': False
        })

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

# Variable global para cache simple
_stock_cache = {
    'data': None,
    'timestamp': None
}

@app.route('/inventario')
@admin_required
def inventario():
    cursor = mysql.connection.cursor(DictCursor)
    
    # Verificar cache (opcional, 30 segundos de cache)
    if _stock_cache['data'] and _stock_cache['timestamp'] and \
       datetime.now() - _stock_cache['timestamp'] < timedelta(seconds=30):
        productos_stock = _stock_cache['data']
        
        # Solo obtener movimientos nuevos
        cursor.execute('''
            SELECT mi.*, p.nombre as producto_nombre, p.codigo,
                   u.nombre as unidad_nombre, u.abreviatura,
                   us.nombre as usuario_nombre
            FROM movimientos_inventario mi
            JOIN productos p ON mi.producto_id = p.id
            LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
            LEFT JOIN usuarios us ON mi.usuario_id = us.id
            ORDER BY mi.fecha_movimiento DESC
            LIMIT 100
        ''')
        movimientos = cursor.fetchall()
        cursor.close()
        
        return render_template('admin/inventario/inventario.html', 
                             movimientos=movimientos,
                             productos_stock=productos_stock)
    
    # Si no hay cache, obtener todo
    cursor.execute('''
        SELECT mi.*, p.nombre as producto_nombre, p.codigo,
               u.nombre as unidad_nombre, u.abreviatura,
               us.nombre as usuario_nombre
        FROM movimientos_inventario mi
        JOIN productos p ON mi.producto_id = p.id
        LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
        LEFT JOIN usuarios us ON mi.usuario_id = us.id
        ORDER BY mi.fecha_movimiento DESC
        LIMIT 100
    ''')
    movimientos = cursor.fetchall()
    
    cursor.execute('''
        SELECT p.id, p.nombre, p.codigo, 
               CAST(COALESCE(p.stock_actual, 0) AS SIGNED) as stock_actual,
               CAST(COALESCE(p.stock_minimo, 0) AS SIGNED) as stock_minimo,
               u.abreviatura as unidad
        FROM productos p
        LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
        WHERE p.activo = 1
        ORDER BY p.nombre
    ''')
    productos_stock = cursor.fetchall()
    cursor.close()
    
    # Actualizar cache
    _stock_cache['data'] = productos_stock
    _stock_cache['timestamp'] = datetime.now()
    
    return render_template('admin/inventario/inventario.html', 
                         movimientos=movimientos,
                         productos_stock=productos_stock)


@app.route('/inventario/entrada', methods=['GET', 'POST'])
@admin_required
def entrada_inventario():
    cursor = mysql.connection.cursor(DictCursor)
    
    if request.method == 'POST':
        producto_id = request.form['producto_id']
        cantidad = int(request.form['cantidad'])
        observaciones = request.form.get('observaciones', '')
        referencia_tipo = request.form.get('referencia_tipo', 'manual')
        referencia_id = request.form.get('referencia_id')
        
        # Validar cantidad positiva
        if cantidad <= 0:
            flash('La cantidad debe ser mayor a cero', 'error')
            return redirect(url_for('entrada_inventario'))
        
        # Obtener cantidad actual del producto
        cursor.execute('SELECT stock_actual FROM productos WHERE id = %s', (producto_id,))
        producto = cursor.fetchone()
        
        if not producto:
            flash('Producto no encontrado', 'error')
            return redirect(url_for('entrada_inventario'))
            
        cantidad_anterior = producto['stock_actual']
        cantidad_nueva = cantidad_anterior + cantidad
        
        # CORRECCIÓN: Convertir referencia_id a None si está vacío
        if referencia_id == '':
            referencia_id = None
        else:
            try:
                referencia_id = int(referencia_id)
            except (ValueError, TypeError):
                referencia_id = None
        
        # Insertar movimiento
        cursor.execute('''
            INSERT INTO movimientos_inventario 
            (producto_id, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva,
             referencia_tipo, referencia_id, usuario_id, observaciones)
            VALUES (%s, 'entrada', %s, %s, %s, %s, %s, %s, %s)
        ''', (producto_id, cantidad, cantidad_anterior, cantidad_nueva,
              referencia_tipo, referencia_id, session['usuario_id'], observaciones))
        
        # Actualizar stock del producto
        cursor.execute('''
            UPDATE productos 
            SET stock_actual = stock_actual + %s 
            WHERE id = %s
        ''', (cantidad, producto_id))
        
        mysql.connection.commit()
        cursor.close()
        
        flash('Entrada de inventario registrada exitosamente', 'success')
        return redirect(url_for('inventario'))
    
    # GET - mostrar formulario
    cursor.execute('''
        SELECT p.*, u.abreviatura as unidad, u.nombre as unidad_nombre
        FROM productos p
        LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
        WHERE p.activo = 1
        ORDER BY p.nombre
    ''')
    productos = cursor.fetchall()
    cursor.close()
    
    return render_template('admin/inventario/entrada_inventario.html', productos=productos)


@app.route('/inventario/salida', methods=['GET', 'POST'])
@admin_required
def salida_inventario():
    cursor = mysql.connection.cursor(DictCursor)
    
    if request.method == 'POST':
        producto_id = request.form['producto_id']
        cantidad = int(request.form['cantidad'])
        observaciones = request.form.get('observaciones', '')
        referencia_tipo = request.form.get('referencia_tipo', 'manual')
        referencia_id = request.form.get('referencia_id')
        
        # Validar cantidad positiva
        if cantidad <= 0:
            flash('La cantidad debe ser mayor a cero', 'error')
            return redirect(url_for('salida_inventario'))
        
        # Verificar stock suficiente
        cursor.execute('SELECT stock_actual FROM productos WHERE id = %s', (producto_id,))
        producto = cursor.fetchone()
        
        if not producto:
            flash('Producto no encontrado', 'error')
            return redirect(url_for('salida_inventario'))
        
        if producto['stock_actual'] < cantidad:
            flash(f'No hay suficiente stock. Stock actual: {producto["stock_actual"]}', 'error')
            return redirect(url_for('salida_inventario'))
        
        cantidad_anterior = producto['stock_actual']
        cantidad_nueva = cantidad_anterior - cantidad
        
        # Insertar movimiento (cantidad negativa para salidas)
        cursor.execute('''
            INSERT INTO movimientos_inventario 
            (producto_id, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva,
             referencia_tipo, referencia_id, usuario_id, observaciones)
            VALUES (%s, 'salida', %s, %s, %s, %s, %s, %s, %s)
        ''', (producto_id, -cantidad, cantidad_anterior, cantidad_nueva,
              referencia_tipo, referencia_id, session['usuario_id'], observaciones))
        
        # Actualizar stock del producto
        cursor.execute('''
            UPDATE productos 
            SET stock_actual = stock_actual - %s 
            WHERE id = %s
        ''', (cantidad, producto_id))
        
        mysql.connection.commit()
        cursor.close()
        
        flash('Salida de inventario registrada exitosamente', 'success')
        return redirect(url_for('inventario'))
    
    # GET - mostrar formulario - CORREGIDO: campo correcto unidad_base_id
    cursor.execute('''
        SELECT p.*, u.abreviatura as unidad, u.nombre as unidad_nombre
        FROM productos p
        LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
        WHERE p.activo = 1 AND p.stock_actual > 0
        ORDER BY p.nombre
    ''')
    productos = cursor.fetchall()
    cursor.close()
    
    return render_template('admin/inventario/salida_inventario.html', productos=productos)


@app.route('/inventario/ajuste', methods=['GET', 'POST'])
@admin_required
def ajuste_inventario():
    cursor = mysql.connection.cursor(DictCursor)
    
    if request.method == 'POST':
        producto_id = request.form['producto_id']
        cantidad_nueva = int(request.form['cantidad_nueva'])
        observaciones = request.form.get('observaciones', '')
        
        # Validar cantidad no negativa
        if cantidad_nueva < 0:
            flash('La cantidad no puede ser negativa', 'error')
            return redirect(url_for('ajuste_inventario'))
        
        # Obtener cantidad actual
        cursor.execute('SELECT stock_actual FROM productos WHERE id = %s', (producto_id,))
        producto = cursor.fetchone()
        
        if not producto:
            flash('Producto no encontrado', 'error')
            return redirect(url_for('ajuste_inventario'))
            
        cantidad_anterior = producto['stock_actual']
        cantidad_ajuste = cantidad_nueva - cantidad_anterior
        
        # Insertar movimiento
        cursor.execute('''
            INSERT INTO movimientos_inventario 
            (producto_id, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva,
             referencia_tipo, usuario_id, observaciones)
            VALUES (%s, 'ajuste', %s, %s, %s, 'ajuste_manual', %s, %s)
        ''', (producto_id, cantidad_ajuste, cantidad_anterior, cantidad_nueva,
              session['usuario_id'], observaciones))
        
        # Actualizar stock del producto
        cursor.execute('''
            UPDATE productos 
            SET stock_actual = %s 
            WHERE id = %s
        ''', (cantidad_nueva, producto_id))
        
        mysql.connection.commit()
        cursor.close()
        
        flash('Ajuste de inventario realizado exitosamente', 'success')
        return redirect(url_for('inventario'))
    
    # GET - mostrar formulario - CORREGIDO: campo correcto unidad_base_id
    cursor.execute('''
        SELECT p.*, u.abreviatura as unidad, u.nombre as unidad_nombre
        FROM productos p
        LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
        WHERE p.activo = 1
        ORDER BY p.nombre
    ''')
    productos = cursor.fetchall()
    cursor.close()
    
    return render_template('admin/inventario/ajuste_inventario.html', productos=productos)


@app.route('/inventario/producto/<int:producto_id>')
@admin_required
def historial_producto(producto_id):
    cursor = mysql.connection.cursor(DictCursor)
    
    # Información del producto - CORREGIDO: campo correcto unidad_base_id
    cursor.execute('''
        SELECT p.*, u.abreviatura as unidad, u.nombre as unidad_nombre
        FROM productos p
        LEFT JOIN unidades_medida u ON p.unidad_base_id = u.id
        WHERE p.id = %s
    ''', (producto_id,))
    producto = cursor.fetchone()
    
    if not producto:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('inventario'))
    
    # Historial de movimientos
    cursor.execute('''
        SELECT mi.*, us.nombre as usuario_nombre
        FROM movimientos_inventario mi
        LEFT JOIN usuarios us ON mi.usuario_id = us.id
        WHERE mi.producto_id = %s
        ORDER BY mi.fecha_movimiento DESC
    ''', (producto_id,))
    
    movimientos = cursor.fetchall()
    cursor.close()
    
    now = date.today()
    
    return render_template('admin/inventario/historial_producto.html', 
                         producto=producto, 
                         movimientos=movimientos,
                         now=now)

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

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

# Manejo de errores
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
