import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import ParkingManagement from './pages/ParkingManagement';
import MetroSchedule from './pages/MetroSchedule';
import PriorityVehicles from './pages/PriorityVehicles';
import Analytics from './pages/Analytics';
import './styles/Layout.css';

function App() {
    return (
        <Router>
            <div className="app-container">
                <Header />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/parking" element={<ParkingManagement />} />
                        <Route path="/metro" element={<MetroSchedule />} />
                        <Route path="/priority" element={<PriorityVehicles />} />
                        <Route path="/analytics" element={<Analytics />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App; 