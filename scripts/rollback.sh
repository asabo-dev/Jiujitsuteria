#!/bin/bash
set -euo pipefail

# --- Paths ---
APP_DIR="/home/deploy/bjj_app"
RELEASES_DIR="$APP_DIR/releases"
CURRENT_LINK="$APP_DIR/current"
LOG_DIR="$APP_DIR/shared/logs"
LOG_FILE="$LOG_DIR/rollback.log"
SCRIPT_DIR="$APP_DIR/Jiujitsuteria/scripts"

GUNICORN_SERVICE="gunicorn"   # change if different
NGINX_SERVICE="nginx"

# --- Config ---
RELEASE_RETENTION=5   # keep only the last 5 releases

# Ensure log dir exists
mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "[Rollback] 🚨 Starting rollback at $(date)"

# Ensure scripts are executable
chmod +x "$SCRIPT_DIR"/*.sh || true

# Get list of releases sorted by time (newest first)
releases=($(ls -1t "$RELEASES_DIR"))

if [ ${#releases[@]} -lt 2 ]; then
    echo "[Rollback] ❌ Not enough releases to rollback."
    exit 1
fi

# Find current release
current_target=$(readlink -f "$CURRENT_LINK")
current_release=$(basename "$current_target")
echo "[Rollback] Current release: $current_release"

# Previous release = second newest
previous_release=${releases[1]}
echo "[Rollback] Target rollback release: $previous_release"

# Update symlink
ln -sfn "$RELEASES_DIR/$previous_release" "$CURRENT_LINK"
echo "[Rollback] 🔗 Updated 'current' symlink -> $previous_release"

# Restart services
echo "[Rollback] 🔄 Restarting services..."
sudo systemctl restart "$GUNICORN_SERVICE"
sudo systemctl restart "$NGINX_SERVICE"

echo "[Rollback] ✅ Rollback complete. Active release is now: $previous_release"

# Cleanup: remove broken release
if [ -d "$RELEASES_DIR/$current_release" ]; then
    echo "[Rollback] 🧹 Cleaning up broken release: $current_release"
    rm -rf "$RELEASES_DIR/$current_release"
fi

# Retention policy: keep only last N releases
if [ ${#releases[@]} -gt $RELEASE_RETENTION ]; then
    old_releases=("${releases[@]:$RELEASE_RETENTION}")
    for rel in "${old_releases[@]}"; do
        echo "[Rollback] 🗑️ Removing old release: $rel"
        rm -rf "$RELEASES_DIR/$rel"
    done
fi

echo "[Rollback] 🎉 Rollback finished at $(date)"
