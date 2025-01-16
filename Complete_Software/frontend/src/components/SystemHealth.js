import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import WebSocketService from '../services/websocket';
import './SystemHealth.css';

const SystemHealth = () => {
    const [healthData, setHealthData] = useState({
        currentStatus: {
            overall: 'healthy',
            components: {
                traffic: 'healthy',
                database: 'healthy',
                api: 'healthy',
                services: 'healthy'
            }
        },
        metrics: {
            responseTime: [],
            errorRate: [],
            availability: [],
            timestamps: []
        },
        issues: []
    });

    useEffect(() => {
        fetchHealthData();
        setupWebSocket();
        const interval = setInterval(fetchHealthData, 60000); // Update every minute

        return () => {
            clearInterval(interval);
            WebSocketService.unsubscribe('health_update', handleHealthUpdate);
        };
    }, []);

    const fetchHealthData = async () => {
        try {
            const response = await fetch('/api/system/health-status');
            const data = await response.json();
            setHealthData(prevData => ({
                ...prevData,
                ...data
            }));
        } catch (error) {
            console.error('Error fetching health data:', error);
        }
    };

    const setupWebSocket = () => {
        WebSocketService.subscribe('health_update', handleHealthUpdate);
    };

    const handleHealthUpdate = (update) => {
        setHealthData(prevData => ({
            ...prevData,
            currentStatus: update.status,
            metrics: {
                ...prevData.metrics,
                responseTime: [...prevData.metrics.responseTime.slice(-59), update.metrics.responseTime],
                errorRate: [...prevData.metrics.errorRate.slice(-59), update.metrics.errorRate],
                availability: [...prevData.metrics.availability.slice(-59), update.metrics.availability],
                timestamps: [...prevData.metrics.timestamps.slice(-59), update.timestamp]
            },
            issues: update.issues
        }));
    };

    const getHealthMetricsChart = () => ({
        labels: healthData.metrics.timestamps.map(t => new Date(t).toLocaleTimeString()),
        datasets: [
            {
                label: 'Response Time (ms)',
                data: healthData.metrics.responseTime,
                borderColor: '#2196F3',
                fill: false
            },
            {
                label: 'Error Rate (%)',
                data: healthData.metrics.errorRate,
                borderColor: '#F44336',
                fill: false
            },
            {
                label: 'Availability (%)',
                data: healthData.metrics.availability,
                borderColor: '#4CAF50',
                fill: false
            }
        ]
    });

    return (
        <div className="system-health">
            <div className="health-overview">
                <div className="health-status-card">
                    <h3>System Health Status</h3>
                    <div className={`status-indicator ${healthData.currentStatus.overall}`}>
                        {healthData.currentStatus.overall.toUpperCase()}
                    </div>
                </div>

                <div className="component-status-grid">
                    {Object.entries(healthData.currentStatus.components).map(([component, status]) => (
                        <div key={component} className="component-status">
                            <h4>{component}</h4>
                            <span className={`status-badge ${status}`}>
                                {status.toUpperCase()}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            <div className="health-metrics">
                <h3>Health Metrics</h3>
                <div className="chart-container">
                    <Line 
                        data={getHealthMetricsChart()}
                        options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            animation: false,
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }}
                    />
                </div>
            </div>

            <div className="health-issues">
                <h3>Active Issues</h3>
                <div className="issues-list">
                    {healthData.issues.map((issue, index) => (
                        <div key={index} className={`issue-item ${issue.severity}`}>
                            <div className="issue-header">
                                <span className="issue-severity">{issue.severity}</span>
                                <span className="issue-time">
                                    {new Date(issue.timestamp).toLocaleString()}
                                </span>
                            </div>
                            <div className="issue-title">{issue.title}</div>
                            <div className="issue-description">{issue.description}</div>
                            {issue.recommendation && (
                                <div className="issue-recommendation">
                                    Recommendation: {issue.recommendation}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default SystemHealth; 