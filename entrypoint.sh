#!/bin/bash
set -e

# Wait for Postgres to be ready
until PGPASSWORD=$DB_PASSWORD pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "Waiting for Postgres at $DB_HOST:$DB_PORT..."
  sleep 2
done


# Execute the command (e.g., gunicorn)
exec "$@"

