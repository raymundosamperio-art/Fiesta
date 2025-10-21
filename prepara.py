import sqlite3

# Conexión a la base de datos (se crea si no existe)
conn = sqlite3.connect("invitados.db")
c = conn.cursor()

# Crear tabla de invitados
c.execute("""
CREATE TABLE IF NOT EXISTS invitados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    telefono TEXT,
    correo TEXT,
    asistira TEXT CHECK(asistira IN ('Sí', 'No', 'No ha confirmado')) DEFAULT 'No ha confirmado',
    acompanantes INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()

print("✅ Base de datos y tabla 'invitados' creadas correctamente.")
