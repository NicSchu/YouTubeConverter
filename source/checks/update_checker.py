import webbrowser
import requests
import PySimpleGUI as Sg

from source.constants import software_name, latest_version_url


def get_latest_tag_version():
    response = requests.get(latest_version_url)
    return response.url.split('/')[-1]


def check_for_updates(v):
    if v != get_latest_tag_version():
        pressed = Sg.popup_yes_no('A newer Version of the ' + software_name + ' is available.\n'
                                  'For proper functionality and new features please consider downloading the newest '
                                  'version. \nDo you want to get to the download page?',
                                  keep_on_top=True,
                                  title='Update available')
        if pressed is None:
            return False
        if pressed == 'Yes':
            webbrowser.open(latest_version_url)
    return True
