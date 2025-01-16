import React, { useState, useEffect } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import WebSocketService from '../services/websocket';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import './SystemMonitor.css';

const SystemMonitor = () => {
    const [systemStats, setSystemStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        fetchSystemStats();
        const interval = setInterval(fetchSystemStats, 30000); // Update every 30 seconds

        return () => clearInterval(interval);
    }, []);

    const fetchSystemStats = async () => {
        try {
            const response = await fetch('/api/system/stats');
            const stats = await response.json();
            setSystemStats(stats);
            setError(null);
        } catch (err) {
            setError('Failed to load system statistics');
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorMessage message={error} onRetry={fetchSystemStats} />;
    if (!systemStats) return null;

    return (
        <div className="system-monitor">
            <h2>System Monitor</h2>
            
            <div className="monitor-tabs">
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
                    className={activeTab === 'logs' ? 'active' : ''}
                    onClick={() => setActiveTab('logs')}
                >
                    System Logs
                </button>
            </div>

            <div className="monitor-content">
                {activeTab === 'overview' && (
                    <div className="overview-grid">
                        <div className="stat-card">
                            <h3>System Status</h3>
                            <p className={`status ${systemStats.status.toLowerCase()}`}>
                                {systemStats.status}
                            </p>
                        </div>
                        <div className="stat-card">
                            <h3>Active Users</h3>
                            <p>{systemStats.activeUsers}</p>
                        </div>
                        <div className="stat-card">
                            <h3>Response Time</h3>
                            <p>{systemStats.avgResponseTime}ms</p>
                        </div>
                        <div className="stat-card">
                            <h3>Error Rate</h3>
                            <p>{systemStats.errorRate}%</p>
                        </div>
                    </div>
                )}

                {activeTab === 'performance' && (
                    <div className="performance-charts">
                        <div className="chart-container">
                            <h3>CPU Usage</h3>
                            <Line data={systemStats.cpuData} options={{ responsive: true }} />
                        </div>
                        <div className="chart-container">
                            <h3>Memory Usage</h3>
                            <Line data={systemStats.memoryData} options={{ responsive: true }} />
                        </div>
                    </div>
                )}

                {activeTab === 'logs' && (
                    <div className="system-logs">
                        <div className="log-filters">
                            <select onChange={(e) => console.log(e.target.value)}>
                                <option value="all">All Logs</option>
                                <option value="error">Errors</option>
                                <option value="warning">Warnings</option>
                                <option value="info">Info</option>
                            </select>
                        </div>
                        <div className="log-entries">
                            {systemStats.logs.map((log, index) => (
                                <div key={index} className={`log-entry ${log.level.toLowerCase()}`}>
                                    <span className="timestamp">{log.timestamp}</span>
                                    <span className="level">{log.level}</span>
                                    <span className="message">{log.message}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SystemMonitor; 