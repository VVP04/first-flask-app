#!/usr/bin/env bash
set -e  # Прекратить выполнение при ошибке

echo "Loading database schema from database.sql..."
psql -v ON_ERROR_STOP=1 -a -d "$DATABASE_URL" -f init.sql
echo "Database schema loaded successfully!"