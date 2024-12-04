#!/bin/sh

set -e

python manage.py collectstatic --no-input
python manage.py waitfordb
python manage.py migrate --fake movies 0001
python manage.py migrate
python manage.py createsuperuser --noinput || true
uwsgi --ini uwsgi.ini
