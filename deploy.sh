#!/usr/bin/env bash
set -euo pipefail

APP_NAME="bjj_app"
DEPLOY_USER="deploy"
APP_DIR="/home/$DEPLOY_USER/$APP_NAME"
RELEASES_DIR="$APP_DIR/releases"
SHARED_DIR="$APP_DIR/shared"
CURRENT_DIR="$APP_DIR/current"
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
NEW_RELEASE_DIR="$RELEASES_DIR/$TIMESTAMP"

echo ">>> Starting deployment to $NEW_RELEASE_DIR"

# 1. Ensure base directories exist
mkdir -p $RELEASES_DIR
mkdir -p $SHARED_DIR/{venv,media,static}

# 2. Clone repo into new release directory
git clone -b main https://github.com/asabo-dev/Jiujitsuteria.git $NEW_RELEASE_DIR

# 3. Link shared resources
ln -sfn $SHARED_DIR/.env $NEW_RELEASE_DIR/.env
ln -sfn $SHARED_DIR/media $NEW_RELEASE_DIR/media
ln -sfn $SHARED_DIR/static $NEW_RELEASE_DIR/static

# 4. Set up virtual environment
if [ ! -d "$SHARED_DIR/venv" ]; then
  echo ">>> Creating virtualenv in $SHARED_DIR/venv"
  python3 -m venv $SHARED_DIR/venv
fi
source $SHARED_DIR/venv/bin/activate
pip install --upgrade pip
pip install -r $NEW_RELEASE_DIR/requirements.lock

# 5. Run Django migrations & collectstatic
cd $NEW_RELEASE_DIR
python3 manage.py migrate --noinput --settings=jiujitsuteria.settings.prod
python3 manage.py collectstatic --noinput --settings=jiujitsuteria.settings.prod

# 6. Update symlink to point to new release
ln -sfn $NEW_RELEASE_DIR $CURRENT_DIR

# 7. Reload Gunicorn + Nginx (graceful, zero downtime)
echo ">>> Reloading services..."
sudo systemctl reload gunicorn
sudo systemctl reload nginx

# 8. Clean up old releases (keep last 5)
echo ">>> Cleaning up old releases..."
ls -1dt $RELEASES_DIR/* | tail -n +6 | xargs rm -rf || true

echo ">>> Deployment finished successfully at $(date)"
