import base64
from io import BytesIO
from datetime import datetime, date

import flet as ft
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from admin.prestamos import (
    obtener_prestamos,
    crear_prestamo,
    marcar_devuelto,
    listar_lectores,
    listar_libros,
)


def prestamos_tab(page: ft.Page) -> ft.Control:
    #Es la cosa que se muestra debajo de las tablas cuando se manda un mensaje
    def snack(msg: str):
        page.snack_bar = ft.SnackBar(ft.Text(str(msg)))
        page.snack_bar.open = True
        page.update()

    #Convierte el dato del tctfecha, que si se mete y no es del tipo normal
    def parse_fecha(v):
        if v is None:
            return None

        if isinstance(v, date) and not isinstance(v, datetime):
            return v

        if isinstance(v, datetime):
            return v.date()

        s = str(v).strip()
        if not s:
            return None

        s = s.split(" ")[0]

        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            try:
                return datetime.fromisoformat(str(v)).date()
            except Exception:
                return None

    
    #Aquí está toda la lógica de la tabla, empezando por el nombre y las configuraciones de la imagen que saldrá cómo gráfica
    txt_info_grafica = ft.Text("", selectable=False)
    img_grafica = ft.Image(
        "",
        visible=False,
        width=900,
        height=380,
    )

    #Este es el contenedor de la gráfica
    contenedor_grafica = ft.Column(
        controls=[txt_info_grafica, img_grafica],
        spacing=8,
    )

    #Y el evento para ver la gráfica
    def ver_grafica(e):
        data = obtener_prestamos() or []

        etiquetas = []
        valores = []

        for r in data:
            f_esperada = parse_fecha(r.get("fecha_devolucion_esperada"))
            f_real = parse_fecha(r.get("fecha_devolucion_real"))

            if not f_esperada or not f_real:
                continue

            diff = (f_real - f_esperada).days  # >0 tarde, 0 a tiempo, <0 antes

            lector = str(r.get("lector", ""))
            libro = str(r.get("libro", ""))
            libro_corto = libro[:14] + ("..." if len(libro) > 14 else "")
            etiqueta = f"{lector} - {libro_corto}"

            etiquetas.append(etiqueta)
            valores.append(diff)

        if not valores:
            img_grafica.visible = False
            txt_info_grafica.value = ""
            page.update()
            snack("No hay préstamos devueltos con fechas completas para graficar.")
            return

        try:
            plt.figure(figsize=(10, 4.5))
            plt.bar(etiquetas, valores)
            plt.axhline(0)
            plt.xticks(rotation=45, ha="right")
            plt.ylabel("Días")
            plt.title("Retrasos en devoluciones")
            plt.tight_layout()

            buffer = BytesIO()
            plt.savefig(buffer, format="png", dpi=120)
            plt.close()
            buffer.seek(0)

            img_b64 = base64.b64encode(buffer.read()).decode("utf-8")

            # ✅ Flet 0.80.5 compatible
            img_grafica.src = f"data:image/png;base64,{img_b64}"
            img_grafica.visible = True

            total = len(valores)
            tarde = sum(1 for x in valores if x > 0)
            a_tiempo = sum(1 for x in valores if x == 0)
            antes = sum(1 for x in valores if x < 0)

            txt_info_grafica.value = (
                f"Registros: {total} | Tarde: {tarde} | "
                f"A tiempo: {a_tiempo} | Antes: {antes}"
            )

            page.update()

        except Exception as ex:
            snack(f"Error al generar gráfica: {ex}")

    # ==========================================================
    # Formulario crear préstamo
    # ==========================================================
    dd_lector = ft.Dropdown(label="Lector", width=420)
    dd_libro = ft.Dropdown(label="Libro", width=420)
    txt_fecha = ft.TextField(label="Devolución esperada", read_only=True, width=260)

    page.fecha_dev = None

    def on_fecha(e):
        if date_picker.value:
            page.fecha_dev = (
                f"{date_picker.value.year:04d}-"
                f"{date_picker.value.month:02d}-"
                f"{date_picker.value.day:02d}"
            )
            txt_fecha.value = page.fecha_dev
            page.update()

    date_picker = ft.DatePicker(on_change=on_fecha)

    if date_picker not in page.overlay:
        page.overlay.append(date_picker)

    def abrir_fecha(e):
        try:
            page.open(date_picker)
        except Exception:
            date_picker.open = True
            page.update()

    def cargar_dropdowns():
        lectores = listar_lectores() or []
        libros = listar_libros() or []

        dd_lector.options = [
            ft.dropdown.Option(str(r["id"]), f'{r["nombre"]} ({r["carnet"]})')
            for r in lectores
        ]

        dd_libro.options = [
            ft.dropdown.Option(str(b["id"]), f'{b["titulo"]} | stock {b["stock"]}')
            for b in libros
        ]

        page.update()

    def limpiar():
        dd_lector.value = None
        dd_libro.value = None
        txt_fecha.value = ""
        page.fecha_dev = None
        page.update()

    def crear_click(e):
        user_id = getattr(page, "user_id", None)

        if not user_id:
            snack("No hay sesión")
            return

        if not dd_lector.value or not dd_libro.value or not page.fecha_dev:
            snack("Completa los campos")
            return

        ok, msg = crear_prestamo(
            dd_lector.value,
            dd_libro.value,
            user_id,
            page.fecha_dev,
        )

        snack(msg)

        if ok:
            limpiar()
            cargar_dropdowns()
            refrescar()

    form = ft.Column(
        controls=[
            ft.Text("Crear préstamo", size=18, weight=ft.FontWeight.BOLD),
            dd_lector,
            dd_libro,
            ft.Row(
                controls=[
                    txt_fecha,
                    ft.OutlinedButton("Elegir fecha", on_click=abrir_fecha),
                ]
            ),
            ft.Row(
                controls=[
                    ft.ElevatedButton("Crear préstamo", on_click=crear_click),
                    ft.TextButton("Limpiar", on_click=lambda e: limpiar()),
                ]
            ),
        ],
        spacing=10,
    )

    # ==========================================================
    # Tabla
    # ==========================================================
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Lector")),
            ft.DataColumn(ft.Text("Libro")),
            ft.DataColumn(ft.Text("Préstamo")),
            ft.DataColumn(ft.Text("Esperada")),
            ft.DataColumn(ft.Text("Estado")),
            ft.DataColumn(ft.Text("Acción")),
        ],
        rows=[],
    )

    def devolver(pid):
        ok, msg = marcar_devuelto(pid)
        snack(msg)
        if ok:
            refrescar()

    def refrescar():
        tabla.rows.clear()

        data = obtener_prestamos() or []

        for r in data:
            devuelto = int(r.get("devuelto", 0))
            estado = "Devuelto" if devuelto == 1 else "Activo"

            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(r.get("lector", "")))),
                        ft.DataCell(ft.Text(str(r.get("libro", "")))),
                        ft.DataCell(ft.Text(str(r.get("fecha_prestamo", "")))),
                        ft.DataCell(ft.Text(str(r.get("fecha_devolucion_esperada", "")))),
                        ft.DataCell(ft.Text(estado)),
                        ft.DataCell(
                            ft.ElevatedButton(
                                "Devolver",
                                disabled=(devuelto == 1),
                                on_click=lambda e, pid=r["id"]: devolver(pid),
                            )
                        ),
                    ]
                )
            )

        page.update()

    cargar_dropdowns()
    refrescar()

    return ft.ListView(
        expand=True,
        padding=20,
        controls=[
            form,
            ft.Divider(),
            ft.Container(content=tabla),
            ft.Divider(),
            ft.Row(
                controls=[
                    ft.ElevatedButton("Ver gráfica", on_click=ver_grafica),
                ]
            ),
            contenedor_grafica,
        ],
    )