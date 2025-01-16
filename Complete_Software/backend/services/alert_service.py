from flask_socketio import emit
from datetime import datetime
import threading
import queue
from utils.logger import system_logger

class AlertService:
    def __init__(self):
        self.alert_queue = queue.Queue()
        self.alert_thresholds = {
            'cpu_usage': 90,
            'memory_usage': 90,
            'error_rate': 5,
            'response_time': 1000  # milliseconds
        }
        self._start_alert_processing()

    def _start_alert_processing(self):
        def process_alerts():
            while True:
                try:
                    alert = self.alert_queue.get()
                    self._handle_alert(alert)
                except Exception as e:
                    system_logger.error(f"Error processing alert: {e}")

        thread = threading.Thread(target=process_alerts, daemon=True)
        thread.start()

    def check_system_metrics(self, metrics):
        if metrics['cpu_percent'] > self.alert_thresholds['cpu_usage']:
            self.create_alert('HIGH_CPU', f"CPU usage at {metrics['cpu_percent']}%", 'warning')

        if metrics['memory_percent'] > self.alert_thresholds['memory_usage']:
            self.create_alert('HIGH_MEMORY', f"Memory usage at {metrics['memory_percent']}%", 'warning')

    def create_alert(self, alert_type, message, severity):
        alert = {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'new'
        }
        self.alert_queue.put(alert)

    def _handle_alert(self, alert):
        # Log the alert
        system_logger.warning(f"Alert: {alert['type']} - {alert['message']}")

        # Broadcast to connected clients
        emit('new_alert', alert, namespace='/alerts', broadcast=True)

        # Store in database
        from models.db import db
        db.alerts.insert_one(alert)

        # Handle critical alerts
        if alert['severity'] == 'critical':
            self._handle_critical_alert(alert)

    def _handle_critical_alert(self, alert):
        # Add notification logic here (email, SMS, etc.)
        pass

alert_service = AlertService() 