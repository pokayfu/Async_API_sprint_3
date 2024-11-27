#!/bin/sh

set -e

python manage.py collectstatic --no-input
python manage.py waitfordb
python manage.py migrate --fake movies 0001
python manage.py migrate

uwsgi --ini uwsgi.ini
