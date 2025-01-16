import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import WebSocketService from '../services/websocket';
import LoadingSpinner from './common/LoadingSpinner';
import ErrorMessage from './common/ErrorMessage';
import './TrafficStatus.css';

const TrafficStatus = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchInitialData();
        setupWebSocket();

        return () => {
            WebSocketService.unsubscribe('traffic_update', handleTrafficUpdate);
        };
    }, []);

    const fetchInitialData = async () => {
        try {
            const response = await fetch('/api/traffic/status');
            const initialData = await response.json();
            setData(initialData);
            setError(null);
        } catch (err) {
            setError('Failed to load traffic data');
        } finally {
            setLoading(false);
        }
    };

    const setupWebSocket = () => {
        WebSocketService.subscribe('traffic_update', handleTrafficUpdate);
    };

    const handleTrafficUpdate = (update) => {
        setData(prevData => ({
            ...prevData,
            ...update
        }));
    };

    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorMessage message={error} onRetry={fetchInitialData} />;
    if (!data) return null;

    const chartData = {
        labels: data.timePoints,
        datasets: [{
            label: 'Traffic Density',
            data: data.densityValues,
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    };

    return (
        <div className="traffic-status">
            <h2>Traffic Status</h2>
            <div className="traffic-grid">
                {[1, 2, 3, 4].map(lane => (
                    <div key={lane} className="lane-status">
                        <h3>Lane {lane}</h3>
                        <div className="traffic-light">
                            <div className={`light red ${data.currentLane === lane && data.status === 'RED' ? 'active' : ''}`}></div>
                            <div className={`light yellow ${data.currentLane === lane && data.status === 'YELLOW' ? 'active' : ''}`}></div>
                            <div className={`light green ${data.currentLane === lane && data.status === 'GREEN' ? 'active' : ''}`}></div>
                        </div>
                        <div className="density-info">
                            <p>Density: {data.lanes[lane-1]?.density || 0}%</p>
                            <p>Timer: {data.currentLane === lane ? data.timer : 0}s</p>
                        </div>
                    </div>
                ))}
            </div>
            <div className="traffic-chart">
                <Line data={chartData} options={{ responsive: true }} />
            </div>
        </div>
    );
};

export default TrafficStatus; 