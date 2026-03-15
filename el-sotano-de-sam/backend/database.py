import sqlite3

def conectar():
    conexion = sqlite3.connect('sotano.db')
    conexion.row_factory = sqlite3.Row
    return conexion

def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            marca TEXT,
            talla TEXT,
            categoria TEXT,
            precio REAL NOT NULL,
            estado TEXT DEFAULT 'disponible',
            stock INTEGER DEFAULT 0,
            fecha_ingreso TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conexion.commit()
    conexion.close()
    print("Tabla 'productos' creada exitosamente")

if __name__ == '__main__':
    crear_tabla()