import React, { useState, useEffect } from 'react';
import './OptimizationRecommendations.css';

const OptimizationRecommendations = () => {
    const [recommendations, setRecommendations] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('all');

    useEffect(() => {
        fetchRecommendations();
        const interval = setInterval(fetchRecommendations, 300000); // Update every 5 minutes

        return () => clearInterval(interval);
    }, []);

    const fetchRecommendations = async () => {
        try {
            const response = await fetch('/api/system/optimization-recommendations');
            const data = await response.json();
            setRecommendations(data);
        } catch (error) {
            console.error('Error fetching recommendations:', error);
        }
    };

    const getFilteredRecommendations = () => {
        if (selectedCategory === 'all') return recommendations;
        return recommendations.filter(rec => rec.category === selectedCategory);
    };

    const getPriorityClass = (priority) => {
        switch (priority) {
            case 'high': return 'priority-high';
            case 'medium': return 'priority-medium';
            case 'low': return 'priority-low';
            default: return '';
        }
    };

    const implementRecommendation = async (id) => {
        try {
            await fetch(`/api/system/implement-recommendation/${id}`, {
                method: 'POST'
            });
            fetchRecommendations(); // Refresh the list
        } catch (error) {
            console.error('Error implementing recommendation:', error);
        }
    };

    return (
        <div className="optimization-recommendations">
            <div className="recommendations-header">
                <h2>Performance Optimization Recommendations</h2>
                <div className="category-filter">
                    <select 
                        value={selectedCategory}
                        onChange={(e) => setSelectedCategory(e.target.value)}
                    >
                        <option value="all">All Categories</option>
                        <option value="cpu">CPU</option>
                        <option value="memory">Memory</option>
                        <option value="disk">Disk</option>
                        <option value="network">Network</option>
                        <option value="database">Database</option>
                    </select>
                </div>
            </div>

            <div className="recommendations-list">
                {getFilteredRecommendations().map(rec => (
                    <div key={rec.id} className={`recommendation-card ${getPriorityClass(rec.priority)}`}>
                        <div className="recommendation-header">
                            <span className="recommendation-category">{rec.category}</span>
                            <span className={`priority-badge ${getPriorityClass(rec.priority)}`}>
                                {rec.priority} Priority
                            </span>
                        </div>

                        <div className="recommendation-content">
                            <h3>{rec.title}</h3>
                            <p className="description">{rec.description}</p>
                            
                            {rec.metrics && (
                                <div className="impact-metrics">
                                    <h4>Expected Impact</h4>
                                    <div className="metrics-grid">
                                        {Object.entries(rec.metrics).map(([key, value]) => (
                                            <div key={key} className="metric-item">
                                                <span className="metric-label">{key}</span>
                                                <span className="metric-value">{value}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <div className="implementation-details">
                                <h4>Implementation</h4>
                                <p>{rec.implementation}</p>
                                {rec.risks && (
                                    <div className="risks">
                                        <strong>Potential Risks:</strong>
                                        <p>{rec.risks}</p>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="recommendation-actions">
                            <button 
                                className="implement-btn"
                                onClick={() => implementRecommendation(rec.id)}
                                disabled={rec.status === 'implemented'}
                            >
                                {rec.status === 'implemented' ? 'Implemented' : 'Implement'}
                            </button>
                            <button className="details-btn">View Details</button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default OptimizationRecommendations; 