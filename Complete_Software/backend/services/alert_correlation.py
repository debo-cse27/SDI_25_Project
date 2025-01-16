import networkx as nx
from collections import defaultdict
import numpy as np
from datetime import datetime, timedelta

class AlertCorrelationEngine:
    def __init__(self):
        self.alert_graph = nx.DiGraph()
        self.correlation_rules = self._load_correlation_rules()
        self.causality_model = self._initialize_causality_model()
        self.time_window = timedelta(minutes=15)

    async def correlate_alerts(self, new_alert):
        try:
            # Find related alerts within time window
            related_alerts = self._find_related_alerts(new_alert)
            
            # Build causality chain
            causality_chain = self._build_causality_chain(related_alerts)
            
            # Identify root cause
            root_cause = self._identify_root_cause(causality_chain)
            
            # Generate correlation insights
            correlation_insights = self._generate_correlation_insights(
                root_cause, 
                causality_chain
            )

            return {
                'root_cause': root_cause,
                'related_alerts': related_alerts,
                'causality_chain': causality_chain,
                'correlation_score': self._calculate_correlation_score(causality_chain),
                'recommended_actions': self._generate_recommendations(root_cause)
            }
        except Exception as e:
            logger.error(f"Alert correlation error: {str(e)}")
            return None

    def _build_causality_chain(self, alerts):
        graph = nx.DiGraph()
        for alert in alerts:
            self._add_alert_to_graph(graph, alert)
        
        # Apply causality rules
        for rule in self.correlation_rules:
            self._apply_correlation_rule(graph, rule)
            
        return self._extract_causality_paths(graph)

    def _identify_root_cause(self, causality_chain):
        # Find the most probable root cause using graph analysis
        if not causality_chain:
            return None
            
        # Calculate centrality measures
        centrality = nx.pagerank(self.alert_graph)
        root_nodes = [node for node in causality_chain 
                     if causality_chain.in_degree(node) == 0]
        
        # Return node with highest centrality
        return max(root_nodes, key=lambda x: centrality[x]) 