#!/usr/bin/env bash
set -euo pipefail

DATABASE_URL=postgres://postgres:example@db/postgres
DUMP_FILE=script/db.dump

echo "Restoring dump to database..."
pg_restore -v --clean --no-acl --no-owner --jobs=4 -d $DATABASE_URL $DUMP_FILE

echo "Done"
