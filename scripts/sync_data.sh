#!/bin/bash
# scripts/sync_data.sh
# Syncs BJJ models from Dev (SQLite) → Prod (RDS)
# Includes auto-backup, rollback support, S3 backup storage,
# backup rotation (keep last 3), and --dry-run support.

set -euo pipefail

# -------------------------
# Config
# -------------------------
PROD_HOST="deploy@your-prod-server"
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

  echo "[*] Running migrations on DEV to ensure all tables exist..."
  python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.dev

  echo "[*] Dumping data from DEV (SQLite)..."
  python3 manage.py dumpdata $MODELS \
    --natural-foreign --natural-primary --indent 2 \
    --settings=jiujitsuteria.settings.dev > $TMP_FILE
  echo "[✓] Dump complete: $TMP_FILE"

  echo "[*] Uploading DEV dump to S3 ($DEV_DUMP_PATH)..."
  aws s3 cp $TMP_FILE $DEV_DUMP_PATH/$TMP_FILE
  echo "[✓] Uploaded $TMP_FILE to $DEV_DUMP_PATH"

  echo "[*] Running migrations on PROD before backup..."
  ssh $PROD_HOST "cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.prod"

  echo "[*] Backing up PROD DB..."
  ssh $PROD_HOST "cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py dumpdata $MODELS \
      --natural-foreign --natural-primary --indent 2 \
      --settings=jiujitsuteria.settings.prod > $SHARED_PATH/$BACKUP_FILE"

  echo "[*] Uploading backup to S3..."
  ssh $PROD_HOST "aws s3 cp $SHARED_PATH/$BACKUP_FILE $BACKUP_BUCKET/"
  echo "[✓] Backup uploaded to $BACKUP_BUCKET/$BACKUP_FILE"

  echo "[*] Cleaning up old S3 backups (keep only last 3)..."
  ssh $PROD_HOST "aws s3 ls $BACKUP_BUCKET/ | grep backup_ | sort | awk '{print \$4}' | head -n -3 | while read old_file; do
      if [ -n \"\$old_file\" ]; then
        echo Deleting old backup: \$old_file
        aws s3 rm $BACKUP_BUCKET/\$old_file
      fi
    done"
  echo "[✓] Old backups pruned, keeping only the last 3."

  if [ "$DRY_RUN" == "true" ]; then
    echo "🚧 Dry-run complete. Skipping data load into production."
    echo "[✓] All other steps (dump, backup, upload, prune) completed successfully."
    return 0
  fi

  echo "[*] Fetching latest DEV dump from S3..."
  ssh $PROD_HOST "aws s3 cp $DEV_DUMP_PATH/$TMP_FILE $SHARED_PATH/$TMP_FILE"

  echo "[*] Loading new data into PROD..."
  ssh $PROD_HOST "cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py loaddata $SHARED_PATH/$TMP_FILE \
      --settings=jiujitsuteria.settings.prod"
  echo "[✓] Sync complete. PROD is now updated."
}

rollback() {
  if [ -z "${1:-}" ]; then
    echo "[!] You must provide the backup file name."
    echo "Usage: $0 --rollback <backup_file.json>"
    exit 1
  fi
  BACKUP_TO_RESTORE=$1
  echo "[*] Restoring PROD DB from $BACKUP_TO_RESTORE..."
  ssh $PROD_HOST "cd $PROD_PATH && source $SHARED_PATH/venv/bin/activate && \
    python3 manage.py loaddata $SHARED_PATH/$BACKUP_TO_RESTORE \
      --settings=jiujitsuteria.settings.prod"
  echo "[✓] Rollback complete."
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
