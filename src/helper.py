import os
from tkinter import Tk
from os.path import isfile, join
from os import listdir


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


def get_clickable_elements():
    return ["MP3", "WAV", "KEEP", "OPEN", "LINK", "FOLDER", "BROWSE", "DOWNLOAD"]


def open_download_folder(folder):
    # subprocess.Popen(r'explorer /select,"%s"' % directory)
    os.startfile(folder)


def find_filename(filename, ending, directory):
    files = list(filter(lambda file: filename in file, [f for f in listdir(directory) if isfile(join(directory, f))]))
    new_filename = filename + ending
    i = 0
    while new_filename in files:
        i += 1
        new_filename = filename + '(' + str(i) + ')' + ending
    return new_filename
