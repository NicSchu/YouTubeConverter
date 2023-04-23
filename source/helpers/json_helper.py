import io
import os
from os import listdir
from os.path import isfile, join

import json
from source.constants import settings_file


def save_to_json(values):
    with io.open(os.path.join("./" + settings_file), 'w') as db_file:
        db_file.write(json.dumps(values))


def load_from_json():
    files = get_files_in_current_dir()
    if settings_file not in files:
        return default_settings()
    try:
        return json.load(open(settings_file))
    except:
        return default_settings()


def default_settings():
    return {
        "KEEP": False,
        "OPEN": True,
        "PLAYLIST": True,
        "MP3": True,
        "WAV": False
    }


def get_files_in_current_dir():
    return list([f for f in listdir('./') if isfile(join('./', f))])
