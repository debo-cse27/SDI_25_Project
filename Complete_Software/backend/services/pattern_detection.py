from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import numpy as np

class PatternDetectionEngine:
    def __init__(self):
        self.sequence_model = self._build_sequence_model()
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.pattern_registry = {}
        self.confidence_threshold = 0.85

    def _build_sequence_model(self):
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(100, 10)),
            LSTM(32),
            Dense(16, activation='relu'),
            Dense(8, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy')
        return model

    async def detect_patterns(self, metrics_stream):
        try:
            # Preprocess metrics
            processed_data = self._preprocess_metrics(metrics_stream)
            
            # Detect known patterns
            known_patterns = self._detect_known_patterns(processed_data)
            
            # Discover new patterns
            new_patterns = self._discover_new_patterns(processed_data)
            
            # Validate patterns
            validated_patterns = self._validate_patterns(known_patterns + new_patterns)
            
            return {
                'detected_patterns': validated_patterns,
                'pattern_metrics': self._calculate_pattern_metrics(validated_patterns),
                'recommendations': self._generate_pattern_based_recommendations(validated_patterns)
            }
        except Exception as e:
            logger.error(f"Pattern detection error: {str(e)}")
            return None

    def _discover_new_patterns(self, data):
        # Use LSTM for sequence pattern discovery
        sequences = self._extract_sequences(data)
        predictions = self.sequence_model.predict(sequences)
        
        # Identify significant patterns
        patterns = []
        for i, pred in enumerate(predictions):
            if pred > self.confidence_threshold:
                pattern = self._extract_pattern_features(sequences[i])
                patterns.append(pattern)
                
        return self._cluster_similar_patterns(patterns) 