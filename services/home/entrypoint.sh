#!/usr/bin/env sh

python manage.py migrate
#python manage.py loaddata seed/fixtures.yaml
python manage.py runserver 0.0.0.0:8000
