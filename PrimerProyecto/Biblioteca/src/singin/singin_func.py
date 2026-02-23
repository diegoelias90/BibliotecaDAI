import flet as ft
import mariadb as mdb
from functions.database.conexion import db_config


def get_connection():
    try:
        return mdb.connect(**db_config)
    except mdb.Error as error:
        print(f"Error al conectar: {error}")
        return None


def signin(nombre, contra, page: ft.Page):

    if not nombre or not contra:
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

        # Verificar si ya existe
        cursor.execute(
            "SELECT id FROM usuarios_sistema WHERE username=%s",
            (nombre.strip(),)
        )

        if cursor.fetchone():
            page.snack_bar = ft.SnackBar(ft.Text("El usuario ya existe"))
            page.snack_bar.open = True
            page.update()
            return

        # Insertar nuevo usuario (por defecto no admin)
        cursor.execute(
            "INSERT INTO usuarios_sistema (username, password, es_admin) VALUES (%s, %s, %s)",
            (nombre.strip(), contra.strip(), False)
        )

        conn.commit()

        page.snack_bar = ft.SnackBar(ft.Text("Cuenta creada correctamente"))
        page.snack_bar.open = True
        page.update()

        page.go("/")

    except mdb.Error as e:
        print("Error MariaDB:", e)
        page.snack_bar = ft.SnackBar(ft.Text("Error al registrar usuario"))
        page.snack_bar.open = True
        page.update()

    finally:
        conn.close()