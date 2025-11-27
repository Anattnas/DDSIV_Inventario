import sqlite3

# Ruta a tu base de datos
db_path = 'ConexionBD/InventarioBD_2.db'

# Conexión
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Obtener todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = cursor.fetchall()

print("\n📌 TABLAS EN LA BASE DE DATOS:\n")
for tabla in tablas:
    print("- " + tabla[0])

print("\n📌 ESTRUCTURA DE CADA TABLA:\n")
for tabla in tablas:
    nombre_tabla = tabla[0]
    print(f"\n🔹 Tabla: {nombre_tabla}")
    print("-" * 40)

    # Describir columnas
    cursor.execute(f"PRAGMA table_info({nombre_tabla});")
    columnas = cursor.fetchall()

    for col in columnas:
        cid, nombre, tipo, notnull, default, pk = col
        print(
            f"Columna: {nombre} | Tipo: {tipo} | NOT NULL: {notnull} | PK: {pk} | Default: {default}")

    # Mostrar primeras filas
    cursor.execute(f"SELECT * FROM {nombre_tabla} LIMIT 5;")
    filas = cursor.fetchall()
    print("\nEjemplo de registros:")
    for fila in filas:
        print(fila)
    print("\n" + "-"*40)

# Cerrar conexión
conn.close()
