import subprocess

import flet as ft
from flet.core.types import ScrollMode

from json_helper import *
from download import *
# from src.download.download_logic import prepare_download
# from src.helpers.json_helper import load_from_json

def main(page: ft.Page):
    controls = {}
    # ------------------------- functions -------------------------
    def on_result_pick_directory(e: ft.FilePickerResultEvent):
        value = e.path
        if value:
            key = Settings.DIRECTORY.value
            controls[key].value = value
            page.session.set(key, value)
            page.update()
            update_settings_json(key, value)


    def on_change_field(e: ft.ControlEvent):
        key = e.control.data
        value = e.control.value
        page.session.set(key, value)
        update_settings_json(key, value)


    def print_session(e: ft.ControlEvent):
        for k in page.session.get_keys():
            print(f"{k}: {page.session.get(k)}")


    def download_action(e: ft.ControlEvent):
        log = controls["log"]
        on_download(page, log)
        # controls["log"].controls.append(ft.Text(f"- {title} - ({abr})"))
        # page.update()
        if page.session.get(Settings.OPEN_DIRECTORY.value):
            subprocess.run(f'explorer "{page.session.get(Settings.DIRECTORY.value)}"')


    # ------------------------- load/set settings -------------------------
    load_from_json(page)
    print_session(page)

    page.title = f"{constants.software_name} (v-{constants.version})"
    file_picker = ft.FilePicker(on_result=on_result_pick_directory)
    page.overlay.append(file_picker)
    page.update()

    controls[Settings.DIRECTORY.value] = ft.TextField(label="Download Folder", value=page.session.get(Settings.DIRECTORY.value), on_blur=on_change_field, data=Settings.DIRECTORY.value, expand=True)
    controls["log"] = ft.Column(controls=[
        ft.Text("Titles:")
    ],scroll=ScrollMode.ALWAYS, expand=True)

    page.add(
        ft.Column(controls=[
            ft.Row(controls=[
                ft.TextField(label="YouTube URL", expand=True, data=Session.URL.value, on_blur=on_change_field),
            ]),
            ft.Row(controls=[
                controls[Settings.DIRECTORY.value],
                ft.ElevatedButton("Browse...",
                                  on_click=lambda _: file_picker.get_directory_path("Select a download folder"))
            ]),
            ft.Dropdown(label="Format", width=100, value=page.session.get(Settings.FORMAT.value),
                        options=[
                            ft.dropdown.Option(".mp3"),
                            ft.dropdown.Option(".wav"),
                            ft.dropdown.Option(".mp4")
                        ], on_change=on_change_field, data=Settings.FORMAT.value),
            ft.Dropdown(label="Quality", value=page.session.get(Settings.QUALITY.value),
                        options=[
                            ft.dropdown.Option("low"),
                            ft.dropdown.Option("medium"),
                            ft.dropdown.Option("high")
                        ], on_change=on_change_field, data=Settings.QUALITY.value),
            ft.Checkbox(label="Keep mp4", value=page.session.get(Settings.KEEP_MP4.value), on_change=on_change_field, data=Settings.KEEP_MP4.value),
            ft.Checkbox(label="Open Download Folder", value=page.session.get(Settings.OPEN_DIRECTORY.value), on_change=on_change_field, data=Settings.OPEN_DIRECTORY.value),
            ft.Checkbox(label="Enable Playlist Detection", value=page.session.get(Settings.DETECT_PLAYLIST.value), on_change=on_change_field, data=Settings.DETECT_PLAYLIST.value),
        ]),
        controls["log"],

    )
    download = ft.ElevatedButton("Download and convert", on_click=download_action)
    page.add(download)


ft.app(main)


# todo:
# Integrate progress bar with current download logic.
# Handle playlist downloads in a background thread.
# Ensure quality + format selection works together.
# Improve console layout.
# find a solution like “folder opened” flag to avoid multiple explorer windows.
# pack everything into executable/program dir