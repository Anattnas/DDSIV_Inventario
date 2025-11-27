import sqlite3

# Ruta a tu base de datos
db_path = 'ConexionBD/InventarioBD_2.db'

# Conexión
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Usuarios a eliminar
usuarios_a_eliminar = ['almacen1', 'productor1']

# Ejecutar borrado
for usuario in usuarios_a_eliminar:
    cursor.execute("DELETE FROM usuarios WHERE usuario = ?", (usuario,))
    print(f"Usuario eliminado: {usuario}")

# Guardar cambios y cerrar conexión
conn.commit()
conn.close()

print("Eliminación completada.")
