#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Running Alembic migrations..."
alembic upgrade head

echo "Running Django migrations..."
python manage.py migrate

echo "Starting server..."
exec "$@"
