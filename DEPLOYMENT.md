# Tenet Dashboard | Server Deployment Guide

## Prerequisites

On your Linux server, ensure you have:
- Docker and Docker Compose installed
- Git installed
- sudo privileges for running Docker commands

### Install Docker (if not already installed)
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

### Install Docker Compose
```bash
sudo apt-get install docker-compose -y
```

## Deployment Steps

### 1. Clone Repository
```bash
cd /opt
sudo git clone https://github.com/hameedibrh/system-dashboard.git tenet-dashboard
cd tenet-dashboard
sudo chown -R $USER:$USER .
```

### 2. Create Deployment Script
Create `/opt/tenet-dashboard/scripts/pull-and-rebuild.sh`:
```bash
#!/bin/bash
cd /opt/tenet-dashboard
git pull origin main
docker-compose down
docker-compose up -d
echo "Tenet Dashboard deployed at http://$(hostname -I | awk '{print $1}'):8081"
```

Make it executable:
```bash
chmod +x /opt/tenet-dashboard/scripts/pull-and-rebuild.sh
```

### 3. Create GitHub Webhook Listener
Create `/opt/tenet-dashboard/scripts/webhook-server.py` to listen for GitHub webhooks and trigger deployments.

Run it as a service:
```bash
sudo tee /etc/systemd/system/tenet-webhook.service > /dev/null <<EOF
[Unit]
Description=Tenet Webhook Listener
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/tenet-dashboard
ExecStart=/usr/bin/python3 /opt/tenet-dashboard/scripts/webhook-server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable tenet-webhook.service
sudo systemctl start tenet-webhook.service
```

### 4. Configure GitHub Webhook
1. Go to your repository: https://github.com/hameedibrh/system-dashboard/settings/hooks
2. Click "Add webhook"
3. **Payload URL**: `http://your-server-ip:5001/webhook`
4. **Content type**: `application/json`
5. **Events**: Select "Just the push event"
6. Click "Add webhook"

### 5. First Deployment
```bash
cd /opt/tenet-dashboard
docker-compose up -d
```

Access Tenet Dashboard at: `http://your-server-ip:8081`

### 6. Auto-deployment Test
```bash
echo "# Test comment" >> README.md
git add README.md
git commit -m "Test deployment trigger"
git push origin main
```

Check the webhook delivery at GitHub and verify deployment on server.

## Monitoring

Check service status:
```bash
sudo systemctl status tenet-webhook.service
```

View logs:
```bash
sudo systemctl logs -u tenet-webhook.service -f
```

Check running containers:
```bash
docker-compose ps
```

Access logs:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Troubleshooting

### Port 8081 already in use
```bash
# Find and kill process using port 8081
sudo lsof -i :8081
sudo kill -9 <PID>
```

### Docker socket permission denied
Ensure user is in docker group:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Webhook not triggering
Check webhook deliveries in GitHub repository settings and verify firewall allows inbound on port 5001.
