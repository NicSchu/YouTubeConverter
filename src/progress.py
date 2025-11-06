import re


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
