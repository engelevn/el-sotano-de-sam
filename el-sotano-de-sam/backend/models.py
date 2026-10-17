from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='cliente')  # 'admin' o 'cliente'
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def es_admin(self):
        return self.rol == 'admin'


class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    marca = db.Column(db.String(80))
    talla = db.Column(db.String(20))
    categoria = db.Column(db.String(80))
    precio = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default='disponible')
    stock = db.Column(db.Integer, default=0)
    fecha_ingreso = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'marca': self.marca,
            'talla': self.talla,
            'categoria': self.categoria,
            'precio': self.precio,
            'estado': self.estado,
            'stock': self.stock,
            'fecha_ingreso': self.fecha_ingreso.isoformat() if self.fecha_ingreso else None,
        }