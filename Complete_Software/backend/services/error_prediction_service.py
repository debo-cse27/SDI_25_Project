import numpy as np
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import pandas as pd

class ErrorPredictionService:
    def __init__(self):
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.sequence_model = self._build_sequence_model()
        self.error_patterns = self._load_error_patterns()
        self.prediction_threshold = 0.75

    def _build_sequence_model(self):
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(100, 10)),
            Dropout(0.2),
            LSTM(32),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    async def predict_potential_errors(self, metrics_stream):
        try:
            # Process real-time metrics
            processed_data = self._preprocess_metrics(metrics_stream)
            
            # Detect anomalies
            anomalies = self.anomaly_detector.predict(processed_data)
            
            # Predict sequence-based errors
            sequence_predictions = self.sequence_model.predict(processed_data)
            
            # Combine predictions
            predictions = self._combine_predictions(anomalies, sequence_predictions)
            
            return self._generate_error_warnings(predictions)
        except Exception as e:
            logger.error(f"Error in error prediction: {str(e)}")
            return []

    def _generate_error_warnings(self, predictions):
        warnings = []
        for pred in predictions:
            if pred['probability'] > self.prediction_threshold:
                warnings.append({
                    'type': pred['error_type'],
                    'probability': pred['probability'],
                    'estimated_time': pred['time_to_error'],
                    'affected_components': pred['components'],
                    'suggested_actions': self._get_mitigation_steps(pred)
                })
        return warnings 