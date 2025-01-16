import React, { useState, useEffect } from 'react';
import WebSocketService from '../services/websocket';
import './AlertMonitor.css';

const AlertMonitor = () => {
    const [alerts, setAlerts] = useState([]);
    const [showAlerts, setShowAlerts] = useState(false);

    useEffect(() => {
        fetchAlerts();
        setupWebSocket();

        return () => {
            WebSocketService.unsubscribe('new_alert', handleNewAlert);
        };
    }, []);

    const fetchAlerts = async () => {
        try {
            const response = await fetch('/api/alerts/recent');
            const data = await response.json();
            setAlerts(data);
        } catch (error) {
            console.error('Error fetching alerts:', error);
        }
    };

    const setupWebSocket = () => {
        WebSocketService.subscribe('new_alert', handleNewAlert);
    };

    const handleNewAlert = (alert) => {
        setAlerts(prevAlerts => [alert, ...prevAlerts].slice(0, 50));
        if (alert.severity === 'critical') {
            showNotification(alert);
        }
    };

    const showNotification = (alert) => {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Critical Alert', {
                body: alert.message,
                icon: '/alert-icon.png'
            });
        }
    };

    const markAsRead = async (alertId) => {
        try {
            await fetch(`/api/alerts/${alertId}/read`, { method: 'POST' });
            setAlerts(prevAlerts =>
                prevAlerts.map(alert =>
                    alert.id === alertId ? { ...alert, status: 'read' } : alert
                )
            );
        } catch (error) {
            console.error('Error marking alert as read:', error);
        }
    };

    return (
        <div className="alert-monitor">
            <div className="alert-header" onClick={() => setShowAlerts(!showAlerts)}>
                <h3>System Alerts</h3>
                <span className="alert-count">
                    {alerts.filter(a => a.status === 'new').length}
                </span>
            </div>

            {showAlerts && (
                <div className="alert-list">
                    {alerts.map(alert => (
                        <div 
                            key={alert.id} 
                            className={`alert-item ${alert.severity} ${alert.status}`}
                            onClick={() => markAsRead(alert.id)}
                        >
                            <div className="alert-time">
                                {new Date(alert.timestamp).toLocaleTimeString()}
                            </div>
                            <div className="alert-content">
                                <div className="alert-type">{alert.type}</div>
                                <div className="alert-message">{alert.message}</div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default AlertMonitor; 