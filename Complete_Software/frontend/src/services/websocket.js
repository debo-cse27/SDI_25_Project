import io from 'socket.io-client';

class WebSocketService {
    constructor() {
        this.socket = null;
        this.subscribers = new Map();
    }

    connect() {
        this.socket = io(process.env.REACT_APP_WEBSOCKET_URL || 'http://localhost:5000');
        
        this.socket.on('connect', () => {
            console.log('WebSocket connected');
        });

        this.socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
        });

        // Set up listeners for different update types
        this.setupListeners();
    }

    setupListeners() {
        const updateTypes = ['traffic_update', 'parking_update', 'priority_vehicle', 'metro_update'];
        
        updateTypes.forEach(type => {
            this.socket.on(type, (data) => {
                if (this.subscribers.has(type)) {
                    this.subscribers.get(type).forEach(callback => callback(data));
                }
            });
        });
    }

    subscribe(updateType, callback) {
        if (!this.subscribers.has(updateType)) {
            this.subscribers.set(updateType, new Set());
        }
        this.subscribers.get(updateType).add(callback);
        this.socket.emit('subscribe', { channel: updateType });
    }

    unsubscribe(updateType, callback) {
        if (this.subscribers.has(updateType)) {
            this.subscribers.get(updateType).delete(callback);
            if (this.subscribers.get(updateType).size === 0) {
                this.socket.emit('unsubscribe', { channel: updateType });
            }
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
    }
}

export default new WebSocketService(); 