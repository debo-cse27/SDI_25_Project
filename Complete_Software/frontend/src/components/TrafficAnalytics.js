import React, { useState, useEffect } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import WebSocketService from '../services/websocket';
import './TrafficAnalytics.css';

const TrafficAnalytics = () => {
    const [trafficData, setTrafficData] = useState({
        hourly: [],
        daily: [],
        patterns: {},
        congestionPoints: []
    });
    const [timeRange, setTimeRange] = useState('24h');
    const [viewMode, setViewMode] = useState('flow');

    useEffect(() => {
        fetchTrafficData();
        setupRealTimeUpdates();

        return () => {
            WebSocketService.unsubscribe('traffic_update', handleTrafficUpdate);
        };
    }, [timeRange]);

    const fetchTrafficData = async () => {
        try {
            const response = await fetch(`/api/traffic/analytics?range=${timeRange}`);
            const data = await response.json();
            setTrafficData(data);
        } catch (error) {
            console.error('Error fetching traffic data:', error);
        }
    };

    const setupRealTimeUpdates = () => {
        WebSocketService.subscribe('traffic_update', handleTrafficUpdate);
    };

    const handleTrafficUpdate = (update) => {
        setTrafficData(prev => ({
            ...prev,
            hourly: [...prev.hourly.slice(1), update.current],
            congestionPoints: update.congestionPoints
        }));
    };

    const getFlowChartData = () => ({
        labels: trafficData.hourly.map(d => new Date(d.timestamp).toLocaleTimeString()),
        datasets: [
            {
                label: 'Traffic Flow (vehicles/hour)',
                data: trafficData.hourly.map(d => d.flow),
                borderColor: '#2196F3',
                fill: false
            },
            {
                label: 'Congestion Level',
                data: trafficData.hourly.map(d => d.congestion),
                borderColor: '#F44336',
                fill: false
            }
        ]
    });

    const getPatternChartData = () => ({
        labels: Object.keys(trafficData.patterns),
        datasets: [{
            label: 'Traffic Patterns',
            data: Object.values(trafficData.patterns),
            backgroundColor: [
                '#2196F3',
                '#4CAF50',
                '#FFC107',
                '#F44336',
                '#9C27B0'
            ]
        }]
    });

    return (
        <div className="traffic-analytics">
            <div className="analytics-header">
                <h2>Traffic Analysis</h2>
                <div className="controls">
                    <select 
                        value={timeRange}
                        onChange={(e) => setTimeRange(e.target.value)}
                    >
                        <option value="24h">Last 24 Hours</option>
                        <option value="7d">Last 7 Days</option>
                        <option value="30d">Last 30 Days</option>
                    </select>
                    <div className="view-toggles">
                        <button 
                            className={viewMode === 'flow' ? 'active' : ''}
                            onClick={() => setViewMode('flow')}
                        >
                            Flow Analysis
                        </button>
                        <button 
                            className={viewMode === 'patterns' ? 'active' : ''}
                            onClick={() => setViewMode('patterns')}
                        >
                            Traffic Patterns
                        </button>
                    </div>
                </div>
            </div>

            <div className="analytics-content">
                {viewMode === 'flow' ? (
                    <div className="flow-analysis">
                        <div className="chart-container">
                            <Line 
                                data={getFlowChartData()}
                                options={{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    scales: {
                                        y: {
                                            beginAtZero: true
                                        }
                                    }
                                }}
                            />
                        </div>
                        <div className="congestion-points">
                            <h3>Current Congestion Points</h3>
                            <div className="points-list">
                                {trafficData.congestionPoints.map((point, index) => (
                                    <div key={index} className="congestion-point">
                                        <div className="location">{point.location}</div>
                                        <div className="severity" data-level={point.severity}>
                                            {point.severity.toUpperCase()}
                                        </div>
                                        <div className="details">
                                            <span>Delay: {point.delay} min</span>
                                            <span>Queue Length: {point.queueLength} m</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="pattern-analysis">
                        <div className="chart-container">
                            <Bar 
                                data={getPatternChartData()}
                                options={{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    plugins: {
                                        legend: {
                                            position: 'bottom'
                                        }
                                    }
                                }}
                            />
                        </div>
                        <div className="pattern-insights">
                            <h3>Traffic Pattern Insights</h3>
                            <div className="insights-list">
                                {Object.entries(trafficData.patterns).map(([pattern, value]) => (
                                    <div key={pattern} className="pattern-insight">
                                        <div className="pattern-name">{pattern}</div>
                                        <div className="pattern-value">{value}%</div>
                                        <div className="pattern-bar">
                                            <div 
                                                className="pattern-fill"
                                                style={{ width: `${value}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TrafficAnalytics; 