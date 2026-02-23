import mariadb as mdb
from functions.database.conexion import db_config

def get_connection():
    try:
        return mdb.connect(**db_config)
    except mdb.Error as error:
        print(f"Error al conectar: {error}")
        return None

def registrar_prestamo(lector_id, libro_id, usuario_id, fecha_vence):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT stock FROM libros WHERE id = %s", (int(libro_id),))
        row = cursor.fetchone()
        if not row or row[0] <= 0: return False, "Sin stock"

        query = """
            INSERT INTO prestamos (lector_id, libro_id, usuario_sistema_id, fecha_prestamo, fecha_devolucion_esperada, devuelto) 
            VALUES (%s, %s, %s, CURDATE(), %s, 0)
        """
        cursor.execute(query, (int(lector_id), int(libro_id), int(usuario_id), fecha_vence))
        cursor.execute("UPDATE libros SET stock = stock - 1 WHERE id = %s", (int(libro_id),))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Préstamo registrado ✅"
    except mdb.Error as err: return False, str(err)

def registrar_devolucion(prestamo_id, libro_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE prestamos SET devuelto = 1, fecha_devolucion_real = CURDATE() WHERE id = %s", (int(prestamo_id),))
        cursor.execute("UPDATE libros SET stock = stock + 1 WHERE id = %s", (int(libro_id),))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Devuelto ✅"
    except mdb.Error as err: return False, str(err)

def obtener_prestamos_activos(busqueda=""):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        # SQL con buscador: busca por nombre del lector o titulo del libro
        query = """
            SELECT p.id, l.nombre as lector, b.titulo as libro, p.fecha_devolucion_esperada, p.libro_id
            FROM prestamos p
            JOIN lectores l ON p.lector_id = l.id
            JOIN libros b ON p.libro_id = b.id
            WHERE p.devuelto = 0 AND (l.nombre LIKE %s OR b.titulo LIKE %s)
        """
        cursor.execute(query, (f"%{busqueda}%", f"%{busqueda}%"))
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return res
    except mdb.Error: return []