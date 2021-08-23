import os
import os.path
import re
import subprocess
from os import listdir
from os.path import isfile, join

import PySimpleGUI as sg
from pytube import YouTube


# ------------------------- layout -------------------------
def get_layout():
    input_col = [
        [
            sg.Text("Download Folder", size=(15, 1)),
            sg.In(default_text=get_download_folder(), size=(25, 1), enable_events=True, key="FOLDER"),
            sg.FolderBrowse()
        ],
        [
            sg.Text("Youtube Link", size=(15, 1)),
            sg.In(size=(25, 1), key="LINK")
        ],
        [
            sg.Column([
                [sg.Checkbox("Keep mp4?", default=False, key="KEEP")],
                [sg.Checkbox("Open Download Folder?", default=True, key="OPEN")]
            ]),
            sg.Column([
                [sg.Text("Format:")],
                [sg.Radio("mp3", "FORMAT", default=True, key="MP3")],
                [sg.Radio("wav", "FORMAT", key="WAV")]
                # sg.Checkbox("Convert to mp3", default=True, key="CONVERT"),
            ])
        ],
        [
            sg.Button("Download and convert", key="DOWNLOAD")
        ],
    ]
    menu = [[
             "Help", "About"
    ]]
    output_col = [[sg.Multiline(key='OUT', size=(50, 10), background_color='black', pad=((5, 0), (5, 5)))]]
    return [[
        sg.Menu(menu, background_color="darkgrey", key="MENU"),
        sg.Column(input_col),
        sg.VSeparator(),
        sg.Column(output_col)
    ]]


# ------------------------- string checker -------------------------
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
def download_mp4(videos):
    # v_num = int(input("Enter vid num: "))
    v_num = 0
    parent_dir = r"" + directory
    videos[v_num].download(parent_dir)
    return videos, v_num


def get_youtube_object(youtube_link):
    yt = YouTube(youtube_link)

    videos = list(yt.streams)
    videos = list(filter(lambda stream: stream.mime_type == "video/mp4", videos))
    return yt, videos


def find_filename(filename, ending):
    files = list(filter(lambda file: filename in file, [f for f in listdir(directory) if isfile(join(directory, f))]))
    new_filename = filename + ending
    i = 0
    while new_filename in files:
        i += 1
        new_filename = filename + '(' + str(i) + ')' + ending
    return new_filename


def convert_to_format(videos, v_num, audio_format):

    default_filename = videos[v_num].default_filename
    filename = default_filename.rsplit('.')[0]

    new_filename = find_filename(filename, audio_format)

    subprocess.run([
        './ffmpeg/ffmpeg',
        '-i', os.path.join(directory, default_filename),
        os.path.join(directory, new_filename)
    ])
    if not values["KEEP"]:
        mp4_file = directory + "\\" + default_filename
        os.remove(mp4_file)


# ------------------------- little helper -------------------------
def print_to_multi(text, color):
    window["OUT"].print(text, text_color=color)


def get_download_folder():
    home = os.path.expanduser("~")
    return os.path.join(home, "Downloads")


def open_download_folder():
    # subprocess.Popen(r'explorer /select,"%s"' % directory)
    os.startfile(directory)


def download_and_convert():
    yt, videos = get_youtube_object(values["LINK"])
    print_to_multi(yt.title, "white")
    videos, v_num = download_mp4(videos)
    audio_format = '.mp3' if values["MP3"] else '.wav'
    convert_to_format(videos, v_num, audio_format)
    if values["OPEN"]:
        open_download_folder()


# ------------------------- main -------------------------
def handle_menu_click():
    sg.popup("YouTube Converter 2021.1.1\n"
             "(built on August 23, 2021)")


if __name__ == '__main__':
    # sg.theme_previewer()
    sg.theme("DarkGrey14")
    window = sg.Window("Youtube Converter", get_layout())
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "DOWNLOAD":
            link = values["LINK"]
            directory = values["FOLDER"]
            if link == "" or not is_correct_url(link):
                print_to_multi("Bitte richtigen YouTube Link eingeben!", "red")
            elif directory == "":
                print_to_multi("Bitte Downloadpfad eingeben!", "red")
            else:
                download_and_convert()
        elif event == "About":
            handle_menu_click()
    window.close()
