from datetime import datetime, timedelta
import numpy as np
from models.db import db
from utils.logger import system_logger
from services.alert_service import alert_service

class PerformanceAnalyzer:
    def __init__(self):
        self.baseline_metrics = None
        self.anomaly_thresholds = {
            'cpu': {
                'warning': 70,
                'critical': 85
            },
            'memory': {
                'warning': 75,
                'critical': 90
            },
            'disk_io': {
                'warning': 50_000_000,  # 50MB/s
                'critical': 100_000_000  # 100MB/s
            },
            'response_time': {
                'warning': 500,  # ms
                'critical': 1000  # ms
            }
        }

    def analyze_metrics(self, current_metrics):
        """Analyze current metrics and detect anomalies"""
        analysis_results = {
            'anomalies': [],
            'recommendations': [],
            'performance_score': 100
        }

        # CPU Analysis
        cpu_score = self._analyze_cpu(current_metrics['cpu'])
        analysis_results['performance_score'] *= (cpu_score / 100)

        # Memory Analysis
        memory_score = self._analyze_memory(current_metrics['memory'])
        analysis_results['performance_score'] *= (memory_score / 100)

        # Disk I/O Analysis
        disk_score = self._analyze_disk_io(current_metrics['disk'])
        analysis_results['performance_score'] *= (disk_score / 100)

        # Network Analysis
        network_score = self._analyze_network(current_metrics['network'])
        analysis_results['performance_score'] *= (network_score / 100)

        # Calculate final score
        analysis_results['performance_score'] = round(analysis_results['performance_score'], 2)

        return analysis_results

    def _analyze_cpu(self, cpu_metrics):
        score = 100
        usage = cpu_metrics['usage_percent']

        if usage > self.anomaly_thresholds['cpu']['critical']:
            score = 50
            alert_service.create_alert(
                'CRITICAL_CPU_USAGE',
                f"Critical CPU usage detected: {usage}%",
                'critical'
            )
        elif usage > self.anomaly_thresholds['cpu']['warning']:
            score = 75
            alert_service.create_alert(
                'HIGH_CPU_USAGE',
                f"High CPU usage detected: {usage}%",
                'warning'
            )

        return score

    def _analyze_memory(self, memory_metrics):
        score = 100
        usage = memory_metrics['percent']

        if usage > self.anomaly_thresholds['memory']['critical']:
            score = 50
            alert_service.create_alert(
                'CRITICAL_MEMORY_USAGE',
                f"Critical memory usage detected: {usage}%",
                'critical'
            )
        elif usage > self.anomaly_thresholds['memory']['warning']:
            score = 75
            alert_service.create_alert(
                'HIGH_MEMORY_USAGE',
                f"High memory usage detected: {usage}%",
                'warning'
            )

        return score

    def _analyze_disk_io(self, disk_metrics):
        score = 100
        read_rate = disk_metrics['read_bytes']
        write_rate = disk_metrics['write_bytes']

        total_io = read_rate + write_rate
        if total_io > self.anomaly_thresholds['disk_io']['critical']:
            score = 50
            alert_service.create_alert(
                'CRITICAL_DISK_IO',
                f"Critical disk I/O detected: {total_io/1_000_000:.1f} MB/s",
                'critical'
            )
        elif total_io > self.anomaly_thresholds['disk_io']['warning']:
            score = 75
            alert_service.create_alert(
                'HIGH_DISK_IO',
                f"High disk I/O detected: {total_io/1_000_000:.1f} MB/s",
                'warning'
            )

        return score

    def _analyze_network(self, network_metrics):
        score = 100
        bytes_total = network_metrics['bytes_sent'] + network_metrics['bytes_recv']
        packets_total = network_metrics['packets_sent'] + network_metrics['packets_recv']

        # Calculate packet loss rate (if available)
        if hasattr(network_metrics, 'packets_dropped'):
            packet_loss_rate = network_metrics['packets_dropped'] / packets_total
            if packet_loss_rate > 0.01:  # More than 1% packet loss
                score -= 25
                alert_service.create_alert(
                    'HIGH_PACKET_LOSS',
                    f"High packet loss rate detected: {packet_loss_rate*100:.1f}%",
                    'warning'
                )

        return score

    def get_performance_recommendations(self, analysis_results):
        """Generate performance improvement recommendations"""
        recommendations = []

        if analysis_results['performance_score'] < 60:
            recommendations.append({
                'priority': 'high',
                'category': 'general',
                'message': 'System performance is critically low. Consider immediate investigation.'
            })

        # Add specific recommendations based on metrics
        for anomaly in analysis_results['anomalies']:
            if anomaly['type'] == 'HIGH_CPU_USAGE':
                recommendations.append({
                    'priority': 'medium',
                    'category': 'cpu',
                    'message': 'Consider optimizing CPU-intensive processes or scaling up CPU resources.'
                })
            elif anomaly['type'] == 'HIGH_MEMORY_USAGE':
                recommendations.append({
                    'priority': 'medium',
                    'category': 'memory',
                    'message': 'Consider increasing available memory or optimizing memory usage.'
                })

        return recommendations

performance_analyzer = PerformanceAnalyzer() 