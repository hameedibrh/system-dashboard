"""Docker container management and monitoring"""

import docker
from docker.errors import DockerException
import logging

logger = logging.getLogger(__name__)

def get_docker_client():
    """Get Docker client"""
    try:
        return docker.from_env()
    except Exception as e:
        logger.error(f"Failed to connect to Docker: {str(e)}")
        raise

def get_containers(all_containers=True):
    """Get list of Docker containers"""
    containers_list = []
    
    try:
        client = get_docker_client()
        containers = client.containers.list(all=all_containers)
        
        for container in containers:
            try:
                # Get container stats
                stats = None
                if container.status == 'running':
                    try:
                        stats_data = container.stats(stream=False)
                        stats = {
                            'cpu_percent': calculate_cpu_percent(stats_data),
                            'memory_usage': stats_data['memory_stats'].get('usage', 0),
                            'memory_limit': stats_data['memory_stats'].get('limit', 0),
                        }
                    except Exception as e:
                        logger.warning(f"Could not get stats for {container.name}: {e}")
                
                container_info = {
                    'id': container.id[:12],  # Short ID
                    'name': container.name,
                    'image': container.image.tags[0] if container.image.tags else container.image.id[:12],
                    'status': container.status,
                    'state': container.attrs['State']['Status'] if 'State' in container.attrs else 'unknown',
                    'created': container.attrs['Created'],
                    'started': container.attrs['State'].get('StartedAt', None) if 'State' in container.attrs else None,
                    'ports': parse_ports(container.attrs.get('NetworkSettings', {}).get('Ports', {})),
                    'stats': stats,
                }
                containers_list.append(container_info)
            except Exception as e:
                logger.error(f"Error processing container: {str(e)}")
                continue
    
    except DockerException as e:
        logger.error(f"Docker error: {str(e)}")
        raise
    
    return containers_list

def get_container_stats(container_id):
    """Get detailed stats for a specific container"""
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)
        
        if container.status != 'running':
            return {'error': 'Container is not running'}
        
        stats_data = container.stats(stream=False)
        
        return {
            'container_id': container.id[:12],
            'name': container.name,
            'cpu_percent': calculate_cpu_percent(stats_data),
            'memory_usage': stats_data['memory_stats'].get('usage', 0),
            'memory_limit': stats_data['memory_stats'].get('limit', 0),
            'memory_percent': (stats_data['memory_stats'].get('usage', 0) / stats_data['memory_stats'].get('limit', 1)) * 100,
            'network': stats_data.get('networks', {}),
        }
    except DockerException as e:
        logger.error(f"Docker error: {str(e)}")
        raise

def start_container(container_id):
    """Start a Docker container"""
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)
        
        if container.status == 'running':
            return {'success': True, 'message': f'Container {container.name} is already running'}
        
        container.start()
        logger.info(f"Started container: {container.name}")
        return {'success': True, 'message': f'Container {container.name} started successfully'}
    
    except DockerException as e:
        logger.error(f"Docker error: {str(e)}")
        return {'success': False, 'error': str(e)}

def stop_container(container_id):
    """Stop a Docker container"""
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)
        
        if container.status != 'running':
            return {'success': True, 'message': f'Container {container.name} is not running'}
        
        container.stop(timeout=10)
        logger.info(f"Stopped container: {container.name}")
        return {'success': True, 'message': f'Container {container.name} stopped successfully'}
    
    except DockerException as e:
        logger.error(f"Docker error: {str(e)}")
        return {'success': False, 'error': str(e)}

def get_container_logs(container_id, tail=100):
    """Get logs for a specific container"""
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)
        logs = container.logs(tail=tail, timestamps=True).decode('utf-8')
        return logs.split('\n')
    except DockerException as e:
        logger.error(f"Docker error: {str(e)}")
        raise

def calculate_cpu_percent(stats):
    """Calculate CPU usage percentage"""
    try:
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
        cpu_percent = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpus']) * 100.0
        return round(cpu_percent, 2)
    except (KeyError, ZeroDivisionError):
        return 0.0

def parse_ports(ports_dict):
    """Parse Docker ports dictionary"""
    ports = []
    for container_port, host_bindings in ports_dict.items():
        if host_bindings:
            for binding in host_bindings:
                ports.append({
                    'container_port': container_port,
                    'host_port': binding.get('HostPort'),
                    'host_ip': binding.get('HostIp', '0.0.0.0'),
                })
    return ports
