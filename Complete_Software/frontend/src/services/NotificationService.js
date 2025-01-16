import WebSocketService from './websocket';

class NotificationService {
    constructor() {
        this.notifications = [];
        this.listeners = new Set();
        this.maxNotifications = 50;
        this.notificationSound = new Audio('/notification-sound.mp3');
    }

    init() {
        this.setupWebSocket();
        this.requestPermission();
    }

    setupWebSocket() {
        WebSocketService.subscribe('notification', this.handleNewNotification.bind(this));
    }

    async requestPermission() {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                console.log('Notification permission granted');
            }
        }
    }

    handleNewNotification(notification) {
        // Add new notification to the beginning of the array
        this.notifications = [
            { ...notification, id: Date.now(), read: false },
            ...this.notifications
        ].slice(0, this.maxNotifications);

        // Notify all listeners
        this.notifyListeners();

        // Show system notification if important
        if (notification.importance === 'high') {
            this.showSystemNotification(notification);
            this.playNotificationSound();
        }
    }

    showSystemNotification(notification) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(notification.title, {
                body: notification.message,
                icon: notification.icon || '/notification-icon.png',
                tag: notification.id
            });
        }
    }

    playNotificationSound() {
        this.notificationSound.play().catch(error => {
            console.error('Error playing notification sound:', error);
        });
    }

    markAsRead(notificationId) {
        this.notifications = this.notifications.map(notification =>
            notification.id === notificationId
                ? { ...notification, read: true }
                : notification
        );
        this.notifyListeners();
    }

    markAllAsRead() {
        this.notifications = this.notifications.map(notification => ({
            ...notification,
            read: true
        }));
        this.notifyListeners();
    }

    clearNotification(notificationId) {
        this.notifications = this.notifications.filter(
            notification => notification.id !== notificationId
        );
        this.notifyListeners();
    }

    clearAll() {
        this.notifications = [];
        this.notifyListeners();
    }

    subscribe(listener) {
        this.listeners.add(listener);
        return () => this.listeners.delete(listener);
    }

    notifyListeners() {
        this.listeners.forEach(listener => listener(this.notifications));
    }

    getUnreadCount() {
        return this.notifications.filter(notification => !notification.read).length;
    }
}

export default new NotificationService(); 