# ============================================
# app.py — Servidor Flask con API REST
# El Sótano de Sam — Stock en Línea
# ============================================

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import conectar, crear_tabla

# Ruta al frontend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)
crear_tabla()

# ==========================================
# RUTAS FRONTEND
# ==========================================
@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/login')
def login():
    return send_from_directory(FRONTEND_DIR, 'login.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory(FRONTEND_DIR, 'dashboard.html')

# ==========================================
# RUTA 1: Obtener todos los productos (GET)
# ==========================================
@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM productos ORDER BY id DESC')
    productos = [dict(row) for row in cursor.fetchall()]
    conexion.close()
    return jsonify(productos), 200

# ==========================================
# RUTA 2: Agregar un producto nuevo (POST)
# ==========================================
@app.route('/api/productos', methods=['POST'])
def agregar_producto():
    datos = request.get_json()
    if not datos.get('nombre') or not datos.get('precio'):
        return jsonify({'error': 'Nombre y precio son obligatorios'}), 400
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO productos (nombre, marca, talla, categoria, precio, estado, stock)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        datos['nombre'], datos.get('marca', ''), datos.get('talla', ''),
        datos.get('categoria', ''), datos['precio'],
        datos.get('estado', 'disponible'), datos.get('stock', 0)
    ))
    conexion.commit()
    nuevo_id = cursor.lastrowid
    conexion.close()
    return jsonify({'mensaje': 'Producto agregado exitosamente', 'id': nuevo_id}), 201

# ==========================================
# RUTA 3: Actualizar un producto (PUT)
# ==========================================
@app.route('/api/productos/<int:id>', methods=['PUT'])
def actualizar_producto(id):
    datos = request.get_json()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''
        UPDATE productos 
        SET nombre=?, marca=?, talla=?, categoria=?, precio=?, estado=?, stock=?
        WHERE id=?
    ''', (
        datos.get('nombre'), datos.get('marca'), datos.get('talla'),
        datos.get('categoria'), datos.get('precio'),
        datos.get('estado'), datos.get('stock'), id
    ))
    conexion.commit()
    conexion.close()
    return jsonify({'mensaje': 'Producto actualizado exitosamente'}), 200

# ==========================================
# RUTA 4: Eliminar un producto (DELETE)
# ==========================================
@app.route('/api/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('DELETE FROM productos WHERE id=?', (id,))
    conexion.commit()
    conexion.close()
    return jsonify({'mensaje': 'Producto eliminado exitosamente'}), 200

# ==========================================
# RUTA 5: Buscar un producto por ID (GET)
# ==========================================
@app.route('/api/productos/<int:id>', methods=['GET'])
def obtener_producto(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM productos WHERE id=?', (id,))
    producto = cursor.fetchone()
    conexion.close()
    if producto:
        return jsonify(dict(producto)), 200
    else:
        return jsonify({'error': 'Producto no encontrado'}), 404

# ==========================================
# Iniciar el servidor
# ==========================================
if __name__ == '__main__':
    print("=" * 50)
    print("  EL SÓTANO DE SAM — Servidor API")
    print("  http://127.0.0.1:5000")
    print("=" * 50)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)