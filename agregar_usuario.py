import sqlite3

# Conexión a la base de datos
conn = sqlite3.connect('ConexionBD/InventarioBD_2.db')
cursor = conn.cursor()

# Datos del usuario a insertar
usuario = 'almacen1'
password = '123456'
cargo = 'almacen'

# Insertar usuario
cursor.execute(
    "INSERT INTO usuarios (usuario, pass, cargo) VALUES (?, ?, ?)",
    (usuario, password, cargo)
)

conn.commit()
conn.close()

print("Usuario 'almacen1' agregado correctamente.")
