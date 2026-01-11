"""
Visualization Service Module
Generates graph structures and visualization data for frontend rendering
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import hashlib


class VisualizationService:
    """Service for generating visualization data structures."""
    
    def __init__(self):
        self.color_palette = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
        ]
    
    def generate_cluster_graph(self,
                               vectors: List[List[float]],
                               labels: List[int],
                               reduced: List[List[float]],
                               metadata: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate graph structure for cluster visualization.
        
        Args:
            vectors: Original feature vectors
            labels: Cluster labels
            reduced: Reduced dimension coordinates
            metadata: Optional metadata for each node
            
        Returns:
            Graph structure with nodes and edges
        """
        if not vectors or not labels or not reduced:
            return {'nodes': [], 'edges': []}
        
        nodes = self._create_nodes(vectors, labels, reduced, metadata)
        edges = self._create_edges(vectors, labels)
        
        return {
            'nodes': nodes,
            'edges': edges,
            'clusters': self._get_cluster_info(labels),
            'bounds': self._get_bounds(reduced)
        }
    
    def _create_nodes(self,
                     vectors: List[List[float]],
                     labels: List[int],
                     reduced: List[List[float]],
                     metadata: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Create node objects for graph."""
        nodes = []
        
        for i, (vector, label, pos) in enumerate(zip(vectors, labels, reduced)):
            node_id = f"node_{i}"
            
            node = {
                'id': node_id,
                'x': float(pos[0]) if len(pos) > 0 else 0.0,
                'y': float(pos[1]) if len(pos) > 1 else 0.0,
                'cluster': int(label),
                'color': self.color_palette[int(label) % len(self.color_palette)],
                'size': self._compute_node_size(vector),
                'vector_summary': self._summarize_vector(vector)
            }
            
            if metadata and i < len(metadata):
                node['metadata'] = metadata[i]
            
            nodes.append(node)
        
        return nodes
    
    def _create_edges(self,
                     vectors: List[List[float]],
                     labels: List[int],
                     similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Create edge objects based on vector similarity."""
        edges = []
        n = len(vectors)
        
        if n < 2:
            return edges
        
        arr = np.array(vectors)
        
        for i in range(n):
            for j in range(i + 1, n):
                similarity = self._cosine_similarity(arr[i], arr[j])
                
                if similarity > similarity_threshold:
                    edge = {
                        'id': f"edge_{i}_{j}",
                        'source': f"node_{i}",
                        'target': f"node_{j}",
                        'weight': float(similarity),
                        'same_cluster': labels[i] == labels[j]
                    }
                    edges.append(edge)
        
        return edges
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def _compute_node_size(self, vector: List[float], min_size: float = 5, max_size: float = 20) -> float:
        """Compute node size based on vector magnitude."""
        magnitude = np.linalg.norm(vector)
        size = min_size + (magnitude / (magnitude + 1)) * (max_size - min_size)
        return float(size)
    
    def _summarize_vector(self, vector: List[float], top_k: int = 5) -> Dict[str, float]:
        """Create summary of vector with top features."""
        arr = np.array(vector)
        top_indices = np.argsort(np.abs(arr))[-top_k:][::-1]
        
        return {
            'mean': float(np.mean(arr)),
            'std': float(np.std(arr)),
            'max': float(np.max(arr)),
            'min': float(np.min(arr)),
            'top_indices': top_indices.tolist()
        }
    
    def _get_cluster_info(self, labels: List[int]) -> List[Dict[str, Any]]:
        """Get information about each cluster."""
        unique_labels = sorted(set(labels))
        
        cluster_info = []
        for label in unique_labels:
            count = sum(1 for l in labels if l == label)
            cluster_info.append({
                'id': int(label),
                'count': count,
                'color': self.color_palette[int(label) % len(self.color_palette)]
            })
        
        return cluster_info
    
    def _get_bounds(self, reduced: List[List[float]]) -> Dict[str, float]:
        """Get bounding box for reduced coordinates."""
        if not reduced:
            return {'min_x': 0, 'max_x': 1, 'min_y': 0, 'max_y': 1}
        
        arr = np.array(reduced)
        
        return {
            'min_x': float(np.min(arr[:, 0])),
            'max_x': float(np.max(arr[:, 0])),
            'min_y': float(np.min(arr[:, 1])) if arr.shape[1] > 1 else 0.0,
            'max_y': float(np.max(arr[:, 1])) if arr.shape[1] > 1 else 1.0
        }
    
    def generate_feature_heatmap(self,
                                 features: Dict[str, float],
                                 categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate heatmap data for feature visualization."""
        if not features:
            return {'data': [], 'labels': [], 'values': []}
        
        if categories:
            grouped = {}
            for key, value in features.items():
                for cat in categories:
                    if key.startswith(cat):
                        if cat not in grouped:
                            grouped[cat] = {}
                        grouped[cat][key] = value
                        break
            
            data = []
            for cat, cat_features in grouped.items():
                row = {
                    'category': cat,
                    'features': list(cat_features.keys()),
                    'values': list(cat_features.values())
                }
                data.append(row)
            
            return {'data': data, 'grouped': True}
        
        return {
            'labels': list(features.keys()),
            'values': list(features.values()),
            'grouped': False
        }
    
    def generate_radar_chart_data(self,
                                  category_scores: Dict[str, float]) -> Dict[str, Any]:
        """Generate radar chart data for category scores."""
        labels = list(category_scores.keys())
        values = list(category_scores.values())
        
        max_val = max(values) if values else 1
        normalized = [v / max_val for v in values] if max_val > 0 else values
        
        return {
            'labels': labels,
            'values': values,
            'normalized': normalized,
            'max_value': max_val
        }
    
    def generate_timeline_data(self,
                               messages: List[Dict[str, Any]],
                               sentiments: List[float]) -> Dict[str, Any]:
        """Generate timeline data for sentiment visualization."""
        if not messages or not sentiments:
            return {'points': [], 'trend': []}
        
        points = []
        for i, (msg, sentiment) in enumerate(zip(messages, sentiments)):
            point = {
                'index': i,
                'timestamp': msg.get('timestamp', i),
                'sentiment': float(sentiment),
                'sender': msg.get('sender', 'unknown')
            }
            points.append(point)
        
        window_size = min(5, len(sentiments))
        trend = []
        for i in range(len(sentiments)):
            start = max(0, i - window_size + 1)
            window = sentiments[start:i+1]
            trend.append(float(np.mean(window)))
        
        return {
            'points': points,
            'trend': trend
        }
    
    def generate_comparison_data(self,
                                 vector1: List[float],
                                 vector2: List[float],
                                 labels: List[str]) -> Dict[str, Any]:
        """Generate comparison data for two vectors."""
        if len(vector1) != len(vector2) or len(vector1) != len(labels):
            return {'error': 'Vector length mismatch'}
        
        differences = [v1 - v2 for v1, v2 in zip(vector1, vector2)]
        
        return {
            'labels': labels,
            'vector1': vector1,
            'vector2': vector2,
            'differences': differences,
            'similarity': self._cosine_similarity(np.array(vector1), np.array(vector2))
        }
    
    def generate_distribution_data(self,
                                   vectors: List[List[float]],
                                   feature_index: int = 0) -> Dict[str, Any]:
        """Generate distribution data for a specific feature."""
        if not vectors:
            return {'histogram': [], 'stats': {}}
        
        arr = np.array(vectors)
        if feature_index >= arr.shape[1]:
            return {'histogram': [], 'stats': {}}
        
        values = arr[:, feature_index]
        
        hist, bin_edges = np.histogram(values, bins=20)
        
        histogram = []
        for i in range(len(hist)):
            histogram.append({
                'bin_start': float(bin_edges[i]),
                'bin_end': float(bin_edges[i+1]),
                'count': int(hist[i])
            })
        
        stats = {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'median': float(np.median(values))
        }
        
        return {
            'histogram': histogram,
            'stats': stats,
            'feature_index': feature_index
        }
    
    def normalize_coordinates(self,
                             reduced: List[List[float]],
                             target_range: Tuple = (0, 100)) -> List[List[float]]:
        """Normalize reduced coordinates to target range."""
        if not reduced:
            return []
        
        arr = np.array(reduced)
        min_vals = np.min(arr, axis=0)
        max_vals = np.max(arr, axis=0)
        
        range_vals = max_vals - min_vals
        range_vals = np.where(range_vals == 0, 1, range_vals)
        
        normalized = (arr - min_vals) / range_vals
        scaled = normalized * (target_range[1] - target_range[0]) + target_range[0]
        
        return scaled.tolist()


from typing import Tuple
