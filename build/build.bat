@echo off
echo %1
echo %2

mkdir ..\releases\%1
mkdir ..\releases\%1\%1%2
IF %2 == "" (
move .\dist\youtube_converter ..\releases\%1\%1%2\youtube_converter
xcopy ..\releases\ffmpeg\ ..\releases\%1\%1%2\youtube_converter\ffmpeg\ /E
) ELSE (
mkdir ..\releases\%1\%1%2\ffmpeg
move .\dist\youtube_converter.exe ..\releases\%1\%1%2\youtube_converter.exe
xcopy ..\releases\ffmpeg\ ..\releases\%1\%1%2\ffmpeg\ /E
)
7z a -r ..\releases\%1\%1%2.zip ..\releases\%1\%1%2
7z a -r ..\releases\%1\%1%2.7z ..\releases\%1\%1%2