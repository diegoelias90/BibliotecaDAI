import flet as ft
import admin.libros as libros  # módulo completo para libro_id_seleccionado

from admin.libros import (
    obtener_libros,
    agregarLibro,
    obtener_libro_por_id,
    actualizar_libro,
    eliminar_libro_seguro,
    seleccionar_libro,
    listar_categorias,
)


def libros_tab(page: ft.Page) -> ft.Control:
    # Inputs
    txt_titulo = ft.TextField(label="Título", width=300)
    txt_autor = ft.TextField(label="Autor", width=300)

    # ✅ Combobox / Dropdown de categorías (muestra nombre, guarda id)
    dd_categoria = ft.Dropdown(label="Categoría", width=300)

    txt_stock = ft.TextField(
        label="Stock",
        width=300,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    info = ft.Text()

    # ✅ Quitamos columna ID (solo visual)
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Título")),
            ft.DataColumn(ft.Text("Autor")),
            ft.DataColumn(ft.Text("Categoría")),
            ft.DataColumn(ft.Text("Stock")),
        ],
        rows=[],
        expand=True,
    )

    def snack(msg: str, ok=True):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    def cargar_categorias():
        categorias = listar_categorias() or []

        dd_categoria.options = [
            ft.dropdown.Option(str(c["id"]), c["nombre"])
            for c in categorias
        ]

        page.update()

    def limpiar_form():
        txt_titulo.value = ""
        txt_autor.value = ""
        dd_categoria.value = None
        txt_stock.value = ""
        page.update()

    def refrescar_tabla():
        tabla.rows.clear()
        data = obtener_libros() or []

        if not data:
            info.value = "No hay libros registrados."
            page.update()
            return

        info.value = ""

        for row in data:
            rid = row["id"]  # 👈 se sigue usando internamente, aunque no se muestre
            titulo = row["titulo"]
            autor = row["autor"]
            categoria = row["categoria"]
            stock = row["stock"]

            def on_select(e, rid=rid):
                seleccionar_libro(rid)
                libro = obtener_libro_por_id(rid)
                if libro:
                    txt_titulo.value = libro["titulo"]
                    txt_autor.value = libro["autor"]
                    dd_categoria.value = (
                        str(libro["categoria_id"]) if libro["categoria_id"] is not None else None
                    )
                    txt_stock.value = str(libro["stock"])
                page.update()

            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(titulo))),
                        ft.DataCell(ft.Text(str(autor))),
                        ft.DataCell(ft.Text(str(categoria))),
                        ft.DataCell(ft.Text(str(stock))),
                    ],
                    on_select_change=on_select,
                )
            )

        page.update()

    def btn_agregar(e):
        try:
            if not txt_titulo.value or not txt_autor.value or not dd_categoria.value or not txt_stock.value:
                snack("Completa todos los campos.", ok=False)
                return

            ok, msg = agregarLibro(
                txt_titulo.value.strip(),
                txt_autor.value.strip(),
                int(dd_categoria.value),   # ✅ id real de la categoría seleccionada
                int(txt_stock.value.strip()),
            )

            snack(msg, ok=ok)

            if ok:
                limpiar_form()
                refrescar_tabla()

        except ValueError:
            snack("Stock debe ser número.", ok=False)
        except Exception as ex:
            snack(f"Error: {ex}", ok=False)

    def btn_actualizar(e):
        try:
            if libros.libro_id_seleccionado is None:
                snack("Selecciona un libro en la tabla primero.", ok=False)
                return

            if not txt_titulo.value or not txt_autor.value or not dd_categoria.value or not txt_stock.value:
                snack("Completa todos los campos.", ok=False)
                return

            ok, msg = actualizar_libro(
                libros.libro_id_seleccionado,
                txt_titulo.value.strip(),
                txt_autor.value.strip(),
                int(dd_categoria.value),   # ✅ id real de categoría
                int(txt_stock.value.strip()),
            )

            snack(msg, ok=ok)

            if ok:
                refrescar_tabla()

        except ValueError:
            snack("Stock debe ser número.", ok=False)
        except Exception as ex:
            snack(f"Error: {ex}", ok=False)

    def btn_eliminar(e):
        if libros.libro_id_seleccionado is None:
            snack("Selecciona un libro en la tabla primero.", ok=False)
            return

        ok, msg = eliminar_libro_seguro(libros.libro_id_seleccionado)
        snack(msg, ok=ok)

        if ok:
            limpiar_form()
            refrescar_tabla()

    # Arranque
    cargar_categorias()
    refrescar_tabla()

    form = ft.Container(
        padding=15,
        border_radius=12,
        bgcolor="#F7F9FB",
        content=ft.Column(
            controls=[
                ft.Text("Acciones Libros", size=18, weight=ft.FontWeight.BOLD),
                txt_titulo,
                txt_autor,
                dd_categoria,   # ✅ antes era txt_categoria_id
                txt_stock,
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Agregar", on_click=btn_agregar),
                        ft.OutlinedButton("Actualizar", on_click=btn_actualizar),
                        ft.OutlinedButton("Eliminar", on_click=btn_eliminar),
                        ft.TextButton("Limpiar", on_click=lambda e: limpiar_form()),
                    ],
                    wrap=True,
                ),
                info,
            ],
            spacing=10,
        ),
    )

    listado = ft.Container(
        padding=15,
        border_radius=12,
        bgcolor="#F7F9FB",
        content=ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    alignment="spaceBetween",
                    controls=[
                        ft.Text("Listado de libros", size=18, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton("Refrescar", on_click=lambda e: refrescar_tabla()),
                    ],
                ),
                ft.Container(content=tabla, expand=True),
            ],
        ),
    )

    return ft.Container(
        padding=20,
        content=ft.Row(
            controls=[form, listado],
            spacing=20,
            alignment="center",
            vertical_alignment="start",
        ),
    )