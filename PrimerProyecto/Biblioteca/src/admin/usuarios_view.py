import flet as ft
import admin.usuarios as db_u

def usuarios_tab(page: ft.Page) -> ft.Control:
    # --- COMPONENTES UI ---
    txt_user = ft.TextField(label="Nombre de Usuario", width=300)
    txt_pass = ft.TextField(label="Contraseña", width=300, password=True, can_reveal_password=True)
    chk_admin = ft.Checkbox(label="Permisos de Administrador", value=False)

    tabla = ft.DataTable(
        column_spacing=20,
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Usuario")),
            ft.DataColumn(ft.Text("Rol")),
            ft.DataColumn(ft.Text("Acción")),
        ], 
        rows=[]
    )

    def snack(msg: str):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    def refrescar_staff(e=None):
        tabla.rows.clear()
        data = db_u.obtener_staff()
        for u in data:
            u_id = u['id']
            rol_nombre = "Admin" if u['es_admin'] else "Empleado"
            
            
            tabla.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(u_id))),
                ft.DataCell(ft.Container(ft.Text(u['username']), width=150)),
                ft.DataCell(ft.Text(rol_nombre)),
                ft.DataCell(
                    ft.ElevatedButton(
                        "Eliminar", 
                        bgcolor="red", 
                        color="white",
                        on_click=lambda _, x=u_id: borrar_usuario(x)
                    )
                )
            ]))
        page.update()

    def guardar_usuario(e):
        if not txt_user.value or not txt_pass.value:
            snack("Completa los campos")
            return
        
        ok, msg = db_u.registrar_empleado(txt_user.value, txt_pass.value, chk_admin.value)
        if ok:
            txt_user.value = ""
            txt_pass.value = ""
            chk_admin.value = False
            refrescar_staff()
        snack(msg)

    def borrar_usuario(u_id):
        # Evitar borrar al admin ID 1
        if u_id == 1:
            snack("No puedes eliminar al admin principal")
            return
        
        db_u.eliminar_empleado(u_id)
        snack("Usuario eliminado")
        refrescar_staff()

    refrescar_staff()

    # --- DISEÑO IGUAL A PRESTAMOS ---
    form = ft.Container(
        padding=15, border_radius=12, bgcolor="#F7F9FB",
        content=ft.Column(controls=[
            ft.Text("Gestión de Staff", size=18, weight="bold"),
            txt_user, 
            txt_pass, 
            chk_admin,
            ft.ElevatedButton("Registrar Usuario", on_click=guardar_usuario, width=300, bgcolor="#0B636B", color="white")
        ], spacing=10)
    )

    listado = ft.Container(
        padding=15, border_radius=12, bgcolor="#F7F9FB", expand=True,
        content=ft.Column(
            expand=True, 
            scroll=ft.ScrollMode.ALWAYS,
            controls=[
                ft.Text("Personal Autorizado", size=18, weight="bold"),
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