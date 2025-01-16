import numpy as np
from scipy import stats
import networkx as nx
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

class MetricCorrelator:
    def __init__(self):
        self.correlation_graph = nx.Graph()
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)
        self.correlation_threshold = 0.7

    async def analyze_correlations(self, metrics_data):
        try:
            # Preprocess metrics
            processed_data = self._preprocess_metrics(metrics_data)
            
            # Calculate correlations
            correlations = self._calculate_correlations(processed_data)
            
            # Build correlation graph
            self._build_correlation_graph(correlations)
            
            # Find significant patterns
            patterns = self._find_correlation_patterns()
            
            # Generate insights
            insights = self._generate_correlation_insights(patterns)
            
            return {
                'correlation_matrix': correlations,
                'significant_patterns': patterns,
                'insights': insights,
                'recommendations': self._generate_recommendations(patterns)
            }
        except Exception as e:
            logger.error(f"Correlation analysis error: {str(e)}")
            return None

    def _calculate_correlations(self, data):
        # Calculate Pearson correlation
        pearson_corr = np.corrcoef(data.T)
        
        # Calculate Spearman correlation for non-linear relationships
        spearman_corr = stats.spearmanr(data)[0]
        
        # Combine correlations
        return self._combine_correlations(pearson_corr, spearman_corr) 