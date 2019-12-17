#! /usr/bin/env sh
set -e
echo "Running inside /app/prestart.sh"
export DJANGO_SETTINGS_MODULE=djocker.settings.preprod
# Don't stop building when compilemessages fail
cd /app && python manage.py migrate && python manage.py compilemessages --settings=djocker.settings.test || true
# TODO: collectstatic in shared volume for nginx !

exec "$@"

