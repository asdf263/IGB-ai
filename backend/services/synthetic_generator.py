"""
Synthetic Data Generation Module
Generates synthetic behavior vectors using SMOTE, noise injection, and embedding jitter
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import random
import hashlib


class SyntheticGenerator:
    """Generates synthetic behavior vectors and chat data."""
    
    def __init__(self, random_seed: Optional[int] = None):
        if random_seed is not None:
            np.random.seed(random_seed)
            random.seed(random_seed)
    
    def generate_synthetic_vectors(self, 
                                   original_vectors: List[List[float]], 
                                   n_synthetic: int = 10,
                                   method: str = 'smote') -> List[List[float]]:
        """
        Generate synthetic vectors from original vectors.
        
        Args:
            original_vectors: List of original feature vectors
            n_synthetic: Number of synthetic vectors to generate
            method: Generation method ('smote', 'noise', 'jitter', 'interpolate')
            
        Returns:
            List of synthetic feature vectors
        """
        if not original_vectors:
            return []
        
        original_arr = np.array(original_vectors)
        
        if method == 'smote':
            return self._smote_generate(original_arr, n_synthetic)
        elif method == 'noise':
            return self._noise_generate(original_arr, n_synthetic)
        elif method == 'jitter':
            return self._jitter_generate(original_arr, n_synthetic)
        elif method == 'interpolate':
            return self._interpolate_generate(original_arr, n_synthetic)
        elif method == 'adasyn':
            return self._adasyn_generate(original_arr, n_synthetic)
        else:
            return self._smote_generate(original_arr, n_synthetic)
    
    def _smote_generate(self, vectors: np.ndarray, n_synthetic: int) -> List[List[float]]:
        """Generate synthetic vectors using SMOTE-like interpolation."""
        synthetic = []
        n_samples = len(vectors)
        
        if n_samples < 2:
            return self._noise_generate(vectors, n_synthetic)
        
        for _ in range(n_synthetic):
            idx1 = np.random.randint(0, n_samples)
            idx2 = np.random.randint(0, n_samples)
            while idx2 == idx1 and n_samples > 1:
                idx2 = np.random.randint(0, n_samples)
            
            alpha = np.random.random()
            new_vector = vectors[idx1] + alpha * (vectors[idx2] - vectors[idx1])
            
            noise = np.random.normal(0, 0.01, len(new_vector))
            new_vector = new_vector + noise
            
            synthetic.append(new_vector.tolist())
        
        return synthetic
    
    def _noise_generate(self, vectors: np.ndarray, n_synthetic: int) -> List[List[float]]:
        """Generate synthetic vectors by adding Gaussian noise."""
        synthetic = []
        n_samples = len(vectors)
        
        std_per_feature = np.std(vectors, axis=0) if n_samples > 1 else np.ones(vectors.shape[1]) * 0.1
        std_per_feature = np.where(std_per_feature == 0, 0.01, std_per_feature)
        
        for _ in range(n_synthetic):
            idx = np.random.randint(0, n_samples)
            base_vector = vectors[idx].copy()
            
            noise = np.random.normal(0, std_per_feature * 0.1)
            new_vector = base_vector + noise
            
            synthetic.append(new_vector.tolist())
        
        return synthetic
    
    def _jitter_generate(self, vectors: np.ndarray, n_synthetic: int) -> List[List[float]]:
        """Generate synthetic vectors using uniform jitter."""
        synthetic = []
        n_samples = len(vectors)
        
        range_per_feature = np.ptp(vectors, axis=0) if n_samples > 1 else np.ones(vectors.shape[1]) * 0.2
        range_per_feature = np.where(range_per_feature == 0, 0.02, range_per_feature)
        
        for _ in range(n_synthetic):
            idx = np.random.randint(0, n_samples)
            base_vector = vectors[idx].copy()
            
            jitter = np.random.uniform(-range_per_feature * 0.05, range_per_feature * 0.05)
            new_vector = base_vector + jitter
            
            synthetic.append(new_vector.tolist())
        
        return synthetic
    
    def _interpolate_generate(self, vectors: np.ndarray, n_synthetic: int) -> List[List[float]]:
        """Generate synthetic vectors using multi-point interpolation."""
        synthetic = []
        n_samples = len(vectors)
        
        if n_samples < 3:
            return self._smote_generate(vectors, n_synthetic)
        
        for _ in range(n_synthetic):
            n_points = min(np.random.randint(2, 5), n_samples)
            indices = np.random.choice(n_samples, n_points, replace=False)
            weights = np.random.dirichlet(np.ones(n_points))
            
            new_vector = np.zeros(vectors.shape[1])
            for idx, weight in zip(indices, weights):
                new_vector += weight * vectors[idx]
            
            synthetic.append(new_vector.tolist())
        
        return synthetic
    
    def _adasyn_generate(self, vectors: np.ndarray, n_synthetic: int) -> List[List[float]]:
        """Generate synthetic vectors using ADASYN-like adaptive sampling."""
        synthetic = []
        n_samples = len(vectors)
        
        if n_samples < 2:
            return self._noise_generate(vectors, n_synthetic)
        
        centroid = np.mean(vectors, axis=0)
        distances = np.array([np.linalg.norm(v - centroid) for v in vectors])
        
        weights = distances / (np.sum(distances) + 1e-10)
        weights = weights + 0.1
        weights = weights / np.sum(weights)
        
        for _ in range(n_synthetic):
            idx1 = np.random.choice(n_samples, p=weights)
            idx2 = np.random.randint(0, n_samples)
            while idx2 == idx1 and n_samples > 1:
                idx2 = np.random.randint(0, n_samples)
            
            alpha = np.random.random()
            new_vector = vectors[idx1] + alpha * (vectors[idx2] - vectors[idx1])
            
            synthetic.append(new_vector.tolist())
        
        return synthetic
    
    def generate_synthetic_messages(self, 
                                    original_messages: List[Dict[str, Any]],
                                    n_synthetic: int = 10) -> List[List[Dict[str, Any]]]:
        """
        Generate synthetic chat message sequences.
        
        Args:
            original_messages: Original message sequence
            n_synthetic: Number of synthetic sequences to generate
            
        Returns:
            List of synthetic message sequences
        """
        if not original_messages:
            return []
        
        synthetic_sequences = []
        
        for _ in range(n_synthetic):
            synthetic_seq = self._generate_message_sequence(original_messages)
            synthetic_sequences.append(synthetic_seq)
        
        return synthetic_sequences
    
    def _generate_message_sequence(self, 
                                   original_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate a single synthetic message sequence."""
        synthetic = []
        
        base_timestamp = original_messages[0].get('timestamp', 0) if original_messages else 0
        
        intervals = []
        for i in range(1, len(original_messages)):
            ts1 = original_messages[i-1].get('timestamp', 0)
            ts2 = original_messages[i].get('timestamp', 0)
            if ts1 and ts2:
                intervals.append(ts2 - ts1)
        
        avg_interval = np.mean(intervals) if intervals else 60
        std_interval = np.std(intervals) if len(intervals) > 1 else avg_interval * 0.2
        
        current_timestamp = base_timestamp + np.random.randint(-3600, 3600)
        
        for msg in original_messages:
            synthetic_msg = {
                'sender': msg.get('sender', 'user'),
                'text': self._perturb_text(msg.get('text', '')),
                'timestamp': current_timestamp
            }
            synthetic.append(synthetic_msg)
            
            interval = max(1, np.random.normal(avg_interval, std_interval))
            current_timestamp += int(interval)
        
        return synthetic
    
    def _perturb_text(self, text: str) -> str:
        """Apply small perturbations to text while preserving meaning."""
        if not text:
            return text
        
        words = text.split()
        if not words:
            return text
        
        synonyms = {
            'good': ['great', 'nice', 'fine', 'excellent'],
            'bad': ['poor', 'terrible', 'awful', 'not good'],
            'happy': ['glad', 'pleased', 'delighted', 'joyful'],
            'sad': ['unhappy', 'upset', 'down', 'blue'],
            'big': ['large', 'huge', 'enormous', 'massive'],
            'small': ['little', 'tiny', 'mini', 'compact'],
            'fast': ['quick', 'rapid', 'speedy', 'swift'],
            'slow': ['sluggish', 'gradual', 'unhurried', 'leisurely'],
            'like': ['enjoy', 'love', 'appreciate', 'prefer'],
            'think': ['believe', 'feel', 'consider', 'suppose'],
            'want': ['wish', 'desire', 'hope', 'need'],
            'know': ['understand', 'realize', 'recognize', 'see'],
            'very': ['really', 'quite', 'extremely', 'highly'],
            'just': ['simply', 'merely', 'only', 'exactly']
        }
        
        new_words = []
        for word in words:
            word_lower = word.lower()
            if word_lower in synonyms and random.random() < 0.15:
                replacement = random.choice(synonyms[word_lower])
                if word[0].isupper():
                    replacement = replacement.capitalize()
                new_words.append(replacement)
            else:
                new_words.append(word)
        
        return ' '.join(new_words)
    
    def add_behavior_modulation(self, 
                                vector: List[float],
                                modulation_type: str = 'random') -> List[float]:
        """
        Apply behavior pattern modulation to a vector.
        
        Args:
            vector: Original feature vector
            modulation_type: Type of modulation ('random', 'energetic', 'calm', 'formal', 'casual')
            
        Returns:
            Modulated feature vector
        """
        arr = np.array(vector)
        
        if modulation_type == 'random':
            scale = np.random.uniform(0.8, 1.2, len(arr))
            shift = np.random.uniform(-0.05, 0.05, len(arr))
            return (arr * scale + shift).tolist()
        
        elif modulation_type == 'energetic':
            arr = arr * 1.1
            arr = np.clip(arr, 0, 1)
            return arr.tolist()
        
        elif modulation_type == 'calm':
            arr = arr * 0.9
            return arr.tolist()
        
        elif modulation_type == 'formal':
            arr = arr * np.random.uniform(0.95, 1.05, len(arr))
            return arr.tolist()
        
        elif modulation_type == 'casual':
            noise = np.random.normal(0, 0.02, len(arr))
            return (arr + noise).tolist()
        
        return vector
    
    def validate_vector(self, vector: List[float], 
                       min_val: float = -10.0, 
                       max_val: float = 10.0) -> Tuple[bool, List[float]]:
        """
        Validate and clip vector to valid ranges.
        
        Returns:
            Tuple of (is_valid, clipped_vector)
        """
        arr = np.array(vector)
        
        has_nan = np.any(np.isnan(arr))
        has_inf = np.any(np.isinf(arr))
        
        arr = np.nan_to_num(arr, nan=0.0, posinf=max_val, neginf=min_val)
        arr = np.clip(arr, min_val, max_val)
        
        is_valid = not (has_nan or has_inf)
        
        return is_valid, arr.tolist()
    
    def batch_generate(self,
                      original_vectors: List[List[float]],
                      n_per_method: int = 5) -> Dict[str, List[List[float]]]:
        """
        Generate synthetic vectors using all methods.
        
        Returns:
            Dictionary mapping method names to synthetic vectors
        """
        methods = ['smote', 'noise', 'jitter', 'interpolate', 'adasyn']
        results = {}
        
        for method in methods:
            results[method] = self.generate_synthetic_vectors(
                original_vectors, n_per_method, method
            )
        
        return results
