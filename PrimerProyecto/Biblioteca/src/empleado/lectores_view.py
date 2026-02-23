import flet as ft
import empleado.lectores as lectores 
from empleado.lectores import (
    obtener_lectores, agregarLector, obtener_lector_por_id,
    actualizar_lector, eliminar_lector_seguro, seleccionar_lector,
)

def lectores_tab(page: ft.Page) -> ft.Control:
    txt_nombre = ft.TextField(label="Nombre Completo", width=300)
    txt_carnet = ft.TextField(label="Carnet / DUI", width=300)
    txt_telefono = ft.TextField(label="Teléfono", width=300)
    txt_correo = ft.TextField(label="Correo Electrónico", width=300)

    info = ft.Text()

    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Carnet")),
            ft.DataColumn(ft.Text("Teléfono")),
            ft.DataColumn(ft.Text("Correo")),
        ],
        rows=[],
        expand=True,
    )

    def snack(msg: str):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    def limpiar_form():
        txt_nombre.value = ""
        txt_carnet.value = ""
        txt_telefono.value = ""
        txt_correo.value = ""
        lectores.lector_id_seleccionado = None
        page.update()

    def refrescar_tabla():
        tabla.rows.clear()
        data = obtener_lectores() or []
        if not data:
            info.value = "No hay registros."
            page.update()
            return
        info.value = ""
        for row in data:
            rid = row["id"]
            # IMPORTANTE: Definir rid=rid dentro del on_select para no perder la referencia
            def on_select(e, rid=rid):
                seleccionar_lector(rid)
                lector = obtener_lector_por_id(rid)
                if lector:
                    txt_nombre.value = lector["nombre"]
                    txt_carnet.value = lector["carnet"]
                    txt_telefono.value = lector["telefono"]
                    txt_correo.value = lector["correo"]
                page.update()

            tabla.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(rid))),
                ft.DataCell(ft.Text(row["nombre"])),
                ft.DataCell(ft.Text(row["carnet"])),
                ft.DataCell(ft.Text(row["telefono"])),
                ft.DataCell(ft.Text(row["correo"] if row["correo"] else "")),
            ], on_select_change=on_select))
        page.update()

    def btn_agregar(e):
        agregarLector(txt_nombre.value, txt_carnet.value, txt_telefono.value, txt_correo.value)
        snack("Registrado")
        limpiar_form()
        refrescar_tabla()

    def btn_eliminar(e):
        if lectores.lector_id_seleccionado is None:
            snack("Selecciona uno de la tabla")
            return
        ok, msg = eliminar_lector_seguro(lectores.lector_id_seleccionado)
        snack(msg)
        if ok:
            limpiar_form()
            refrescar_tabla()

    refrescar_tabla()

    form = ft.Container(
        padding=15, border_radius=12, bgcolor="#F7F9FB",
        content=ft.Column(controls=[
            ft.Text("Nuevo Lector", size=18, weight="bold"),
            txt_nombre, txt_carnet, txt_telefono, txt_correo,
            ft.Row(
                controls=[
                    ft.ElevatedButton("Agregar", on_click=btn_agregar),
                    ft.ElevatedButton("Eliminar", bgcolor="red", color="white", on_click=btn_eliminar),
                ]
            ),
        ], spacing=10)
    )

    listado = ft.Container(
        padding=15, border_radius=12, bgcolor="#F7F9FB",
        content=ft.Column(expand=True, controls=[
            ft.Text("Lista de Lectores", size=18, weight="bold"),
            ft.Container(content=tabla, expand=True),
        ])
    )

    return ft.Container(
        padding=20,
        content=ft.Row(controls=[form, listado], spacing=20, alignment="center", vertical_alignment="start")
    )