#!/usr/bin/env python3
"""
GitHub Webhook Listener for automatic deployments

Listens for push events and triggers the deployment script
"""

from flask import Flask, request, jsonify
import subprocess
import hashlib
import hmac
import json
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GitHub webhook secret (set this from environment variable)
GITHUB_SECRET = None

def verify_signature(payload_body, signature):
    """Verify GitHub webhook signature"""
    if not GitHub_SECRET:
        return True
    
    hash_object = hmac.new(
        GitHub_SECRET.encode(),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = 'sha256=' + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle GitHub webhook"""
    
    signature = request.headers.get('X-Hub-Signature-256', '')
    payload = request.get_data()
    
    if not verify_signature(payload, signature):
        logger.warning(f"Invalid signature: {signature}")
        return jsonify({'error': 'Invalid signature'}), 401
    
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    
    logger.info(f"Received {event_type} event from {data.get('repository', {}).get('full_name')}")
    
    if event_type == 'push':
        branch = data['ref'].split('/')[-1]
        if branch == 'main':
            logger.info("Push to main branch detected. Triggering deployment...")
            try:
                result = subprocess.run(
                    ['/bin/bash', '/opt/system-dashboard/scripts/pull-and-rebuild.sh'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    logger.info("Deployment successful")
                    return jsonify({'status': 'success', 'message': 'Deployment triggered'}), 200
                else:
                    logger.error(f"Deployment failed: {result.stderr}")
                    return jsonify({'status': 'error', 'message': result.stderr}), 500
            except Exception as e:
                logger.error(f"Error running deployment script: {str(e)}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
    
    return jsonify({'status': 'ignored'}), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()}), 200

if __name__ == '__main__':
    logger.info("Starting webhook listener on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=False)
