#!/bin/bash

# Tenet - System Dashboard auto-deployment script
# Triggered by GitHub webhook when changes are pushed to main branch
# This script pulls the latest changes and rebuilds Docker containers

set -e  # Exit on error

# Configuration
DASHBOARD_DIR="/opt/tenet-dashboard"
LOG_FILE="/var/log/tenet-dashboard-deploy.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Logging function
log() {
    echo "[$TIMESTAMP] $1" >> $LOG_FILE
    echo "[$TIMESTAMP] $1"
}

log "========================================"
log "Starting Tenet - System Dashboard deployment..."
log "========================================"

# Check if directory exists
if [ ! -d "$DASHBOARD_DIR" ]; then
    log "ERROR: Dashboard directory not found at $DASHBOARD_DIR"
    exit 1
fi

cd $DASHBOARD_DIR
log "Working directory: $(pwd)"

# Pull latest changes
log "Pulling latest changes from GitHub..."
if ! git pull origin main >> $LOG_FILE 2>&1; then
    log "ERROR: Failed to pull from GitHub"
    exit 1
fi
log "Successfully pulled latest code"

# Check docker and docker-compose
if ! command -v docker &> /dev/null; then
    log "ERROR: Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log "ERROR: Docker Compose is not installed"
    exit 1
fi

log "Docker version: $(docker --version)"
log "Docker Compose version: $(docker-compose --version)"

# Stop running containers
log "Stopping running containers..."
if docker-compose down >> $LOG_FILE 2>&1; then
    log "Successfully stopped containers"
else
    log "WARNING: Could not stop containers (they may not be running)"
fi

# Build images
log "Building Docker images..."
if ! docker-compose build >> $LOG_FILE 2>&1; then
    log "ERROR: Failed to build Docker images"
    exit 1
fi
log "Successfully built Docker images"

# Start containers
log "Starting Docker containers..."
if ! docker-compose up -d >> $LOG_FILE 2>&1; then
    log "ERROR: Failed to start Docker containers"
    exit 1
fi
log "Successfully started Docker containers"

# Wait for services to be ready
log "Waiting for services to be ready..."
sleep 5

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    log "SUCCESS: All containers are running"
    SERVER_IP=$(hostname -I | awk '{print $1}')
    log "Tenet Dashboard available at http://$SERVER_IP:8081"
    log "========================================"
    log "Deployment completed successfully!"
    log "========================================"
else
    log "ERROR: Some containers failed to start"
    log "Showing container status:"
    docker-compose ps >> $LOG_FILE 2>&1
    exit 1
fi
