from conftest import crear_usuario

PRODUCTO = {'nombre': 'Chaqueta vintage', 'precio': 85000}


def login(client, email, password='clave-segura-123'):
    return client.post('/api/login', json={'email': email, 'password': password})


def test_crear_producto_sin_login_da_401(client):
    assert client.post('/api/productos', json=PRODUCTO).status_code == 401


def test_login_con_clave_incorrecta_da_401(client):
    crear_usuario('admin@test.com', 'admin')
    assert login(client, 'admin@test.com', 'mala').status_code == 401


def test_login_con_correo_inexistente_da_401(client):
    assert login(client, 'nadie@test.com').status_code == 401


def test_admin_puede_crear_producto(client):
    crear_usuario('admin@test.com', 'admin')
    login(client, 'admin@test.com')
    assert client.post('/api/productos', json=PRODUCTO).status_code == 201


def test_cliente_no_puede_crear_producto(client):
    crear_usuario('cliente@test.com', 'cliente')
    login(client, 'cliente@test.com')
    assert client.post('/api/productos', json=PRODUCTO).status_code == 403


def test_precio_negativo_da_400(client):
    crear_usuario('admin@test.com', 'admin')
    login(client, 'admin@test.com')
    r = client.post('/api/productos', json={'nombre': 'x', 'precio': -5})
    assert r.status_code == 400