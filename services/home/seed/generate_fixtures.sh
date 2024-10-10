# May need to set `DB_HOST` i.e. `DB_HOST=localhost`
python manage.py dumpdata \
    auth.user \
    core \
    clients \
    controllers \
    devices \
    routines \
    --format=yaml --indent 2 > seed/fixtures.yaml