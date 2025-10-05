#!/bin/bash
# =====================================================================
# Syncs only BJJ app models from Dev → Prod
# Supports auto-backup, rollback, S3 backup storage,
# backup rotation, dry-run, and internal JSON validation.
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

# Only sync your app's models
MODELS="bjj.Video bjj.Tag bjj.Position bjj.Technique bjj.Guard"

BACKUP_BUCKET="s3://jiujitsuteria-mediia/backups"
DEV_DUMP_PATH="s3://jiujitsuteria-mediia/dev-dumps"

# -------------------------
# Functions
# -------------------------

validate_json() {
  local FILE=$1
  echo "[*] Validating JSON file: $FILE"
  if ! command -v jq > /dev/null; then
    echo "❌ jq is required to validate JSON."
    exit 1
  fi
  MODELS_IN_FILE=$(jq -r '.[].model' "$FILE" | sort -u)
  for m in $MODELS_IN_FILE; do
    if ! [[ " $MODELS " =~ " $m " ]]; then
      echo "❌ Validation failed: Disallowed model found in JSON: $m"
      exit 1
    fi
  done
  echo "[✓] JSON validation passed. Only allowed models present."
}

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
  echo "[1/7] Running migrations on DEV..."
  python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.dev

  echo "[2/7] Dumping DEV app data..."
  python3 manage.py dumpdata $MODELS \
    --natural-foreign --natural-primary --indent 2 \
    --settings=jiujitsuteria.settings.dev > "$TMP_FILE"

  # Validate JSON locally before upload
  validate_json "$TMP_FILE"

  # Upload DEV dump to S3
  echo "[3/7] Uploading DEV dump to S3..."
  aws s3 cp "$TMP_FILE" "$DEV_DUMP_PATH/$TMP_FILE"
  echo "[✓] Uploaded to $DEV_DUMP_PATH/$TMP_FILE"

  # PROD migrations
  echo "[4/7] Running migrations on PROD..."
  ssh "$PROD_HOST" "cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.prod"

  # Backup PROD app data only
  echo "[5/7] Backing up PROD app data..."
  ssh "$PROD_HOST" "cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py dumpdata $MODELS \
      --natural-foreign --natural-primary --indent 2 \
      --settings=jiujitsuteria.settings.prod > $SHARED_PATH/$BACKUP_FILE"

  # Upload PROD backup to S3
  echo "[6/7] Uploading PROD backup to S3..."
  ssh "$PROD_HOST" "aws s3 cp $SHARED_PATH/$BACKUP_FILE $BACKUP_BUCKET/"
  echo "[✓] Backup uploaded to $BACKUP_BUCKET/$BACKUP_FILE"

  # Dry-run exit
  if [ "$DRY_RUN" == "true" ]; then
    echo "[7/7] Dry-run complete — skipping PROD load."
    rm -f "$TMP_FILE"
    return 0
  fi

  # Load DEV dump into PROD
  echo "[7/7] Loading DEV app data into PROD..."
  ssh "$PROD_HOST" "aws s3 cp $DEV_DUMP_PATH/$TMP_FILE $SHARED_PATH/$TMP_FILE && \
    cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py loaddata $SHARED_PATH/$TMP_FILE --settings=jiujitsuteria.settings.prod"
  echo "[✓] Sync complete — PROD updated with latest DEV app data."

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

  # Validate backup JSON locally (download from S3 first)
  aws s3 cp "$BACKUP_BUCKET/$BACKUP_TO_RESTORE" "$BACKUP_TO_RESTORE"
  validate_json "$BACKUP_TO_RESTORE"

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
