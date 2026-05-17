#!/usr/bin/env python3
"""
Tenet - GitHub Webhook Listener for automatic deployments

Listens for GitHub webhook push events and triggers the deployment script
to automatically deploy changes to the Linux server.

Setup:
1. Add this as a systemd service
2. Configure GitHub webhook to POST to http://your-server:5001/webhook
3. Set GITHUB_SECRET environment variable for signature verification
"""

import os
import sys
import subprocess
import hashlib
import hmac
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/tenet-webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# GitHub webhook secret (set via environment variable)
GITHUB_SECRET = os.getenv('GITHUB_SECRET', None)
DEPLOYMENT_SCRIPT = '/opt/tenet-dashboard/scripts/pull-and-rebuild.sh'

def verify_signature(payload_body, signature):
    """
    Verify GitHub webhook signature
    
    GitHub sends a signature in the X-Hub-Signature-256 header
    Format: sha256=<hash>
    """
    if not GITHUB_SECRET:
        logger.warning("GITHUB_SECRET not set - skipping signature verification")
        return True
    
    try:
        hash_object = hmac.new(
            GITHUB_SECRET.encode(),
            msg=payload_body,
            digestmod=hashlib.sha256
        )
        expected_signature = 'sha256=' + hash_object.hexdigest()
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}")
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Handle GitHub webhook events
    
    Triggers deployment on push to main branch
    """
    logger.info(f"Received webhook from {request.remote_addr}")
    
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256', '')
    payload = request.get_data()
    
    if not verify_signature(payload, signature):
        logger.warning(f"Invalid signature: {signature}")
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Parse JSON
    try:
        data = request.json
    except Exception as e:
        logger.error(f"Failed to parse JSON: {str(e)}")
        return jsonify({'error': 'Invalid JSON'}), 400
    
    # Get event type and branch
    event_type = request.headers.get('X-GitHub-Event')
    repo_name = data.get('repository', {}).get('full_name', 'unknown')
    ref = data.get('ref', 'unknown')
    branch = ref.split('/')[-1] if ref else 'unknown'
    
    logger.info(f"Event: {event_type}, Repo: {repo_name}, Branch: {branch}")
    
    # Check if this is a push to main branch
    if event_type == 'push' and branch == 'main':
        logger.info("Push to main branch detected - triggering deployment")
        
        try:
            # Check if deployment script exists
            if not os.path.exists(DEPLOYMENT_SCRIPT):
                logger.error(f"Deployment script not found: {DEPLOYMENT_SCRIPT}")
                return jsonify({
                    'status': 'error',
                    'message': 'Deployment script not found'
                }), 500
            
            # Make script executable
            os.chmod(DEPLOYMENT_SCRIPT, 0o755)
            
            # Run deployment script
            logger.info("Executing deployment script...")
            result = subprocess.run(
                ['/bin/bash', DEPLOYMENT_SCRIPT],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("Deployment successful")
                return jsonify({
                    'status': 'success',
                    'message': 'Deployment triggered successfully'
                }), 200
            else:
                logger.error(f"Deployment failed: {result.stderr}")
                return jsonify({
                    'status': 'error',
                    'message': f'Deployment failed: {result.stderr}'
                }), 500
        
        except subprocess.TimeoutExpired:
            logger.error("Deployment script timed out")
            return jsonify({
                'status': 'error',
                'message': 'Deployment timed out'
            }), 500
        except Exception as e:
            logger.error(f"Error running deployment script: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Error: {str(e)}'
            }), 500
    else:
        logger.info(f"Ignoring event: {event_type} on branch {branch}")
        return jsonify({'status': 'ignored', 'reason': 'Not a push to main branch'}), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'Tenet - Webhook Listener'
    }), 200

@app.route('/logs', methods=['GET'])
def get_logs():
    """Get recent deployment logs (last 50 lines)"""
    log_file = '/var/log/tenet-dashboard-deploy.log'
    
    if not os.path.exists(log_file):
        return jsonify({'logs': [], 'message': 'No logs found'}), 200
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            recent_logs = lines[-50:] if len(lines) > 50 else lines
            return jsonify({
                'logs': [line.rstrip() for line in recent_logs],
                'total_lines': len(lines)
            }), 200
    except Exception as e:
        logger.error(f"Error reading logs: {str(e)}")
        return jsonify({'error': 'Could not read logs'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Tenet - GitHub Webhook Listener...")
    logger.info(f"Listening on 0.0.0.0:5001")
    logger.info(f"Deployment script: {DEPLOYMENT_SCRIPT}")
    logger.info(f"GitHub secret verification: {'Enabled' if GITHUB_SECRET else 'Disabled'}")
    
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
