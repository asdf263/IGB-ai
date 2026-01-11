"""
Synthetic Data Generation Module
Generates synthetic chat message sequences with text perturbations
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import random


class SyntheticGenerator:
    """Generates synthetic chat data and validates vectors."""
    
    def __init__(self, random_seed: Optional[int] = None):
        if random_seed is not None:
            np.random.seed(random_seed)
            random.seed(random_seed)
    
    def generate_synthetic_vectors(self, 
                                   original_vectors: List[List[float]], 
                                   n_synthetic: int = 10,
                                   method: str = 'deprecated') -> List[List[float]]:
        """
        Vector augmentation removed - returns empty list.
        
        Args:
            original_vectors: List of original feature vectors (ignored)
            n_synthetic: Number of synthetic vectors to generate (ignored)
            method: Generation method (deprecated)
            
        Returns:
            Empty list (augmentation removed)
        """
        return []
    
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
