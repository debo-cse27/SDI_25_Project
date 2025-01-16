import React, { useState, useEffect } from 'react';
import './AdminPanel.css';

const AdminPanel = () => {
    const [systemConfig, setSystemConfig] = useState({
        trafficTimings: {
            minGreenTime: 10,
            maxGreenTime: 90,
            yellowTime: 3
        },
        priorityVehicles: {
            responseTime: 10,
            clearanceTime: 5
        },
        parkingLots: []
    });

    const [users, setUsers] = useState([]);
    const [selectedTab, setSelectedTab] = useState('config');

    useEffect(() => {
        fetchSystemConfig();
        fetchUsers();
    }, []);

    const fetchSystemConfig = async () => {
        try {
            const response = await fetch('/api/admin/config');
            const data = await response.json();
            setSystemConfig(data);
        } catch (error) {
            console.error('Error fetching config:', error);
        }
    };

    const fetchUsers = async () => {
        try {
            const response = await fetch('/api/admin/users');
            const data = await response.json();
            setUsers(data);
        } catch (error) {
            console.error('Error fetching users:', error);
        }
    };

    const updateConfig = async (newConfig) => {
        try {
            await fetch('/api/admin/config', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newConfig)
            });
            setSystemConfig(newConfig);
        } catch (error) {
            console.error('Error updating config:', error);
        }
    };

    return (
        <div className="admin-panel">
            <div className="admin-header">
                <h2>Admin Panel</h2>
                <div className="tab-navigation">
                    <button 
                        className={selectedTab === 'config' ? 'active' : ''}
                        onClick={() => setSelectedTab('config')}
                    >
                        System Configuration
                    </button>
                    <button 
                        className={selectedTab === 'users' ? 'active' : ''}
                        onClick={() => setSelectedTab('users')}
                    >
                        User Management
                    </button>
                    <button 
                        className={selectedTab === 'logs' ? 'active' : ''}
                        onClick={() => setSelectedTab('logs')}
                    >
                        System Logs
                    </button>
                </div>
            </div>

            <div className="admin-content">
                {selectedTab === 'config' && (
                    <div className="config-section">
                        <h3>Traffic Signal Configuration</h3>
                        <div className="config-form">
                            <div className="form-group">
                                <label>Minimum Green Time (seconds)</label>
                                <input
                                    type="number"
                                    value={systemConfig.trafficTimings.minGreenTime}
                                    onChange={(e) => updateConfig({
                                        ...systemConfig,
                                        trafficTimings: {
                                            ...systemConfig.trafficTimings,
                                            minGreenTime: parseInt(e.target.value)
                                        }
                                    })}
                                />
                            </div>
                            {/* Add more configuration options */}
                        </div>
                    </div>
                )}

                {selectedTab === 'users' && (
                    <div className="users-section">
                        <h3>User Management</h3>
                        <table className="users-table">
                            <thead>
                                <tr>
                                    <th>Username</th>
                                    <th>Role</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map(user => (
                                    <tr key={user.id}>
                                        <td>{user.username}</td>
                                        <td>{user.role}</td>
                                        <td>{user.status}</td>
                                        <td>
                                            <button>Edit</button>
                                            <button>Delete</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminPanel; 