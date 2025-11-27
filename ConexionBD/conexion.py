import sqlite3  # Importamos el módulo sqlite3 para manejar la base de datos SQLite

# Ruta de la base de datos dentro de la carpeta ConexionBD
DB_PATH = 'ConexionBD/InventarioBD_2.db'


def get_connection():
    """
    Retorna una conexión a la base de datos InventarioBD_2.db
    """
    try:
        # Se abre la conexión con la base de datos
        conn = sqlite3.connect(DB_PATH)
        # Configuramos que las filas se puedan acceder como diccionarios
        conn.row_factory = sqlite3.Row
        # Retornamos la conexión lista para usar
        return conn
    except sqlite3.Error as e:
        # Si ocurre un error al abrir la conexión, se imprime
        print(f"Error al conectar a la BD: {e}")
        # Retornamos None para indicar que no se pudo conectar
        return None


def init_connection(tabla):
    """
    Intenta conectarse y verifica que la tabla especificada exista.
    Retorna un mensaje de éxito o error.
    """
    # Obtenemos la conexión a la base de datos
    conn = get_connection()
    if conn:
        try:
            # Creamos un cursor para ejecutar comandos SQL
            cursor = conn.cursor()
            # Intentamos seleccionar al menos un registro de la tabla para verificar que existe
            cursor.execute(f"SELECT * FROM {tabla} LIMIT 1")
            # Cerramos la conexión después de la consulta
            conn.close()
            # Retornamos un mensaje de éxito
            return f"Conexión a la BD-{tabla} exitosa"
        except sqlite3.Error as e:
            # Si ocurre un error al consultar la tabla, retornamos un mensaje de error
            return f"Error al consultar la tabla {tabla}: {e}"
    else:
        # Si la conexión no se pudo abrir, retornamos un mensaje de error general
        return "Error al conectar a la base de datos"
