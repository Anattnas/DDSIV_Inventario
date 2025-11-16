import sqlite3

# Conexión a la base de datos
conn = sqlite3.connect('ConexionBD/InventarioBD_2.db')
cursor = conn.cursor()

# Datos del segundo usuario
usuario = 'productor1'
password = '123456'
cargo = 'productor'

# Insertar usuario
cursor.execute(
    "INSERT INTO usuarios (usuario, pass, cargo) VALUES (?, ?, ?)",
    (usuario, password, cargo)
)

conn.commit()
conn.close()

print("Usuario 'productor1' agregado correctamente.")
