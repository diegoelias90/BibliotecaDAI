import flet as ft

from views.login_view import login_view
from views.admin_view import admin_view
from views.empleado_view import empleado_view

def main(page: ft.Page):
    page.title = "Biblioteca"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    def route_change(e):
        page.views.clear()

        #Aquí si no hay ruta
        if page.route == "/":
            page.views.append(login_view(page))
            #Si se va a admin
        elif page.route == "/admin":
            page.views.append(admin_view(page))
            #Para empleado
        elif page.route == "/empleado":
            page.views.append(empleado_view(page))      
        else:
            page.views.append(login_view(page))

        page.update()

    page.on_route_change = route_change

    page.route = "/"
    route_change(None)

ft.run(main, assets_dir="assets")         