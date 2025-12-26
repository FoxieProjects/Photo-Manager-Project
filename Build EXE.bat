@echo off
pyinstaller --noconsole --onedir --collect-all customtkinter --icon=logo.ico SC.py
pause
