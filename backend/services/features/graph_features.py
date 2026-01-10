"""
Graph-Based Feature Extraction Module
Extracts ~10 graph metrics and social signature features from chat messages
"""
import numpy as np
from typing import List, Dict, Any
from collections import defaultdict


class GraphFeatureExtractor:
    """Extracts graph-based social signature features from chat messages."""
    
    def __init__(self):
        self.feature_names = [
            'node_degree',
            'weighted_degree',
            'reciprocity_score',
            'betweenness_centrality',
            'closeness_centrality',
            'clustering_coefficient',
            'dominance_asymmetry',
            'social_balance',
            'dyadic_symmetry',
            'interaction_density'
        ]
    
    def extract(self, messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract all graph features from messages."""
        if not messages:
            return {name: 0.0 for name in self.feature_names}
        
        graph = self._build_interaction_graph(messages)
        
        features = {}
        
        features['node_degree'] = self._compute_node_degree(graph)
        features['weighted_degree'] = self._compute_weighted_degree(graph)
        features['reciprocity_score'] = self._compute_reciprocity(graph)
        features['betweenness_centrality'] = self._compute_betweenness(graph)
        features['closeness_centrality'] = self._compute_closeness(graph)
        features['clustering_coefficient'] = self._compute_clustering(graph)
        features['dominance_asymmetry'] = self._compute_dominance_asymmetry(messages)
        features['social_balance'] = self._compute_social_balance(messages)
        features['dyadic_symmetry'] = self._compute_dyadic_symmetry(messages)
        features['interaction_density'] = self._compute_interaction_density(messages)
        
        return features
    
    def _build_interaction_graph(self, messages: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        """Build directed weighted graph from message interactions."""
        graph = defaultdict(lambda: defaultdict(int))
        
        for i in range(1, len(messages)):
            sender = messages[i].get('sender', 'unknown')
            prev_sender = messages[i-1].get('sender', 'unknown')
            
            if sender != prev_sender:
                graph[prev_sender][sender] += 1
        
        return dict(graph)
    
    def _compute_node_degree(self, graph: Dict[str, Dict[str, int]]) -> float:
        """Compute average node degree."""
        if not graph:
            return 0.0
        
        degrees = []
        all_nodes = set(graph.keys())
        for targets in graph.values():
            all_nodes.update(targets.keys())
        
        for node in all_nodes:
            out_degree = len(graph.get(node, {}))
            in_degree = sum(1 for src in graph if node in graph[src])
            degrees.append(out_degree + in_degree)
        
        return float(np.mean(degrees)) if degrees else 0.0
    
    def _compute_weighted_degree(self, graph: Dict[str, Dict[str, int]]) -> float:
        """Compute average weighted degree."""
        if not graph:
            return 0.0
        
        weighted_degrees = []
        all_nodes = set(graph.keys())
        for targets in graph.values():
            all_nodes.update(targets.keys())
        
        for node in all_nodes:
            out_weight = sum(graph.get(node, {}).values())
            in_weight = sum(graph[src].get(node, 0) for src in graph)
            weighted_degrees.append(out_weight + in_weight)
        
        return float(np.mean(weighted_degrees)) if weighted_degrees else 0.0
    
    def _compute_reciprocity(self, graph: Dict[str, Dict[str, int]]) -> float:
        """Compute reciprocity score."""
        if not graph:
            return 0.0
        
        reciprocal_edges = 0
        total_edges = 0
        
        for src, targets in graph.items():
            for tgt, weight in targets.items():
                total_edges += 1
                if tgt in graph and src in graph[tgt]:
                    reciprocal_edges += 1
        
        return reciprocal_edges / total_edges if total_edges > 0 else 0.0
    
    def _compute_betweenness(self, graph: Dict[str, Dict[str, int]]) -> float:
        """Compute simplified betweenness centrality for user node."""
        if not graph or 'user' not in graph:
            return 0.0
        
        all_nodes = set(graph.keys())
        for targets in graph.values():
            all_nodes.update(targets.keys())
        
        if len(all_nodes) <= 2:
            return 0.5
        
        user_connections = len(graph.get('user', {}))
        max_possible = len(all_nodes) - 1
        
        return user_connections / max_possible if max_possible > 0 else 0.0
    
    def _compute_closeness(self, graph: Dict[str, Dict[str, int]]) -> float:
        """Compute simplified closeness centrality for user node."""
        if not graph:
            return 0.0
        
        all_nodes = set(graph.keys())
        for targets in graph.values():
            all_nodes.update(targets.keys())
        
        if 'user' not in all_nodes:
            return 0.0
        
        reachable = set()
        queue = ['user']
        visited = {'user'}
        
        while queue:
            current = queue.pop(0)
            if current in graph:
                for neighbor in graph[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        reachable.add(neighbor)
                        queue.append(neighbor)
        
        return len(reachable) / (len(all_nodes) - 1) if len(all_nodes) > 1 else 0.0
    
    def _compute_clustering(self, graph: Dict[str, Dict[str, int]]) -> float:
        """Compute clustering coefficient."""
        if len(graph) < 2:
            return 0.0
        
        all_nodes = set(graph.keys())
        for targets in graph.values():
            all_nodes.update(targets.keys())
        
        if len(all_nodes) < 3:
            return 0.0
        
        triangles = 0
        possible_triangles = 0
        
        for node in all_nodes:
            neighbors = set()
            if node in graph:
                neighbors.update(graph[node].keys())
            for src in graph:
                if node in graph[src]:
                    neighbors.add(src)
            
            neighbors_list = list(neighbors)
            n = len(neighbors_list)
            
            if n >= 2:
                possible_triangles += n * (n - 1) / 2
                
                for i in range(n):
                    for j in range(i + 1, n):
                        n1, n2 = neighbors_list[i], neighbors_list[j]
                        if (n1 in graph and n2 in graph[n1]) or \
                           (n2 in graph and n1 in graph[n2]):
                            triangles += 1
        
        return triangles / possible_triangles if possible_triangles > 0 else 0.0
    
    def _compute_dominance_asymmetry(self, messages: List[Dict[str, Any]]) -> float:
        """Compute dominance asymmetry between user and bot."""
        user_words = sum(len(m.get('text', '').split()) 
                        for m in messages if m.get('sender') == 'user')
        bot_words = sum(len(m.get('text', '').split()) 
                       for m in messages if m.get('sender') == 'bot')
        
        total = user_words + bot_words
        if total == 0:
            return 0.0
        
        return abs(user_words - bot_words) / total
    
    def _compute_social_balance(self, messages: List[Dict[str, Any]]) -> float:
        """Compute social balance (turn-taking equality)."""
        user_count = sum(1 for m in messages if m.get('sender') == 'user')
        bot_count = len(messages) - user_count
        
        total = user_count + bot_count
        if total == 0:
            return 0.0
        
        return 1.0 - abs(user_count - bot_count) / total
    
    def _compute_dyadic_symmetry(self, messages: List[Dict[str, Any]]) -> float:
        """Compute dyadic symmetry (response pattern similarity)."""
        if len(messages) < 4:
            return 0.5
        
        user_response_lengths = []
        bot_response_lengths = []
        
        for i in range(1, len(messages)):
            msg = messages[i]
            prev_msg = messages[i-1]
            
            if msg.get('sender') != prev_msg.get('sender'):
                length = len(msg.get('text', '').split())
                if msg.get('sender') == 'user':
                    user_response_lengths.append(length)
                else:
                    bot_response_lengths.append(length)
        
        if not user_response_lengths or not bot_response_lengths:
            return 0.5
        
        user_mean = np.mean(user_response_lengths)
        bot_mean = np.mean(bot_response_lengths)
        
        max_mean = max(user_mean, bot_mean)
        if max_mean == 0:
            return 1.0
        
        return 1.0 - abs(user_mean - bot_mean) / max_mean
    
    def _compute_interaction_density(self, messages: List[Dict[str, Any]]) -> float:
        """Compute interaction density (messages per time unit)."""
        if len(messages) < 2:
            return 0.0
        
        timestamps = []
        for msg in messages:
            ts = msg.get('timestamp', 0)
            if isinstance(ts, (int, float)) and ts > 0:
                timestamps.append(ts)
        
        if len(timestamps) < 2:
            return 0.0
        
        duration = max(timestamps) - min(timestamps)
        if duration <= 0:
            return 0.0
        
        messages_per_minute = len(messages) / (duration / 60)
        return min(1.0, messages_per_minute / 10)
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names."""
        return self.feature_names.copy()
