import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "app.db"

def create_schema():
    """
    Crea las tablas en la base de datos 'app.db' dentro de data/ y añade índices.
    """
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo_via TEXT,
            nombre_via TEXT,
            numero_via TEXT,
            puerta TEXT,
            codigo_postal TEXT,
            cif_nif TEXT,
            telefono1 TEXT,
            telefono2 TEXT,
            telefono3 TEXT,
            telefono4 TEXT,
            mail1 TEXT,
            mail2 TEXT,
            poblacion TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_cif_nif ON clientes (cif_nif)")

    # Proyectos (actualizado para incluir la columna nombre_via)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            tipo_proyecto TEXT NOT NULL,
            calle TEXT,
            nombre_via TEXT,
            numero TEXT,
            puerta TEXT,
            codigo_postal TEXT,
            poblacion TEXT,
            nombre_proyecto TEXT,
            fecha_creacion TEXT,
            referencia TEXT UNIQUE,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_proyectos_referencia ON proyectos (referencia)")

    # Presupuestos (con dirección separada)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS presupuestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_proyecto INTEGER NOT NULL,
            referencia TEXT NOT NULL,
            fecha TEXT NOT NULL,
            tipo_via TEXT,
            nombre_via TEXT,
            numero_via TEXT,
            puerta TEXT,
            codigo_postal TEXT,
            poblacion TEXT,
            titulo TEXT,
            notas TEXT,
            tecnico_encargado TEXT,
            aprobacion TEXT,
            fecha_aprobacion TEXT,
            estado TEXT,
            FOREIGN KEY (id_proyecto) REFERENCES proyectos(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_presupuestos_referencia ON presupuestos (referencia)")

    # Capitulos (presupuestos)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS capitulos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_presupuesto INTEGER NOT NULL,
            numero TEXT NOT NULL,
            descripcion TEXT,
            FOREIGN KEY (id_presupuesto) REFERENCES presupuestos(id) ON DELETE CASCADE
        )
    """)

    # Partidas (presupuestos)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_presupuesto INTEGER NOT NULL,
            capitulo_numero TEXT NOT NULL,
            descripcion TEXT,
            unitario TEXT,
            cantidad REAL,
            precio REAL,
            total REAL,
            margen REAL,
            final REAL,
            FOREIGN KEY (id_presupuesto) REFERENCES presupuestos(id) ON DELETE CASCADE
        )
    """)

    # Proveedores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referencia TEXT UNIQUE,
            tipo TEXT,
            nombre TEXT NOT NULL,
            razon_social TEXT,
            direccion TEXT,
            codigo_postal TEXT,
            localidad TEXT,
            provincia TEXT,
            pais TEXT,
            telefono1 TEXT,
            telefono2 TEXT,
            telefono3 TEXT,
            telefono4 TEXT,
            email1 TEXT,
            email2 TEXT,
            contacto TEXT,
            contacto_telefono1 TEXT,
            contacto_telefono2 TEXT,
            contacto_email TEXT,
            fecha_alta TEXT,
            fecha_modificacion TEXT,
            facturas INTEGER DEFAULT 0,
            especialidad TEXT DEFAULT 'Ninguna'
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_proveedores_referencia ON proveedores (referencia)")

    # Hojas de Trabajo (nueva tabla para clonación en hoja de trabajo)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hojas_trabajo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_proyecto INTEGER NOT NULL,
            referencia TEXT NOT NULL,
            fecha TEXT NOT NULL,
            tipo_via TEXT,
            nombre_via TEXT,
            numero_via TEXT,
            puerta TEXT,
            codigo_postal TEXT,
            poblacion TEXT,
            titulo TEXT,
            notas TEXT,
            tecnico_encargado TEXT,
            aprobacion TEXT,
            fecha_aprobacion TEXT,
            estado TEXT,
            FOREIGN KEY (id_proyecto) REFERENCES proyectos(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hojas_referencia ON hojas_trabajo (referencia)")

    # Capitulos de Hojas de Trabajo
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS capitulos_hojas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_hoja INTEGER NOT NULL,
            numero TEXT NOT NULL,
            descripcion TEXT,
            FOREIGN KEY (id_hoja) REFERENCES hojas_trabajo(id) ON DELETE CASCADE
        )
    """)

    # Partidas de Hojas de Trabajo
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidas_hojas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_hoja INTEGER NOT NULL,
            capitulo_numero TEXT NOT NULL,
            descripcion TEXT,
            unitario TEXT,
            cantidad REAL,
            precio REAL,
            total REAL,
            margen REAL,
            final REAL,
            FOREIGN KEY (id_hoja) REFERENCES hojas_trabajo(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

class DBHelper:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def execute_query(self, query, params=(), fetch=False, fetchone=False):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = None
            if fetch:
                result = cursor.fetchall()
            elif fetchone:
                result = cursor.fetchone()
            else:
                result = cursor.lastrowid
            conn.commit()
        return result
