import flet as ft
from login.login_func import login

def login_view(page: ft.Page) -> ft.View:

    txt_user = ft.TextField(label="Usuario", width=320)
    txt_pass = ft.TextField(
        label="Clave",
        password=True,
        can_reveal_password=True,
        width=320
    )

    def iniciar_sesion(e):
        user = txt_user.value.strip()
        pw = txt_pass.value.strip()

        if not user or not pw:
            page.snack_bar = ft.SnackBar(ft.Text("Completa todos los campos"))
            page.snack_bar.open = True
            page.update()
            return

        rol = login(user, pw, page) 

        if rol == "admin":
            page.go("/admin")

        elif rol == "empleado":
            # page.go("/empleado")  # lo hará tu compa
            page.snack_bar = ft.SnackBar(ft.Text("Vista empleado pendiente"))
            page.snack_bar.open = True

        else:
            page.snack_bar = ft.SnackBar(ft.Text("Credenciales incorrectas"))
            page.snack_bar.open = True

        page.update()

    return ft.View(
        route="/",
        controls=[
            ft.Container(
                alignment=ft.Alignment.CENTER,
                expand=True,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Sistema Biblioteca", size=28, weight=ft.FontWeight.BOLD),
                        ft.Container(height=20),
                        txt_user,
                        txt_pass,
                        ft.ElevatedButton("Iniciar sesión", on_click=iniciar_sesion),
                    ],
                ),
            )
        ],
    )