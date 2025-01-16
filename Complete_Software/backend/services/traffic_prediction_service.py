import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from models.db import db
from utils.logger import system_logger

class TrafficPredictionService:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)
        self.last_training = None
        self.accuracy = 0
        self.training_interval = timedelta(hours=24)
        self.initialize_model()

    def initialize_model(self):
        try:
            historical_data = self.get_historical_data()
            if historical_data:
                self.train_model(historical_data)
        except Exception as e:
            system_logger.error(f"Error initializing traffic prediction model: {str(e)}")

    def get_historical_data(self):
        # Fetch last 30 days of traffic data
        query = """
            SELECT timestamp, volume, weather, day_of_week, hour
            FROM traffic_data
            WHERE timestamp >= NOW() - INTERVAL '30 days'
            ORDER BY timestamp ASC
        """
        return db.execute_query(query)

    def train_model(self, data):
        try:
            X = self.prepare_features(data)
            y = [row['volume'] for row in data]
            
            self.model.fit(X, y)
            self.last_training = datetime.now()
            self.accuracy = self.calculate_accuracy(X, y)
            
            system_logger.info(f"Traffic prediction model trained. Accuracy: {self.accuracy}%")
        except Exception as e:
            system_logger.error(f"Error training traffic prediction model: {str(e)}")

    def prepare_features(self, data):
        features = []
        for row in data:
            feature_vector = [
                row['day_of_week'],
                row['hour'],
                row['weather'],
                self.get_is_holiday(row['timestamp']),
                self.get_is_rush_hour(row['hour'])
            ]
            features.append(feature_vector)
        return features

    def get_predictions(self, hours_ahead=24):
        try:
            current_time = datetime.now()
            predictions = []
            
            for hour in range(hours_ahead):
                future_time = current_time + timedelta(hours=hour)
                features = self.prepare_prediction_features(future_time)
                volume = self.model.predict([features])[0]
                confidence = self.calculate_confidence_interval(features)
                
                predictions.append({
                    'time': future_time.strftime('%H:%M'),
                    'volume': int(volume),
                    'confidence': confidence,
                    'trend': self.calculate_trend(volume, hour > 0 and predictions[-1]['volume']),
                    'trendValue': self.calculate_trend_value(volume, hour > 0 and predictions[-1]['volume'])
                })
            
            return {
                'shortTerm': predictions[:6],  # Next 6 hours
                'longTerm': predictions[6:],   # Beyond 6 hours
                'accuracy': round(self.accuracy, 1)
            }
        except Exception as e:
            system_logger.error(f"Error generating traffic predictions: {str(e)}")
            return None

    def calculate_confidence_interval(self, features):
        # Implement confidence interval calculation
        # This is a simplified version
        predictions = []
        for _ in range(10):
            predictions.append(self.model.predict([features])[0])
        return {
            'lower': int(np.percentile(predictions, 25)),
            'upper': int(np.percentile(predictions, 75))
        }

    def calculate_trend(self, current, previous):
        if not previous:
            return 'stable'
        return 'up' if current > previous else 'down'

    def calculate_trend_value(self, current, previous):
        if not previous:
            return 0
        return round(((current - previous) / previous) * 100, 1)

    @staticmethod
    def get_is_holiday(timestamp):
        # Implement holiday detection
        # This is a placeholder
        return 0

    @staticmethod
    def get_is_rush_hour(hour):
        return 1 if hour in [8, 9, 16, 17, 18] else 0

traffic_prediction_service = TrafficPredictionService() 