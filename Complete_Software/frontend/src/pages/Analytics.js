import React, { useState, useEffect } from 'react';
import { Line, Bar, Pie } from 'react-chartjs-2';
import './Analytics.css';

const Analytics = () => {
    const [trafficData, setTrafficData] = useState(null);
    const [parkingData, setParkingData] = useState(null);
    const [metroData, setMetroData] = useState(null);

    useEffect(() => {
        fetchAnalytics();
    }, []);

    const fetchAnalytics = async () => {
        try {
            const [trafficRes, parkingRes, metroRes] = await Promise.all([
                fetch('/api/traffic/analytics'),
                fetch('/api/parking/analytics'),
                fetch('/api/metro/analytics')
            ]);

            const traffic = await trafficRes.json();
            const parking = await parkingRes.json();
            const metro = await metroRes.json();

            setTrafficData(traffic);
            setParkingData(parking);
            setMetroData(metro);
        } catch (error) {
            console.error('Error fetching analytics:', error);
        }
    };

    return (
        <div className="analytics-dashboard">
            <h2>System Analytics</h2>
            
            <div className="analytics-grid">
                <div className="analytics-card">
                    <h3>Traffic Flow Analysis</h3>
                    {trafficData && (
                        <Line 
                            data={trafficData}
                            options={{
                                responsive: true,
                                plugins: {
                                    title: {
                                        display: true,
                                        text: 'Traffic Density Over Time'
                                    }
                                }
                            }}
                        />
                    )}
                </div>

                <div className="analytics-card">
                    <h3>Parking Utilization</h3>
                    {parkingData && (
                        <Bar 
                            data={parkingData}
                            options={{
                                responsive: true,
                                plugins: {
                                    title: {
                                        display: true,
                                        text: 'Parking Space Usage'
                                    }
                                }
                            }}
                        />
                    )}
                </div>

                <div className="analytics-card">
                    <h3>Metro Statistics</h3>
                    {metroData && (
                        <Pie 
                            data={metroData}
                            options={{
                                responsive: true,
                                plugins: {
                                    title: {
                                        display: true,
                                        text: 'Metro Station Traffic'
                                    }
                                }
                            }}
                        />
                    )}
                </div>

                <div className="analytics-card">
                    <h3>Key Metrics</h3>
                    <div className="metrics-grid">
                        <div className="metric-box">
                            <h4>Average Wait Time</h4>
                            <p>{trafficData?.averageWaitTime || '0'} seconds</p>
                        </div>
                        <div className="metric-box">
                            <h4>Parking Efficiency</h4>
                            <p>{parkingData?.efficiency || '0'}%</p>
                        </div>
                        <div className="metric-box">
                            <h4>Priority Vehicle Response</h4>
                            <p>{trafficData?.priorityResponse || '0'} minutes</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Analytics; 