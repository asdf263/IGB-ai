"""
Semantic Feature Extraction Module
Extracts ~25 semantic embedding and topic features from chat messages
"""
import numpy as np
from typing import List, Dict, Any, Optional
import hashlib


class SemanticFeatureExtractor:
    """Extracts semantic embedding features from chat messages."""
    
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.model = None
        self._init_model()
        
        self.feature_names = [
            'embedding_mean_norm',
            'embedding_std_norm',
            'embedding_min_component',
            'embedding_max_component',
            'embedding_sparsity',
            'cosine_sim_mean',
            'cosine_sim_std',
            'cosine_sim_min',
            'cosine_sim_max',
            'semantic_drift_rate',
            'semantic_coherence',
            'topic_concentration',
            'topic_diversity',
            'semantic_novelty_mean',
            'semantic_novelty_std',
            'centroid_distance_mean',
            'centroid_distance_std',
            'pairwise_sim_entropy',
            'embedding_cluster_count',
            'semantic_stability',
            'content_density',
            'abstraction_level',
            'specificity_score',
            'semantic_momentum',
            'topic_switch_count'
        ]
    
    def _init_model(self):
        """Initialize sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_dim = 384
        except ImportError:
            self.model = None
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a single text."""
        if self.model is not None:
            return self.model.encode(text, convert_to_numpy=True)
        else:
            return self._deterministic_embedding(text)
    
    def _deterministic_embedding(self, text: str) -> np.ndarray:
        """Generate deterministic pseudo-embedding when model unavailable."""
        hash_bytes = hashlib.sha512(text.encode()).digest()
        extended = hash_bytes * (self.embedding_dim // len(hash_bytes) + 1)
        values = np.array([b / 255.0 for b in extended[:self.embedding_dim]])
        values = (values - 0.5) * 2
        norm = np.linalg.norm(values)
        if norm > 0:
            values = values / norm
        return values
    
    def extract(self, messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract all semantic features from messages."""
        if not messages:
            return {name: 0.0 for name in self.feature_names}
        
        texts = [msg.get('text', '') for msg in messages if msg.get('text')]
        if not texts:
            return {name: 0.0 for name in self.feature_names}
        
        embeddings = np.array([self._get_embedding(t) for t in texts])
        
        features = {}
        
        # Embedding statistics
        norms = np.linalg.norm(embeddings, axis=1)
        features['embedding_mean_norm'] = float(np.mean(norms))
        features['embedding_std_norm'] = float(np.std(norms))
        features['embedding_min_component'] = float(np.min(embeddings))
        features['embedding_max_component'] = float(np.max(embeddings))
        features['embedding_sparsity'] = float(np.mean(np.abs(embeddings) < 0.01))
        
        # Cosine similarity features
        sim_features = self._compute_similarity_features(embeddings)
        features.update(sim_features)
        
        # Semantic drift and coherence
        drift_features = self._compute_drift_features(embeddings)
        features.update(drift_features)
        
        # Topic features
        topic_features = self._compute_topic_features(embeddings)
        features.update(topic_features)
        
        # Novelty features
        novelty_features = self._compute_novelty_features(embeddings)
        features.update(novelty_features)
        
        # Centroid features
        centroid_features = self._compute_centroid_features(embeddings)
        features.update(centroid_features)
        
        # Additional semantic features
        features['content_density'] = self._compute_content_density(embeddings)
        features['abstraction_level'] = self._compute_abstraction_level(texts)
        features['specificity_score'] = self._compute_specificity(embeddings)
        features['semantic_momentum'] = self._compute_semantic_momentum(embeddings)
        features['topic_switch_count'] = self._count_topic_switches(embeddings)
        
        return features
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def _compute_similarity_features(self, embeddings: np.ndarray) -> Dict[str, float]:
        """Compute pairwise cosine similarity features."""
        n = len(embeddings)
        if n < 2:
            return {
                'cosine_sim_mean': 1.0,
                'cosine_sim_std': 0.0,
                'cosine_sim_min': 1.0,
                'cosine_sim_max': 1.0,
                'pairwise_sim_entropy': 0.0
            }
        
        similarities = []
        for i in range(n):
            for j in range(i + 1, n):
                sim = self._cosine_similarity(embeddings[i], embeddings[j])
                similarities.append(sim)
        
        similarities = np.array(similarities)
        
        hist, _ = np.histogram(similarities, bins=10, range=(-1, 1), density=True)
        hist = hist / (hist.sum() + 1e-10)
        entropy = -np.sum(hist * np.log(hist + 1e-10))
        
        return {
            'cosine_sim_mean': float(np.mean(similarities)),
            'cosine_sim_std': float(np.std(similarities)),
            'cosine_sim_min': float(np.min(similarities)),
            'cosine_sim_max': float(np.max(similarities)),
            'pairwise_sim_entropy': float(entropy)
        }
    
    def _compute_drift_features(self, embeddings: np.ndarray) -> Dict[str, float]:
        """Compute semantic drift over time."""
        n = len(embeddings)
        if n < 2:
            return {
                'semantic_drift_rate': 0.0,
                'semantic_coherence': 1.0,
                'semantic_stability': 1.0
            }
        
        consecutive_sims = []
        for i in range(n - 1):
            sim = self._cosine_similarity(embeddings[i], embeddings[i + 1])
            consecutive_sims.append(sim)
        
        drift_rate = 1.0 - np.mean(consecutive_sims)
        coherence = np.mean(consecutive_sims)
        stability = 1.0 - np.std(consecutive_sims)
        
        return {
            'semantic_drift_rate': float(drift_rate),
            'semantic_coherence': float(coherence),
            'semantic_stability': float(stability)
        }
    
    def _compute_topic_features(self, embeddings: np.ndarray) -> Dict[str, float]:
        """Compute topic-related features."""
        n = len(embeddings)
        if n < 2:
            return {
                'topic_concentration': 1.0,
                'topic_diversity': 0.0,
                'embedding_cluster_count': 1.0
            }
        
        centroid = np.mean(embeddings, axis=0)
        distances = [np.linalg.norm(e - centroid) for e in embeddings]
        
        concentration = 1.0 / (1.0 + np.mean(distances))
        diversity = np.std(distances)
        
        cluster_count = self._estimate_cluster_count(embeddings)
        
        return {
            'topic_concentration': float(concentration),
            'topic_diversity': float(diversity),
            'embedding_cluster_count': float(cluster_count)
        }
    
    def _estimate_cluster_count(self, embeddings: np.ndarray, threshold: float = 0.7) -> int:
        """Estimate number of topic clusters using simple greedy clustering."""
        n = len(embeddings)
        if n < 2:
            return 1
        
        assigned = [False] * n
        clusters = 0
        
        for i in range(n):
            if assigned[i]:
                continue
            clusters += 1
            assigned[i] = True
            for j in range(i + 1, n):
                if not assigned[j]:
                    sim = self._cosine_similarity(embeddings[i], embeddings[j])
                    if sim > threshold:
                        assigned[j] = True
        
        return clusters
    
    def _compute_novelty_features(self, embeddings: np.ndarray) -> Dict[str, float]:
        """Compute semantic novelty features."""
        n = len(embeddings)
        if n < 2:
            return {
                'semantic_novelty_mean': 0.0,
                'semantic_novelty_std': 0.0
            }
        
        novelties = []
        for i in range(1, n):
            prev_centroid = np.mean(embeddings[:i], axis=0)
            novelty = 1.0 - self._cosine_similarity(embeddings[i], prev_centroid)
            novelties.append(novelty)
        
        return {
            'semantic_novelty_mean': float(np.mean(novelties)),
            'semantic_novelty_std': float(np.std(novelties))
        }
    
    def _compute_centroid_features(self, embeddings: np.ndarray) -> Dict[str, float]:
        """Compute centroid distance features."""
        centroid = np.mean(embeddings, axis=0)
        distances = [np.linalg.norm(e - centroid) for e in embeddings]
        
        return {
            'centroid_distance_mean': float(np.mean(distances)),
            'centroid_distance_std': float(np.std(distances))
        }
    
    def _compute_content_density(self, embeddings: np.ndarray) -> float:
        """Compute content density (how packed the semantic space is)."""
        n = len(embeddings)
        if n < 2:
            return 0.0
        
        centroid = np.mean(embeddings, axis=0)
        avg_dist = np.mean([np.linalg.norm(e - centroid) for e in embeddings])
        return float(1.0 / (1.0 + avg_dist))
    
    def _compute_abstraction_level(self, texts: List[str]) -> float:
        """Estimate abstraction level based on text characteristics."""
        abstract_words = {'concept', 'idea', 'theory', 'principle', 'abstract', 'general',
                         'overall', 'fundamental', 'essential', 'philosophical', 'theoretical'}
        concrete_words = {'specific', 'example', 'instance', 'particular', 'detail', 'exact',
                         'precise', 'actual', 'real', 'physical', 'tangible', 'practical'}
        
        all_text = ' '.join(texts).lower()
        words = all_text.split()
        
        abstract_count = sum(1 for w in words if w in abstract_words)
        concrete_count = sum(1 for w in words if w in concrete_words)
        
        total = abstract_count + concrete_count
        if total == 0:
            return 0.5
        
        return float(abstract_count / total)
    
    def _compute_specificity(self, embeddings: np.ndarray) -> float:
        """Compute specificity score based on embedding variance."""
        variance = np.var(embeddings)
        return float(1.0 / (1.0 + variance))
    
    def _compute_semantic_momentum(self, embeddings: np.ndarray) -> float:
        """Compute semantic momentum (consistency of direction change)."""
        n = len(embeddings)
        if n < 3:
            return 0.0
        
        directions = []
        for i in range(n - 1):
            diff = embeddings[i + 1] - embeddings[i]
            norm = np.linalg.norm(diff)
            if norm > 0:
                directions.append(diff / norm)
        
        if len(directions) < 2:
            return 0.0
        
        momentum_scores = []
        for i in range(len(directions) - 1):
            sim = self._cosine_similarity(directions[i], directions[i + 1])
            momentum_scores.append(sim)
        
        return float(np.mean(momentum_scores))
    
    def _count_topic_switches(self, embeddings: np.ndarray, threshold: float = 0.5) -> float:
        """Count number of topic switches based on similarity drops."""
        n = len(embeddings)
        if n < 2:
            return 0.0
        
        switches = 0
        for i in range(n - 1):
            sim = self._cosine_similarity(embeddings[i], embeddings[i + 1])
            if sim < threshold:
                switches += 1
        
        return float(switches)
    
    def get_embeddings(self, messages: List[Dict[str, Any]]) -> np.ndarray:
        """Get raw embeddings for messages."""
        texts = [msg.get('text', '') for msg in messages if msg.get('text')]
        if not texts:
            return np.array([])
        return np.array([self._get_embedding(t) for t in texts])
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names."""
        return self.feature_names.copy()
