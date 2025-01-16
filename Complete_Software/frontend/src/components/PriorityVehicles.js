import React, { useState } from 'react';
import './PriorityVehicles.css';

const PriorityVehicles = () => {
    const [vehicleData, setVehicleData] = useState({
        vehicle_type: '',
        vehicle_id: '',
        rfid_tag: ''
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('/api/priority/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(vehicleData)
            });
            const data = await response.json();
            if (data.status === 'success') {
                alert('Vehicle registered successfully');
                setVehicleData({
                    vehicle_type: '',
                    vehicle_id: '',
                    rfid_tag: ''
                });
            }
        } catch (error) {
            console.error('Error registering vehicle:', error);
        }
    };

    return (
        <div className="priority-vehicles">
            <h2>Priority Vehicle Registration</h2>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Vehicle Type</label>
                    <select 
                        value={vehicleData.vehicle_type}
                        onChange={(e) => setVehicleData({
                            ...vehicleData,
                            vehicle_type: e.target.value
                        })}
                    >
                        <option value="">Select Type</option>
                        <option value="ambulance">Ambulance</option>
                        <option value="fire">Fire Engine</option>
                        <option value="police">Police</option>
                        <option value="vip">VIP</option>
                    </select>
                </div>
                <div className="form-group">
                    <label>Vehicle ID</label>
                    <input 
                        type="text"
                        value={vehicleData.vehicle_id}
                        onChange={(e) => setVehicleData({
                            ...vehicleData,
                            vehicle_id: e.target.value
                        })}
                    />
                </div>
                <div className="form-group">
                    <label>RFID Tag</label>
                    <input 
                        type="text"
                        value={vehicleData.rfid_tag}
                        onChange={(e) => setVehicleData({
                            ...vehicleData,
                            rfid_tag: e.target.value
                        })}
                    />
                </div>
                <button type="submit">Register Vehicle</button>
            </form>
        </div>
    );
};

export default PriorityVehicles; 