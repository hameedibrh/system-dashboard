# Tenet - System Dashboard | Local Development Guide

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git
- 2GB+ RAM available

### Run Tenet Locally

```bash
# Clone repository
git clone https://github.com/hameedibrh/system-dashboard.git
cd system-dashboard

# Start all services
docker-compose up -d

# Wait 10 seconds for services to initialize
sleep 10

# Access Tenet at http://localhost:8081
open http://localhost:8081
# or
curl http://localhost:8081
```

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:5000/api/health | json_pp

# System metrics
curl http://localhost:5000/api/system | json_pp

# Docker containers
curl http://localhost:5000/api/docker/containers | json_pp
```

### Stop Services

```bash
docker-compose down
```

### Rebuild Images

```bash
docker-compose build
docker-compose up -d
```

## Development Tips

### Backend Development

Edit files in `backend/` and restart:
```bash
docker-compose restart backend

# Or rebuild if requirements.txt changed
docker-compose build backend
docker-compose up -d backend
```

### Frontend Development

Edit files in `frontend/src/` - changes automatically reload:
```bash
# Changes are hot-reloaded in the container
# Just refresh the browser
```

### Access Container Shell

```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh
```

### View Container Logs

```bash
docker-compose logs backend --tail 50 -f
docker-compose logs frontend --tail 50 -f
```

### Clean Up

```bash
# Remove containers and volumes
docker-compose down -v

# Remove images too
docker-compose down -v --rmi all
```

## Architecture

```
http://localhost:8081 (Frontend - Nginx)
         ↓
    Reverse Proxy
         ↓
    /api/* → Backend (Port 5000 - Flask)
    /socket.io → WebSocket connection to Backend
```

## File Structure

```
.
├── docker-compose.yml       # Orchestration
├── backend/
│   ├── Dockerfile
│   ├── app.py              # Flask app
│   ├── requirements.txt
│   └── api/
│       ├── system.py       # System metrics
│       └── docker_mgmt.py  # Docker management
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── nginx.conf
│   └── src/
│       ├── App.jsx         # Main app
│       ├── services/
│       │   └── api.js      # API client
│       └── components/     # React components
├── scripts/
│   ├── pull-and-rebuild.sh
│   ├── webhook-server.py
│   └── health-check.sh
└── docs/
    ├── SERVER-DEPLOYMENT.md # Deployment guide
    └── LOCAL-DEV.md        # This file
```

## Debugging

### Check Docker Networks

```bash
docker network ls
docker network inspect dashboard-network
```

### Check Container Status

```bash
docker-compose ps

# Detailed info
docker-compose ps -a

# Only running
docker-compose ps --filter "status=running"
```

### DNS Issues

Containers communicate by service name (backend, frontend):
```bash
# Test from frontend
docker-compose exec frontend ping backend

# Test from backend
docker-compose exec backend ping frontend
```

### Port Issues

```bash
# Check if ports are free
lsof -i :8081
lsof -i :5000

# Check with netstat
netstat -tulpn | grep 8081
```

## Common Issues

### "Connection refused" when accessing http://localhost:8081
- Wait 10 seconds for services to fully start
- Check `docker-compose ps` - all should be "Up"
- Check logs: `docker-compose logs frontend`

### Backend returns "Cannot connect to Docker"
- Ensure docker.sock is mounted in docker-compose.yml
- Check current user can access docker: `docker ps`
- Try: `sudo usermod -aG docker $USER`

### High CPU usage
- Normal during initial build
- Check if something is running: `docker-compose ps`
- Restart: `docker-compose restart`

### Out of disk space
- Clean up old images: `docker system prune -a`
- Check disk: `df -h`

## Project Naming

Tenet - System Dashboard is the official project name. All code, documentation, and deployment references use this naming.
