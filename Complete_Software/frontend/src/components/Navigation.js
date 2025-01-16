import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
    const location = useLocation();

    return (
        <nav className="nav-menu">
            <Link 
                to="/" 
                className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
            >
                Dashboard
            </Link>
            <Link 
                to="/parking" 
                className={`nav-link ${location.pathname === '/parking' ? 'active' : ''}`}
            >
                Parking
            </Link>
            <Link 
                to="/metro" 
                className={`nav-link ${location.pathname === '/metro' ? 'active' : ''}`}
            >
                Metro
            </Link>
            <Link 
                to="/priority" 
                className={`nav-link ${location.pathname === '/priority' ? 'active' : ''}`}
            >
                Priority Vehicles
            </Link>
            <Link 
                to="/analytics" 
                className={`nav-link ${location.pathname === '/analytics' ? 'active' : ''}`}
            >
                Analytics
            </Link>
        </nav>
    );
};

export default Navigation; 