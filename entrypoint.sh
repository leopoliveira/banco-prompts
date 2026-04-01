#!/bin/bash
set -e

echo "Running Django migrations..."
python src/manage.py migrate --noinput

echo "Running Alembic migrations..."
DJANGO_SETTINGS_MODULE=config.settings PYTHONPATH=src alembic upgrade head

exec "$@"
