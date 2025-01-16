import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import './TrafficPrediction.css';

const TrafficPrediction = () => {
    const [predictions, setPredictions] = useState({
        shortTerm: [], // Next 1 hour
        longTerm: [],  // Next 24 hours
        accuracy: 0
    });

    useEffect(() => {
        fetchPredictions();
        const interval = setInterval(fetchPredictions, 300000); // Update every 5 minutes

        return () => clearInterval(interval);
    }, []);

    const fetchPredictions = async () => {
        try {
            const response = await fetch('/api/traffic/predictions');
            const data = await response.json();
            setPredictions(data);
        } catch (error) {
            console.error('Error fetching predictions:', error);
        }
    };

    const getPredictionChartData = () => ({
        labels: predictions.shortTerm.map(p => p.time),
        datasets: [
            {
                label: 'Predicted Traffic Volume',
                data: predictions.shortTerm.map(p => p.volume),
                borderColor: '#4CAF50',
                fill: false
            },
            {
                label: 'Confidence Interval',
                data: predictions.shortTerm.map(p => p.confidence),
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                borderColor: 'transparent',
                fill: true
            }
        ]
    });

    return (
        <div className="traffic-prediction">
            <div className="prediction-header">
                <h3>Traffic Predictions</h3>
                <div className="accuracy-indicator">
                    <span>Model Accuracy:</span>
                    <div className="accuracy-value">{predictions.accuracy}%</div>
                </div>
            </div>

            <div className="prediction-content">
                <div className="chart-container">
                    <Line 
                        data={getPredictionChartData()}
                        options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                tooltip: {
                                    callbacks: {
                                        label: (context) => {
                                            const value = context.raw;
                                            return `Predicted Volume: ${value} vehicles/hour`;
                                        }
                                    }
                                }
                            }
                        }}
                    />
                </div>

                <div className="prediction-insights">
                    <h4>Traffic Insights</h4>
                    <div className="insights-grid">
                        {predictions.shortTerm.slice(0, 4).map((prediction, index) => (
                            <div key={index} className="insight-card">
                                <div className="time">{prediction.time}</div>
                                <div className="prediction-value">
                                    {prediction.volume} vehicles/hour
                                </div>
                                <div className="trend-indicator" data-trend={prediction.trend}>
                                    {prediction.trend === 'up' ? '↑' : '↓'}
                                    {prediction.trendValue}%
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TrafficPrediction; 