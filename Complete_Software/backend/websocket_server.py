from flask_socketio import SocketIO, emit
from flask import request
import json
from datetime import datetime

socketio = SocketIO()

# Connected clients tracking
connected_clients = {}

@socketio.on('connect')
def handle_connect():
    client_id = request.sid
    connected_clients[client_id] = {
        'connected_at': datetime.utcnow(),
        'subscriptions': []
    }
    emit('connection_established', {'client_id': client_id})

@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid
    if client_id in connected_clients:
        del connected_clients[client_id]

@socketio.on('subscribe')
def handle_subscribe(data):
    client_id = request.sid
    channel = data.get('channel')
    if channel and client_id in connected_clients:
        if channel not in connected_clients[client_id]['subscriptions']:
            connected_clients[client_id]['subscriptions'].append(channel)
            emit('subscription_success', {'channel': channel})

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    client_id = request.sid
    channel = data.get('channel')
    if channel and client_id in connected_clients:
        if channel in connected_clients[client_id]['subscriptions']:
            connected_clients[client_id]['subscriptions'].remove(channel)

def broadcast_traffic_update(data):
    socketio.emit('traffic_update', data, namespace='/traffic')

def broadcast_parking_update(data):
    socketio.emit('parking_update', data, namespace='/parking')

def broadcast_priority_vehicle(data):
    socketio.emit('priority_vehicle', data, namespace='/priority')

def broadcast_metro_update(data):
    socketio.emit('metro_update', data, namespace='/metro') 