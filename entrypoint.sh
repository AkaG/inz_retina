#!/bin/sh

# Exit on error
set -e

# Create database migrations
python manage.py makemigrations

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Exec default
exec "$@"