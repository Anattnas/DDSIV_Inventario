import sqlite3

# Conexión a la base de datos
conexion = sqlite3.connect('ConexionBD/InventarioBD_2.db')
cursor = conexion.cursor()

# Agregar columnas si no existen
try:
    cursor.execute("ALTER TABLE productos ADD COLUMN ultimo_usuario TEXT")
except sqlite3.OperationalError:
    print("La columna 'ultimo_usuario' ya existe.")

try:
    cursor.execute("ALTER TABLE productos ADD COLUMN ultima_modificacion TEXT")
except sqlite3.OperationalError:
    print("La columna 'ultima_modificacion' ya existe.")

conexion.commit()
conexion.close()

print("Campos agregados correctamente a la tabla 'productos'.")
