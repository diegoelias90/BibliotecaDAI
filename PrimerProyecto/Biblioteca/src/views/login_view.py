import flet as ft
from login.login_func import login

def login_view(page: ft.Page) -> ft.View:

    txt_user = ft.TextField(
        label="Usuario",
        width=320,
        bgcolor=ft.Colors.WHITE
    )
    txt_pass = ft.TextField(
        label="Clave",
        password=True,
        can_reveal_password=True,
        width=320,
        bgcolor=ft.Colors.WHITE
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
            page.snack_bar = ft.SnackBar(ft.Text("Vista empleado pendiente"))
            page.snack_bar.open = True

        else:
            page.snack_bar = ft.SnackBar(ft.Text("Credenciales incorrectas"))
            page.snack_bar.open = True

        page.update()

    tarjeta_login = ft.Container(
        width=420,
        padding=30,
        border_radius=20,
        bgcolor=ft.Colors.with_opacity(0.78, ft.Colors.WHITE),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
            offset=ft.Offset(0, 8),
        ),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
            controls=[
                ft.Text(
                    "Biblioteca Institucional",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=20),
                txt_user,
                txt_pass,
                ft.Container(height=10),
                ft.ElevatedButton("Iniciar sesión", on_click=iniciar_sesion),
            ],
        ),
    )

    fondo_contenido = ft.Stack(
    expand=True,
    controls=[
        ft.Image(
            src="fondo.jpg",
            fit="cover",   # compatible 0.80.5
            expand=True,
        ),
        ft.Container(
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
        ),
        ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,  # <- aquí el fix
            content=tarjeta_login,
        ),
    ],
)

    return ft.View(
        route="/",
        padding=0,
        controls=[fondo_contenido],
    )