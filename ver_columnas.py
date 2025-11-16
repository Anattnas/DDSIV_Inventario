import sqlite3

# Conectamos a la base de datos
conexion = sqlite3.connect('ConexionBD/InventarioBD_2.db')
cursor = conexion.cursor()

# Ejecutamos PRAGMA para ver la estructura de la tabla productos
cursor.execute("PRAGMA table_info(productos);")
columnas = cursor.fetchall()

# Mostramos la información de las columnas
for columna in columnas:
    print(columna)

conexion.close()
