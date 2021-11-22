#!/usr/bin/env bash
set -euo pipefail

DATABASE_URL=postgres://postgres:example@db/postgres
DUMP_FILE=script/db.dump

echo "Dumping database..."
pg_dump -vFc $DATABASE_URL > $DUMP_FILE

echo "Done"
