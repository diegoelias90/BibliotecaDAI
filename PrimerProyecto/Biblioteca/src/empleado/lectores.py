import mariadb as mdb
from functions.database.conexion import db_config  # Configuración de conexión a MariaDB

def get_connection():
    # Crea una conexión a la BD y devuelve None si ocurre un error.
    try:
        return mdb.connect(**db_config)
    except mdb.Error as error:
        print(f"Error al conectar: {error}")
        return None

# Guarda el id del lector seleccionado para usarlo en la interfaz.
lector_id_seleccionado = None

def seleccionar_lector(lector_id):
    # Actualiza la variable global con el id del lector seleccionado.
    global lector_id_seleccionado
    lector_id_seleccionado = lector_id

def agregarLector(nombre, carnet, telefono, correo):
    # Inserta un nuevo lector en la tabla lectores y retorna estado + mensaje.
    try:
        conn = get_connection()
        if conn is None: return False, "No se pudo conectar a la BD"
        cursor = conn.cursor()
        query = "INSERT INTO lectores (nombre, carnet, telefono, correo) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (nombre, carnet, telefono, correo))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Lector registrado"
    except mdb.Error as err:
        return False, f"Error BD: {err}"

def obtener_lector_por_id(lector_id):
    # Busca un lector por id y devuelve sus datos como diccionario.
    try:
        conn = get_connection()
        if conn is None: return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, carnet, telefono, correo FROM lectores WHERE id = %s", (lector_id,))
        lector = cursor.fetchone()
        cursor.close()
        conn.close()
        return lector
    except mdb.Error:
        return None

def actualizar_lector(lector_id, nombre, carnet, telefono, correo):
    # Actualiza los datos de un lector existente según su id.
    try:
        conn = get_connection()
        if conn is None: return False
        cursor = conn.cursor()
        query = "UPDATE lectores SET nombre=%s, carnet=%s, telefono=%s, correo=%s WHERE id=%s"
        cursor.execute(query, (nombre, carnet, telefono, correo, lector_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Lector actualizado"
    except mdb.Error:
        return False

def eliminar_lector_seguro(lector_id):
    # Elimina un lector solo si no tiene préstamos pendientes y borra su historial previo.
    try:
        conn = get_connection()
        if conn is None: return False, "Sin conexión"
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM prestamos WHERE lector_id = %s AND devuelto = 0", (lector_id,))
        if cursor.fetchone()[0] > 0:
            cursor.close()
            conn.close()
            return False, "No se puede eliminar: tiene préstamos pendientes de devolver"

        cursor.execute("DELETE FROM prestamos WHERE lector_id = %s", (lector_id,))
        cursor.execute("DELETE FROM lectores WHERE id = %s", (lector_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Lector eliminado correctamente junto a su historial"
    except mdb.Error as err:
        return False, f"Error SQL: {err}"

def obtener_lectores():
    # Obtiene y devuelve todos los lectores ordenados por id.
    try:
        conn = get_connection()
        if conn is None: return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, carnet, telefono, correo FROM lectores ORDER BY id")
        lectores = cursor.fetchall()
        cursor.close()
        conn.close()
        return lectores
    except mdb.Error:
        return []