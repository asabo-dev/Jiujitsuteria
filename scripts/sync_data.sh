#!/usr/bin/env bash
# =====================================================================
# Syncs only BJJ app models from Dev → Prod
# Supports auto-backup, rollback, S3 backup storage,
# backup rotation, dry-run, and internal JSON validation.
# Works both locally and in GitHub Actions.
# =====================================================================
set -euo pipefail
trap 'rm -f "$TMP_FILE"' EXIT

# -------------------------
# Config
# -------------------------
PROD_HOST="deploy@ec2-18-142-37-231.ap-southeast-1.compute.amazonaws.com"
PROD_PATH="/home/deploy/bjj_app/current"
SHARED_PATH="/home/deploy/bjj_app/shared"
TMP_FILE="bjj_data.json"
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).json"

# Only sync your app's models
MODELS='bjj.Video bjj.Tag bjj.Position bjj.Technique bjj.Guard'

BACKUP_BUCKET="s3://jiujitsuteria-mediia/backups"
DEV_DUMP_PATH="s3://jiujitsuteria-mediia/dev-dumps"

# -------------------------
# Functions
# -------------------------

activate_venv() {
  if [ -d "venv" ]; then
    echo "[*] Activating virtual environment (venv)..."
    source venv/bin/activate
  elif [ -d ".venv" ]; then
    echo "[*] Activating virtual environment (.venv)..."
    source .venv/bin/activate
  else
    echo "[!] No virtual environment found — proceeding with system Python."
  fi
}

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
  echo "[✓] JSON validation passed."
}

sync_data() {
  local DRY_RUN=${1:-false}
  echo "-----------------------------------------------"
  echo "[*] Starting sync process (Dry-run: $DRY_RUN)"
  echo "-----------------------------------------------"

  activate_venv

  if [ ! -f "db.sqlite3" ]; then
    echo "❌ Dev database (db.sqlite3) not found!"
    exit 1
  fi
  echo "[✓] Dev database found."

  echo "[1/7] Running migrations on DEV..."
  python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.dev

  echo "[2/7] Dumping DEV app data..."
  python3 manage.py dumpdata $MODELS \
    --natural-foreign --natural-primary --indent 2 \
    --settings=jiujitsuteria.settings.dev > "$TMP_FILE"

  validate_json "$TMP_FILE"

  echo "[3/7] Uploading DEV dump to S3..."
  aws s3 cp "$TMP_FILE" "$DEV_DUMP_PATH/$TMP_FILE"

  echo "[4/7] Running migrations on PROD..."
  ssh -o StrictHostKeyChecking=no "$PROD_HOST" "cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.prod"

  echo "[5/7] Backing up PROD data..."
  ssh -o StrictHostKeyChecking=no "$PROD_HOST" "cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py dumpdata $MODELS \
      --natural-foreign --natural-primary --indent 2 \
      --settings=jiujitsuteria.settings.prod > $SHARED_PATH/$BACKUP_FILE"

  echo "[6/7] Uploading PROD backup to S3..."
  ssh -o StrictHostKeyChecking=no "$PROD_HOST" "aws s3 cp $SHARED_PATH/$BACKUP_FILE $BACKUP_BUCKET/"

  if [ "$DRY_RUN" == "true" ]; then
    echo "[7/7] Dry-run complete — skipping PROD load."
    return 0
  fi

  echo "[7/7] Loading DEV app data into PROD..."
  ssh -o StrictHostKeyChecking=no "$PROD_HOST" "aws s3 cp $DEV_DUMP_PATH/$TMP_FILE $SHARED_PATH/$TMP_FILE && \
    cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py loaddata $SHARED_PATH/$TMP_FILE --settings=jiujitsuteria.settings.prod"

  echo "[✓] Sync complete — PROD updated with latest DEV data."
}

rollback() {
  local BACKUP_TO_RESTORE=${1:-}
  if [ -z "$BACKUP_TO_RESTORE" ]; then
    echo "[!] Specify a backup file name (e.g. backup_YYYYMMDD_HHMMSS.json)."
    exit 1
  fi
  echo "[*] Restoring PROD from $BACKUP_TO_RESTORE ..."
  activate_venv
  aws s3 cp "$BACKUP_BUCKET/$BACKUP_TO_RESTORE" "$BACKUP_TO_RESTORE"
  validate_json "$BACKUP_TO_RESTORE"
  ssh -o StrictHostKeyChecking=no "$PROD_HOST" "aws s3 cp $BACKUP_BUCKET/$BACKUP_TO_RESTORE $SHARED_PATH/$BACKUP_TO_RESTORE && \
    cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py loaddata $SHARED_PATH/$BACKUP_TO_RESTORE --settings=jiujitsuteria.settings.prod"
  echo "[✓] Rollback complete."
}

case "${1:-}" in
  --rollback) rollback "${2:-}" ;;
  --dry-run)  sync_data true ;;
  *)          sync_data false ;;
esac
