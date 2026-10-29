#!/bin/bash

# Configuration
SERVER="yportal@194.163.154.154"
TARGET_DIR="/home/yportal/yemenportal"

echo "======================================"
echo "🚀 Deploying Yemen Portal to Production"
echo "======================================"

# Sync files using rsync (excluding local dev files)
echo "[1/3] Syncing files to server..."
rsync -avz --delete \
    --exclude '.git' \
    --exclude '.env' \
    --exclude '.env.*' \
    --exclude 'docker-compose.override.yml' \
    --exclude 'local_seed.json' \
    --exclude 'celerybeat-schedule' \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '*.sqlite3' \
    --exclude 'media' \
    --exclude 'staticfiles' \
    --exclude 'node_modules' \
    --exclude 'yp.sql' \
    --exclude 'rails_source' \
    ./ $SERVER:$TARGET_DIR

# SSH into the server and run docker-compose
echo "[2/3] Building and restarting containers on the server..."
ssh $SERVER << 'EOF'
    cd /home/yportal/yemenportal
    echo "yementimes" | sudo -S docker compose -f docker-compose.yml -f docker-compose.prod.yml build
    echo "yementimes" | sudo -S docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
EOF

echo "[3/3] Running migrations and collecting static files..."
ssh $SERVER << 'EOF'
    cd /home/yportal/yemenportal
    echo "yementimes" | sudo -S docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T web python manage.py migrate
    echo "yementimes" | sudo -S docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput
EOF

echo "✅ Deployment complete! The website should be available at http://194.163.154.154"
