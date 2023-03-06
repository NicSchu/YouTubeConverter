import os
import os.path
import subprocess
import threading

import PySimpleGUI as Sg
from pytube import YouTube
from pytube import Playlist

from source.components.menu import handle_about_click, handle_settings_click
from source.constants import software_name, version
from source.components.layout import get_layout
from source.checks.update_checker import check_for_updates
from source.checks.url_checker import is_correct_url
from source.components.popups import playlist_popup
from source.helpers.json import save_to_json, load_from_json
from source.helpers.progress import get_time_code_in_seconds, get_time_code
from source.helpers.helper import get_from_clipboard, copy_to_clipboard, get_clickable_elements, open_download_folder, \
    find_filename


# ------------------------- video download and converting -------------------------
def download_mp4(video):
    parent_dir = r"" + directory
    video.download(parent_dir)
    return video


def get_youtube_object(youtube_link):
    yt = YouTube(youtube_link)

    videos = list(yt.streams)
    videos = list(filter(lambda stream: stream.mime_type == "video/mp4", videos))
    return yt, videos


def convert_progress(line, duration):
    if 'size=' in line:
        seconds_done = get_time_code_in_seconds(get_time_code(line))
        percent_value = ((50 * seconds_done) / duration) + 50
        window["PROGRESSBAR"].update(current_count=percent_value)
        window["PERCENT"].update(value=f'%.0f' % percent_value + '%')
        window.refresh()


# ------------------------- window helper -------------------------
def print_to_multi(text, color):
    window["OUT"].print(text, text_color=color)


def switch_elements_disabled(disabled):
    reset_progress_bar()
    for element in get_clickable_elements():
        window[element].update(disabled=disabled)
    if disabled:
        window["LINK"].update(text_color="black")
        window["FOLDER"].update(text_color="black")
    else:
        window["LINK"].update(text_color="white")
        window["FOLDER"].update(text_color="white")


def reset_progress_bar():
    window["PROGRESSBAR"].update(current_count=0)
    window["PERCENT"].update(value=f'%.0f' % 0 + '%')


def progressbar(stream=None, chunk=None, remaining=None):
    percent_value = (50 * (stream.filesize - remaining)) / stream.filesize
    window["PROGRESSBAR"].update(current_count=percent_value)
    window["PERCENT"].update(value=f'%.0f' % percent_value + '%')
    window.refresh()


def complete():
    window["PROGRESS"].update(visible=False)


# ------------------------- converting -------------------------
def convert_to_format(video, audio_format, duration):
    default_filename = video.default_filename
    filename = default_filename.rsplit('.')[0]

    new_filename = find_filename(filename, audio_format, directory)
    command = './ffmpeg/ffmpeg -i "%s" "%s"' % (os.path.join(directory, default_filename),
                                                os.path.join(directory, new_filename))
    process = subprocess.Popen(command, stdout=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW,
                               stderr=subprocess.STDOUT, universal_newlines=True, startupinfo=subprocess.STARTUPINFO())
    for line in process.stdout:
        convert_progress(line, duration)

    if not values["KEEP"]:
        mp4_file = directory + "\\" + default_filename
        os.remove(mp4_file)


# ------------------------- download routine -------------------------
def download_and_convert_title(title_link):
    yt = YouTube(title_link, on_progress_callback=progressbar)
    print_to_multi(yt.title, "white")
    video = yt.streams.filter(progressive=True, file_extension='mp4').first()
    video = download_mp4(video)
    audio_format = '.mp3' if values["MP3"] else '.wav'
    convert_to_format(video, audio_format, yt.length)


def download_thread(playlist):
    switch_elements_disabled(True)
    window["PROGRESS"].update(visible=True)

    if playlist:
        p = Playlist(values["LINK"])
        print_to_multi("\nDownloading Playlist: %s\n" % p.title, "yellow")
        i = 1
        for video in p.videos:
            download_and_convert_title(video.watch_url)
            i += 1
        print_to_multi("\nPlaylist complete")
    else:
        download_and_convert_title(values["LINK"])
    switch_elements_disabled(False)
    complete()
    if values["OPEN"]:
        open_download_folder(values["FOLDER"])


def prepare_download():
    download_playlist = False
    if values["PLAYLIST"]:
        try:
            playlist = Playlist(values["LINK"])
            if playlist.length > 0:
                download_playlist = playlist_popup(playlist)
        except:
            pass
    if download_playlist is not None:
        thread = threading.Thread(target=download_thread(download_playlist == 'Yes'), daemon=True)
        thread.start()


# ------------------------- main -------------------------
if __name__ == '__main__':
    # Sg.theme_previewer()
    Sg.theme("DarkGrey14")
    window = Sg.Window(software_name + ' ' + version, get_layout())
    run = check_for_updates(version)
    # event, values = window.read()
    # values = load_from_json(values)
    while run:
        event, values = window.read()
        if event == "Exit" or event == Sg.WIN_CLOSED:
            break
        elif event == "DOWNLOAD":
            link = values["LINK"]
            directory = values["FOLDER"]
            if link == "" or not is_correct_url(link):
                print_to_multi("The link entered is not a working YouTube Link!", "red")
            elif directory == "":
                print_to_multi("Please enter a path for the download!", "red")
            else:
                prepare_download()
        elif event == "About":
            handle_about_click()
        elif event == "Settings":
            handle_settings_click(window, values)
        elif event == 'Copy':
            copy_to_clipboard(values['LINK'])
        elif event == 'Paste':
            window['LINK'].update(get_from_clipboard())
        elif event == 'Clear':
            window['LINK'].update('')
    # if values is not None:
    #     save_to_json(values)
    window.close()
