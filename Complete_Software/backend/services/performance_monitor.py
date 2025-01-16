import psutil
import time
from datetime import datetime, timedelta
from threading import Thread
from models.db import db
from utils.logger import system_logger
from services.alert_service import alert_service

class PerformanceMonitor:
    def __init__(self):
        self.sampling_interval = 5  # seconds
        self.metrics_history = {}
        self.running = False
        
    def start_monitoring(self):
        self.running = True
        Thread(target=self._monitor_loop, daemon=True).start()
        
    def stop_monitoring(self):
        self.running = False
        
    def _monitor_loop(self):
        while self.running:
            try:
                metrics = self._collect_metrics()
                self._store_metrics(metrics)
                self._analyze_performance(metrics)
                time.sleep(self.sampling_interval)
            except Exception as e:
                system_logger.error(f"Error in performance monitoring: {e}")
                
    def _collect_metrics(self):
        cpu_times = psutil.cpu_times_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_io_counters()
        network = psutil.net_io_counters()
        
        return {
            'timestamp': datetime.utcnow(),
            'cpu': {
                'usage_percent': psutil.cpu_percent(interval=1),
                'user': cpu_times.user,
                'system': cpu_times.system,
                'idle': cpu_times.idle
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            },
            'disk': {
                'read_bytes': disk.read_bytes,
                'write_bytes': disk.write_bytes,
                'read_count': disk.read_count,
                'write_count': disk.write_count
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
        }
        
    def _store_metrics(self, metrics):
        # Store in database
        db.performance_metrics.insert_one(metrics)
        
        # Clean up old metrics
        db.performance_metrics.delete_many({
            'timestamp': {'$lt': datetime.utcnow() - timedelta(days=7)}
        })
        
    def _analyze_performance(self, metrics):
        # CPU analysis
        if metrics['cpu']['usage_percent'] > 80:
            alert_service.create_alert(
                'HIGH_CPU_USAGE',
                f"CPU usage is at {metrics['cpu']['usage_percent']}%",
                'warning'
            )
            
        # Memory analysis
        if metrics['memory']['percent'] > 85:
            alert_service.create_alert(
                'HIGH_MEMORY_USAGE',
                f"Memory usage is at {metrics['memory']['percent']}%",
                'warning'
            )
            
        # Disk I/O analysis
        current_time = time.time()
        if current_time - self.last_io_check >= 300:  # Check every 5 minutes
            self.last_io_check = current_time
            self._analyze_disk_io(metrics['disk'])
            
    def _analyze_disk_io(self, disk_metrics):
        # Calculate I/O rates
        read_rate = disk_metrics['read_bytes'] - self.last_disk_metrics.get('read_bytes', 0)
        write_rate = disk_metrics['write_bytes'] - self.last_disk_metrics.get('write_bytes', 0)
        
        # Update last metrics
        self.last_disk_metrics = disk_metrics
        
        # Check for high I/O rates
        if read_rate > 100_000_000 or write_rate > 100_000_000:  # 100MB/s threshold
            alert_service.create_alert(
                'HIGH_DISK_IO',
                f"High disk I/O detected: Read {read_rate/1_000_000:.1f}MB/s, Write {write_rate/1_000_000:.1f}MB/s",
                'warning'
            )
            
    def get_performance_report(self):
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        metrics = list(db.performance_metrics.find({
            'timestamp': {'$gte': start_time, '$lte': end_time}
        }).sort('timestamp', 1))
        
        return {
            'cpu_usage': [m['cpu']['usage_percent'] for m in metrics],
            'memory_usage': [m['memory']['percent'] for m in metrics],
            'timestamps': [m['timestamp'] for m in metrics],
            'disk_io': {
                'read_rate': self._calculate_rates([m['disk']['read_bytes'] for m in metrics]),
                'write_rate': self._calculate_rates([m['disk']['write_bytes'] for m in metrics])
            },
            'network_io': {
                'received': self._calculate_rates([m['network']['bytes_recv'] for m in metrics]),
                'sent': self._calculate_rates([m['network']['bytes_sent'] for m in metrics])
            }
        }
        
    def _calculate_rates(self, values):
        rates = []
        for i in range(1, len(values)):
            rate = (values[i] - values[i-1]) / self.sampling_interval
            rates.append(rate)
        return rates

performance_monitor = PerformanceMonitor() 