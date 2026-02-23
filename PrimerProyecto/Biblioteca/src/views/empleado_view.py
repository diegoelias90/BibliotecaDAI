import flet as ft
from empleado.lectores_view import lectores_tab
from empleado.prestamos_view import prestamos_tab

# Paleta de colores usada en el panel de empleado.
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

def empleado_view(page: ft.Page) -> ft.View:
    # Construye la vista principal del empleado con topbar, sidebar y secciones dinámicas.
    state = {"section": "lectores"}

    def salir(e):
        # Cierra sesión del usuario y redirige al login.
        page.user_id = None
        page.esadmin = False
        page.go("/")

    user_id = getattr(page, "user_id", "N/A")

    # Contenedor visual de la sección de lectores.
    content_lectores = ft.Container(
        expand=True,
        padding=14,
        bgcolor=CARD_BG,
        border_radius=16,
        border=ft.border.all(1, BORDER),
        content=lectores_tab(page),
    )

    # Contenedor visual de la sección de préstamos.
    content_prestamos = ft.Container(
        expand=True,
        padding=14,
        bgcolor=CARD_BG,
        border_radius=16,
        border=ft.border.all(1, BORDER),
        content=prestamos_tab(page),
    )

    content_host = ft.Container(expand=True)

    title_txt = ft.Text("", size=22, weight=ft.FontWeight.BOLD, color=TEXT)
    subtitle_txt = ft.Text("", size=12, color=MUTED)

    nav_items = {}

    def refresh_ui():
        # Actualiza resaltado del menú y cambia el contenido mostrado según la sección activa.
        for k, item in nav_items.items():
            if k == state["section"]:
                item.bgcolor = NAV_ACTIVE
                item.border = ft.border.all(1, "#C8D6FF")
            else:
                item.bgcolor = "transparent"
                item.border = None

        if state["section"] == "lectores":
            title_txt.value = "Gestión de Lectores"
            subtitle_txt.value = "Registro y eliminación de lectores."
            content_host.content = content_lectores
        else:
            title_txt.value = "Préstamos y Devoluciones"
            subtitle_txt.value = "Administración de préstamos, devoluciones y control de flujo."
            content_host.content = content_prestamos

    def set_section(key: str):
        # Cambia la sección activa, refresca la interfaz y actualiza la página.
        state["section"] = key
        refresh_ui()
        page.update()

    def nav_item(key: str, label: str):
        # Crea un botón del menú lateral que cambia a la sección indicada.
        c = ft.Container(
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            border_radius=14,
            bgcolor="transparent",
            content=ft.Row(
                spacing=10,
                vertical_alignment="center",
                controls=[
                    ft.Text(label, color=TEXT, size=13, weight=ft.FontWeight.BOLD),
                ],
            ),
        )
        nav_items[key] = c

        return ft.GestureDetector(
            on_tap=lambda e: set_section(key),
            content=c,
        )

    # Barra superior con título, usuario y botón de cierre de sesión.
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
                        ft.Column(
                            spacing=0,
                            controls=[
                                ft.Text(
                                    "Panel Empleado",
                                    color="#FFFFFF",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    "Biblioteca • Operación diaria",
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

    # Menú lateral con accesos a secciones del panel.
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
                            ft.Text("Menú", size=13, weight=ft.FontWeight.BOLD, color=TEXT),
                            ft.Text("Secciones del sistema", size=11, color=MUTED),
                        ],
                    ),
                ),
                nav_item("lectores", "Lectores"),
                nav_item("prestamos", "Préstamos"),
                ft.Container(expand=True),
            ],
        ),
    )

    # Encabezado del contenido principal con título de sección y rol.
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
                    content=ft.Text("Rol: Empleado", color=TEXT, size=12, weight=ft.FontWeight.BOLD),
                ),
            ],
        ),
    )

    # Área principal donde se renderiza el contenido de la sección seleccionada.
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

    # Estructura raíz de la vista con topbar y layout lateral.
    root = ft.Container(
        expand=True,
        bgcolor=APP_BG,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[topbar, ft.Row(expand=True, spacing=0, controls=[sidebar, main_area])],
        ),
    )

    refresh_ui()

    return ft.View(route="/empleado", controls=[root], padding=0)