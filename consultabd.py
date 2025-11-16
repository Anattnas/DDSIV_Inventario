import sqlite3

# Ruta a tu base de datos
db_path = 'ConexionBD/InventarioBD_2.db'

# Conexión a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1️⃣ Listar todas las tablas de la base de datos
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = cursor.fetchall()
print("Tablas en la base de datos:")
for tabla in tablas:
    print("-", tabla[0])

# 2️⃣ Opcional: mostrar las primeras filas de cada tabla
for tabla in tablas:
    print(f"\nContenido de la tabla '{tabla[0]}':")
    cursor.execute(f"SELECT * FROM {tabla[0]} LIMIT 10;")
    filas = cursor.fetchall()
    for fila in filas:
        print(fila)

# Cerrar conexión
conn.close()
