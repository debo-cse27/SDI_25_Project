import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    handler = RotatingFileHandler(
        f'logs/{log_file}',
        maxBytes=10000000,  # 10MB
        backupCount=5
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Create different loggers for different components
traffic_logger = setup_logger('traffic', 'traffic.log')
parking_logger = setup_logger('parking', 'parking.log')
priority_logger = setup_logger('priority', 'priority.log')
metro_logger = setup_logger('metro', 'metro.log')
security_logger = setup_logger('security', 'security.log')
system_logger = setup_logger('system', 'system.log')

def log_traffic_event(event_type, data):
    traffic_logger.info(f"Traffic Event - Type: {event_type} - Data: {data}")

def log_parking_event(event_type, data):
    parking_logger.info(f"Parking Event - Type: {event_type} - Data: {data}")

def log_priority_vehicle(vehicle_type, action, data):
    priority_logger.info(f"Priority Vehicle - Type: {vehicle_type} - Action: {action} - Data: {data}")

def log_metro_update(station, event_type, data):
    metro_logger.info(f"Metro Update - Station: {station} - Type: {event_type} - Data: {data}")

def log_security_event(event_type, severity, details):
    security_logger.info(f"Security Event - Type: {event_type} - Severity: {severity} - Details: {details}")

def log_system_event(component, event_type, status, details=None):
    system_logger.info(
        f"System Event - Component: {component} - Type: {event_type} - "
        f"Status: {status} - Details: {details if details else 'None'}"
    ) 