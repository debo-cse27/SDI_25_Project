from flask import Blueprint, jsonify, request
from models.db import db
from traffic_light_controller import TrafficJunction, get_traffic_density, get_signal_timing
import threading
import time

traffic_bp = Blueprint('traffic', __name__)

# Global variables to store traffic system state
current_state = {
    'active_lane': 0,
    'timer': 0,
    'light_status': 'RED',
    'density': 0,
    'is_running': False
}

# Initialize traffic junction
lanes = [
    {
        'current': 'static/images/lane1_current.jpg',
        'reference': 'static/images/lane1_empty.jpg'
    },
    {
        'current': 'static/images/lane2_current.jpg',
        'reference': 'static/images/lane2_empty.jpg'
    },
    {
        'current': 'static/images/lane3_current.jpg',
        'reference': 'static/images/lane3_empty.jpg'
    },
    {
        'current': 'static/images/lane4_current.jpg',
        'reference': 'static/images/lane4_empty.jpg'
    }
]

junction = TrafficJunction(lanes)

def run_traffic_system():
    while current_state['is_running']:
        for i in range(len(lanes)):
            if check_priority_vehicle():
                handle_priority_vehicle()
                continue
                
            current_state['active_lane'] = i + 1
            timing, density = junction.process_lane(i)
            current_state['density'] = round(density, 2)
            
            # Store traffic data
            db.traffic_data.insert_one({
                'timestamp': time.time(),
                'lane': i + 1,
                'density': density,
                'timing': timing
            })
            
            # Green light phase
            current_state['light_status'] = 'GREEN'
            for remaining in range(timing, 0, -1):
                current_state['timer'] = remaining
                time.sleep(1)
                if not current_state['is_running']:
                    return
            
            # Yellow light phase
            current_state['light_status'] = 'YELLOW'
            for remaining in range(3, 0, -1):
                current_state['timer'] = remaining
                time.sleep(1)
                if not current_state['is_running']:
                    return
            
            current_state['light_status'] = 'RED'

def check_priority_vehicle():
    # Check if any priority vehicle is approaching
    priority_vehicles = db.priority_vehicles.find({
        'status': 'approaching',
        'timestamp': {'$gt': time.time() - 300}  # Within last 5 minutes
    })
    return bool(list(priority_vehicles))

def handle_priority_vehicle():
    # Handle priority vehicle passage
    current_state['light_status'] = 'RED'
    time.sleep(2)
    current_state['light_status'] = 'GREEN'
    time.sleep(10)  # Give priority vehicle time to pass
    current_state['light_status'] = 'YELLOW'
    time.sleep(3)
    current_state['light_status'] = 'RED'

@traffic_bp.route('/start', methods=['POST'])
def start_system():
    if not current_state['is_running']:
        current_state['is_running'] = True
        thread = threading.Thread(target=run_traffic_system)
        thread.start()
    return jsonify({'status': 'success'})

@traffic_bp.route('/stop', methods=['POST'])
def stop_system():
    current_state['is_running'] = False
    return jsonify({'status': 'success'})

@traffic_bp.route('/status', methods=['GET'])
def get_status():
    return jsonify(current_state)

@traffic_bp.route('/analytics', methods=['GET'])
def get_analytics():
    # Get traffic analytics for the last 24 hours
    start_time = time.time() - (24 * 60 * 60)
    analytics = db.traffic_data.aggregate([
        {
            '$match': {
                'timestamp': {'$gt': start_time}
            }
        },
        {
            '$group': {
                '_id': '$lane',
                'avg_density': {'$avg': '$density'},
                'avg_timing': {'$avg': '$timing'},
                'total_vehicles': {'$sum': 1}
            }
        }
    ])
    return jsonify(list(analytics)) 