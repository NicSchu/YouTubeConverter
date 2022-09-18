import datetime
import os
import os.path
import re
import subprocess
import threading
import time
import webbrowser
from os.path import isfile, join
from tkinter import Tk
from os import listdir

import PySimpleGUI as Sg
import requests
from pytube import YouTube
from pytube import Playlist


# ------------------------- string checker -------------------------
from source.layout import get_layout


def is_correct_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None and "youtube" in url


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


def get_time_code(line):
    _list = line.replace(',', '').replace('=', ' ').split()
    pattern = re.compile(r"[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{2}")
    for element in _list:
        if pattern.match(element):
            return element
    return None


def get_time_code_in_seconds(time_code):
    times = time_code.split(':')
    return round(float(times[2])) + (int(times[1]) * 60) + (int(times[0]) * 3600)


def convert_progress(line, duration):
    if 'size=' in line:
        seconds_done = get_time_code_in_seconds(get_time_code(line))
        percent_value = ((50 * seconds_done) / duration) + 50
        window["PROGRESSBAR"].update(current_count=percent_value)
        window["PERCENT"].update(value=f'%.0f' % percent_value + '%')
        window.refresh()


# ------------------------- helper -------------------------
def print_to_multi(text, color):
    window["OUT"].print(text, text_color=color)


def get_clickable_elements():
    return ["MP3", "WAV", "KEEP", "OPEN", "LINK", "FOLDER", "BROWSE", "DOWNLOAD"]


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


def open_download_folder():
    # subprocess.Popen(r'explorer /select,"%s"' % directory)
    os.startfile(directory)


def progressbar(stream=None, chunk=None, remaining=None):
    percent_value = (50 * (stream.filesize - remaining)) / stream.filesize
    window["PROGRESSBAR"].update(current_count=percent_value)
    window["PERCENT"].update(value=f'%.0f' % percent_value + '%')
    window.refresh()


def complete():
    window["PROGRESS"].update(visible=False)


def find_filename(filename, ending):
    files = list(filter(lambda file: filename in file, [f for f in listdir(directory) if isfile(join(directory, f))]))
    new_filename = filename + ending
    i = 0
    while new_filename in files:
        i += 1
        new_filename = filename + '(' + str(i) + ')' + ending
    return new_filename


def convert_to_format(video, audio_format, duration):
    default_filename = video.default_filename
    filename = default_filename.rsplit('.')[0]

    new_filename = find_filename(filename, audio_format)
    command = './ffmpeg/ffmpeg -i "%s" "%s"' % (os.path.join(directory, default_filename),
                                                os.path.join(directory, new_filename))
    process = subprocess.Popen(command, stdout=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW,
                               stderr=subprocess.STDOUT, universal_newlines=True, startupinfo=subprocess.STARTUPINFO())
    for line in process.stdout:
        convert_progress(line, duration)

    if not values["KEEP"]:
        mp4_file = directory + "\\" + default_filename
        os.remove(mp4_file)


def download_and_convert_title(title_link):
    yt = YouTube(title_link, on_progress_callback=progressbar)
    print_to_multi(yt.title, "white")
    video = yt.streams.filter(progressive=True, file_extension='mp4').first()
    video = download_mp4(video)
    audio_format = '.mp3' if values["MP3"] else '.wav'
    convert_to_format(video, audio_format, yt.length)


def playlist_popup(playlist):
    pressed = Sg.popup_yes_no('The video link is part of the playlist ' + playlist.title + '. \n'
                              'Do you want to download the whole playlist?',
                              keep_on_top=True,
                              title='Download playlist?')
    while pressed is None:
        time.sleep(0.1)
    return pressed == 'Yes'


def download(playlist):
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
        open_download_folder()


def prepare_download():
    download_playlist = False
    try:
        playlist = Playlist(values["LINK"])
        if playlist.length > 0:
            download_playlist = playlist_popup(playlist)
    except:
        pass
    thread = threading.Thread(target=download(download_playlist), daemon=True)
    thread.start()


def copy_to_clipboard(to_copy):
    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(to_copy)
    r.update()
    r.destroy()


def get_from_clipboard():
    r = Tk()
    r.withdraw()
    clipped = r.clipboard_get()
    r.destroy()
    return clipped


def get_latest_tag_version():
    response = requests.get(latest_version_url)
    return response.url.split('/')[-1]


def check_for_updates(v):
    if v != get_latest_tag_version():
        pressed = Sg.popup_yes_no('A newer Version of this ' + software_name + ' is available.\n'
                                  'For proper functionality please consider downloading the newest version. \n'
                                  'Do you want to get to the download page?',
                                  keep_on_top=True,
                                  title='Update available')
        if pressed is None:
            return False
        if pressed == 'Yes':
            webbrowser.open(latest_version_url)
    return True


# ------------------------- menu -------------------------
def handle_menu_click():
    urls = {
        'Github': github_repo_url
    }
    font = ('Helvetica', 10, 'underline')
    popup_layout = [
        [
            Sg.Text(software_name + ' ' + version + "\n"
                                                    "(built on %s %s, %s)\n" %
                    (build_date.strftime("%B"), build_date.strftime("%d"), build_date.strftime("%Y")))
        ],
        [
            Sg.Text("Check out my Github page for updates", text_color='yellow', font=font, enable_events=True,
                    key=f'URL {urls["Github"]}')
        ]
    ]
    popup_window = Sg.Window("About", popup_layout, modal=True)
    while True:
        p_event, p_values = popup_window.read()
        if p_event == "Exit" or p_values == Sg.WIN_CLOSED or p_event is None:
            break
        elif p_event.startswith("URL "):
            url = p_event.split(' ')[1]
            webbrowser.open(url)
    popup_window.close()


# ---------------------- variables ----------------------
version = 'v1.2.5'
build_date = datetime.datetime(2022, 3, 17)
software_name = 'Youtube Converter'
latest_version_url = 'https://github.com/NicSchu/YouTubeConverter/releases/latest'
github_repo_url = 'https://github.com/NicSchu/YouTubeConverter'

# ------------------------- main -------------------------
if __name__ == '__main__':
    # sg.theme_previewer()
    Sg.theme("DarkGrey14")
    window = Sg.Window(software_name + ' ' + version, get_layout())
    run = check_for_updates(version)
    while run:
        event, values = window.read()
        if event == "Exit" or event == Sg.WIN_CLOSED:
            break
        elif event == "DOWNLOAD":
            link = values["LINK"]
            directory = values["FOLDER"]
            if link == "" or not is_correct_url(link):
                print_to_multi("Bitte korrekten YouTube Link eingeben!", "red")
            elif directory == "":
                print_to_multi("Bitte Downloadpfad eingeben!", "red")
            else:
                prepare_download()
        elif event == "About":
            handle_menu_click()
        elif event == 'Copy':
            copy_to_clipboard(values['LINK'])
        elif event == 'Paste':
            window['LINK'].update(get_from_clipboard())
        elif event == 'Clear':
            window['LINK'].update('')
    window.close()
