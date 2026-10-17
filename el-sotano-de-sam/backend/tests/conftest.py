import os
import sys

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'  # base temporal en memoria
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import app as flask_app
from models import Usuario, db


@pytest.fixture
def app():
    flask_app.config.update(TESTING=True)
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def crear_usuario(email, rol, password='clave-segura-123'):
    u = Usuario(email=email, rol=rol)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return u