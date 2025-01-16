import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import WebSocketService from '../services/websocket';
import './PerformanceMonitor.css';

const PerformanceMonitor = () => {
    const [performanceData, setPerformanceData] = useState({
        cpu: [],
        memory: [],
        disk: { read: [], write: [] },
        network: { in: [], out: [] },
        timestamps: []
    });

    const [selectedMetric, setSelectedMetric] = useState('cpu');
    const maxDataPoints = 60; // 1 hour of data at 1 minute intervals

    useEffect(() => {
        fetchInitialData();
        setupWebSocket();

        return () => {
            WebSocketService.unsubscribe('performance_update', handlePerformanceUpdate);
        };
    }, []);

    const fetchInitialData = async () => {
        try {
            const response = await fetch('/api/system/performance');
            const data = await response.json();
            setPerformanceData(data);
        } catch (error) {
            console.error('Error fetching performance data:', error);
        }
    };

    const setupWebSocket = () => {
        WebSocketService.subscribe('performance_update', handlePerformanceUpdate);
    };

    const handlePerformanceUpdate = (update) => {
        setPerformanceData(prevData => {
            const newData = { ...prevData };
            
            // Add new data points
            newData.cpu.push(update.cpu.usage_percent);
            newData.memory.push(update.memory.percent);
            newData.disk.read.push(update.disk.read_rate);
            newData.disk.write.push(update.disk.write_rate);
            newData.network.in.push(update.network.bytes_recv);
            newData.network.out.push(update.network.bytes_sent);
            newData.timestamps.push(update.timestamp);

            // Limit the number of data points
            Object.keys(newData).forEach(key => {
                if (Array.isArray(newData[key])) {
                    newData[key] = newData[key].slice(-maxDataPoints);
                } else if (typeof newData[key] === 'object') {
                    Object.keys(newData[key]).forEach(subKey => {
                        newData[key][subKey] = newData[key][subKey].slice(-maxDataPoints);
                    });
                }
            });

            return newData;
        });
    };

    const getChartData = () => {
        let datasets = [];
        
        switch (selectedMetric) {
            case 'cpu':
                datasets = [{
                    label: 'CPU Usage (%)',
                    data: performanceData.cpu,
                    borderColor: '#2196F3',
                    fill: false
                }];
                break;
            case 'memory':
                datasets = [{
                    label: 'Memory Usage (%)',
                    data: performanceData.memory,
                    borderColor: '#4CAF50',
                    fill: false
                }];
                break;
            case 'disk':
                datasets = [
                    {
                        label: 'Read Rate (MB/s)',
                        data: performanceData.disk.read.map(v => v / 1_000_000),
                        borderColor: '#FF9800',
                        fill: false
                    },
                    {
                        label: 'Write Rate (MB/s)',
                        data: performanceData.disk.write.map(v => v / 1_000_000),
                        borderColor: '#F44336',
                        fill: false
                    }
                ];
                break;
            case 'network':
                datasets = [
                    {
                        label: 'Network In (MB/s)',
                        data: performanceData.network.in.map(v => v / 1_000_000),
                        borderColor: '#9C27B0',
                        fill: false
                    },
                    {
                        label: 'Network Out (MB/s)',
                        data: performanceData.network.out.map(v => v / 1_000_000),
                        borderColor: '#607D8B',
                        fill: false
                    }
                ];
                break;
        }

        return {
            labels: performanceData.timestamps.map(t => new Date(t).toLocaleTimeString()),
            datasets
        };
    };

    return (
        <div className="performance-monitor">
            <div className="metric-selector">
                <button 
                    className={selectedMetric === 'cpu' ? 'active' : ''}
                    onClick={() => setSelectedMetric('cpu')}
                >
                    CPU
                </button>
                <button 
                    className={selectedMetric === 'memory' ? 'active' : ''}
                    onClick={() => setSelectedMetric('memory')}
                >
                    Memory
                </button>
                <button 
                    className={selectedMetric === 'disk' ? 'active' : ''}
                    onClick={() => setSelectedMetric('disk')}
                >
                    Disk I/O
                </button>
                <button 
                    className={selectedMetric === 'network' ? 'active' : ''}
                    onClick={() => setSelectedMetric('network')}
                >
                    Network
                </button>
            </div>

            <div className="chart-container">
                <Line 
                    data={getChartData()}
                    options={{
                        responsive: true,
                        animation: false,
                        scales: {
                            x: {
                                display: true,
                                title: {
                                    display: true,
                                    text: 'Time'
                                }
                            },
                            y: {
                                display: true,
                                title: {
                                    display: true,
                                    text: selectedMetric === 'cpu' || selectedMetric === 'memory' 
                                        ? 'Percentage' 
                                        : 'MB/s'
                                }
                            }
                        }
                    }}
                />
            </div>
        </div>
    );
};

export default PerformanceMonitor; 