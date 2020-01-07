#! /usr/bin/env sh
set -e
echo "Running inside /app/prestart.sh"
export DJANGO_SETTINGS_MODULE=schedulesy.settings.test
# Don't stop building when compilemessages fail
cd /app
python manage.py migrate
python manage.py compilemessages --settings=schedulesy.settings.test || true
python manage.py collectstatic
# TODO: collectstatic in shared volume for nginx !

exec "$@"

