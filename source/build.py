import subprocess

import PyInstaller.__main__

from source.youtube_converter import version


def build_one_file():
    PyInstaller.__main__.run([
        'youtube_converter.py',
        '--onefile',
        '--windowed'
    ])
    subprocess.call([r'build.bat', version, '-onefile'])


def build_normal():
    PyInstaller.__main__.run([
        'youtube_converter.py',
        '--windowed'
    ])
    subprocess.call([r'build.bat', version, ''])


if __name__ == '__main__':
    build_one_file()
    build_normal()
