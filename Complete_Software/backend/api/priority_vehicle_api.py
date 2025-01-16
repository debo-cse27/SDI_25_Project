from flask import Blueprint, jsonify, request
from models.db import db
import time
from datetime import datetime
import numpy as np

priority_bp = Blueprint('priority', __name__)

VEHICLE_TYPES = {
    'ambulance': 1,
    'fire': 1,
    'police': 2,
    'vip': 3
}

@priority_bp.route('/register', methods=['POST'])
def register_vehicle():
    data = request.json
    required_fields = ['vehicle_type', 'vehicle_id', 'rfid_tag']
    
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
    data['registration_date'] = datetime.now()
    data['priority_level'] = VEHICLE_TYPES.get(data['vehicle_type'], 3)
    
    db.priority_vehicles.insert_one(data)
    return jsonify({'status': 'success', 'message': 'Vehicle registered successfully'})

@priority_bp.route('/approach', methods=['POST'])
def vehicle_approaching():
    data = request.json
    rfid_tag = data.get('rfid_tag')
    junction_id = data.get('junction_id')
    
    vehicle = db.priority_vehicles.find_one({'rfid_tag': rfid_tag})
    if not vehicle:
        return jsonify({'status': 'error', 'message': 'Vehicle not registered'}), 404
    
    approach_data = {
        'rfid_tag': rfid_tag,
        'junction_id': junction_id,
        'timestamp': time.time(),
        'status': 'approaching',
        'priority_level': vehicle['priority_level']
    }
    
    db.priority_vehicles.update_one(
        {'rfid_tag': rfid_tag},
        {'$set': {'last_seen': time.time(), 'current_junction': junction_id}}
    )
    
    return jsonify({'status': 'success', 'priority_level': vehicle['priority_level']})

@priority_bp.route('/route', methods=['POST'])
def optimize_route():
    data = request.json
    start_point = data.get('start')
    end_point = data.get('end')
    vehicle_type = data.get('vehicle_type')
    
    # Get traffic density data
    traffic_data = list(db.traffic_data.find({
        'timestamp': {'$gt': time.time() - 300}  # Last 5 minutes
    }))
    
    # Simple route optimization using traffic density
    route = calculate_optimal_route(start_point, end_point, traffic_data)
    
    return jsonify({
        'route': route,
        'estimated_time': calculate_eta(route, traffic_data),
        'traffic_conditions': get_traffic_conditions(route)
    })

def calculate_optimal_route(start, end, traffic_data):
    # Simplified route calculation
    # In real implementation, use A* or Dijkstra's algorithm
    return {
        'path': [start, 'junction1', 'junction2', end],
        'distance': 5.2,
        'junctions': ['junction1', 'junction2']
    }

def calculate_eta(route, traffic_data):
    # Calculate estimated time of arrival
    base_time = route['distance'] * 2  # 2 minutes per km
    traffic_factor = 1 + (sum(d['density'] for d in traffic_data) / len(traffic_data)) / 100
    return base_time * traffic_factor

def get_traffic_conditions(route):
    # Get current traffic conditions along the route
    conditions = {}
    for junction in route['junctions']:
        density = db.traffic_data.find_one(
            {'junction_id': junction},
            sort=[('timestamp', -1)]
        )
        conditions[junction] = {
            'density': density['density'] if density else 0,
            'status': 'heavy' if density and density['density'] > 70 else 'normal'
        }
    return conditions

@priority_bp.route('/complete', methods=['POST'])
def complete_priority_passage():
    data = request.json
    rfid_tag = data.get('rfid_tag')
    junction_id = data.get('junction_id')
    
    db.priority_vehicles.update_one(
        {'rfid_tag': rfid_tag},
        {'$set': {'status': 'completed', 'completion_time': time.time()}}
    )
    
    return jsonify({'status': 'success'}) 