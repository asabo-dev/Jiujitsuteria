#!/bin/bash
# =====================================================================
# Syncs BJJ models from Dev (SQLite) → Prod (RDS)
# Supports auto-backup, rollback, S3 backup storage, 
# backup rotation (keep last 3), and --dry-run support.
# =====================================================================
set -euo pipefail

# -------------------------
# Config
# -------------------------
PROD_HOST="deploy@ec2-18-142-37-231.ap-southeast-1.compute.amazonaws.com"
PROD_PATH="/home/deploy/bjj_app/current"
SHARED_PATH="/home/deploy/bjj_app/shared"
TMP_FILE="bjj_data.json"
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).json"
MODELS="bjj.Video bjj.Tag bjj.Position bjj.Technique bjj.Guard"

BACKUP_BUCKET="s3://jiujitsuteria-mediia/backups"
DEV_DUMP_PATH="s3://jiujitsuteria-mediia/dev-dumps"

# -------------------------
# Functions
# -------------------------

sync_data() {
  local DRY_RUN=${1:-false}

  echo "-----------------------------------------------"
  echo "[*] Starting sync process (Dry-run: $DRY_RUN)"
  echo "-----------------------------------------------"

  # Ensure Dev DB exists
  if [ ! -f "db.sqlite3" ]; then
    echo "❌ Dev database (db.sqlite3) not found!"
    exit 1
  fi
  echo "[✓] Dev database found: db.sqlite3"

  # DEV migrations & dump
  echo "[1/8] Running migrations on DEV..."
  python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.dev

  echo "[2/8] Dumping DEV data..."
  python3 manage.py dumpdata $MODELS \
    --natural-foreign --natural-primary --indent 2 \
    --settings=jiujitsuteria.settings.dev > "$TMP_FILE"

  # Upload DEV dump to S3
  echo "[3/8] Uploading DEV dump to S3..."
  aws s3 cp "$TMP_FILE" "$DEV_DUMP_PATH/$TMP_FILE"
  echo "[✓] Uploaded to $DEV_DUMP_PATH/$TMP_FILE"

  # PROD migrations
  echo "[4/8] Running migrations on PROD..."
  ssh "$PROD_HOST" "cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.prod"

  # Backup PROD
  echo "[5/8] Backing up PROD DB..."
  ssh "$PROD_HOST" "cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py dumpdata $MODELS \
      --natural-foreign --natural-primary --indent 2 \
      --settings=jiujitsuteria.settings.prod > $SHARED_PATH/$BACKUP_FILE"

  # Upload PROD backup to S3
  echo "[6/8] Uploading PROD backup to S3..."
  ssh "$PROD_HOST" "aws s3 cp $SHARED_PATH/$BACKUP_FILE $BACKUP_BUCKET/"
  echo "[✓] Backup uploaded to $BACKUP_BUCKET/$BACKUP_FILE"

  # Prune old backups (keep last 3)
  echo "[7/8] Pruning old S3 backups..."
  OLD_FILES=$(aws s3 ls "$BACKUP_BUCKET/" | awk '{print $4}' | grep '^backup_' | sort)
  if [ -n "$OLD_FILES" ]; then
    COUNT=$(echo "$OLD_FILES" | wc -l)
    if [ "$COUNT" -gt 3 ]; then
      TO_DELETE_COUNT=$((COUNT - 3))
      echo "$OLD_FILES" | head -n "$TO_DELETE_COUNT" | while read -r oldf; do
        [ -n "$oldf" ] && aws s3 rm "$BACKUP_BUCKET/$oldf"
        echo "Deleted old backup: $oldf"
      done
    else
      echo "No prune needed ($COUNT backups found)."
    fi
  else
    echo "No S3 backups found to prune."
  fi

  # Dry-run exit
  if [ "$DRY_RUN" == "true" ]; then
    echo "[8/8] Dry-run complete — skipping PROD load."
    rm -f "$TMP_FILE"
    return 0
  fi

  # Load DEV dump into PROD
  echo "[8/8] Loading DEV dump into PROD DB..."
  ssh "$PROD_HOST" "aws s3 cp $DEV_DUMP_PATH/$TMP_FILE $SHARED_PATH/$TMP_FILE && \
    cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.prod && \
    python3 manage.py loaddata $SHARED_PATH/$TMP_FILE --settings=jiujitsuteria.settings.prod"
  echo "[✓] Sync complete — PROD updated with latest DEV data."

  # Cleanup
  rm -f "$TMP_FILE"
}

rollback() {
  if [ -z "${1:-}" ]; then
    echo "[!] Specify a backup file name (e.g. backup_YYYYMMDD_HHMMSS.json)."
    exit 1
  fi
  local BACKUP_TO_RESTORE=$1
  echo "[*] Restoring PROD from $BACKUP_TO_RESTORE ..."

  if ! aws s3 ls "$BACKUP_BUCKET/$BACKUP_TO_RESTORE" > /dev/null 2>&1; then
    echo "❌ Backup file not found in S3!"
    exit 1
  fi

  ssh "$PROD_HOST" "aws s3 cp $BACKUP_BUCKET/$BACKUP_TO_RESTORE $SHARED_PATH/$BACKUP_TO_RESTORE && \
    cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py loaddata $SHARED_PATH/$BACKUP_TO_RESTORE --settings=jiujitsuteria.settings.prod"

  echo "[✓] Rollback complete."
}

# -------------------------
# Main
# -------------------------
case "${1:-}" in
  --rollback) rollback "$2" ;;
  --dry-run)  sync_data true ;;
  *)          sync_data false ;;
esac
