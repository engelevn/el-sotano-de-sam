from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from database import conectar, crear_tabla

app = Flask(__name__)
CORS(app)

# Crear tabla al iniciar
crear_tabla()


@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM productos")
    productos = [dict(row) for row in cursor.fetchall()]

    conexion.close()
    return jsonify(productos)


@app.route('/api/productos', methods=['POST'])
def agregar_producto():
    datos = request.json

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
    INSERT INTO productos (nombre, marca, talla, categoria, precio, estado, stock)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datos['nombre'],
        datos['marca'],
        datos['talla'],
        datos['categoria'],
        datos['precio'],
        datos['estado'],
        datos['stock']
    ))

    conexion.commit()
    nuevo_id = cursor.lastrowid
    conexion.close()

    return jsonify({
        "mensaje": "Producto agregado exitosamente",
        "id": nuevo_id
    })


if __name__ == '__main__':
    app.run(debug=True)