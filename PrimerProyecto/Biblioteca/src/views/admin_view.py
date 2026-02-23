import flet as ft
from admin.libros_view import libros_tab
from admin.prestamos_view import prestamos_tab
from admin.usuarios_view import usuarios_tab


def admin_view(page: ft.Page) -> ft.View:
    def salir(e):
        page.user_id = None
        page.esadmin = False
        page.go("/")

    user_id = getattr(page, "user_id", None)

    topbar = ft.Container(
        padding=12,
        bgcolor="#0B636B",
        border_radius=12,
        content=ft.Row(
            alignment="spaceBetween",
            controls=[
                ft.Text(
                    "Panel Admin",
                    color="white",
                    weight=ft.FontWeight.BOLD,
                    size=18,
                ),
                ft.Row(
                    controls=[
                        ft.Text(f"Usuario: {user_id}", color="white", opacity=0.85),
                        ft.ElevatedButton("Cerrar sesión", on_click=salir),
                    ],
                    spacing=10,
                ),
            ],
        ),
    )

    tabs = ft.Tabs(
        length=3,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Libros"),
                        ft.Tab(label="Usuarios"),
                        ft.Tab(label="Préstamos"),
                    ]
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        ft.Container(
                            expand=True,
                            content=ft.ListView(
                                expand=True,
                                controls=[libros_tab(page)],
                            ),
                        ),
                        ft.Container(
                            expand=True,
                            content=ft.ListView(
                                expand=True,
                                controls=[usuarios_tab(page)],
                            ),
                        ),
                        ft.Container(
                            expand=True,
                            content=ft.ListView(
                                expand=True,
                                controls=[prestamos_tab(page)],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    return ft.View(
        route="/admin",
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Container(
                width=1000,
                padding=16,
                content=ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[topbar, tabs],
                ),
            )
        ],
        expand=True,
    )