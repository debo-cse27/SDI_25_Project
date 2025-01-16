import React from 'react';
import './ErrorMessage.css';

const ErrorMessage = ({ message, onRetry }) => (
    <div className="error-container">
        <div className="error-icon">⚠️</div>
        <p className="error-text">{message}</p>
        {onRetry && (
            <button className="retry-button" onClick={onRetry}>
                Try Again
            </button>
        )}
    </div>
);

export default ErrorMessage; 