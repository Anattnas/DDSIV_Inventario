# Importamos Flask y módulos necesarios
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3  # Para conectarnos a la base de datos
from datetime import datetime
from flask import request


app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Es necesario para usar flash messages

# ===========================
# Ruta principal de login
# ===========================


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Página de login que valida usuario y contraseña.
    Redirige siempre a home.html y guarda usuario y cargo en session.
    """
    mensaje = ""  # Variable para mensajes flotantes

    if request.method == 'POST':
        usuario = request.form['usuario']  # Tomamos el usuario del formulario
        # Tomamos la contraseña del formulario
        password = request.form['password']

        # Encriptamos la contraseña usando MD5
        import hashlib
        password_md5 = hashlib.md5(password.encode()).hexdigest()

        try:
            # Conectamos a la base de datos
            conexion = sqlite3.connect('ConexionBD/InventarioBD_2.db')
            conexion.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
            cursor = conexion.cursor()

            # Buscamos usuario con contraseña encriptada
            cursor.execute(
                "SELECT * FROM usuarios WHERE usuario=? AND pass=?", (usuario, password_md5))
            resultado = cursor.fetchone()

            if resultado:  # Usuario válido
                cargo = resultado['cargo']

                # Guardamos usuario y cargo en session
                from flask import session
                session['usuario'] = usuario
                session['cargo'] = cargo

                # ==============================
                # ACTUALIZAR FECHA/HORA ÚLTIMO INICIO
                # ==============================
                from datetime import datetime
                ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                try:
                    # Intentamos agregar columna si no existe
                    cursor.execute(
                        "ALTER TABLE usuarios ADD COLUMN fecha_hora_ultimo_inicio TEXT")
                except sqlite3.OperationalError:
                    pass  # Si ya existe, ignoramos el error

                # Actualizamos fecha_hora_ultimo_inicio
                cursor.execute(
                    "UPDATE usuarios SET fecha_hora_ultimo_inicio=? WHERE id=?",
                    (ahora, resultado['id'])
                )
                conexion.commit()
                conexion.close()

                # Mensaje flotante en home
                from flask import flash
                flash("Inicio de sesión exitoso", "success")
                # Redirigimos siempre a home.html
                from flask import redirect, url_for
                return redirect(url_for('home'))

            else:
                mensaje = "Usuario o contraseña incorrectos"
                conexion.close()

        except sqlite3.Error as e:
            mensaje = f"Error al conectar a la base de datos: {e}"

    # Renderizamos login.html con mensaje si lo hay
    return render_template('login.html', mensaje=mensaje)

# --- NUEVA RUTA /home MODIFICASTE ESTO PARA CUMPLIR CON LA NUEVA INSTRUCCION NO BORRAR RUTA ---


@app.route('/home')
def home():
    """
    Vista principal después del login.
    Muestra contenido diferente según el cargo del usuario.
    """
    from flask import session, redirect, url_for, render_template
    if 'usuario' not in session:  # Si no hay sesión activa
        return redirect(url_for('login'))

    # Pasamos usuario y cargo a la plantilla para mostrar opciones dinámicas
    return render_template('home.html',
                           usuario=session['usuario'],
                           cargo=session['cargo'])

# ===========================
# Ruta para mostrar almacenes
# ===========================


@app.route('/almacenes')
def vista_almacenes():
    """
    Vista que muestra la lista de almacenes.
    También pasa a la plantilla los datos de último usuario y última modificación
    """
    mensaje = ""
    # Obtener filtro desde los parámetros GET
    filtro_nombre = request.args.get('nombre', '').strip()

    try:
        conexion = sqlite3.connect('ConexionBD/InventarioBD_2.db')
        cursor = conexion.cursor()

        # Construir consulta base
        consulta = "SELECT * FROM almacenes WHERE 1=1"
        parametros = []

        # Filtro por nombre
        if filtro_nombre:
            consulta += " AND nombre LIKE ?"
            parametros.append(f"%{filtro_nombre}%")

        # Ejecutar consulta con parámetros
        cursor.execute(consulta, parametros)
        almacenes = cursor.fetchall()

        # Obtener último usuario en ingresar desde la tabla usuarios
        try:
            cursor.execute(
                "SELECT usuario FROM usuarios ORDER BY fecha_hora_ultimo_inicio DESC LIMIT 1")
            resultado_usuario = cursor.fetchone()
            if resultado_usuario:
                ultimo_usuario = resultado_usuario[0]
            else:
                ultimo_usuario = ""
        except sqlite3.Error:
            ultimo_usuario = ""

        # DEJA ESTA VARIABLE AQUI VACIA POR ALGUNA RAZON HACE REFERENCIA EN almacenes.html PERO NO ENCONTRASTE DONDE
        # y no es en las tarjetas
        ultima_modificacion = ""

        conexion.close()
        mensaje = "Conexión a la BD - Almacenes exitosa"
    except sqlite3.Error as e:
        almacenes = []
        ultimo_usuario = ""
        ultima_modificacion = ""
        mensaje = f"Error al conectar a la BD - Almacenes: {e}"

    return render_template('almacenes.html',
                           almacenes=almacenes,
                           mensaje=mensaje,
                           ultimo_usuario=ultimo_usuario,
                           ultima_modificacion=ultima_modificacion,
                           cargo=session.get('cargo'))

# ===========================================
# Rutas para las opciones crud de almacenes
# ===========================================

# Ruta para el formulario de crear un nuevo almacén


@app.route('/crear_almacen', methods=['GET', 'POST'])
def crear_almacen():
    """
    Renderiza la plantilla crear_almacen.html y procesa el formulario
    para agregar un nuevo almacén a la base de datos.
    """
    if request.method == 'POST':
        nombre = request.form['nombre']

        try:
            conexion = sqlite3.connect('ConexionBD/InventarioBD_2.db')
            cursor = conexion.cursor()

            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO almacenes (nombre, ultima_modificacion, fecha_hora_creacion) VALUES (?, ?, ?)",
                           (nombre, fecha_actual, fecha_actual)
                           )
            conexion.commit()
            conexion.close()
            flash(f"Almacén '{nombre}' creado correctamente", "success")
            return redirect(url_for('vista_almacenes'))

        except sqlite3.Error as e:
            flash(f"Error al crear el almacén: {e}", "danger")
            return redirect(url_for('crear_almacen'))

    # Si es GET, simplemente renderiza la plantilla
    return render_template('crear_almacen.html')


# Ruta para el formulario de modificar un almacén existente

@app.route('/modificar_almacen/<int:almacen_id>', methods=['GET', 'POST'])
def modificar_almacen(almacen_id):
    """
    Renderiza la plantilla modificar_almacen.html y procesa
    la actualización de un almacén existente.
    """
    try:
        conexion = sqlite3.connect('ConexionBD/InventarioBD_2.db')
        cursor = conexion.cursor()

        if request.method == 'POST':
            # Tomamos el nuevo nombre desde el formulario
            nuevo_nombre = request.form['nombre']
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE almacenes SET nombre=?, ultima_modificacion=? WHERE id=?",
                           (nuevo_nombre, fecha_actual, almacen_id)
                           )
            conexion.commit()
            flash(
                f"Almacén actualizado correctamente a '{nuevo_nombre}'", "success")
            return redirect(url_for('vista_almacenes'))

        else:
            # GET: obtenemos los datos actuales para mostrar en el formulario
            cursor.execute("SELECT * FROM almacenes WHERE id=?", (almacen_id,))
            almacen = cursor.fetchone()
            if not almacen:
                flash("Almacén no encontrado", "danger")
                return redirect(url_for('vista_almacenes'))

        conexion.close()

    except sqlite3.Error as e:
        flash(f"Error al modificar el almacén: {e}", "danger")
        return redirect(url_for('vista_almacenes'))

    # Renderizamos el formulario con los datos actuales
    return render_template('modificar_almacen.html', almacen=almacen)


# Ruta para eliminar un almacén

@app.route('/eliminar_almacen/<int:almacen_id>', methods=['POST'])
def eliminar_almacen(almacen_id):
    """
    Elimina un registro de la tabla almacenes.
    El formulario llama a esta ruta con el id del almacén.
    """
    try:
        # Conectamos a la BD
        conexion = sqlite3.connect('ConexionBD/InventarioBD_2.db')
        cursor = conexion.cursor()

        # Ejecutamos la eliminación
        cursor.execute("DELETE FROM almacenes WHERE id=?", (almacen_id,))
        conexion.commit()  # Guardamos los cambios
        conexion.close()

        # Mensaje de éxito
        flash("Almacén eliminado correctamente", "success")

    except sqlite3.Error as e:
        # Mensaje de error si falla la operación
        flash(f"Error al eliminar el almacén: {e}", "danger")

    # Redirigimos a la vista de almacenes para ver la lista actualizada
    return redirect(url_for('vista_almacenes'))


# =========================================================================================================

# ===========================
# Ruta para mostrar productos
# ===========================

@app.route('/productos')
def vista_productos():
    """
    Vista que muestra la lista de productos.
    También pasa a la plantilla los datos de último usuario y última modificación
    """
    mensaje = ""

    # Obtener filtros desde los parámetros GET
    filtro_nombre = request.args.get('nombre', '').strip()
    filtro_departamento = request.args.get('departamento', '').strip()
    filtro_precio_min = request.args.get('precio_min', '').strip()
    filtro_precio_max = request.args.get('precio_max', '').strip()
    filtro_cantidad_min = request.args.get('cantidad_min', '').strip()
    filtro_cantidad_max = request.args.get('cantidad_max', '').strip()

    try:
        conexion = sqlite3.connect('ConexionBD/InventarioBD_2.db')
        cursor = conexion.cursor()

        # Construir consulta base
        consulta = "SELECT * FROM productos WHERE 1=1"
        parametros = []

        # Aplicar filtros
        if filtro_nombre:
            consulta += " AND nombre LIKE ?"
            parametros.append(f"%{filtro_nombre}%")
        if filtro_departamento:
            consulta += " AND departamento LIKE ?"
            parametros.append(f"%{filtro_departamento}%")
        if filtro_precio_min:
            consulta += " AND precio >= ?"
            parametros.append(float(filtro_precio_min))
        if filtro_precio_max:
            consulta += " AND precio <= ?"
            parametros.append(float(filtro_precio_max))
        if filtro_cantidad_min:
            consulta += " AND cantidad >= ?"
            parametros.append(int(filtro_cantidad_min))
        if filtro_cantidad_max:
            consulta += " AND cantidad <= ?"
            parametros.append(int(filtro_cantidad_max))

        # Ejecutar consulta con parámetros
        cursor.execute(consulta, parametros)
        productos = cursor.fetchall()

        # Obtener último usuario en ingresar desde la tabla usuarios
        try:
            cursor.execute(
                "SELECT usuario FROM usuarios ORDER BY fecha_hora_ultimo_inicio DESC LIMIT 1")
            resultado_usuario = cursor.fetchone()
            if resultado_usuario:
                ultimo_usuario = resultado_usuario[0]
            else:
                ultimo_usuario = ""
        except sqlite3.Error:
            ultimo_usuario = ""

        # Mantener ultima_modificacion de la primera fila de productos
        if len(productos) > 0:
            ultima_modificacion = productos[0][-1]  # Última columna
        else:
            ultima_modificacion = ""

            conexion.close()
            mensaje = "Conexión a la BD - Productos exitosa"

    except sqlite3.Error as e:
        productos = []
        ultimo_usuario = ""
        ultima_modificacion = ""
        mensaje = f"Error al conectar a la BD - Productos: {e}"

    return render_template('productos.html',
                           productos=productos,
                           mensaje=mensaje,
                           ultimo_usuario=ultimo_usuario,
                           ultima_modificacion=ultima_modificacion,
                           cargo=session.get('cargo'))


# ===========================================
# Rutas para las opciones crud de prodcutos
# ===========================================

# Ruta para crear un nuevo producto


@app.route('/crear_producto', methods=['GET', 'POST'])
def crear_producto():
    """
    Ruta para crear un nuevo producto.
    """
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        cantidad = request.form['cantidad']       # antes era stock
        departamento = request.form['departamento']  # antes era categoria

        try:
            conexion = sqlite3.connect('ConexionBD/InventarioBD_2.db')
            cursor = conexion.cursor()

            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("INSERT INTO productos (nombre, precio, cantidad, departamento, ultima_modificacion, fecha_hora_creacion) VALUES (?, ?, ?, ?, ?, ?)",
                           (nombre, precio, cantidad, departamento,
                            fecha_actual, fecha_actual)
                           )
            conexion.commit()
            conexion.close()
            flash(f"Producto '{nombre}' creado correctamente", "success")
            return redirect(url_for('vista_productos'))
        except sqlite3.Error as e:
            flash(f"Error al crear el producto: {e}", "danger")
            return redirect(url_for('vista_productos'))

    # GET: mostrar el formulario vacío
    return render_template('crear_producto.html')


# Ruta para modificar un producto existente

@app.route('/modificar_producto/<int:producto_id>', methods=['GET', 'POST'])
def modificar_producto(producto_id):
    """
    Permite modificar un producto existente.
    """
    try:
        conexion = sqlite3.connect('ConexionBD/InventarioBD_2.db')
        cursor = conexion.cursor()

        if request.method == 'POST':
            # Tomar los datos del formulario
            nombre = request.form['nombre']
            precio = request.form['precio']
            cantidad = request.form['cantidad']
            departamento = request.form['departamento']

            # Actualizar la base de datos
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("UPDATE productos SET nombre=?, precio=?, cantidad=?, departamento=?, ultima_modificacion=? WHERE id=?",
                           (nombre, precio, cantidad, departamento,
                            fecha_actual, producto_id)
                           )
            conexion.commit()
            flash(f"Producto '{nombre}' modificado correctamente", "success")
            return redirect(url_for('vista_productos'))

        # GET: obtener los datos actuales del producto para mostrar en el formulario
        cursor.execute("SELECT * FROM productos WHERE id=?", (producto_id,))
        producto = cursor.fetchone()
        conexion.close()

        if producto is None:
            flash("Producto no encontrado", "danger")
            return redirect(url_for('vista_productos'))

        return render_template('modificar_producto.html', producto=producto)

    except sqlite3.Error as e:
        flash(f"Error al modificar el producto: {e}", "danger")
        return redirect(url_for('vista_productos'))


# Ruta para eliminar un producto

@app.route('/eliminar_producto/<int:producto_id>', methods=['POST'])
def eliminar_producto(producto_id):
    """
    Elimina un registro de la tabla productos.
    El formulario llama a esta ruta con el id del producto.
    """
    try:
        # Conectamos a la BD
        conexion = sqlite3.connect('ConexionBD/InventarioBD_2.db')
        cursor = conexion.cursor()

        # Ejecutamos la eliminación
        cursor.execute("DELETE FROM productos WHERE id=?", (producto_id,))
        conexion.commit()  # Guardamos los cambios
        conexion.close()

        # Mensaje de éxito
        flash("Producto eliminado correctamente", "success")

    except sqlite3.Error as e:
        # Mensaje de error si falla la operación
        flash(f"Error al eliminar el producto: {e}", "danger")

    # Redirigimos a la vista de productos para ver la lista actualizada
    return redirect(url_for('vista_productos'))


# ===========================
# Ejecutamos la app
# ===========================
if __name__ == '__main__':
    app.run(debug=True)
