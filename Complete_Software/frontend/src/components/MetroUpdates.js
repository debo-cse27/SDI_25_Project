import React, { useState, useEffect } from 'react';
import './MetroUpdates.css';

const MetroUpdates = () => {
    const [selectedStation, setSelectedStation] = useState(null);
    const [schedule, setSchedule] = useState(null);
    const [stations, setStations] = useState([]);

    useEffect(() => {
        fetchStations();
    }, []);

    useEffect(() => {
        if (selectedStation) {
            fetchSchedule(selectedStation);
        }
    }, [selectedStation]);

    const fetchStations = async () => {
        try {
            const response = await fetch('/api/metro/stations');
            const data = await response.json();
            setStations(data);
        } catch (error) {
            console.error('Error fetching stations:', error);
        }
    };

    const fetchSchedule = async (stationId) => {
        try {
            const response = await fetch(`/api/metro/schedule/${stationId}`);
            const data = await response.json();
            setSchedule(data);
        } catch (error) {
            console.error('Error fetching schedule:', error);
        }
    };

    return (
        <div className="metro-updates">
            <h2>Metro Schedule</h2>
            <select 
                value={selectedStation || ''} 
                onChange={(e) => setSelectedStation(e.target.value)}
            >
                <option value="">Select Station</option>
                {stations.map(station => (
                    <option key={station.id} value={station.id}>
                        {station.name}
                    </option>
                ))}
            </select>

            {schedule && (
                <div className="schedule-container">
                    <h3>Upcoming Trains</h3>
                    <div className="schedule-grid">
                        {schedule.schedule.map((train, index) => (
                            <div key={index} className="train-info">
                                <p className="train-id">{train.train_id}</p>
                                <p className="destination">{train.destination}</p>
                                <p className="time">{train.departure_time}</p>
                                <p className={`status ${train.status.toLowerCase()}`}>
                                    {train.status}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default MetroUpdates; 