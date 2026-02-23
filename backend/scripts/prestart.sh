#! /usr/bin/env bash

# Exit on error
set -e
set -x

echo "Running prestart script..."
# Let the DB start
python app/backend_pre_start.py

# Run Alembic migrations
echo "Running database migrations..."
alembic upgrade head

echo "Prestart completed successfully!"
