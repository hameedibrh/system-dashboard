#!/usr/bin/env python3
"""
Tenet - System Dashboard Backend API

Provides real-time system and Docker metrics via REST API and WebSocket
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging
from datetime import datetime
import threading
import time

from api.system import get_system_metrics, get_system_info
from api.docker_mgmt import (
    get_containers,
    get_container_stats,
    start_container,
    stop_container,
    get_container_logs
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tenet-dashboard-secret-key-change-in-production'
CORS(app)

# Initialize Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for WebSocket management
metrics_thread = None
metrics_thread_stop = threading.Event()

# ==================== REST API Endpoints ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'Tenet - System Dashboard API'
    }), 200

@app.route('/api/system', methods=['GET'])
def system_metrics():
    """Get current system metrics"""
    try:
        metrics = get_system_metrics()
        info = get_system_info()
        return jsonify({
            'status': 'success',
            'metrics': metrics,
            'info': info,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching system metrics: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/docker/containers', methods=['GET'])
def list_containers():
    """Get list of all Docker containers"""
    try:
        containers = get_containers()
        return jsonify({
            'status': 'success',
            'containers': containers,
            'count': len(containers),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching containers: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/docker/containers/<container_id>/stats', methods=['GET'])
def container_stats(container_id):
    """Get stats for a specific container"""
    try:
        stats = get_container_stats(container_id)
        return jsonify({
            'status': 'success',
            'container_id': container_id,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching container stats: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/docker/containers/<container_id>/start', methods=['POST'])
def start_container_endpoint(container_id):
    """Start a Docker container"""
    try:
        result = start_container(container_id)
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error starting container: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/docker/containers/<container_id>/stop', methods=['POST'])
def stop_container_endpoint(container_id):
    """Stop a Docker container"""
    try:
        result = stop_container(container_id)
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error stopping container: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/docker/containers/<container_id>/logs', methods=['GET'])
def container_logs_endpoint(container_id):
    """Get logs for a specific container"""
    try:
        tail = request.args.get('tail', default=100, type=int)
        logs = get_container_logs(container_id, tail=tail)
        return jsonify({
            'status': 'success',
            'container_id': container_id,
            'logs': logs,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching container logs: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==================== WebSocket Events ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connection_response', {
        'data': 'Connected to Tenet - System Dashboard',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('start_metrics_stream')
def start_metrics_stream():
    """Start streaming metrics to client"""
    logger.info(f"Metrics stream started for {request.sid}")
    emit('stream_started', {'message': 'Metrics streaming started'})
    
    # Stream metrics every 2 seconds
    try:
        while True:
            metrics = get_system_metrics()
            containers = get_containers()
            
            socketio.emit('metrics_update', {
                'metrics': metrics,
                'containers': containers,
                'timestamp': datetime.now().isoformat()
            }, to=request.sid)
            
            time.sleep(2)
    except Exception as e:
        logger.error(f"Error in metrics stream: {str(e)}")
        emit('stream_error', {'error': str(e)})

@socketio.on('stop_metrics_stream')
def stop_metrics_stream():
    """Stop streaming metrics to client"""
    logger.info(f"Metrics stream stopped for {request.sid}")
    emit('stream_stopped', {'message': 'Metrics streaming stopped'})

@socketio.on('request_metrics')
def request_metrics():
    """Send current metrics on demand"""
    try:
        metrics = get_system_metrics()
        containers = get_containers()
        emit('metrics_data', {
            'metrics': metrics,
            'containers': containers,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error sending metrics: {str(e)}")
        emit('error', {'message': str(e)})

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

# ==================== Main ====================

if __name__ == '__main__':
    logger.info("Starting Tenet - System Dashboard Backend API...")
    logger.info("Available endpoints:")
    logger.info("  GET  /api/health")
    logger.info("  GET  /api/system")
    logger.info("  GET  /api/docker/containers")
    logger.info("  GET  /api/docker/containers/<id>/stats")
    logger.info("  POST /api/docker/containers/<id>/start")
    logger.info("  POST /api/docker/containers/<id>/stop")
    logger.info("  GET  /api/docker/containers/<id>/logs")
    logger.info("\nWebSocket events:")
    logger.info("  start_metrics_stream")
    logger.info("  stop_metrics_stream")
    logger.info("  request_metrics")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
