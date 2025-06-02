@echo off
call venv\Scripts\activate
set FLASK_DEBUG=1
set FLASK_ENV=development
flask --app main.py run --debug 