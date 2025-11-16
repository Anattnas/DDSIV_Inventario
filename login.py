# Importamos Flask y módulos necesarios
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3  # Para conectarnos a la base de datos
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necesario para usar flash messages

# ===========================
# Ruta principal de login
# ===========================


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Página de login que valida usuario y contraseña.
    Dependiendo del cargo, redirige a la página de almacenes o productos.
    """
    mensaje = ""  # Variable para mensajes flotantes

    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        try:
            # Conectamos a la base de datos
            conexion = sqlite3.connect('ConexionBD/InventarioBD_2.db')
            cursor = conexion.cursor()

            # Buscamos usuario y contraseña
            cursor.execute(
                "SELECT cargo FROM usuarios WHERE usuario=? AND pass=?", (usuario, password))
            resultado = cursor.fetchone()

            if resultado:
                cargo = resultado[0]

                # ==============================
                # ACTUALIZAR FECHA/HORA Y USUARIO
                # ==============================
                # Tomamos la fecha y hora actual
                ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if cargo == 'almacen':
                    # Actualizamos la tabla almacenes con el último usuario y fecha/hora
                    cursor.execute(
                        "UPDATE almacenes SET ultimo_usuario=?, ultima_modificacion=?",
                        (usuario, ahora)
                    )
                    conexion.commit()
                    flash("Conexión a la BD - Almacenes exitosa", "success")
                    conexion.close()
                    return redirect(url_for('vista_almacenes'))

                elif cargo == 'productor':
                    # Actualizamos la tabla productos con el último usuario y fecha/hora
                    cursor.execute(
                        "UPDATE productos SET ultimo_usuario=?, ultima_modificacion=?",
                        (usuario, ahora)
                    )
                    conexion.commit()
                    flash("Conexión a la BD - Productos exitosa", "success")
                    conexion.close()
                    return redirect(url_for('vista_productos'))

                else:
                    mensaje = "Cargo no reconocido"
                    conexion.close()
            else:
                mensaje = "Usuario o contraseña incorrectos"
                conexion.close()

        except sqlite3.Error as e:
            mensaje = f"Error al conectar a la base de datos: {e}"

    # Renderizamos la plantilla con mensaje si lo hay
    return render_template('login.html', mensaje=mensaje)

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
    try:
        conexion = sqlite3.connect('ConexionBD/InventarioBD_2.db')
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM almacenes")
        almacenes = cursor.fetchall()

        # Obtener último usuario y fecha/hora de la primera fila (asumimos misma info para todos)
        if len(almacenes) > 0:
            # Penúltima columna: ultimo_usuario
            ultimo_usuario = almacenes[0][-2]
            # Última columna: ultima_modificacion
            ultima_modificacion = almacenes[0][-1]
        else:
            ultimo_usuario = ""
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
                           ultima_modificacion=ultima_modificacion)

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
            cursor.execute(
                "INSERT INTO almacenes (nombre) VALUES (?)", (nombre,))
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
            cursor.execute(
                "UPDATE almacenes SET nombre=? WHERE id=?", (nuevo_nombre, almacen_id))
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
    try:
        conexion = sqlite3.connect('ConexionBD/InventarioBD_2.db')
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()

        # Obtener último usuario y fecha/hora de la primera fila (asumimos misma info para todos)
        if len(productos) > 0:
            # Penúltima columna: ultimo_usuario
            ultimo_usuario = productos[0][-2]
            # Última columna: ultima_modificacion
            ultima_modificacion = productos[0][-1]
        else:
            ultimo_usuario = ""
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
                           ultima_modificacion=ultima_modificacion)

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
            cursor.execute(
                "INSERT INTO productos (nombre, precio, cantidad, departamento) VALUES (?, ?, ?, ?)",
                (nombre, precio, cantidad, departamento)
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
            cursor.execute(
                "UPDATE productos SET nombre=?, precio=?, cantidad=?, departamento=? WHERE id=?",
                (nombre, precio, cantidad, departamento, producto_id)
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
