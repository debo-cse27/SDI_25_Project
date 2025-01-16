import React, { useState, useEffect } from 'react';
import TrafficStatus from '../components/TrafficStatus';
import ParkingOverview from '../components/ParkingOverview';
import MetroUpdates from '../components/MetroUpdates';

function Dashboard() {
  const [trafficData, setTrafficData] = useState(null);
  const [parkingData, setParkingData] = useState(null);
  const [metroData, setMetroData] = useState(null);

  useEffect(() => {
    // Fetch data from backend
    fetchTrafficData();
    fetchParkingData();
    fetchMetroData();
  }, []);

  return (
    <div className="dashboard">
      <h1>Traffic Management Dashboard</h1>
      <div className="grid">
        <TrafficStatus data={trafficData} />
        <ParkingOverview data={parkingData} />
        <MetroUpdates data={metroData} />
      </div>
    </div>
  );
}

export default Dashboard; 