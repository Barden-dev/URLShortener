#!/bin/sh

echo "Database migration started"

alembic upgrade head

echo "Database migration ended"

exec "$@"