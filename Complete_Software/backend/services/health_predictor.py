import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

class SystemHealthPredictor:
    def __init__(self):
        self.short_term_model = self._build_short_term_model()
        self.long_term_model = self._build_long_term_model()
        self.health_metrics = self._initialize_health_metrics()
        self.prediction_thresholds = self._load_prediction_thresholds()

    def _build_short_term_model(self):
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=(60, 20)),
            Dropout(0.2),
            LSTM(64),
            Dense(32, activation='relu'),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy')
        return model

    async def predict_system_health(self, current_metrics, prediction_window='1h'):
        try:
            # Generate predictions
            short_term = await self._predict_short_term(current_metrics)
            long_term = await self._predict_long_term(current_metrics)
            
            # Analyze potential issues
            potential_issues = self._analyze_potential_issues(
                short_term, 
                long_term
            )
            
            # Generate health score
            health_score = self._calculate_health_score(
                current_metrics,
                short_term,
                long_term
            )

            return {
                'current_health_score': health_score,
                'short_term_predictions': short_term,
                'long_term_predictions': long_term,
                'potential_issues': potential_issues,
                'recommendations': self._generate_health_recommendations(
                    health_score,
                    potential_issues
                )
            }
        except Exception as e:
            logger.error(f"Health prediction error: {str(e)}")
            return None

    def _analyze_potential_issues(self, short_term, long_term):
        issues = []
        
        # Analyze trends
        for metric, predictions in short_term.items():
            if self._is_concerning_trend(predictions):
                issues.append({
                    'metric': metric,
                    'severity': self._calculate_severity(predictions),
                    'time_to_critical': self._estimate_time_to_critical(predictions),
                    'recommended_actions': self._get_mitigation_actions(metric, predictions)
                })
                
        return self._prioritize_issues(issues) 