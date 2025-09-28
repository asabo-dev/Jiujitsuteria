#!/bin/bash
set -e

APP_DIR=/home/deploy/bjj_app/current
VENV_DIR=/home/deploy/bjj_app/shared/venv
LOG_DIR=/home/deploy/bjj_app/shared/logs
LOG_FILE=$LOG_DIR/deploy.log

# Ensure log dir exists
mkdir -p $LOG_DIR

# Redirect stdout and stderr to log file + console
exec > >(tee -a $LOG_FILE) 2>&1

echo "🚀 Starting deployment as $(whoami) at $(date)"

# 1. Go to project root
cd $APP_DIR

# 2. Pull latest code
echo "📥 Pulling latest code..."
git fetch origin main
git reset --hard origin/main

# 3. Create venv if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtualenv..."
    python3 -m venv $VENV_DIR
fi

# 4. Activate venv & install dependencies
echo "📦 Installing dependencies..."
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Collect static files with prod settings
echo "🎨 Collecting static files..."
python3 manage.py collectstatic --noinput --settings=jiujitsuteria.settings.prod

# 6. Apply migrations with prod settings
echo "🗂️ Applying migrations..."
python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.prod

# 7. Restart services
echo "🔄 Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "✅ Deployment finished successfully at $(date)"
