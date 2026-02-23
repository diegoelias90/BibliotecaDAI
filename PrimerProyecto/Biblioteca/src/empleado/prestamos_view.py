import flet as ft
import empleado.prestamos as db_p
import empleado.lectores as db_l
import admin.libros as db_b

# Pestaña de préstamos para registrar préstamos y gestionar devoluciones activas.
def prestamos_tab(page: ft.Page) -> ft.Control:
    txt_buscar_lector = ft.TextField(label="Buscar Alumno...", width=300, on_change=lambda _: filtrar_catalogos())
    dd_lector = ft.Dropdown(label="Seleccionar Lector", width=300)
    dd_libro = ft.Dropdown(label="Seleccionar Libro", width=300)
    txt_vence = ft.TextField(label="Vence (AAAA-MM-DD)", value="2025-02-28", width=300)

    txt_buscar_dev = ft.TextField(label="Filtrar por nombre...", on_change=lambda e: refrescar_tabla(e.control.value))

    tabla = ft.DataTable(
        column_spacing=20,
        columns=[
            ft.DataColumn(ft.Text("Lector")),
            ft.DataColumn(ft.Text("Libro")),
            ft.DataColumn(ft.Text("Vence")),
            ft.DataColumn(ft.Text("Acción")),
        ],
        rows=[]
    )

    def snack(msg: str, ok=True):
        # Muestra un mensaje visual con color según éxito o error.
        page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor="#0B636B" if ok else "red")
        page.snack_bar.open = True
        page.update()

    def filtrar_catalogos():
        # Filtra lectores por nombre o carnet y actualiza el dropdown de selección.
        valor = txt_buscar_lector.value.lower()
        lectores_data = db_l.obtener_lectores()
        dd_lector.options = [
            ft.dropdown.Option(str(x['id']), x['nombre'])
            for x in lectores_data if valor in x['nombre'].lower() or valor in x['carnet'].lower()
        ]
        page.update()

    def refrescar_tabla(busqueda=""):
        # Recarga la tabla con préstamos activos y agrega botón para procesar devolución.
        tabla.rows.clear()
        activos = db_p.obtener_prestamos_activos(busqueda)
        for p in activos:
            pid, lid = p['id'], p['libro_id']
            tabla.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Container(ft.Text(p['lector']), width=140)),
                ft.DataCell(ft.Container(ft.Text(p['libro']), width=200)),
                ft.DataCell(ft.Text(str(p['fecha_devolucion_esperada']))),
                ft.DataCell(
                    ft.ElevatedButton(
                        "Devolver", bgcolor="#0B636B", color="white",
                        on_click=lambda _, pid=pid, lid=lid: procesar_dev(pid, lid)
                    )
                )
            ]))
        page.update()

    def inicializar_data():
        # Carga libros disponibles, lectores filtrables y la tabla inicial de devoluciones.
        libros_data = db_b.obtener_libros()
        dd_libro.options = [ft.dropdown.Option(str(x['id']), f"{x['titulo']} ({x['stock']})") for x in libros_data if x['stock'] > 0]
        filtrar_catalogos()
        refrescar_tabla()
        page.update()

    def procesar_p(e):
        # Registra un préstamo nuevo usando lector, libro, usuario y fecha de vencimiento.
        if not dd_lector.value or not dd_libro.value:
            snack("Selecciona alumno y libro", False)
            return
        u_id = getattr(page, "user_id", 1)
        ok, msg = db_p.registrar_prestamo(dd_lector.value, dd_libro.value, u_id, txt_vence.value)
        snack(msg, ok)
        if ok:
            inicializar_data()

    def procesar_dev(pid, lid):
        # Registra la devolución de un préstamo y actualiza catálogos y tabla.
        ok, msg = db_p.registrar_devolucion(pid, lid)
        snack(msg, ok)
        inicializar_data()

    inicializar_data()

    form = ft.Container(
        padding=15, border_radius=12, bgcolor="#F7F9FB",
        content=ft.Column(controls=[
            ft.Text("Registrar Préstamo", size=18, weight="bold"),
            txt_buscar_lector,
            dd_lector,
            dd_libro,
            txt_vence,
            ft.ElevatedButton("Prestar", icon="save", on_click=procesar_p, width=300),
            ft.TextButton("Refrescar catálogos", icon="refresh", on_click=lambda _: inicializar_data())
        ], spacing=10)
    )

    listado = ft.Container(
        padding=15, border_radius=12, bgcolor="#F7F9FB", expand=True,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.ALWAYS,
            controls=[
                ft.Text("Control Devoluciones", size=18, weight="bold"),
                txt_buscar_dev,
                ft.Row([tabla], scroll=ft.ScrollMode.ALWAYS)
            ]
        )
    )

    return ft.Container(
        padding=20,
        content=ft.Row(
            controls=[form, listado],
            spacing=20, alignment="center", vertical_alignment="start"
        )
    )