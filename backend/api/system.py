"""System metrics collection and management"""

import psutil
import platform
from datetime import datetime

def get_cpu_metrics():
    """Get CPU metrics"""
    return {
        'percent': psutil.cpu_percent(interval=1),
        'count': psutil.cpu_count(logical=False),
        'count_logical': psutil.cpu_count(logical=True),
        'freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
    }

def get_memory_metrics():
    """Get memory metrics"""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    return {
        'total': mem.total,
        'available': mem.available,
        'used': mem.used,
        'free': mem.free,
        'percent': mem.percent,
        'swap_total': swap.total,
        'swap_used': swap.used,
        'swap_free': swap.free,
        'swap_percent': swap.percent,
    }

def get_disk_metrics():
    """Get disk metrics for all partitions"""
    disks = {}
    
    try:
        partitions = psutil.disk_partitions(all=False)
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks[partition.device] = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent,
                }
            except (PermissionError, OSError):
                continue
    except Exception as e:
        print(f"Error getting disk metrics: {e}")
    
    return disks

def get_network_metrics():
    """Get network metrics"""
    net_io = psutil.net_io_counters()
    
    return {
        'bytes_sent': net_io.bytes_sent,
        'bytes_recv': net_io.bytes_recv,
        'packets_sent': net_io.packets_sent,
        'packets_recv': net_io.packets_recv,
        'errin': net_io.errin,
        'errout': net_io.errout,
        'dropin': net_io.dropin,
        'dropout': net_io.dropout,
    }

def get_process_metrics():
    """Get top processes by CPU and memory"""
    processes = []
    try:
        # Get top 10 processes by CPU
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'] or 0,
                    'memory_percent': proc.info['memory_percent'] or 0,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage and get top 10
        processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]
    except Exception as e:
        print(f"Error getting process metrics: {e}")
    
    return processes

def get_system_metrics():
    """Get all system metrics"""
    return {
        'cpu': get_cpu_metrics(),
        'memory': get_memory_metrics(),
        'disk': get_disk_metrics(),
        'network': get_network_metrics(),
        'processes': get_process_metrics(),
        'timestamp': datetime.now().isoformat(),
    }

def get_system_info():
    """Get system information (OS, hostname, uptime, etc.)"""
    boot_time = datetime.fromtimestamp(psutil.boot_time()).isoformat()
    
    return {
        'hostname': platform.node(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'architecture': platform.architecture()[0],
        'processor': platform.processor(),
        'boot_time': boot_time,
        'uptime_seconds': int(datetime.now().timestamp() - psutil.boot_time()),
    }
