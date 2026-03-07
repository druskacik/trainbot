#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Running Alembic migrations..."
alembic upgrade head

echo "Running Django migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Configure Prefect to use the same PostgreSQL database
# This avoids "database is locked" errors common with SQLite
export PREFECT_API_DATABASE_CONNECTION_URL="postgresql+asyncpg://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
export PREFECT_SERVER_ANALYTICS_ENABLED=False
export PREFECT_API_DATABASE_TIMEOUT=60
export PREFECT_HOME=/app/.prefect

echo "Starting Prefect flow worker in background..."
python src/flows.py &

echo "Starting server..."
exec "$@"
