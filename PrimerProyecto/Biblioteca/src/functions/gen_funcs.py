import flet as ft
import mariadb as mdb

def logout(page: ft.Page):
    page.session.close()
    page.go("Biblioteca\src\login\login.py")