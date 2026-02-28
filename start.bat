@echo off
if not defined IS_MINIMIZED (
    set IS_MINIMIZED=1
    start "" /min "%~dpnx0" %*
    exit
)

call venv\Scripts\activate.bat
python manage.py runserver