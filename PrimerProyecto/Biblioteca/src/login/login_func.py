import flet as ft
import mariadb as mdb
from functions.database.conexion import db_config


def get_connection():
    try:
        return mdb.connect(**db_config)
    except mdb.Error as error:
        print(f"Error al conectar: {error}")
        return None


def login(username, password, page: ft.Page):
    if not username or not password:
        page.snack_bar = ft.SnackBar(ft.Text("Completa usuario y contraseña"))
        page.snack_bar.open = True
        page.update()
        return

    conn = get_connection()
    if conn is None:
        page.snack_bar = ft.SnackBar(ft.Text("No se pudo conectar a la base de datos"))
        page.snack_bar.open = True
        page.update()
        return

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, es_admin FROM usuarios_sistema WHERE username=%s AND password=%s",
            (username.strip(), password.strip())
        )
        user = cursor.fetchone()

        if user:
            user_id, esadmin = user

            # ✅ Guardar en el page (simple y funciona en cualquier versión)
            page.user_id = user_id
            page.esadmin = bool(esadmin)

            if page.esadmin:
                page.go("/admin")
            else:
                page.go("/empleado")
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Usuario o contraseña incorrectos"))
            page.snack_bar.open = True
            page.update()

    except mdb.Error as e:
        print("Error MariaDB:", e)
        page.snack_bar = ft.SnackBar(ft.Text("Error en la base de datos"))
        page.snack_bar.open = True
        page.update()

    finally:
        conn.close()