#!/bin/bash
set -euo pipefail

# --- Paths ---
BASE_DIR=/home/deploy/bjj_app
RELEASES_DIR=$BASE_DIR/releases
CURRENT_LINK=$BASE_DIR/current
VENV_DIR=$BASE_DIR/shared/venv
LOG_DIR=$BASE_DIR/shared/logs
LOG_FILE=$LOG_DIR/deploy.log
SCRIPT_DIR=$BASE_DIR/Jiujitsuteria/scripts

# --- Flags ---
DRY_RUN=false
for arg in "$@"; do
    case $arg in
        --dry-run) DRY_RUN=true ;;
    esac
done

# Ensure log dir exists
mkdir -p "$LOG_DIR"

# Redirect stdout and stderr to log file + console
exec > >(tee -a "$LOG_FILE") 2>&1

echo "🚀 Starting deployment as $(whoami) at $(date)"
if $DRY_RUN; then
    echo "⚠️  Running in DRY-RUN mode (no services will be restarted)"
fi

# --- Functions ---
rollback() {
    echo "❌ Deployment failed! Rolling back..."
    bash "$SCRIPT_DIR/rollback.sh" || echo "⚠️ Rollback script failed, manual intervention required!"
    exit 1
}

trap rollback ERR

# Ensure scripts are executable
chmod +x "$SCRIPT_DIR"/*.sh || true

# 1. Prepare new release folder
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
NEW_RELEASE=$RELEASES_DIR/$TIMESTAMP
mkdir -p "$NEW_RELEASE"

echo "📂 New release directory: $NEW_RELEASE"

# 2. Copy latest repo into new release
rsync -a --exclude "venv" --exclude "logs" $BASE_DIR/Jiujitsuteria/ $NEW_RELEASE/

# 3. Create venv if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtualenv..."
    python3 -m venv "$VENV_DIR"
fi

# 4. Activate venv & install dependencies
echo "📦 Installing dependencies..."
source "$VENV_DIR/bin/activate"
python3 -m pip install --upgrade pip
python3 -m pip install -r $NEW_RELEASE/requirements.txt

# 5. Collect static files with prod settings
echo "🎨 Collecting static files..."
python3 $NEW_RELEASE/manage.py collectstatic --noinput --settings=jiujitsuteria.settings.prod

# 6. Apply migrations with prod settings
echo "🗂️ Applying migrations..."
python3 $NEW_RELEASE/manage.py migrate --noinput --settings=jiujitsuteria.settings.prod

# 7. Update symlink to point to new release
ln -sfn "$NEW_RELEASE" "$CURRENT_LINK"
echo "🔗 Updated current symlink to $NEW_RELEASE"

# 8. Restart services (skip if dry-run)
if $DRY_RUN; then
    echo "⏭️ Skipping service restart (dry-run mode)"
else
    echo "🔄 Restarting services..."
    sudo systemctl restart gunicorn
    sudo systemctl restart nginx
fi

echo "✅ Deployment finished successfully at $(date)"
