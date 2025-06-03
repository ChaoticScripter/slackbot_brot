#!/bin/bash

# Konstanten
SERVER="root@45.149.204.117"
DEPLOY_PATH="/var/www/brotbot"

# Server-Verzeichnis vorbereiten
ssh $SERVER "mkdir -p $DEPLOY_PATH && \
    apt update && \
    apt install -y python3-pip python3-venv rsync supervisor nginx && \
    mkdir -p /var/log/brotbot && \
    chown -R www-data:www-data /var/log/brotbot"

# Dateien synchronisieren
rsync -avz --exclude 'venv' \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude '.env' \
    ./ $SERVER:$DEPLOY_PATH/

# Deployment auf Server
ssh $SERVER "cd $DEPLOY_PATH && \
    python3 -m venv venv && \
    source venv/bin/activate && \
    pip install -r requirements.txt && \
    chown -R www-data:www-data . && \
    systemctl restart supervisor && \
    supervisorctl restart brotbot"

echo "Deployment abgeschlossen!"
