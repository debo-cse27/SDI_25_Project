import React, { useState, useEffect } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import WebSocketService from '../services/websocket';
import './DetailedMetrics.css';

const DetailedMetrics = () => {
    const [metrics, setMetrics] = useState({
        traffic: {
            throughput: [],
            responseTime: [],
            errorRate: [],
            timestamps: []
        },
        resources: {
            cpu: [],
            memory: [],
            disk: [],
            network: []
        },
        distribution: {
            requestTypes: {},
            responseStatus: {}
        }
    });

    useEffect(() => {
        fetchInitialMetrics();
        setupRealTimeUpdates();

        return () => {
            WebSocketService.unsubscribe('metrics_update', handleMetricsUpdate);
        };
    }, []);

    const fetchInitialMetrics = async () => {
        try {
            const response = await fetch('/api/system/detailed-metrics');
            const data = await response.json();
            setMetrics(data);
        } catch (error) {
            console.error('Error fetching metrics:', error);
        }
    };

    const setupRealTimeUpdates = () => {
        WebSocketService.subscribe('metrics_update', handleMetricsUpdate);
    };

    const handleMetricsUpdate = (update) => {
        setMetrics(prevMetrics => ({
            ...prevMetrics,
            traffic: {
                throughput: [...prevMetrics.traffic.throughput.slice(-59), update.throughput],
                responseTime: [...prevMetrics.traffic.responseTime.slice(-59), update.responseTime],
                errorRate: [...prevMetrics.traffic.errorRate.slice(-59), update.errorRate],
                timestamps: [...prevMetrics.traffic.timestamps.slice(-59), update.timestamp]
            },
            resources: {
                cpu: [...prevMetrics.resources.cpu.slice(-59), update.cpu],
                memory: [...prevMetrics.resources.memory.slice(-59), update.memory],
                disk: [...prevMetrics.resources.disk.slice(-59), update.disk],
                network: [...prevMetrics.resources.network.slice(-59), update.network]
            },
            distribution: update.distribution
        }));
    };

    const getTrafficChartData = () => ({
        labels: metrics.traffic.timestamps.map(t => new Date(t).toLocaleTimeString()),
        datasets: [
            {
                label: 'Throughput (req/s)',
                data: metrics.traffic.throughput,
                borderColor: '#2196F3',
                fill: false
            },
            {
                label: 'Response Time (ms)',
                data: metrics.traffic.responseTime,
                borderColor: '#4CAF50',
                fill: false
            },
            {
                label: 'Error Rate (%)',
                data: metrics.traffic.errorRate,
                borderColor: '#F44336',
                fill: false
            }
        ]
    });

    const getResourcesChartData = () => ({
        labels: metrics.traffic.timestamps.map(t => new Date(t).toLocaleTimeString()),
        datasets: [
            {
                label: 'CPU Usage (%)',
                data: metrics.resources.cpu,
                backgroundColor: 'rgba(33, 150, 243, 0.5)',
                borderColor: '#2196F3',
                borderWidth: 1
            },
            {
                label: 'Memory Usage (%)',
                data: metrics.resources.memory,
                backgroundColor: 'rgba(76, 175, 80, 0.5)',
                borderColor: '#4CAF50',
                borderWidth: 1
            }
        ]
    });

    const getDistributionChartData = () => ({
        labels: Object.keys(metrics.distribution.requestTypes),
        datasets: [{
            data: Object.values(metrics.distribution.requestTypes),
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
        <div className="detailed-metrics">
            <div className="metrics-grid">
                <div className="metric-card">
                    <h3>Traffic Metrics</h3>
                    <div className="chart-container">
                        <Line 
                            data={getTrafficChartData()}
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

                <div className="metric-card">
                    <h3>Resource Usage</h3>
                    <div className="chart-container">
                        <Bar 
                            data={getResourcesChartData()}
                            options={{
                                responsive: true,
                                maintainAspectRatio: false,
                                animation: false,
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                        max: 100
                                    }
                                }
                            }}
                        />
                    </div>
                </div>

                <div className="metric-card">
                    <h3>Request Distribution</h3>
                    <div className="chart-container">
                        <Doughnut 
                            data={getDistributionChartData()}
                            options={{
                                responsive: true,
                                maintainAspectRatio: false,
                                animation: false
                            }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DetailedMetrics; 