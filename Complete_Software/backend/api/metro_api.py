from flask import Blueprint, jsonify, request
import requests
from datetime import datetime, timedelta
from models.db import db

metro_bp = Blueprint('metro', __name__)

# Mock DMRC API endpoint (replace with actual DMRC API when available)
DMRC_API_BASE = "https://api.dmrc.in/v1"
API_KEY = "your_dmrc_api_key"

@metro_bp.route('/stations', methods=['GET'])
def get_stations():
    try:
        # In real implementation, fetch from DMRC API
        stations = [
            {
                'id': 'KB01',
                'name': 'Kashmere Gate',
                'lines': ['Red', 'Yellow', 'Violet'],
                'coordinates': {'lat': 28.6684, 'lng': 77.2288},
                'parking_available': True
            },
            # Add more stations...
        ]
        return jsonify(stations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@metro_bp.route('/schedule/<station_id>', methods=['GET'])
def get_schedule(station_id):
    try:
        # In real implementation, fetch from DMRC API
        current_time = datetime.now()
        schedule = []
        
        # Mock schedule data
        for i in range(5):  # Next 5 trains
            departure_time = current_time + timedelta(minutes=5*i)
            schedule.append({
                'train_id': f'T{100+i}',
                'destination': 'Huda City Centre',
                'departure_time': departure_time.strftime('%H:%M'),
                'platform': 1,
                'status': 'On Time'
            })
            
        return jsonify({
            'station_id': station_id,
            'current_time': current_time.strftime('%H:%M'),
            'schedule': schedule
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@metro_bp.route('/route', methods=['POST'])
def get_route():
    data = request.json
    source = data.get('source')
    destination = data.get('destination')
    
    try:
        # Calculate route with interchanges
        route = calculate_metro_route(source, destination)
        return jsonify(route)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@metro_bp.route('/fare', methods=['POST'])
def calculate_fare():
    data = request.json
    source = data.get('source')
    destination = data.get('destination')
    
    try:
        fare = calculate_metro_fare(source, destination)
        return jsonify({'fare': fare})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_metro_route(source, destination):
    # Mock route calculation
    return {
        'source': source,
        'destination': destination,
        'duration': 45,  # minutes
        'interchanges': [
            {
                'station': 'Rajiv Chowk',
                'from_line': 'Blue',
                'to_line': 'Yellow'
            }
        ],
        'steps': [
            {
                'type': 'board',
                'line': 'Blue',
                'station': source,
                'time': '10:00'
            },
            {
                'type': 'interchange',
                'station': 'Rajiv Chowk',
                'time': '10:30'
            },
            {
                'type': 'board',
                'line': 'Yellow',
                'station': 'Rajiv Chowk',
                'time': '10:35'
            },
            {
                'type': 'exit',
                'station': destination,
                'time': '10:45'
            }
        ]
    }

def calculate_metro_fare(source, destination):
    # Mock fare calculation
    base_fare = 10
    per_station = 2
    stations = 10  # Calculate actual number of stations
    return base_fare + (stations * per_station)

@metro_bp.route('/crowding/<station_id>', methods=['GET'])
def get_station_crowding(station_id):
    try:
        # In real implementation, get real-time crowding data
        crowding_level = calculate_crowding_level(station_id)
        return jsonify({
            'station_id': station_id,
            'crowding_level': crowding_level,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_crowding_level(station_id):
    # Mock crowding calculation
    # 0: Low, 1: Moderate, 2: High, 3: Very High
    return {
        'level': 1,
        'description': 'Moderate',
        'waiting_time': '5-10 minutes'
    } 