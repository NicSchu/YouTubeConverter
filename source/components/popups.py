import PySimpleGUI as Sg


def playlist_popup(playlist):
    return Sg.popup_yes_no('The video link is part of the playlist ' + playlist.title + '. \n'
                           'Do you want to download the whole playlist?',
                           keep_on_top=True,
                           title='Download playlist?')
