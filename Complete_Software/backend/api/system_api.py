from flask import Blueprint, jsonify
import psutil
import time
from datetime import datetime, timedelta
from models.db import db
from utils.logger import system_logger
import os

system_bp = Blueprint('system', __name__)

def get_system_metrics():
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'network_io': psutil.net_io_counters()._asdict()
    }

@system_bp.route('/stats')
def get_system_stats():
    # Get current metrics
    metrics = get_system_metrics()
    
    # Get active users count
    active_users = db.users.count_documents({
        'last_active': {'$gte': datetime.utcnow() - timedelta(minutes=5)}
    })
    
    # Calculate error rate
    total_requests = db.system_metrics.count_documents({
        'timestamp': {'$gte': datetime.utcnow() - timedelta(hours=1)}
    })
    error_requests = db.system_metrics.count_documents({
        'timestamp': {'$gte': datetime.utcnow() - timedelta(hours=1)},
        'status_code': {'$gte': 500}
    })
    error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
    
    # Get historical CPU and memory data
    historical_data = list(db.system_metrics.find(
        {'timestamp': {'$gte': datetime.utcnow() - timedelta(hours=1)}},
        {'_id': 0, 'cpu_percent': 1, 'memory_percent': 1, 'timestamp': 1}
    ).sort('timestamp', -1).limit(60))
    
    # Format data for charts
    cpu_data = {
        'labels': [d['timestamp'].strftime('%H:%M:%S') for d in historical_data],
        'datasets': [{
            'label': 'CPU Usage (%)',
            'data': [d['cpu_percent'] for d in historical_data],
            'borderColor': '#2196F3',
            'fill': False
        }]
    }
    
    memory_data = {
        'labels': [d['timestamp'].strftime('%H:%M:%S') for d in historical_data],
        'datasets': [{
            'label': 'Memory Usage (%)',
            'data': [d['memory_percent'] for d in historical_data],
            'borderColor': '#4CAF50',
            'fill': False
        }]
    }
    
    # Get recent logs
    logs = list(db.system_logs.find(
        {},
        {'_id': 0}
    ).sort('timestamp', -1).limit(100))
    
    return jsonify({
        'status': 'online',
        'activeUsers': active_users,
        'avgResponseTime': round(sum(d.get('response_time', 0) for d in historical_data) / len(historical_data) if historical_data else 0, 2),
        'errorRate': round(error_rate, 2),
        'cpuData': cpu_data,
        'memoryData': memory_data,
        'currentMetrics': metrics,
        'logs': logs
    })

@system_bp.route('/health')
def health_check():
    metrics = get_system_metrics()
    status = 'healthy'
    
    # Define thresholds
    if metrics['cpu_percent'] > 90 or metrics['memory_percent'] > 90:
        status = 'degraded'
    
    system_logger.info(f"Health check - Status: {status}")
    
    return jsonify({
        'status': status,
        'timestamp': datetime.utcnow().isoformat(),
        'metrics': metrics
    })

def record_metrics():
    """Background task to record system metrics"""
    while True:
        try:
            metrics = get_system_metrics()
            metrics['timestamp'] = datetime.utcnow()
            
            db.system_metrics.insert_one(metrics)
            
            # Clean up old metrics
            db.system_metrics.delete_many({
                'timestamp': {'$lt': datetime.utcnow() - timedelta(days=7)}
            })
            
            time.sleep(60)  # Record metrics every minute
            
        except Exception as e:
            system_logger.error(f"Error recording metrics: {str(e)}")
            time.sleep(60) 