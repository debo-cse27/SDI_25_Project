import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import pandas as pd

class AdvancedAnalyticsService:
    def __init__(self):
        self.anomaly_detector = DBSCAN(eps=0.3, min_samples=4)
        self.lstm_model = self._build_lstm_model()
        self.scaler = StandardScaler()

    def _build_lstm_model(self):
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(24, 5)),
            LSTM(32),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model

    def detect_anomalies(self, data):
        scaled_data = self.scaler.fit_transform(data)
        clusters = self.anomaly_detector.fit_predict(scaled_data)
        return clusters == -1  # True for anomalies

    def predict_peak_hours(self, historical_data):
        # Advanced peak hour prediction using LSTM
        sequence_data = self._prepare_sequences(historical_data)
        predictions = self.lstm_model.predict(sequence_data)
        return self._process_predictions(predictions)

    def analyze_patterns(self, data):
        return {
            'daily_patterns': self._analyze_daily_patterns(data),
            'weekly_patterns': self._analyze_weekly_patterns(data),
            'seasonal_trends': self._analyze_seasonal_trends(data),
            'correlations': self._analyze_correlations(data)
        }

    def generate_optimization_suggestions(self, analysis_results):
        suggestions = []
        if analysis_results['peak_load'] > threshold:
            suggestions.append({
                'type': 'capacity',
                'priority': 'high',
                'description': 'Increase system capacity during peak hours',
                'expected_impact': '+30% throughput'
            })
        return suggestions 