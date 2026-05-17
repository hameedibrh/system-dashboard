#!/bin/bash

# Quick health check for the dashboard
# Useful for monitoring and verification

echo "Checking Dashboard Services..."
echo ""

BACKEND_URL="http://localhost:5000/api/health"
FRONTEND_URL="http://localhost:8081"

echo "Backend API:"
curl -s $BACKEND_URL | python3 -m json.tool || echo "Backend not responding"

echo ""
echo "Frontend:"
if curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL | grep -q "200"; then
    echo "✓ Frontend is responding (HTTP 200)"
else
    echo "✗ Frontend is not responding"
fi

echo ""
echo "Docker Containers:"
docker-compose ps

echo ""
echo "Network Test:"
echo "Pinging frontend..."
docker-compose exec -T frontend ping -c 1 backend || echo "Cannot reach backend from frontend"
