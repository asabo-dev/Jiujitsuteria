#!/bin/bash
# scripts/sync_data.sh
# Syncs BJJ models from Dev (SQLite) → Prod (RDS)
# Includes auto-backup, rollback support, and S3 backup storage

set -euo pipefail

# -------------------------
# Config
# -------------------------
PROD_HOST="deploy@your-prod-server"
PROD_PATH="/home/deploy/bjj_app/current"
TMP_FILE="bjj_data.json"
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).json"
MODELS="bjj.Video bjj.Tag bjj.Position bjj.Technique bjj.Guard"

# S3 bucket for backups
BACKUP_BUCKET="s3://jiujitsuteria-mediia/backups"

# -------------------------
# Helper Functions
# -------------------------
sync_data() {
  echo "[*] Dumping from DEV (SQLite)..."
  python3 manage.py dumpdata $MODELS \
    --natural-foreign --natural-primary --indent 2 > $TMP_FILE

  echo "[*] Copying JSON to PROD..."
  scp $TMP_FILE $PROD_HOST:$PROD_PATH/

  echo "[*] Backing up PROD DB..."
  ssh $PROD_HOST "cd $PROD_PATH && source ../shared/venv/bin/activate && \
    python3 manage.py dumpdata $MODELS \
      --natural-foreign --natural-primary --indent 2 > $BACKUP_FILE \
      --settings=jiujitsuteria.settings.prod"

  echo "[✓] Backup saved as $BACKUP_FILE on PROD"

  echo "[*] Uploading backup to S3..."
  ssh $PROD_HOST "aws s3 cp $PROD_PATH/$BACKUP_FILE $BACKUP_BUCKET/"
  echo "[✓] Backup uploaded to $BACKUP_BUCKET"

  echo "[*] Loading new data into PROD..."
  ssh $PROD_HOST "cd $PROD_PATH && source ../shared/venv/bin/activate && \
    python3 manage.py loaddata $TMP_FILE \
      --settings=jiujitsuteria.settings.prod"

  echo "[✓] Sync complete."
}

rollback() {
  if [ -z "${1:-}" ]; then
    echo "[!] You must provide the backup file name."
    echo "Usage: $0 --rollback <backup_file.json>"
    exit 1
  fi
  BACKUP_TO_RESTORE=$1
  echo "[*] Restoring PROD DB from $BACKUP_TO_RESTORE..."
  ssh $PROD_HOST "cd $PROD_PATH && source ../shared/venv/bin/activate && \
    python3 manage.py loaddata $BACKUP_TO_RESTORE \
      --settings=jiujitsuteria.settings.prod"
  echo "[✓] Rollback complete."
}

# -------------------------
# Main
# -------------------------
if [ "${1:-}" == "--rollback" ]; then
  rollback "$2"
else
  sync_data
fi
