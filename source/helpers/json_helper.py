import io
import os
from os import listdir
from os.path import isfile, join

import json
from source.constants import settings_file


def save_to_json(values):
    # file = settings_file
    with io.open(os.path.join(settings_file), 'w') as db_file:
        db_file.write(json.dumps(values))
    # with open(file, 'w') as file:
    #     file.seek(0)
    #     json.dump(values, file)
    #     file.truncate()


def load_from_json(values):
    files = get_files_in_current_dir()
    if settings_file not in files:
        return values
    d = json.load(open(settings_file))

    for key, value in d.items():
        if key in values:
            values[key] = value
    return values


def get_files_in_current_dir():
    return list(filter(lambda file: settings_file in file, [f for f in listdir('./') if isfile(join('./', f))]))
