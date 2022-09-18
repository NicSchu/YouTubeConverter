import os

import PySimpleGUI as Sg


def get_download_folder():
    home = os.path.expanduser("~")
    return os.path.join(home, "Downloads")


def get_layout():
    progress_bar = [
        [Sg.ProgressBar(100, size=(16, 20), pad=(0, 0), key='PROGRESSBAR', bar_color=('green', 'white')),
         Sg.Text("  0%", size=(4, 1), key='PERCENT')],
    ]
    input_col = [
        [
            Sg.Text("Download Folder", size=(15, 1)),
            Sg.In(default_text=get_download_folder(), size=(25, 1), enable_events=True, key="FOLDER"),
            Sg.FolderBrowse(key="BROWSE")
        ],
        [
            Sg.Text("Youtube Link", size=(15, 1)),
            Sg.In(size=(25, 1), key="LINK", right_click_menu=['&Right', ['Copy', 'Paste', 'Clear']])
        ],
        [
            Sg.Column([
                [Sg.Checkbox("Keep mp4", default=False, key="KEEP")],
                [Sg.Checkbox("Auto open Download Folder", default=True, key="OPEN")],
                [Sg.Checkbox("Enable Playlist detection", default=True, key="")]
            ]),
            Sg.Column([
                [Sg.Text("Format:")],
                [Sg.Radio("mp3", "FORMAT", default=True, key="MP3")],
                [Sg.Radio("wav", "FORMAT", key="WAV")]
            ])
        ],
        [
            Sg.Button("Download and convert", key="DOWNLOAD"),
            Sg.pin(Sg.Column(progress_bar, key='PROGRESS', visible=False))
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
