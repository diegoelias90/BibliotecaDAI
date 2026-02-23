import flet as ft
from admin.libros_view import libros_tab
from admin.prestamos_view import prestamos_tab
from admin.usuarios_view import usuarios_tab

APP_BG = "#EEF2F7"
TOP_BG = "#162C6B"
TOP_BG_2 = "#1B3A8A"
NAV_BG = "#F7F9FC"
NAV_ACTIVE = "#E6EEFF"
CARD_BG = "#FFFFFF"
BORDER = "#D7DEEA"
ACCENT = "#2F6FED"
TEXT = "#0F172A"
MUTED = "#475569"


def admin_view(page: ft.Page) -> ft.View:
    state = {"section": "libros"}

    def salir(e):
        page.user_id = None
        page.esadmin = False
        page.go("/")

    user_id = getattr(page, "user_id", "N/A")

    # ====== Contenidos por sección (con scroll) ======
    content_libros = ft.Container(
        expand=True,
        padding=14,
        bgcolor=CARD_BG,
        border_radius=16,
        border=ft.border.all(1, BORDER),
        content=ft.ListView(expand=True, controls=[libros_tab(page)]),
    )

    content_usuarios = ft.Container(
        expand=True,
        padding=14,
        bgcolor=CARD_BG,
        border_radius=16,
        border=ft.border.all(1, BORDER),
        content=ft.ListView(expand=True, controls=[usuarios_tab(page)]),
    )

    content_prestamos = ft.Container(
        expand=True,
        padding=14,
        bgcolor=CARD_BG,
        border_radius=16,
        border=ft.border.all(1, BORDER),
        content=ft.ListView(expand=True, controls=[prestamos_tab(page)]),
    )

    content_host = ft.Container(expand=True)

    title_txt = ft.Text("", size=22, weight=ft.FontWeight.BOLD, color=TEXT)
    subtitle_txt = ft.Text("", size=12, color=MUTED)

    nav_items = {}

    def refresh_ui():
        # sidebar highlight
        for k, item in nav_items.items():
            if k == state["section"]:
                item.bgcolor = NAV_ACTIVE
                item.border = ft.border.all(1, "#C8D6FF")
            else:
                item.bgcolor = "transparent"
                item.border = None

        # contenido principal
        if state["section"] == "libros":
            title_txt.value = "Gestión de Libros"
            subtitle_txt.value = "CRUD de libros, stock y categorías (si aplica)."
            content_host.content = content_libros
        elif state["section"] == "usuarios":
            title_txt.value = "Gestión de Usuarios"
            subtitle_txt.value = "Crear empleados/admin y administrar accesos."
            content_host.content = content_usuarios
        else:
            title_txt.value = "Préstamos y Devoluciones"
            subtitle_txt.value = "Registro, seguimiento, devoluciones y control de flujo."
            content_host.content = content_prestamos

    def set_section(key: str):
        state["section"] = key
        refresh_ui()
        page.update()

    # Sidebar item seguro (sin on_click en Container)
    def nav_item(key: str, label: str):
        c = ft.Container(
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            border_radius=14,
            bgcolor="transparent",
            content=ft.Row(
                spacing=10,
                vertical_alignment="center",
                controls=[
                    ft.Container(
                        width=10,
                        height=10,
                        border_radius=999,
                        bgcolor=ACCENT if key == state["section"] else "#B9C6DA",
                    ),
                    ft.Text(label, color=TEXT, size=13, weight=ft.FontWeight.BOLD),
                ],
            ),
        )
        nav_items[key] = c
        return ft.GestureDetector(on_tap=lambda e: set_section(key), content=c)

    # ====== TOPBAR ======
    topbar = ft.Container(
        height=74,
        padding=ft.padding.symmetric(horizontal=18, vertical=12),
        bgcolor=TOP_BG,
        content=ft.Row(
            alignment="spaceBetween",
            vertical_alignment="center",
            controls=[
                ft.Row(
                    spacing=12,
                    vertical_alignment="center",
                    controls=[
                        ft.Container(
                            width=42,
                            height=42,
                            border_radius=16,
                            bgcolor=TOP_BG_2,
                            border=ft.border.all(1, "#2B4FB2"),
                            content=ft.Row(
                                controls=[ft.Text("A", size=16, color="#FFFFFF", weight=ft.FontWeight.BOLD)],
                                alignment="center",
                                vertical_alignment="center",
                            ),
                        ),
                        ft.Column(
                            spacing=0,
                            controls=[
                                ft.Text(
                                    "Panel Administrador",
                                    color="#FFFFFF",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    "Biblioteca • Administración",
                                    color="#D7E3FF",
                                    size=12,
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    vertical_alignment="center",
                    controls=[
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            border_radius=999,
                            bgcolor=TOP_BG_2,
                            border=ft.border.all(1, "#2B4FB2"),
                            content=ft.Text(
                                f"{user_id}",
                                color="#FFFFFF",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ),
                        ft.ElevatedButton("Cerrar sesión", on_click=salir),
                    ],
                ),
            ],
        ),
    )

    # ====== SIDEBAR ======
    sidebar = ft.Container(
        width=240,
        bgcolor=NAV_BG,
        border=ft.border.all(1, BORDER),
        padding=12,
        content=ft.Column(
            expand=True,
            spacing=10,
            controls=[
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=10, vertical=12),
                    border_radius=14,
                    bgcolor="#FFFFFF",
                    border=ft.border.all(1, BORDER),
                    content=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text("Menú Admin", size=13, weight=ft.FontWeight.BOLD, color=TEXT),
                            ft.Text("Módulos del sistema", size=11, color=MUTED),
                        ],
                    ),
                ),
                nav_item("libros", "Libros"),
                nav_item("usuarios", "Usuarios"),
                nav_item("prestamos", "Préstamos"),
                ft.Container(expand=True),
                ft.Container(
                    padding=10,
                    border_radius=14,
                    bgcolor="#FFFFFF",
                    border=ft.border.all(1, BORDER),
                    content=ft.Text("Tip: Cambia de módulo desde el menú.", size=11, color=MUTED),
                ),
            ],
        ),
    )

    # ====== MAIN CONTENT ======
    header_section = ft.Container(
        padding=ft.padding.symmetric(horizontal=4, vertical=0),
        content=ft.Row(
            alignment="spaceBetween",
            vertical_alignment="center",
            controls=[
                ft.Column(spacing=2, controls=[title_txt, subtitle_txt]),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    border_radius=999,
                    bgcolor="#EAF2FF",
                    border=ft.border.all(1, "#C8D6FF"),
                    content=ft.Text("Rol: Administrador", color=TEXT, size=12, weight=ft.FontWeight.BOLD),
                ),
            ],
        ),
    )

    main_area = ft.Container(
        expand=True,
        bgcolor=APP_BG,
        padding=16,
        content=ft.Column(
            expand=True,
            spacing=12,
            controls=[header_section, content_host],
        ),
    )

    # ====== ROOT (full pantalla) ======
    root = ft.Container(
        expand=True,
        bgcolor=APP_BG,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                topbar,
                ft.Row(expand=True, spacing=0, controls=[sidebar, main_area]),
            ],
        ),
    )

    # init sin update (evita bugs en on_route_change)
    refresh_ui()

    return ft.View(route="/admin", controls=[root], padding=0)