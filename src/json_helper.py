import io
import os
from enum import Enum
from os import listdir
from os.path import isfile, join

import flet as ft
import json
import constants

class Settings(Enum):
    DIRECTORY = "DIRECTORY"
    KEEP_MP4 = "KEEP_MP4"
    OPEN_DIRECTORY = "OPEN_DIRECTORY"
    DETECT_PLAYLIST = "DETECT_PLAYLIST"
    FORMAT = "FORMAT"
    QUALITY = "QUALITY"


def update_settings_json(key, value):
    settings = get_settings()
    settings[key] = value
    save_to_json(settings)


def save_to_json(values):
    with io.open(os.path.join("./" + constants.settings_file), 'w') as db_file:
        db_file.write(json.dumps(values))


def load_from_json(page: ft.Page):
    settings = get_settings()

    for setting in Settings:
        page.session.set(setting.value, settings.get(setting.value))


def get_settings():
    files = get_files_in_current_dir()
    if constants.settings_file not in files:
        return default_settings()
    try:
        return json.load(open(constants.settings_file))
    except:
        return default_settings()


def default_settings():
    return {
        "DIRECTORY": os.path.join(os.path.expanduser("~"), "Downloads"),
        "KEEP_MP4": False,
        "OPEN_DIRECTORY": True,
        "DETECT_PLAYLIST": True,
        "FORMAT": ".mp3",
        "QUALITY": "medium"
    }


def get_files_in_current_dir():
    return list([f for f in listdir('./') if isfile(join('./', f))])
