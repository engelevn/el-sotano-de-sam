import os
from functools import wraps

import click
from flask import Flask, jsonify, redirect, request, send_from_directory
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from flask_migrate import Migrate

from models import Producto, Usuario, db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

# ---------- Configuración ----------
en_produccion = bool(os.environ.get('RENDER'))
secret = os.environ.get('SECRET_KEY')
if en_produccion and not secret:
    raise RuntimeError('Falta la variable de entorno SECRET_KEY')
app.config['SECRET_KEY'] = secret or 'solo-para-desarrollo-local'

db_url = os.environ.get('DATABASE_URL',
                        'sqlite:///' + os.path.join(BASE_DIR, 'sotano.db'))
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = en_produccion

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def cargar_usuario(user_id):
    return db.session.get(Usuario, int(user_id))


@login_manager.unauthorized_handler
def no_autenticado():
    return jsonify({'error': 'Debes iniciar sesión'}), 401


def admin_required(f):
    @wraps(f)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.es_admin:
            return jsonify({'error': 'Permisos insuficientes'}), 403
        return f(*args, **kwargs)
    return wrapper


# ---------- Utilidades ----------
def leer_json():
    return request.get_json(silent=True) or {}


def numero(valor, tipo):
    """Convierte a número >= 0; devuelve None si no es válido."""
    try:
        n = tipo(valor)
    except (TypeError, ValueError):
        return None
    return n if n >= 0 else None


# ---------- Páginas ----------
@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/login')
def login():
    return send_from_directory(FRONTEND_DIR, 'login.html')


@app.route('/dashboard')
def dashboard():
    if not (current_user.is_authenticated and current_user.es_admin):
        return redirect('/login')
    return send_from_directory(FRONTEND_DIR, 'dashboard.html')


# ---------- Autenticación ----------
@app.route('/api/login', methods=['POST'])
def api_login():
    datos = leer_json()
    email = (datos.get('email') or '').strip().lower()
    password = datos.get('password') or ''
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario is None or not usuario.check_password(password):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    login_user(usuario)
    return jsonify({'email': usuario.email, 'rol': usuario.rol}), 200


@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'mensaje': 'Sesión cerrada'}), 200


@app.route('/api/me', methods=['GET'])
@login_required
def api_me():
    return jsonify({'email': current_user.email, 'rol': current_user.rol}), 200


# ---------- Productos ----------
@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    productos = Producto.query.order_by(Producto.id.desc()).all()
    return jsonify([p.to_dict() for p in productos]), 200


@app.route('/api/productos/<int:id>', methods=['GET'])
def obtener_producto(id):
    producto = db.session.get(Producto, id)
    if producto is None:
        return jsonify({'error': 'Producto no encontrado'}), 404
    return jsonify(producto.to_dict()), 200


@app.route('/api/productos', methods=['POST'])
@admin_required
def agregar_producto():
    datos = leer_json()
    if not datos.get('nombre') or datos.get('precio') is None:
        return jsonify({'error': 'Nombre y precio son obligatorios'}), 400
    precio = numero(datos['precio'], float)
    stock = numero(datos.get('stock', 0), int)
    if precio is None or stock is None:
        return jsonify({'error': 'Precio y stock deben ser números mayores o iguales a 0'}), 400
    producto = Producto(
        nombre=datos['nombre'], marca=datos.get('marca', ''),
        talla=datos.get('talla', ''), categoria=datos.get('categoria', ''),
        precio=precio, estado=datos.get('estado', 'disponible'), stock=stock,
    )
    db.session.add(producto)
    db.session.commit()
    return jsonify({'mensaje': 'Producto agregado exitosamente', 'id': producto.id}), 201


@app.route('/api/productos/<int:id>', methods=['PUT'])
@admin_required
def actualizar_producto(id):
    producto = db.session.get(Producto, id)
    if producto is None:
        return jsonify({'error': 'Producto no encontrado'}), 404
    datos = leer_json()
    for campo in ('nombre', 'marca', 'talla', 'categoria', 'estado'):
        if campo in datos:
            setattr(producto, campo, datos[campo])
    if 'precio' in datos:
        precio = numero(datos['precio'], float)
        if precio is None:
            return jsonify({'error': 'Precio inválido'}), 400
        producto.precio = precio
    if 'stock' in datos:
        stock = numero(datos['stock'], int)
        if stock is None:
            return jsonify({'error': 'Stock inválido'}), 400
        producto.stock = stock
    db.session.commit()
    return jsonify({'mensaje': 'Producto actualizado exitosamente'}), 200


@app.route('/api/productos/<int:id>', methods=['DELETE'])
@admin_required
def eliminar_producto(id):
    producto = db.session.get(Producto, id)
    if producto is None:
        return jsonify({'error': 'Producto no encontrado'}), 404
    db.session.delete(producto)
    db.session.commit()
    return jsonify({'mensaje': 'Producto eliminado exitosamente'}), 200


# ---------- Comando para crear el admin ----------
@app.cli.command('crear-admin')
@click.argument('email')
def crear_admin(email):
    password = click.prompt('Contraseña (mínimo 8 caracteres)',
                            hide_input=False, confirmation_prompt=True)
    if len(password) < 8:
        raise click.ClickException('La contraseña es muy corta')
    email = email.strip().lower()
    if Usuario.query.filter_by(email=email).first():
        raise click.ClickException('Ese correo ya existe')
    admin = Usuario(email=email, rol='admin')
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    click.echo(f'Admin creado: {email}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)