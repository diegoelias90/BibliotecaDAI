import mariadb as mdb
from functions.database.conexion import db_config


def get_connection():
    try:
        return mdb.connect(**db_config)
    except mdb.Error as error:
        print(f"Error al conectar: {error}")
        return None


# Para guardar el libro seleccionado
libro_id_seleccionado = None


def seleccionar_libro(libro_id):
    global libro_id_seleccionado
    libro_id_seleccionado = libro_id


def listar_categorias():
    try:
        conn = get_connection()
        if conn is None:
            return []

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
        data = cursor.fetchall()

        cursor.close()
        conn.close()
        return data

    except mdb.Error as err:
        print("Error MariaDB (listar_categorias):", err)
        return []


def agregarLibro(titulo, autor, categoria_id, stock):
    try:
        conn = get_connection()
        if conn is None:
            return False, "No se pudo conectar a la BD"

        cursor = conn.cursor()
        query = """
            INSERT INTO libros (titulo, autor, categoria_id, stock)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (titulo, autor, categoria_id, stock))
        conn.commit()

        cursor.close()
        conn.close()
        return True, "Libro agregado correctamente"

    except mdb.Error as err:
        print("Error MariaDB:", err)
        return False, f"Error BD: {err}"


def obtener_libro_por_id(libro_id):
    try:
        conn = get_connection()
        if conn is None:
            return None

        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT id, titulo, autor, categoria_id, stock
            FROM libros
            WHERE id = %s
        """
        cursor.execute(query, (libro_id,))
        libro = cursor.fetchone()

        cursor.close()
        conn.close()
        return libro

    except mdb.Error as err:
        print("Error MariaDB:", err)
        return None


def actualizar_libro(libro_id, titulo, autor, categoria_id, stock):
    try:
        conn = get_connection()
        if conn is None:
            return False, "No se pudo conectar a la BD"

        cursor = conn.cursor()
        query = """
            UPDATE libros
            SET titulo = %s,
                autor = %s,
                categoria_id = %s,
                stock = %s
            WHERE id = %s
        """
        cursor.execute(query, (titulo, autor, categoria_id, stock, libro_id))
        conn.commit()

        cursor.close()
        conn.close()
        return True, "Libro actualizado correctamente"

    except mdb.Error as err:
        print("Error MariaDB:", err)
        return False, f"Error BD: {err}"


def eliminar_libro_seguro(libro_id):
    """
    OJO: aquí ya NO recibimos conn por parámetro.
    La función se encarga de abrir/cerrar conexión.
    """
    try:
        conn = get_connection()
        if conn is None:
            return False, "No se pudo conectar a la BD"

        cursor = conn.cursor()

        # verificar préstamos pendientes
        cursor.execute("""
            SELECT COUNT(*)
            FROM prestamos
            WHERE libro_id = %s AND devuelto = 0
        """, (libro_id,))
        pendientes = cursor.fetchone()[0]

        if pendientes > 0:
            cursor.close()
            conn.close()
            return False, "No se puede eliminar: hay préstamos pendientes"

        cursor.execute("DELETE FROM libros WHERE id = %s", (libro_id,))
        conn.commit()

        cursor.close()
        conn.close()
        return True, "Libro eliminado correctamente"

    except mdb.Error as err:
        print("Error MariaDB:", err)
        return False, f"Error BD: {err}"


def obtener_libros():
    try:
        conn = get_connection()
        if conn is None:
            return []

        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                l.id,
                l.titulo,
                l.autor,
                COALESCE(c.nombre, 'Sin categoría') AS categoria,
                l.stock
            FROM libros l
            LEFT JOIN categorias c ON l.categoria_id = c.id
            ORDER BY l.id
        """
        cursor.execute(query)
        libros = cursor.fetchall()

        cursor.close()
        conn.close()
        return libros

    except mdb.Error as err:
        print("Error MariaDB:", err)
        return []