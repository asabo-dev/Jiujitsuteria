#!/bin/bash
set -e

# --- Paths ---
APP_DIR=/home/deploy/bjj_app/current         # always points to latest release
VENV_DIR=/home/deploy/bjj_app/shared/venv    # shared venv across releases
LOG_DIR=/home/deploy/bjj_app/shared/logs
LOG_FILE=$LOG_DIR/deploy.log

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

# 1. Go to project root
cd "$APP_DIR"

# 2. Verify we are inside the expected repo
echo "📂 Verifying repo location..."
git rev-parse --show-toplevel || {
    echo "❌ Not inside a git repo, aborting."
    exit 1
}

# 3. Pull latest code
echo "📥 Pulling latest code..."
git fetch origin main
git reset --hard origin/main

# 4. Create venv if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtualenv..."
    python3 -m venv "$VENV_DIR"
fi

# 5. Activate venv & install dependencies
echo "📦 Installing dependencies..."
source "$VENV_DIR/bin/activate"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# 6. Collect static files with prod settings
echo "🎨 Collecting static files..."
python3 manage.py collectstatic --noinput --settings=jiujitsuteria.settings.prod

# 7. Apply migrations with prod settings
echo "🗂️ Applying migrations..."
python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.prod

# 8. Restart services (skip if dry-run)
if $DRY_RUN; then
    echo "⏭️  Skipping service restart (dry-run mode)"
else
    echo "🔄 Restarting services..."
    sudo systemctl restart gunicorn
    sudo systemctl restart nginx
fi

echo "✅ Deployment finished successfully at $(date)"
