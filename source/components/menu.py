import webbrowser
import PySimpleGUI as Sg

from source.constants import github_repo_url, software_name, version, build_date


def handle_about_click():
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


def handle_settings_click(window, w_values):
    popup_layout = [
        [
            Sg.Column([
                [Sg.Checkbox("Keep mp4", default=w_values["KEEP"], key="KEEP")],
                [Sg.Checkbox("Auto open Download Folder", default=w_values["OPEN"], key="OPEN")],
                [Sg.Checkbox("Enable Playlist detection", default=w_values["PLAYLIST"], key="PLAYLIST")]
            ])
        ]
    ]
    popup_window = Sg.Window("Settings", popup_layout, modal=True, enable_close_attempted_event=True)
    event, values = popup_window.read()
    popup_window.close()
    if popup_window.was_closed():
        window["KEEP"].update(values["KEEP"])
        window["OPEN"].update(values["OPEN"])
        window["PLAYLIST"].update(values["PLAYLIST"])
