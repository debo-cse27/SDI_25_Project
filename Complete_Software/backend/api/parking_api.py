from flask import Blueprint, jsonify, request
from models.db import db
import cv2
import numpy as np
import time
from datetime import datetime, timedelta
import pytesseract  # For number plate recognition

parking_bp = Blueprint('parking', __name__)

class ParkingSpot:
    def __init__(self, spot_id, station_id):
        self.spot_id = spot_id
        self.station_id = station_id
        self.occupied = False
        self.vehicle_number = None
        self.entry_time = None

@parking_bp.route('/spots', methods=['GET'])
def get_parking_spots():
    spots = list(db.parking_spots.find({}, {'_id': 0}))
    return jsonify(spots)

@parking_bp.route('/spots/<station_id>', methods=['GET'])
def get_station_spots(station_id):
    spots = db.parking_spots.find({'station_id': station_id}, {'_id': 0})
    total_spots = db.parking_spots.count_documents({'station_id': station_id})
    occupied_spots = db.parking_spots.count_documents({
        'station_id': station_id,
        'occupied': True
    })
    
    return jsonify({
        'station_id': station_id,
        'total_spots': total_spots,
        'available_spots': total_spots - occupied_spots,
        'spots': list(spots)
    })

@parking_bp.route('/vehicle/entry', methods=['POST'])
def vehicle_entry():
    data = request.files['image']
    station_id = request.form.get('station_id')
    
    # Save the image temporarily
    temp_path = f"temp_{time.time()}.jpg"
    data.save(temp_path)
    
    # Process number plate recognition
    try:
        number_plate = recognize_number_plate(temp_path)
        spot = find_available_spot(station_id)
        
        if not spot:
            return jsonify({
                'status': 'error',
                'message': 'No parking spots available'
            }), 400
            
        # Update spot status
        db.parking_spots.update_one(
            {'spot_id': spot['spot_id']},
            {
                '$set': {
                    'occupied': True,
                    'vehicle_number': number_plate,
                    'entry_time': datetime.now()
                }
            }
        )
        
        # Record entry in parking history
        db.parking_history.insert_one({
            'vehicle_number': number_plate,
            'station_id': station_id,
            'spot_id': spot['spot_id'],
            'entry_time': datetime.now(),
            'status': 'active'
        })
        
        return jsonify({
            'status': 'success',
            'spot_id': spot['spot_id'],
            'vehicle_number': number_plate
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@parking_bp.route('/vehicle/exit', methods=['POST'])
def vehicle_exit():
    data = request.json
    spot_id = data.get('spot_id')
    vehicle_number = data.get('vehicle_number')
    
    # Update spot status
    db.parking_spots.update_one(
        {'spot_id': spot_id},
        {
            '$set': {
                'occupied': False,
                'vehicle_number': None,
                'entry_time': None
            }
        }
    )
    
    # Update parking history
    exit_time = datetime.now()
    entry_record = db.parking_history.find_one({
        'vehicle_number': vehicle_number,
        'status': 'active'
    })
    
    if entry_record:
        duration = (exit_time - entry_record['entry_time']).total_seconds() / 3600  # hours
        fee = calculate_parking_fee(duration)
        
        db.parking_history.update_one(
            {'_id': entry_record['_id']},
            {
                '$set': {
                    'exit_time': exit_time,
                    'duration': duration,
                    'fee': fee,
                    'status': 'completed'
                }
            }
        )
        
        return jsonify({
            'status': 'success',
            'duration': duration,
            'fee': fee
        })
    
    return jsonify({'status': 'error', 'message': 'Entry record not found'}), 404

def recognize_number_plate(image_path):
    # Load image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply preprocessing
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    # Use pytesseract for OCR
    number_plate = pytesseract.image_to_string(thresh, config='--psm 11')
    
    # Clean and validate the number plate
    number_plate = ''.join(e for e in number_plate if e.isalnum())
    
    if len(number_plate) < 8:  # Minimum length for valid number plate
        raise ValueError("Invalid number plate detected")
        
    return number_plate

def find_available_spot(station_id):
    return db.parking_spots.find_one({
        'station_id': station_id,
        'occupied': False
    })

def calculate_parking_fee(duration):
    # Basic fee calculation
    base_fee = 20  # First hour
    additional_fee = 10  # Per additional hour
    
    if duration <= 1:
        return base_fee
    else:
        return base_fee + additional_fee * (int(duration) - 1)

@parking_bp.route('/analytics', methods=['GET'])
def get_parking_analytics():
    station_id = request.args.get('station_id')
    start_date = datetime.now() - timedelta(days=7)
    
    pipeline = [
        {
            '$match': {
                'station_id': station_id,
                'entry_time': {'$gte': start_date}
            }
        },
        {
            '$group': {
                '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$entry_time'}},
                'total_vehicles': {'$sum': 1},
                'avg_duration': {'$avg': '$duration'},
                'total_revenue': {'$sum': '$fee'}
            }
        },
        {'$sort': {'_id': 1}}
    ]
    
    analytics = list(db.parking_history.aggregate(pipeline))
    return jsonify(analytics) 