import os
import os.path
import re
import subprocess
import webbrowser
from os import listdir
from os.path import isfile, join
from tkinter import Tk

import PySimpleGUI as Sg
from pytube import YouTube


# ------------------------- layout -------------------------
def get_layout():
    input_col = [
        [
            Sg.Text("Download Folder", size=(15, 1)),
            Sg.In(default_text=get_download_folder(), size=(25, 1), enable_events=True, key="FOLDER"),
            Sg.FolderBrowse()
        ],
        [
            Sg.Text("Youtube Link", size=(15, 1)),
            Sg.In(size=(25, 1), key="LINK", right_click_menu=['&Right', ['Copy', 'Paste', 'Clear']])
        ],
        [
            Sg.Column([
                [Sg.Checkbox("Keep mp4?", default=False, key="KEEP")],
                [Sg.Checkbox("Open Download Folder?", default=True, key="OPEN")]
            ]),
            Sg.Column([
                [Sg.Text("Format:")],
                [Sg.Radio("mp3", "FORMAT", default=True, key="MP3")],
                [Sg.Radio("wav", "FORMAT", key="WAV")]
            ])
        ],
        [
            Sg.Button("Download and convert", key="DOWNLOAD")
        ],
    ]
    menu = [[
             "Help", "About"
    ]]
    output_col = [[Sg.Multiline(key='OUT', size=(50, 10), background_color='black', pad=((5, 0), (5, 5)))]]
    return [[
        Sg.Menu(menu, background_color="darkgrey", key="MENU"),
        Sg.Column(input_col),
        Sg.VSeparator(),
        Sg.Column(output_col)
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

    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.run([
        './ffmpeg/ffmpeg',
        '-i', os.path.join(directory, default_filename),
        os.path.join(directory, new_filename)
    ], startupinfo=si)
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
    urls = {
        'Github': 'https://github.com/NicSchu/YouTubeConverter'
    }
    font = ('Helvetica', 10, 'underline')
    popup_layout = [
        [
            Sg.Text("YouTube Converter " + version + "\n"
                    "(built on September 09, 2021)\n")
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
    r. destroy()
    return clipped


if __name__ == '__main__':
    # sg.theme_previewer()
    version = 'v1.1'
    Sg.theme("DarkGrey14")
    window = Sg.Window("Youtube Converter " + version, get_layout())
    while True:
        event, values = window.read()
        if event == "Exit" or event == Sg.WIN_CLOSED:
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
        elif event == 'Copy':
            copy_to_clipboard(values['LINK'])
        elif event == 'Paste':
            window['LINK'].update(get_from_clipboard())
        elif event == 'Clear':
            window['LINK'].update('')
    window.close()
