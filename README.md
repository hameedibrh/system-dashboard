# Tenet - System Dashboard

Real-time Linux system monitoring and Docker management dashboard. Keep your infrastructure under control.

## Features
- **System Metrics**: CPU, RAM, disk usage, network stats in real-time
- **Docker Management**: View, start, and stop Docker containers
- **Real-time Updates**: WebSocket-based live data streaming
- **Responsive UI**: Access from any device at port 8081
- **Beautiful Dashboard**: Modern dark theme with smooth animations

## Quick Start

### Local Development
```bash
git clone https://github.com/hameedibrh/system-dashboard.git
cd system-dashboard
docker-compose up -d
```

Access Tenet at `http://localhost:8081`

### Server Deployment
See [SERVER-DEPLOYMENT.md](SERVER-DEPLOYMENT.md) for complete setup instructions.

## Architecture
- **Backend**: Python Flask API + psutil + Docker SDK
- **Frontend**: React dashboard with real-time WebSocket
- **Deployment**: Docker Compose + GitHub webhook auto-deployment

## Documentation
- [Server Deployment Guide](SERVER-DEPLOYMENT.md) - Production setup
- [Local Development](LOCAL-DEV.md) - Development setup
- [Contributing](CONTRIBUTING.md) - How to contribute

## License
MIT License - See [LICENSE](LICENSE)
