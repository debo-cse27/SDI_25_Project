import React, { useState, useEffect } from 'react';
import NotificationService from '../services/NotificationService';
import './NotificationCenter.css';

const NotificationCenter = () => {
    const [notifications, setNotifications] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        NotificationService.init();
        const unsubscribe = NotificationService.subscribe(setNotifications);
        return unsubscribe;
    }, []);

    const getFilteredNotifications = () => {
        switch (filter) {
            case 'unread':
                return notifications.filter(n => !n.read);
            case 'high':
                return notifications.filter(n => n.importance === 'high');
            default:
                return notifications;
        }
    };

    const handleNotificationClick = (notification) => {
        if (!notification.read) {
            NotificationService.markAsRead(notification.id);
        }
        if (notification.onClick) {
            notification.onClick();
        }
    };

    const getTimeString = (timestamp) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return date.toLocaleDateString();
    };

    return (
        <div className="notification-center">
            <button 
                className="notification-toggle"
                onClick={() => setIsOpen(!isOpen)}
            >
                <i className="notification-icon"></i>
                {NotificationService.getUnreadCount() > 0 && (
                    <span className="notification-badge">
                        {NotificationService.getUnreadCount()}
                    </span>
                )}
            </button>

            {isOpen && (
                <div className="notification-panel">
                    <div className="notification-header">
                        <h3>Notifications</h3>
                        <div className="notification-actions">
                            <select 
                                value={filter}
                                onChange={(e) => setFilter(e.target.value)}
                            >
                                <option value="all">All</option>
                                <option value="unread">Unread</option>
                                <option value="high">High Priority</option>
                            </select>
                            <button 
                                className="mark-all-read"
                                onClick={() => NotificationService.markAllAsRead()}
                            >
                                Mark all as read
                            </button>
                        </div>
                    </div>

                    <div className="notifications-list">
                        {getFilteredNotifications().map(notification => (
                            <div 
                                key={notification.id}
                                className={`notification-item ${notification.read ? 'read' : 'unread'} ${notification.importance}`}
                                onClick={() => handleNotificationClick(notification)}
                            >
                                <div className="notification-content">
                                    <div className="notification-title">
                                        {notification.title}
                                    </div>
                                    <div className="notification-message">
                                        {notification.message}
                                    </div>
                                    <div className="notification-time">
                                        {getTimeString(notification.timestamp)}
                                    </div>
                                </div>
                                <button 
                                    className="notification-clear"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        NotificationService.clearNotification(notification.id);
                                    }}
                                >
                                    ×
                                </button>
                            </div>
                        ))}
                        {getFilteredNotifications().length === 0 && (
                            <div className="no-notifications">
                                No notifications
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default NotificationCenter; 