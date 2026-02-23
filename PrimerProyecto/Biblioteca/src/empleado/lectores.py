import mariadb as mdb
from functions.database.conexion import db_config

def get_connection():
    try:
        return mdb.connect(**db_config)
    except mdb.Error as error:
        print(f"Error al conectar: {error}")
        return None

# Variable para la selección
lector_id_seleccionado = None

def seleccionar_lector(lector_id):
    global lector_id_seleccionado
    lector_id_seleccionado = lector_id

def agregarLector(nombre, carnet, telefono, correo):
    try:
        conn = get_connection()
        if conn is None: return False, "No se pudo conectar a la BD"
        cursor = conn.cursor()
        query = "INSERT INTO lectores (nombre, carnet, telefono, correo) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (nombre, carnet, telefono, correo))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Lector registrado ✅"
    except mdb.Error as err:
        return False, f"Error BD: {err}"

def obtener_lector_por_id(lector_id):
    try:
        conn = get_connection()
        if conn is None: return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, carnet, telefono, correo FROM lectores WHERE id = %s", (lector_id,))
        lector = cursor.fetchone()
        cursor.close()
        conn.close()
        return lector
    except mdb.Error: return None

def actualizar_lector(lector_id, nombre, carnet, telefono, correo):
    try:
        conn = get_connection()
        if conn is None: return False
        cursor = conn.cursor()
        query = "UPDATE lectores SET nombre=%s, carnet=%s, telefono=%s, correo=%s WHERE id=%s"
        cursor.execute(query, (nombre, carnet, telefono, correo, lector_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Lector actualizado ✅"
    except mdb.Error: return False

def eliminar_lector_seguro(lector_id):
    try:
        conn = get_connection()
        if conn is None: return False, "Sin conexión"
        cursor = conn.cursor()

        # 1. Verificamos si tiene libros SIN DEVOLVER (devuelto = 0)
        cursor.execute("SELECT COUNT(*) FROM prestamos WHERE lector_id = %s AND devuelto = 0", (lector_id,))
        if cursor.fetchone()[0] > 0:
            cursor.close()
            conn.close()
            return False, "No se puede eliminar: tiene préstamos pendientes de devolver"

        # 2. SI NO DEBE NADA, borramos su historial (los registros de prestamos que tienen devuelto = 1)
        # Esto elimina el bloqueo de SQL por llave foránea
        cursor.execute("DELETE FROM prestamos WHERE lector_id = %s", (lector_id,))

        
        cursor.execute("DELETE FROM lectores WHERE id = %s", (lector_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Lector eliminado correctamente junto a su historial"
    except mdb.Error as err:
        return False, f"Error SQL: {err}"

def obtener_lectores():
    try:
        conn = get_connection()
        if conn is None: return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, carnet, telefono, correo FROM lectores ORDER BY id")
        lectores = cursor.fetchall()
        cursor.close()
        conn.close()
        return lectores
    except mdb.Error: return []