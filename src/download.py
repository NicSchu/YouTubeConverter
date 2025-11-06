from pytubefix import YouTube
import flet as ft

from json_helper import Settings

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



def download_stream(page: ft.Page):
    url = page.session.get("URL")
    yt = YouTube(url)

    title = yt.title
    audio_only = page.session.get(Settings.FORMAT.value) != ".mp4"
    stream = select_stream(yt, quality=page.session.get(Settings.QUALITY.value), audio_only=audio_only)
    stream.download(output_path=page.session.get(Settings.DIRECTORY.value), filename=f"{title}-{stream.abr}.{page.session.get(Settings.FORMAT.value)}")
    return title, stream.abr