import os
import json
import shutil
import flet as ft

DATA_FILE = "games.json"

def main(page: ft.Page):
    page.title = "Game List Builder"
    page.window_width = 800
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
    page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.PURPLE)

    games: list[dict] = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                games = json.load(f)
        except Exception as e:
            print(f"⚠️ Error cargando datos: {e}")

    def save_data():
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(games, f, ensure_ascii=False, indent=4)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ Error guardando: {ex}"))
            page.snack_bar.open = True
            page.update()

    id_field = ft.TextField(label="ID", width=80)
    title_field = ft.TextField(label="Título", expand=True)
    platform_field = ft.TextField(label="Plataforma", width=120)
    url_field = ft.TextField(label="URL", expand=True)
    image_field = ft.TextField(label="Imagen", read_only=True, width=180)
    search_field = ft.TextField(label="Buscar juego...", expand=True, on_change=lambda e: update_list())

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    list_view = ft.ListView(
        height=320,
        spacing=5
    )

    selected_index = None

    def pick_image(e: ft.ControlEvent):
        def on_result(event: ft.FilePickerResultEvent):
            if event.files:
                selected_path = event.files[0].path
                file_name = os.path.basename(selected_path)

                images_folder = os.path.join(os.getcwd(), "imagenes")
                os.makedirs(images_folder, exist_ok=True)

                destination = os.path.join(images_folder, file_name)
                shutil.copy(selected_path, destination)

                image_field.value = file_name
                page.snack_bar = ft.SnackBar(ft.Text(f"✅ Imagen '{file_name}' copiada"))
                page.snack_bar.open = True
                page.update()

        file_picker.on_result = on_result
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg", "gif"])

    def update_list():
        list_view.controls.clear()
        search_term = search_field.value.strip().lower()

        for idx, g in enumerate(games):
            if search_term in g['title'].lower() or search_term in g['platform'].lower():
                row = ft.Row([
                    ft.Text(f"{g['id']} - {g['title']} [{g['platform']}]"),
                    ft.IconButton(icon=ft.Icons.EDIT, on_click=lambda e, i=idx: edit_game(i)),
                    ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda e, i=idx: delete_game(i)),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                list_view.controls.append(row)
        page.update()

    def add_or_edit_game(e: ft.ControlEvent):
        nonlocal selected_index
        try:
            id_, title, platform, url, image = [
                f.value.strip() for f in (id_field, title_field, platform_field, url_field, image_field)
            ]
            if not all([id_, title, platform, url]):
                raise ValueError("Todos los campos son obligatorios (imagen es opcional)")
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ {ex}"))
            page.snack_bar.open = True
            page.update()
            return

        game_data = {
            "id": id_,
            "title": title,
            "platform": platform,
            "url": url,
            "image": image
        }

        if selected_index is None:
            games.append(game_data)
        else:
            games[selected_index] = game_data
            selected_index = None

        save_data()
        clear_fields()
        update_list()

    def edit_game(index: int):
        nonlocal selected_index
        selected_index = index
        game = games[index]
        id_field.value = game["id"]
        title_field.value = game["title"]
        platform_field.value = game["platform"]
        url_field.value = game["url"]
        image_field.value = game.get("image", "")
        page.update()

    def delete_game(index: int):
        try:
            games.pop(index)
            save_data()
            update_list()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ Error eliminando: {ex}"))
            page.snack_bar.open = True
            page.update()

    def clear_fields():
        for f in (id_field, title_field, platform_field, url_field, image_field):
            f.value = ""
        page.update()

    def export_to_py(e: ft.ControlEvent):
        try:
            with open("games_data.py", "w", encoding="utf-8") as f:
                f.write("games = [\n")
                for g in games:
                    line = f'    {json.dumps(g, ensure_ascii=False)},\n'
                    f.write(line)
                f.write("]\n")

            page.snack_bar = ft.SnackBar(ft.Text("✅ Exportado a games_exported.py"))
            page.snack_bar.open = True
            page.update()

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ Error exportando: {ex}"))
            page.snack_bar.open = True
            page.update()

    add_button = ft.ElevatedButton(
        text="💾 Guardar juego",
        on_click=add_or_edit_game,
        elevation=5,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=15)),
    )

    select_image_button = ft.OutlinedButton(
        text="🖼️ Imagen",
        on_click=pick_image,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=15)),
    )

    export_button = ft.ElevatedButton(
        text="📦 Exportar a .py",
        on_click=export_to_py,
        elevation=5,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=15)),
    )

    container = ft.Container(
        padding=20,
        border_radius=20,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        shadow=ft.BoxShadow(blur_radius=15, spread_radius=2, offset=ft.Offset(0, 5)),
        expand=True,
        content=ft.Column([
            ft.Row([
                id_field,
                title_field,
                platform_field,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                url_field,
                image_field,
                select_image_button,
                add_button,
                export_button,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                search_field,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            list_view,
        ], spacing=20),
    )

    page.add(container)

    update_list()

if __name__ == "__main__":
    ft.app(target=main)