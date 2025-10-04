#!/bin/bash
# =====================================================================
# Syncs BJJ models from Dev (SQLite) → Prod (RDS)
# Includes auto-backup, rollback support, S3 backup storage,
# backup rotation (keep last 3), and --dry-run support.
#
# Usage:
#   ./scripts/sync_data.sh            # full sync (Dev -> S3 -> Prod)
#   ./scripts/sync_data.sh --dry-run  # run everything except the final loaddata
#   ./scripts/sync_data.sh --rollback backup_YYYYMMDD_HHMMSS.json
# =====================================================================
set -euo pipefail

# -------------------------
# Config (edit PROD_HOST if needed)
# -------------------------
PROD_HOST="deploy@ec2-18-142-37-231.ap-southeast-1.compute.amazonaws.com"
PROD_PATH="/home/deploy/bjj_app/current"
SHARED_PATH="/home/deploy/bjj_app/shared"
TMP_FILE="bjj_data.json"
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).json"
MODELS="bjj.Video bjj.Tag bjj.Position bjj.Technique bjj.Guard"

# S3 bucket and folder paths
BACKUP_BUCKET="s3://jiujitsuteria-mediia/backups"
DEV_DUMP_PATH="s3://jiujitsuteria-mediia/dev-dumps"

# -------------------------
# Helper Functions
# -------------------------

sync_data() {
  local DRY_RUN=${1:-false}

  echo "-----------------------------------------------"
  echo "[*] Starting sync process (Dry-run: $DRY_RUN)"
  echo "-----------------------------------------------"

  # 0) Safety: ensure dev SQLite DB exists
  if [ ! -f "db.sqlite3" ]; then
    echo "❌ Dev database (db.sqlite3) not found!"
    echo "Make sure it is downloaded before running this script."
    exit 1
  fi
  echo "[✓] Dev database found: db.sqlite3"

  # 1) Run migrations on DEV (so dump won't fail)
  echo "[1/8] Running migrations on DEV..."
  python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.dev

  # 2) Dump selected models from DEV
  echo "[2/8] Dumping data from DEV (SQLite)..."
  python3 manage.py dumpdata $MODELS \
    --natural-foreign --natural-primary --indent 2 \
    --settings=jiujitsuteria.settings.dev > "$TMP_FILE"
  echo "[✓] Dump complete: $TMP_FILE"

  # 3) Upload DEV dump to S3 dev-dumps/
  echo "[3/8] Uploading DEV dump to S3 ($DEV_DUMP_PATH)..."
  aws s3 cp "$TMP_FILE" "$DEV_DUMP_PATH/$TMP_FILE"
  echo "[✓] Uploaded $TMP_FILE to $DEV_DUMP_PATH/$TMP_FILE"

  # 4) Run migrations on PROD (before taking backup)
  echo "[4/8] Running migrations on PROD (before backup)..."
  ssh "$PROD_HOST" "cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.prod"

  # 5) Backup PROD DB and upload to S3
  echo "[5/8] Backing up PROD DB..."
  ssh "$PROD_HOST" "cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py dumpdata $MODELS \
      --natural-foreign --natural-primary --indent 2 \
      --settings=jiujitsuteria.settings.prod > $SHARED_PATH/$BACKUP_FILE"
  echo "[✓] Backup saved on PROD: $SHARED_PATH/$BACKUP_FILE"

  echo "[6/8] Uploading PROD backup to S3 ($BACKUP_BUCKET)..."
  ssh "$PROD_HOST" "aws s3 cp $SHARED_PATH/$BACKUP_FILE $BACKUP_BUCKET/"
  echo "[✓] Backup uploaded to $BACKUP_BUCKET/$BACKUP_FILE"

  # 6b) Prune old S3 backups (keep only last 3)
  echo "[7/8] Pruning old S3 backups (keep last 3)..."
  OLD_FILES=$(ssh "$PROD_HOST" "aws s3 ls $BACKUP_BUCKET/ | awk '{print \$4}' | grep '^backup_' | sort")
  if [ -n "$OLD_FILES" ]; then
    COUNT=$(echo "$OLD_FILES" | wc -l)
    if [ "$COUNT" -gt 3 ]; then
      TO_DELETE_COUNT=$((COUNT - 3))
      echo "$OLD_FILES" | head -n "$TO_DELETE_COUNT" | while read -r oldf; do
        if [ -n "$oldf" ]; then
          echo "Deleting old backup: $oldf"
          ssh "$PROD_HOST" "aws s3 rm $BACKUP_BUCKET/$oldf"
        fi
      done
    else
      echo "No prune needed; $COUNT backups found."
    fi
  else
    echo "No S3 backups found to prune."
  fi
  echo "[✓] S3 backup prune complete."

  # 7) If dry-run, stop here
  if [ "$DRY_RUN" == "true" ]; then
    echo "[8/8] Dry-run mode — skipping load into PROD."
    echo "[✓] Dry-run complete."
    rm -f "$TMP_FILE"
    return 0
  fi

  # 8) Fetch latest DEV dump to PROD and load into DB
  echo "[8/8] Loading DEV dump into PROD DB..."
  ssh "$PROD_HOST" "aws s3 cp $DEV_DUMP_PATH/$TMP_FILE $SHARED_PATH/$TMP_FILE && \
    cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.prod && \
    python3 manage.py loaddata $SHARED_PATH/$TMP_FILE --settings=jiujitsuteria.settings.prod"
  echo "[✓] Sync complete — PROD updated with latest DEV data."

  # Clean up temp dump
  rm -f "$TMP_FILE"
}

rollback() {
  if [ -z "${1:-}" ]; then
    echo "[!] You must provide a backup file name (e.g. backup_20251004_193000.json)."
    echo "Usage: $0 --rollback <backup_file.json>"
    exit 1
  fi
  BACKUP_TO_RESTORE=$1
  echo "[*] Restoring PROD DB from S3 backup: $BACKUP_TO_RESTORE ..."

  # Check backup file exists in S3
  if ! aws s3 ls "$BACKUP_BUCKET/$BACKUP_TO_RESTORE" > /dev/null 2>&1; then
    echo "❌ Backup file not found: $BACKUP_BUCKET/$BACKUP_TO_RESTORE"
    exit 1
  fi

  # Restore the backup into PROD
  ssh "$PROD_HOST" "aws s3 cp $BACKUP_BUCKET/$BACKUP_TO_RESTORE $SHARED_PATH/$BACKUP_TO_RESTORE && \
    cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py loaddata $SHARED_PATH/$BACKUP_TO_RESTORE --settings=jiujitsuteria.settings.prod"

  echo "[✓] Rollback complete — restored from $BACKUP_TO_RESTORE."
}

# -------------------------
# Main
# -------------------------
if [ "${1:-}" == "--rollback" ]; then
  rollback "$2"
elif [ "${1:-}" == "--dry-run" ]; then
  sync_data true
else
  sync_data false
fi
