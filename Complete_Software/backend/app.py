from flask import Flask, jsonify, request
from flask_cors import CORS
from api.traffic_api import traffic_bp
from api.parking_api import parking_bp
from api.metro_api import metro_bp
from api.priority_vehicle_api import priority_bp
from models.db import init_db
from flask_session import Session
from api.auth_api import auth_bp
import secrets
from websocket_server import socketio
from utils.logger import log_system_event
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(traffic_bp, url_prefix='/api/traffic')
app.register_blueprint(parking_bp, url_prefix='/api/parking')
app.register_blueprint(metro_bp, url_prefix='/api/metro')
app.register_blueprint(priority_bp, url_prefix='/api/priority')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Initialize database
init_db()

# Add these configurations
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Initialize SocketIO
socketio.init_app(app, cors_allowed_origins="*")

# Log system startup
@app.before_first_request
def on_startup():
    log_system_event('System', 'Startup', 'Success', {
        'time': datetime.utcnow().isoformat(),
        'environment': os.getenv('FLASK_ENV', 'development')
    })

# Error handling
@app.errorhandler(Exception)
def handle_error(error):
    log_system_event('System', 'Error', 'Failed', {
        'error_type': type(error).__name__,
        'error_message': str(error)
    })
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(error)
    }), 500

if __name__ == '__main__':
    socketio.run(app, debug=True) 