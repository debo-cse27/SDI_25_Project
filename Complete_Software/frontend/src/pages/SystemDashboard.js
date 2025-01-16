import React, { useState, useEffect } from 'react';
import PerformanceMonitor from '../components/PerformanceMonitor';
import AlertMonitor from '../components/AlertMonitor';
import { Line, Bar } from 'react-chartjs-2';
import './SystemDashboard.css';

const SystemDashboard = () => {
    const [systemHealth, setSystemHealth] = useState({
        status: 'healthy',
        score: 100,
        lastUpdate: new Date()
    });
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        fetchSystemHealth();
        const interval = setInterval(fetchSystemHealth, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchSystemHealth = async () => {
        try {
            const response = await fetch('/api/system/health');
            const data = await response.json();
            setSystemHealth(data);
        } catch (error) {
            console.error('Error fetching system health:', error);
        }
    };

    return (
        <div className="system-dashboard">
            <div className="dashboard-header">
                <h1>System Dashboard</h1>
                <div className={`system-status ${systemHealth.status}`}>
                    <span className="status-indicator"></span>
                    System Status: {systemHealth.status.toUpperCase()}
                </div>
            </div>

            <div className="dashboard-nav">
                <button 
                    className={activeTab === 'overview' ? 'active' : ''}
                    onClick={() => setActiveTab('overview')}
                >
                    Overview
                </button>
                <button 
                    className={activeTab === 'performance' ? 'active' : ''}
                    onClick={() => setActiveTab('performance')}
                >
                    Performance
                </button>
                <button 
                    className={activeTab === 'alerts' ? 'active' : ''}
                    onClick={() => setActiveTab('alerts')}
                >
                    Alerts
                </button>
            </div>

            <div className="dashboard-content">
                {activeTab === 'overview' && (
                    <div className="overview-section">
                        <div className="health-score-card">
                            <h3>System Health Score</h3>
                            <div className="score-display">
                                <div 
                                    className="score-circle"
                                    style={{
                                        background: `conic-gradient(
                                            #4CAF50 ${systemHealth.score}%,
                                            #f5f5f5 ${systemHealth.score}%
                                        )`
                                    }}
                                >
                                    <span>{systemHealth.score}%</span>
                                </div>
                            </div>
                            <p className="last-update">
                                Last updated: {new Date(systemHealth.lastUpdate).toLocaleTimeString()}
                            </p>
                        </div>

                        <div className="quick-stats-grid">
                            <div className="stat-card">
                                <h4>Active Users</h4>
                                <p>{systemHealth.activeUsers || 0}</p>
                            </div>
                            <div className="stat-card">
                                <h4>Response Time</h4>
                                <p>{systemHealth.avgResponseTime || 0}ms</p>
                            </div>
                            <div className="stat-card">
                                <h4>Error Rate</h4>
                                <p>{systemHealth.errorRate || 0}%</p>
                            </div>
                            <div className="stat-card">
                                <h4>Uptime</h4>
                                <p>{systemHealth.uptime || '0d 0h 0m'}</p>
                            </div>
                        </div>

                        <div className="recent-alerts-preview">
                            <AlertMonitor compact={true} />
                        </div>
                    </div>
                )}

                {activeTab === 'performance' && (
                    <div className="performance-section">
                        <PerformanceMonitor />
                    </div>
                )}

                {activeTab === 'alerts' && (
                    <div className="alerts-section">
                        <AlertMonitor />
                    </div>
                )}
            </div>
        </div>
    );
};

export default SystemDashboard; 