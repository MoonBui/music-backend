#!/bin/bash
source venv/bin/activate
export FLASK_DEBUG=1
export FLASK_ENV=development
flask --app main.py run --debug 