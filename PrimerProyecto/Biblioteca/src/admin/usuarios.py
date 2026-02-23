import mariadb as mdb
from functions.database.conexion import db_config  # Configuración de conexión a la BD

def get_connection():
    try:
        return mdb.connect(**db_config)  # Abre conexión con MariaDB
    except mdb.Error:
        return None  # Si falla, devuelve None

# Guarda el id del usuario seleccionado en la UI
usuario_id_seleccionado = None

# Inserta un nuevo usuario en la tabla usuarios_sistema y retorna estado + mensaje.
def registrar_empleado(user, password, es_admin):
    try:
        conn = get_connection()  
        cursor = conn.cursor()
        query = "INSERT INTO usuarios_sistema (username, password, es_admin) VALUES (%s, %s, %s)"
        cursor.execute(query, (user, password, es_admin))  # Inserta nuevo usuario
        conn.commit()  
        conn.close() 
        return True, "Empleado registrado"
    except mdb.Error as err:
        return False, str(err)  

 # Consulta y devuelve la lista de usuarios (id, username, es_admin) como diccionarios.
def obtener_staff():
    try:
        conn = get_connection() 
        cursor = conn.cursor(dictionary=True)  # Devuelve resultados como diccionario
        cursor.execute("SELECT id, username, es_admin FROM usuarios_sistema")
        data = cursor.fetchall()  # Obtiene todos los registros
        conn.close()  #
        return data
    except mdb.Error:
        return [] 

 # Elimina un usuario por su id y retorna estado + mensaje del resultado
def eliminar_empleado(u_id):
    try:
        conn = get_connection() 
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios_sistema WHERE id = %s", (u_id,))  # Elimina por id
        conn.commit()  
        conn.close()  
        return True, "Eliminado"
    except mdb.Error as err:
        return False, str(err)  