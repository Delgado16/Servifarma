# Rutas adicionales para administrador
# Importar en app.py: from routes_admin import *

from flask import render_template, request, jsonify
from app import app, mysql, admin_required, login_required
import MySQLdb.cursors

# ========================
# PÁGINAS HTML ADMIN
# ========================

@app.route('/admin/productos')
@admin_required
def admin_productos():
    return render_template('admin/productos.html')

@app.route('/admin/compras')
@admin_required
def admin_compras():
    return render_template('admin/compras.html')

@app.route('/admin/proveedores')
@admin_required
def admin_proveedores():
    return render_template('admin/proveedores.html')

@app.route('/admin/combos')
@admin_required
def admin_combos():
    return render_template('admin/combos.html')

@app.route('/admin/reportes')
@admin_required
def admin_reportes():
    return render_template('admin/reportes.html')

@app.route('/admin/movimientos')
@admin_required
def admin_movimientos():
    return render_template('admin/movimientos.html')

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    return render_template('admin/usuarios.html')

# ========================
# API VARIACIONES DE UNIDAD
# ========================

@app.route('/api/variaciones/<int:producto_id>', methods=['GET', 'POST'])
@admin_required
def api_variaciones(producto_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'GET':
        cursor.execute('''
            SELECT vp.*, u.nombre as unidad_nombre
            FROM variaciones_producto vp
            LEFT JOIN unidades_medida u ON vp.unidad_id = u.id
            WHERE vp.producto_id = %s AND vp.activo = TRUE
        ''', (producto_id,))
        variaciones = cursor.fetchall()
        cursor.close()
        return jsonify(variaciones)
    
    elif request.method == 'POST':
        data = request.get_json()
        
        cursor.execute('''
            INSERT INTO variaciones_producto (producto_id, unidad_id, cantidad_equivalente, 
                                             precio_venta, descripcion)
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            producto_id,
            data['unidad_id'],
            data['cantidad_equivalente'],
            data.get('precio_venta'),
            data.get('descripcion', '')
        ))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True})

# ========================
# API MOVIMIENTOS
# ========================

@app.route('/api/movimientos', methods=['GET'])
@admin_required
def api_movimientos():
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    
    query = '''
        SELECT m.*, p.nombre as producto_nombre, u.nombre as usuario_nombre
        FROM movimientos_inventario m
        LEFT JOIN productos p ON m.producto_id = p.id
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        WHERE 1=1
    '''
    params = []
    
    if fecha_inicio:
        query += ' AND DATE(m.fecha_movimiento) >= %s'
        params.append(fecha_inicio)
    
    if fecha_fin:
        query += ' AND DATE(m.fecha_movimiento) <= %s'
        params.append(fecha_fin)
    
    query += ' ORDER BY m.fecha_movimiento DESC LIMIT 500'
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query, params)
    movimientos = cursor.fetchall()
    cursor.close()
    
    return jsonify(movimientos)

# ========================
# API USUARIOS
# ========================

@app.route('/api/usuarios', methods=['GET', 'POST'])
@admin_required
def api_usuarios():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'GET':
        cursor.execute('SELECT id, nombre, email, rol, activo FROM usuarios')
        usuarios = cursor.fetchall()
        cursor.close()
        return jsonify(usuarios)
    
    elif request.method == 'POST':
        data = request.get_json()
        from app import hash_password
        
        hashed = hash_password(data['contrasena'])
        
        cursor.execute('''
            INSERT INTO usuarios (nombre, email, contrasena, rol, activo)
            VALUES (%s, %s, %s, %s, TRUE)
        ''', (
            data['nombre'],
            data['email'],
            hashed,
            data['rol']
        ))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True})

@app.route('/api/usuarios/<int:usuario_id>', methods=['PUT', 'DELETE'])
@admin_required
def api_usuario_detail(usuario_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'PUT':
        data = request.get_json()
        
        query = 'UPDATE usuarios SET nombre = %s, rol = %s'
        params = [data['nombre'], data['rol']]
        
        if 'contrasena' in data and data['contrasena']:
            from app import hash_password
            query += ', contrasena = %s'
            params.append(hash_password(data['contrasena']))
        
        query += ' WHERE id = %s'
        params.append(usuario_id)
        
        cursor.execute(query, params)
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        cursor.execute('UPDATE usuarios SET activo = FALSE WHERE id = %s', (usuario_id,))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True})

# ========================
# API UNIDADES DE MEDIDA
# ========================

@app.route('/api/unidades', methods=['GET'])
@login_required
def api_unidades():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM unidades_medida')
    unidades = cursor.fetchall()
    cursor.close()
    return jsonify(unidades)

# ========================
# API CATEGORÍAS
# ========================

@app.route('/api/categorias', methods=['GET', 'POST'])
@login_required
def api_categorias():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'GET':
        cursor.execute('SELECT * FROM categorias')
        categorias = cursor.fetchall()
        cursor.close()
        return jsonify(categorias)
    
    elif request.method == 'POST':
        data = request.get_json()
        
        cursor.execute('''
            INSERT INTO categorias (nombre, descripcion)
            VALUES (%s, %s)
        ''', (
            data['nombre'],
            data.get('descripcion', '')
        ))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True})

# ========================
# PÁGINAS ADICIONALES
# ========================

@app.route('/admin/combos')
@admin_required
def admin_combo_page():
    return render_template('admin/combos.html')

# API Combos CRUD
@app.route('/api/combos/<int:combo_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_required
def api_combo_detail(combo_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'GET':
        cursor.execute('SELECT * FROM combos WHERE id = %s', (combo_id,))
        combo = cursor.fetchone()
        
        cursor.execute('''
            SELECT dc.*, p.nombre as producto_nombre, u.nombre as unidad_nombre
            FROM detalles_combo dc
            LEFT JOIN productos p ON dc.producto_id = p.id
            LEFT JOIN unidades_medida u ON dc.unidad_id = u.id
            WHERE dc.combo_id = %s
        ''', (combo_id,))
        detalles = cursor.fetchall()
        
        cursor.close()
        
        if combo:
            combo['detalles'] = detalles
            return jsonify(combo)
        return jsonify({'error': 'Combo no encontrado'}), 404
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        cursor.execute('''
            UPDATE combos SET nombre = %s, descripcion = %s, precio_combo = %s
            WHERE id = %s
        ''', (
            data['nombre'],
            data.get('descripcion', ''),
            data['precio_combo'],
            combo_id
        ))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        cursor.execute('UPDATE combos SET activo = FALSE WHERE id = %s', (combo_id,))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True})
