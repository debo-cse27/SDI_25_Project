import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import './ParkingOverview.css';

const ParkingOverview = ({ data }) => {
    const [selectedStation, setSelectedStation] = useState(null);
    const [parkingData, setParkingData] = useState(null);

    useEffect(() => {
        if (selectedStation) {
            fetchParkingData(selectedStation);
        }
    }, [selectedStation]);

    const fetchParkingData = async (stationId) => {
        try {
            const response = await fetch(`/api/parking/spots/${stationId}`);
            const data = await response.json();
            setParkingData(data);
        } catch (error) {
            console.error('Error fetching parking data:', error);
        }
    };

    const chartData = {
        labels: ['Available', 'Occupied'],
        datasets: [{
            data: [
                parkingData?.available_spots || 0,
                parkingData?.total_spots - (parkingData?.available_spots || 0)
            ],
            backgroundColor: ['#4CAF50', '#f44336']
        }]
    };

    return (
        <div className="parking-overview">
            <h2>Parking Status</h2>
            <select 
                value={selectedStation || ''} 
                onChange={(e) => setSelectedStation(e.target.value)}
            >
                <option value="">Select Station</option>
                {data?.stations.map(station => (
                    <option key={station.id} value={station.id}>
                        {station.name}
                    </option>
                ))}
            </select>

            {parkingData && (
                <div className="parking-stats">
                    <div className="stats-grid">
                        <div className="stat-box">
                            <h3>Total Spots</h3>
                            <p>{parkingData.total_spots}</p>
                        </div>
                        <div className="stat-box">
                            <h3>Available</h3>
                            <p>{parkingData.available_spots}</p>
                        </div>
                        <div className="stat-box">
                            <h3>Occupied</h3>
                            <p>{parkingData.total_spots - parkingData.available_spots}</p>
                        </div>
                    </div>
                    <div className="parking-chart">
                        <Bar data={chartData} options={{ responsive: true }} />
                    </div>
                </div>
            )}
        </div>
    );
};

export default ParkingOverview; 