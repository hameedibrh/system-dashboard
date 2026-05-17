# Tenet - System Dashboard | Server Deployment Guide

## Overview
This guide walks you through deploying Tenet - System Dashboard to your Linux server with automatic GitHub webhook deployments.

## Prerequisites

On your Linux server, ensure you have:
- Docker and Docker Compose installed
- Git installed
- Sudo privileges
- A domain or static IP (for webhook configuration)
- 2GB+ RAM and 5GB+ disk space

## Installation Steps

### Step 1: Install Docker (if not already installed)

```bash
# Download and install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add current user to docker group (avoid needing sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker run hello-world
```

### Step 2: Install Docker Compose

```bash
sudo apt-get update
sudo apt-get install -y docker-compose

# Verify installation
docker-compose --version
```

### Step 3: Clone the Repository

```bash
# Create directory
sudo mkdir -p /opt/tenet-dashboard
cd /opt/tenet-dashboard

# Clone repository
sudo git clone https://github.com/hameedibrh/system-dashboard.git .

# Change ownership to current user
sudo chown -R $USER:$USER /opt/tenet-dashboard
```

### Step 4: Configure Environment

```bash
cd /opt/tenet-dashboard

# Backend configuration
cp backend/.env.example backend/.env
# Edit if needed:
# nano backend/.env

# Frontend configuration
cp frontend/.env.example frontend/.env
# Update REACT_APP_API_URL if using a domain:
# nano frontend/.env
# Set: REACT_APP_API_URL=http://your-server-domain.com:5000
```

### Step 5: Initial Deployment

```bash
cd /opt/tenet-dashboard

# Build and start containers
docker-compose up -d

# Verify all containers are running
docker-compose ps

# Check logs
docker-compose logs -f
```

**Tenet Dashboard is now available at:** `http://your-server-ip:8081`

### Step 6: Set Up Auto-Deployment with GitHub Webhook

#### 6a. Install Webhook Listener as a Service

```bash
# Install Flask for webhook listener
cd /opt/tenet-dashboard/scripts
sudo pip3 install -r requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/tenet-webhook.service > /dev/null <<EOF
[Unit]
Description=Tenet Webhook Listener
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/tenet-dashboard
Environment="GITHUB_SECRET=your-webhook-secret-here"
ExecStart=/usr/bin/python3 /opt/tenet-dashboard/scripts/webhook-server.py
Restart=on-failure
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable tenet-webhook.service
sudo systemctl start tenet-webhook.service

# Check status
sudo systemctl status tenet-webhook.service

# View logs
sudo journalctl -u tenet-webhook.service -f
```

#### 6b. Configure GitHub Webhook

1. Go to your repository settings:
   - https://github.com/hameedibrh/system-dashboard/settings/hooks

2. Click **Add webhook** (or New webhook)

3. Fill in the following:
   - **Payload URL**: `http://your-server-ip:5001/webhook`
     - Or use domain: `http://your-domain.com:5001/webhook`
   - **Content type**: `application/json`
   - **Secret**: Enter a secure random string (optional but recommended)
     - Must match `GITHUB_SECRET` in the systemd service above
   - **Events**: Select "Just the push event"
   - **Active**: Check this box

4. Click **Add webhook**

#### 6c. Test the Webhook

```bash
# Make a test commit and push
echo "# Test deployment" >> README.md
git add README.md
git commit -m "Test auto-deployment"
git push origin main

# Check webhook delivery in GitHub settings
# Recent Deliveries tab should show a successful delivery (green checkmark)

# Check deployment logs
sudo tail -f /var/log/tenet-dashboard-deploy.log

# Or through the webhook listener
curl http://localhost:5001/logs | python3 -m json.tool
```

### Step 7: Set Up Automatic Restart on Reboot

```bash
# Create systemd service for dashboard containers
sudo tee /etc/systemd/system/tenet-dashboard.service > /dev/null <<EOF
[Unit]
Description=Tenet - System Dashboard Docker Compose
After=docker.service
Requires=docker.service

[Service]
Type=forking
WorkingDirectory=/opt/tenet-dashboard
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
Restart=on-failure
RestartSec=10
User=$USER

[Install]
WantedBy=multi-user.target
EOF

# Enable and test
sudo systemctl daemon-reload
sudo systemctl enable tenet-dashboard.service
sudo systemctl start tenet-dashboard.service

# Verify
sudo systemctl status tenet-dashboard.service
```

## Usage

### Accessing Tenet Dashboard

- **Local network**: `http://your-server-ip:8081`
- **Custom domain**: Set up port forwarding and domain DNS

### Managing Containers

```bash
# View all containers
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Start services
docker-compose up -d
```

### Viewing Deployment Status

```bash
# Health check endpoint
curl http://localhost:5001/health

# Recent deployment logs
curl http://localhost:5001/logs | python3 -m json.tool

# Check systemd logs
sudo journalctl -u tenet-webhook.service -n 50
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8081
sudo lsof -i :8081

# Kill process
sudo kill -9 <PID>

# Or modify docker-compose.yml to use different port
```

### Docker Socket Permission Denied

```bash
# Ensure user is in docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
groups
```

### Containers Won't Start

```bash
# Check logs
docker-compose logs

# Verify Docker daemon is running
sudo systemctl status docker

# Check disk space
df -h

# Check memory
free -h
```

### Webhook Not Triggering

1. Check webhook delivery history in GitHub:
   - Go to repository Settings → Webhooks
   - Click the webhook to see recent deliveries
   - Green checkmark = successful, red X = failed

2. Verify webhook server is running:
   ```bash
   sudo systemctl status tenet-webhook.service
   curl http://localhost:5001/health
   ```

3. Check firewall allows port 5001:
   ```bash
   sudo ufw allow 5001/tcp
   # or for iptables:
   sudo iptables -A INPUT -p tcp --dport 5001 -j ACCEPT
   ```

4. Verify GitHub can reach your server:
   - Check public IP in webhook settings
   - Ensure port forwarding is configured (if behind NAT)

### Deployment Script Fails

```bash
# Check deployment logs
sudo tail -f /var/log/tenet-dashboard-deploy.log

# Make sure script has execute permissions
chmod +x /opt/tenet-dashboard/scripts/pull-and-rebuild.sh

# Test script manually
sudo /opt/tenet-dashboard/scripts/pull-and-rebuild.sh
```

## Monitoring

### Health Check Script

```bash
# Run health checks
bash /opt/tenet-dashboard/scripts/health-check.sh
```

### Logs

```bash
# Tenet deployment logs
sudo tail -f /var/log/tenet-dashboard-deploy.log

# Webhook listener logs
sudo journalctl -u tenet-webhook.service -f

# Docker logs
docker-compose logs -f
```

### Auto-restart with Monitoring

Add to crontab for periodic health check:

```bash
crontab -e

# Add this line:
*/5 * * * * /opt/tenet-dashboard/scripts/health-check.sh > /dev/null 2>&1
```

## Security Notes

1. **Change Flask Secret**: Update secret key in production backend/.env
2. **Use HTTPS**: Set up reverse proxy (nginx) with SSL/TLS
3. **Restrict Access**: Use firewall rules to limit access to port 8081
4. **Update Regularly**: Keep Docker images and dependencies updated
5. **GitHub Secret**: Use a strong webhook secret and never commit it

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs for error messages
3. Create an issue on GitHub: https://github.com/hameedibrh/system-dashboard/issues
