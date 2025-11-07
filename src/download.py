from enum import Enum

from pytubefix import YouTube, Playlist
import flet as ft

from json_helper import Settings
from url_checker import is_correct_url


class Session(Enum):
    URL = "URL"

def select_stream(yt, quality="medium", audio_only=True):
    streams = yt.streams.filter(only_audio=audio_only).order_by("abr")
    if not streams:
        return None
    if quality == "low":
        return streams.first()
    elif quality == "medium":
        return streams[len(streams)//2]  # middle bitrate
    elif quality == "high":
        return streams.last()  # highest bitrate
    return streams.last()


def on_download(page: ft.Page, log: ft.Column):
    url = page.session.get(Session.URL.value)
    output_dir = page.session.get(Settings.DIRECTORY.value)
    quality = page.session.get(Settings.QUALITY.value)
    format_ = page.session.get(Settings.FORMAT.value)

    if not url:
        log.controls.append(ft.Text("Please enter an URL"))
        return
    if not is_correct_url(url):
        alert = ft.AlertDialog(
            title=ft.Text("Wrong URL"),
            content=ft.Text("This is not a valid youtube URL. Please check your input"),
            alignment=ft.alignment.center,
            actions=[
                ft.TextButton("OK", on_click=lambda e: page.close(alert)),
            ]
        )
        page.open(alert)
        page.update()
        return

    if page.session.get(Settings.DETECT_PLAYLIST.value):
        # Playlist detected
        def download_playlist(e):
            dlg.open = False
            page.update()
            start_download_playlist(url, output_dir, quality, format_, log)

        def download_single(e):
            dlg.open = False
            page.update()
            start_download_single(url, output_dir, quality, format_, log)

        def close_dialog(e):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Playlist detected"),
            content=ft.Text("Do you want to download the entire playlist or just this video?"),
            actions=[
                ft.TextButton("Whole Playlist", on_click=download_playlist),
                ft.TextButton("Just One Video", on_click=download_single),
                ft.TextButton("Cancel", on_click=close_dialog)
            ],
        )
        page.open(dlg)
        page.update()
    else:
        # Normal video
        start_download_single(url, output_dir, quality, format_, log)


def start_download_single(url, output_dir, quality, format_, log):
    yt = YouTube(url)

    title = yt.title
    audio_only = format_ != ".mp4"
    stream = select_stream(yt, quality=quality, audio_only=audio_only)

    log.controls.append(ft.Text(f"Downloading: {title} - ({stream.abr})"))
    stream.download(output_path=output_dir, filename=f"{title}-{stream.abr}.{format_}")


def start_download_playlist(url, output_dir, quality, format_, log):
    pl = Playlist(url)
    audio_only = format_ != ".mp4"
    for video in pl.videos:
        stream = select_stream(video, quality, audio_only=audio_only)
        log.controls.append(ft.Text(f"Downloading: {stream.title} - ({stream.abr})"))
        stream.download(output_path=output_dir, filename=f"{stream.title}-{stream.abr}.{format_}")
