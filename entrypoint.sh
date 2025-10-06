set -e

# Wait for Postgres to be ready
until PGPASSWORD=$DB_PASSWORD pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "Waiting for Postgres at $DB_HOST:$DB_PORT..."
  sleep 2
done

# Wait for Valkey to be ready (using redis-cli, compatible with Valkey)
until redis-cli -h $CACHE_HOST -p 6379 -a $VALKEY_PASSWORD ping > /dev/null 2>&1; do
  echo "Waiting for Valkey at $CACHE_HOST:6379..."
  sleep 2
done

# Run migrations
python manage.py migrate

# Execute the command (e.g., gunicorn)
exec "$@"