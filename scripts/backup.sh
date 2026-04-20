#!/usr/bin/env bash
# Daily Postgres backup.
# Usage: /opt/anasklad/scripts/backup.sh
#
# Cron:
#   0 3 * * * /opt/anasklad/scripts/backup.sh >> /var/log/anasklad-backup.log 2>&1

set -euo pipefail

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
DB_USER="${POSTGRES_USER:-anasklad}"
DB_NAME="${POSTGRES_DB:-anasklad}"

mkdir -p "$OUT_DIR"

FILE="$OUT_DIR/anasklad_${STAMP}.sql.gz"
echo "[backup] starting → $FILE"

docker compose -f docker-compose.prod.yml exec -T postgres \
    pg_dump -U "$DB_USER" -d "$DB_NAME" --no-owner --clean --if-exists \
    | gzip -9 > "$FILE"

SIZE=$(du -h "$FILE" | cut -f1)
echo "[backup] done: $FILE ($SIZE)"

# Retention — delete older than RETENTION_DAYS
find "$OUT_DIR" -name 'anasklad_*.sql.gz' -mtime +"$RETENTION_DAYS" -delete
echo "[backup] rotated backups older than ${RETENTION_DAYS}d"

# Optional: push to S3-compatible storage
if [ -n "${S3_BUCKET:-}" ]; then
    aws s3 cp "$FILE" "s3://$S3_BUCKET/backups/" --only-show-errors
    echo "[backup] uploaded to s3://$S3_BUCKET/backups/"
fi
