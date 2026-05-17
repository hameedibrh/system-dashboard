#!/bin/bash

# Dashboard auto-deployment script
# Triggered by GitHub webhook

set -e

echo "[$(date)] Starting deployment..."

cd /opt/system-dashboard

echo "[$(date)] Pulling latest changes from GitHub..."
git pull origin main

echo "[$(date)] Rebuilding Docker containers..."
docker-compose down
docker-compose up -d

echo "[$(date)] Deployment complete!"
echo "Dashboard available at http://$(hostname -I | awk '{print $1}'):8081"
