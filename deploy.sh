#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR=/home/ubuntu/bjj_app/Jiujitsuteria
VENV=$PROJECT_DIR/venv

cd $PROJECT_DIR

echo ">>> Pulling latest code from GitHub..."
git fetch origin
git checkout main
git pull origin main

echo ">>> Activating virtualenv and installing dependencies..."
source $VENV/bin/activate
pip install -r requirements.lock

echo ">>> Running migrations..."
python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.prod

echo ">>> Collecting static files..."
python3 manage.py collectstatic --noinput --settings=jiujitsuteria.settings.prod

echo ">>> Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo ">>> Deployment finished at $(date)"



