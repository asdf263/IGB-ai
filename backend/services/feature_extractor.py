"""
Main Feature Extractor Service
Combines all feature extraction modules to produce ~200 behavior vector features
Uses spaCy for NLP and HuggingFace for embeddings
"""
import numpy as np
from typing import List, Dict, Any, Tuple

from .features.temporal_features import TemporalFeatureExtractor
from .features.text_features import TextFeatureExtractor
from .features.linguistic_features_spacy import LinguisticFeatureExtractorSpacy
from .features.semantic_features_hf import SemanticFeatureExtractorHF
from .features.sentiment_features import SentimentFeatureExtractor
from .features.behavioral_features import BehavioralFeatureExtractor
from .features.graph_features import GraphFeatureExtractor
from .features.composite_features import CompositeFeatureExtractor


class FeatureExtractor:
    """Main feature extractor that combines all feature modules."""
    
    def __init__(self, use_gpu: bool = False):
        self.temporal_extractor = TemporalFeatureExtractor()
        self.text_extractor = TextFeatureExtractor()
        self.linguistic_extractor = LinguisticFeatureExtractorSpacy()
        self.semantic_extractor = SemanticFeatureExtractorHF()
        self.sentiment_extractor = SentimentFeatureExtractor()
        self.behavioral_extractor = BehavioralFeatureExtractor()
        self.graph_extractor = GraphFeatureExtractor()
        self.composite_extractor = CompositeFeatureExtractor()
        
        self._feature_names = None
    
    def extract(self, messages: List[Dict[str, Any]]) -> Tuple[List[float], List[str]]:
        """
        Extract all features from messages.
        
        Args:
            messages: List of message dictionaries with 'sender', 'text', 'timestamp'
            
        Returns:
            Tuple of (feature_vector, feature_labels)
        """
        temporal_features = self.temporal_extractor.extract(messages)
        text_features = self.text_extractor.extract(messages)
        linguistic_features = self.linguistic_extractor.extract(messages)
        semantic_features = self.semantic_extractor.extract(messages)
        sentiment_features = self.sentiment_extractor.extract(messages)
        behavioral_features = self.behavioral_extractor.extract(messages)
        graph_features = self.graph_extractor.extract(messages)
        
        composite_features = self.composite_extractor.extract(
            temporal_features=temporal_features,
            text_features=text_features,
            linguistic_features=linguistic_features,
            semantic_features=semantic_features,
            sentiment_features=sentiment_features,
            behavioral_features=behavioral_features,
            graph_features=graph_features
        )
        
        all_features = {}
        all_features.update({f'temporal_{k}': v for k, v in temporal_features.items()})
        all_features.update({f'text_{k}': v for k, v in text_features.items()})
        all_features.update({f'linguistic_{k}': v for k, v in linguistic_features.items()})
        all_features.update({f'semantic_{k}': v for k, v in semantic_features.items()})
        all_features.update({f'sentiment_{k}': v for k, v in sentiment_features.items()})
        all_features.update({f'behavioral_{k}': v for k, v in behavioral_features.items()})
        all_features.update({f'graph_{k}': v for k, v in graph_features.items()})
        all_features.update({f'composite_{k}': v for k, v in composite_features.items()})
        
        feature_labels = list(all_features.keys())
        feature_vector = [float(all_features[k]) for k in feature_labels]
        
        self._feature_names = feature_labels
        
        return feature_vector, feature_labels
    
    def extract_dict(self, messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract features and return as dictionary."""
        vector, labels = self.extract(messages)
        return dict(zip(labels, vector))
    
    def extract_by_category(self, messages: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Extract features grouped by category."""
        return {
            'temporal': self.temporal_extractor.extract(messages),
            'text': self.text_extractor.extract(messages),
            'linguistic': self.linguistic_extractor.extract(messages),
            'semantic': self.semantic_extractor.extract(messages),
            'sentiment': self.sentiment_extractor.extract(messages),
            'behavioral': self.behavioral_extractor.extract(messages),
            'graph': self.graph_extractor.extract(messages),
            'composite': self.composite_extractor.extract(
                temporal_features=self.temporal_extractor.extract(messages),
                text_features=self.text_extractor.extract(messages),
                linguistic_features=self.linguistic_extractor.extract(messages),
                semantic_features=self.semantic_extractor.extract(messages),
                sentiment_features=self.sentiment_extractor.extract(messages),
                behavioral_features=self.behavioral_extractor.extract(messages),
                graph_features=self.graph_extractor.extract(messages)
            )
        }
    
    def get_feature_names(self) -> List[str]:
        """Get list of all feature names."""
        if self._feature_names:
            return self._feature_names.copy()
        
        names = []
        names.extend([f'temporal_{n}' for n in self.temporal_extractor.get_feature_names()])
        names.extend([f'text_{n}' for n in self.text_extractor.get_feature_names()])
        names.extend([f'linguistic_{n}' for n in self.linguistic_extractor.get_feature_names()])
        names.extend([f'semantic_{n}' for n in self.semantic_extractor.get_feature_names()])
        names.extend([f'sentiment_{n}' for n in self.sentiment_extractor.get_feature_names()])
        names.extend([f'behavioral_{n}' for n in self.behavioral_extractor.get_feature_names()])
        names.extend([f'graph_{n}' for n in self.graph_extractor.get_feature_names()])
        names.extend([f'composite_{n}' for n in self.composite_extractor.get_feature_names()])
        
        return names
    
    def get_feature_count(self) -> int:
        """Get total number of features."""
        return len(self.get_feature_names())
    
    def get_embeddings(self, messages: List[Dict[str, Any]]) -> np.ndarray:
        """Get raw semantic embeddings for messages."""
        return self.semantic_extractor.get_embeddings(messages)
    
    def normalize_vector(self, vector: List[float], method: str = 'soft') -> List[float]:
        """
        Normalize feature vector.
        
        Args:
            vector: Feature vector to normalize
            method: 'soft' for sigmoid-based (prevents maxing at 1), 
                   'minmax' for traditional [0,1] range
        """
        arr = np.array(vector)
        
        # Handle NaN and Inf values
        arr = np.nan_to_num(arr, nan=0.0, posinf=1.0, neginf=0.0)
        
        if method == 'soft':
            # Soft sigmoid normalization - maps to (0, 1) without hard clipping
            # Uses tanh for smoother distribution
            normalized = (np.tanh(arr) + 1) / 2
        else:
            # Traditional min-max normalization
            min_val = np.min(arr)
            max_val = np.max(arr)
            
            if max_val - min_val == 0:
                return [0.5] * len(vector)
            
            normalized = (arr - min_val) / (max_val - min_val)
        
        return normalized.tolist()
    
    def get_category_summary(self, messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """Get summary score for each feature category."""
        categories = self.extract_by_category(messages)
        
        summary = {}
        for category, features in categories.items():
            values = list(features.values())
            valid_values = [v for v in values if not np.isnan(v) and not np.isinf(v)]
            if valid_values:
                summary[category] = float(np.mean(valid_values))
            else:
                summary[category] = 0.0
        
        return summary
