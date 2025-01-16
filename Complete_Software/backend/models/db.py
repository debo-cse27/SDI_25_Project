from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['traffic_management']

def init_db():
    # Create collections if they don't exist
    if 'parking_spots' not in db.list_collection_names():
        db.create_collection('parking_spots')
    if 'priority_vehicles' not in db.list_collection_names():
        db.create_collection('priority_vehicles')
    if 'traffic_data' not in db.list_collection_names():
        db.create_collection('traffic_data') 