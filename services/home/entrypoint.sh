#!/usr/bin/env sh

python manage.py migrate
python manage.py loaddata core/fixtures/users.json
python manage.py runserver 0.0.0.0:8000
