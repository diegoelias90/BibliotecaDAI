import mariadb as mdb
from functions.database.conexion import db_config

# Préstamo seleccionado desde la tabla
prestamo_id_seleccionado = None


def seleccionar_prestamo(pid):
    """Permite pid=None para limpiar selección."""
    global prestamo_id_seleccionado
    prestamo_id_seleccionado = pid


def get_connection():
    try:
        return mdb.connect(**db_config)
    except mdb.Error as error:
        print(f"Error al conectar: {error}")
        return None


def obtener_prestamos():
    """Lista préstamos con nombres (lector, libro, usuario)."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                p.id,
                p.lector_id,
                l.nombre AS lector,
                p.libro_id,
                b.titulo AS libro,
                p.usuario_sistema_id,
                u.username AS usuario,
                p.fecha_prestamo,
                p.fecha_devolucion_esperada,
                p.fecha_devolucion_real,
                p.devuelto
            FROM prestamos p
            JOIN lectores l ON l.id = p.lector_id
            JOIN libros b ON b.id = p.libro_id
            JOIN usuarios_sistema u ON u.id = p.usuario_sistema_id
            ORDER BY p.id DESC
        """)
        return cursor.fetchall()
    except mdb.Error as e:
        print("Error MariaDB (obtener_prestamos):", e)
        return []
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()


def obtener_prestamo_por_id(pid):
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, lector_id, libro_id, usuario_sistema_id,
                   fecha_prestamo, fecha_devolucion_esperada, fecha_devolucion_real, devuelto
            FROM prestamos
            WHERE id = %s
        """, (pid,))
        return cursor.fetchone()
    except mdb.Error as e:
        print("Error MariaDB (obtener_prestamo_por_id):", e)
        return None
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()


def crear_prestamo(lector_id, libro_id, usuario_sistema_id, fecha_devolucion_esperada):
    """
    Crea préstamo (devuelto=0) y baja stock del libro si hay stock.
    Reglas:
    - No permitir préstamo duplicado ACTIVO del mismo lector+libro (devuelto=0).
    - Validar existencia de lector/libro/usuario.
    """
    # validaciones rápidas
    try:
        lector_id = int(lector_id)
        libro_id = int(libro_id)
        usuario_sistema_id = int(usuario_sistema_id)
    except Exception:
        return False, "IDs inválidos (deben ser números)."

    if not fecha_devolucion_esperada:
        return False, "Fecha de devolución esperada requerida."

    conn = get_connection()
    if not conn:
        return False, "No se pudo conectar a la BD"

    try:
        cursor = conn.cursor()

        # validar lector
        cursor.execute("SELECT 1 FROM lectores WHERE id=%s", (lector_id,))
        if not cursor.fetchone():
            return False, "Lector no existe"

        # validar usuario_sistema
        cursor.execute("SELECT 1 FROM usuarios_sistema WHERE id=%s", (usuario_sistema_id,))
        if not cursor.fetchone():
            return False, "Usuario del sistema no existe"

        # validar libro + stock
        cursor.execute("SELECT stock FROM libros WHERE id=%s", (libro_id,))
        r = cursor.fetchone()
        if not r:
            return False, "Libro no existe"

        stock = int(r[0] or 0)
        if stock <= 0:
            return False, "No hay stock disponible"

        # ✅ evitar duplicado activo (mismo lector+libro sin devolver)
        cursor.execute("""
            SELECT COUNT(*)
            FROM prestamos
            WHERE lector_id=%s AND libro_id=%s AND devuelto=0
        """, (lector_id, libro_id))
        if int(cursor.fetchone()[0] or 0) > 0:
            return False, "Ese lector ya tiene ese libro prestado (aún no devuelto)."

        # insertar préstamo
        cursor.execute("""
            INSERT INTO prestamos (lector_id, libro_id, usuario_sistema_id, fecha_devolucion_esperada, devuelto)
            VALUES (%s, %s, %s, %s, 0)
        """, (lector_id, libro_id, usuario_sistema_id, fecha_devolucion_esperada))

        # bajar stock
        cursor.execute("UPDATE libros SET stock = stock - 1 WHERE id=%s", (libro_id,))

        conn.commit()
        return True, "Préstamo creado ✅"

    except mdb.Error as e:
        print("Error MariaDB (crear_prestamo):", e)
        try:
            conn.rollback()
        except Exception:
            pass
        return False, "Error en la base de datos"

    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()


def marcar_devuelto(pid):
    """
    Marca préstamo como devuelto=1, setea fecha_devolucion_real=CURDATE() y sube stock del libro.
    """
    if pid is None:
        return False, "Selecciona un préstamo"

    conn = get_connection()
    if not conn:
        return False, "No se pudo conectar a la BD"

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT libro_id, devuelto FROM prestamos WHERE id=%s", (pid,))
        r = cursor.fetchone()
        if not r:
            return False, "Préstamo no existe"

        libro_id, devuelto = r
        if int(devuelto) == 1:
            return False, "Ya estaba devuelto"

        cursor.execute("""
            UPDATE prestamos
            SET devuelto = 1,
                fecha_devolucion_real = CURDATE()
            WHERE id = %s
        """, (pid,))

        cursor.execute("UPDATE libros SET stock = stock + 1 WHERE id=%s", (libro_id,))
        conn.commit()
        return True, "Devuelto ✅"

    except mdb.Error as e:
        print("Error MariaDB (marcar_devuelto):", e)
        try:
            conn.rollback()
        except Exception:
            pass
        return False, "Error en la base de datos"

    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()


def eliminar_prestamo(pid):
    """
    Elimina préstamo. Si NO estaba devuelto, regresa el stock.
    """
    if pid is None:
        return False, "Selecciona un préstamo"

    conn = get_connection()
    if not conn:
        return False, "No se pudo conectar a la BD"

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT libro_id, devuelto FROM prestamos WHERE id=%s", (pid,))
        r = cursor.fetchone()
        if not r:
            return False, "Préstamo no existe"

        libro_id, devuelto = r

        cursor.execute("DELETE FROM prestamos WHERE id=%s", (pid,))

        # si estaba activo, devolvemos stock
        if int(devuelto) == 0:
            cursor.execute("UPDATE libros SET stock = stock + 1 WHERE id=%s", (libro_id,))

        conn.commit()
        return True, "Préstamo eliminado ✅"

    except mdb.Error as e:
        print("Error MariaDB (eliminar_prestamo):", e)
        try:
            conn.rollback()
        except Exception:
            pass
        return False, "Error en la base de datos"

    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()


def listar_lectores():
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, nombre, carnet FROM lectores ORDER BY nombre")
        return cur.fetchall()
    except mdb.Error as e:
        print("Error MariaDB (listar_lectores):", e)
        return []
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()


def listar_libros():
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, titulo, stock FROM libros ORDER BY titulo")
        return cur.fetchall()
    except mdb.Error as e:
        print("Error MariaDB (listar_libros):", e)
        return []
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()