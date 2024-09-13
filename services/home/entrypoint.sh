#!/usr/bin/env sh

python manage.py migrate
python manage.py loaddata core/fixtures/users.json
python manage.py loaddata core/fixtures/locations.json
python manage.py loaddata core/fixtures/profiles.json
python manage.py loaddata devices/fixtures/device_types.json
python manage.py loaddata devices/fixtures/devices.json
python manage.py loaddata devices/fixtures/systems.json
python manage.py loaddata devices/fixtures/plugs.json
python manage.py runserver 0.0.0.0:8000
