import mariadb as mdb
from functions.database.conexion import db_config

def get_connection():
    try:
        return mdb.connect(**db_config)
    except mdb.Error: return None

# Para guardar selección
usuario_id_seleccionado = None

def registrar_empleado(user, password, es_admin):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "INSERT INTO usuarios_sistema (username, password, es_admin) VALUES (%s, %s, %s)"
        cursor.execute(query, (user, password, es_admin))
        conn.commit()
        conn.close()
        return True, "Empleado registrado ✅"
    except mdb.Error as err: return False, str(err)

def obtener_staff():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, es_admin FROM usuarios_sistema")
        data = cursor.fetchall()
        conn.close()
        return data
    except mdb.Error: return []

def eliminar_empleado(u_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # No dejar que el admin se borre a sí mismo o borrar por ID
        cursor.execute("DELETE FROM usuarios_sistema WHERE id = %s", (u_id,))
        conn.commit()
        conn.close()
        return True, "Eliminado"
    except mdb.Error as err: return False, str(err)