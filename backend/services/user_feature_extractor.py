"""
User-Based Feature Extractor
Extracts behavior vectors for individual users within a conversation,
focusing on how they react to and interact with the other person.
"""
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

from .features.temporal_features import TemporalFeatureExtractor
from .features.text_features import TextFeatureExtractor
from .features.linguistic_features_spacy import LinguisticFeatureExtractorSpacy
from .features.semantic_features_hf import SemanticFeatureExtractorHF
from .features.sentiment_features import SentimentFeatureExtractor
from .features.behavioral_features import BehavioralFeatureExtractor
from .features.graph_features import GraphFeatureExtractor
from .features.composite_features import CompositeFeatureExtractor
from .features.reaction_features import ReactionFeatureExtractor


class UserFeatureExtractor:
    """Extracts behavior vectors for individual users in a conversation."""
    
    def __init__(self, use_gpu: bool = False):
        self.temporal_extractor = TemporalFeatureExtractor()
        self.text_extractor = TextFeatureExtractor()
        self.linguistic_extractor = LinguisticFeatureExtractorSpacy()
        self.semantic_extractor = SemanticFeatureExtractorHF()
        self.sentiment_extractor = SentimentFeatureExtractor()
        self.behavioral_extractor = BehavioralFeatureExtractor()
        self.graph_extractor = GraphFeatureExtractor()
        self.composite_extractor = CompositeFeatureExtractor()
        self.reaction_extractor = ReactionFeatureExtractor()
        
        self._feature_names = None
    
    def get_participants(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Get list of unique participants in the conversation."""
        return list(set(msg.get('sender', 'unknown') for msg in messages))
    
    def extract_for_user(self, messages: List[Dict[str, Any]], target_user: str) -> Tuple[List[float], List[str]]:
        """
        Extract features for a specific user in the conversation.
        
        Args:
            messages: All messages in the conversation
            target_user: The user to extract features for
            
        Returns:
            Tuple of (feature_vector, feature_labels)
        """
        # Filter messages by this user
        user_messages = [msg for msg in messages if msg.get('sender') == target_user]
        
        if not user_messages:
            return [], []
        
        # Extract standard features from user's messages only
        temporal_features = self.temporal_extractor.extract(user_messages)
        text_features = self.text_extractor.extract(user_messages)
        linguistic_features = self.linguistic_extractor.extract(user_messages)
        semantic_features = self.semantic_extractor.extract(user_messages)
        sentiment_features = self.sentiment_extractor.extract(user_messages)
        behavioral_features = self.behavioral_extractor.extract(messages)  # Needs full context
        graph_features = self.graph_extractor.extract(messages)  # Needs full context
        
        # Extract reaction features (how user reacts to the other person)
        reaction_features = self.reaction_extractor.extract_for_user(messages, target_user)
        
        # Compute composite features
        composite_features = self.composite_extractor.extract(
            temporal_features=temporal_features,
            text_features=text_features,
            linguistic_features=linguistic_features,
            semantic_features=semantic_features,
            sentiment_features=sentiment_features,
            behavioral_features=behavioral_features,
            graph_features=graph_features
        )
        
        # Combine all features with proper normalization
        all_features = {}
        all_features.update({f'temporal_{k}': v for k, v in temporal_features.items()})
        all_features.update({f'text_{k}': v for k, v in text_features.items()})
        all_features.update({f'linguistic_{k}': v for k, v in linguistic_features.items()})
        all_features.update({f'semantic_{k}': v for k, v in semantic_features.items()})
        all_features.update({f'sentiment_{k}': v for k, v in sentiment_features.items()})
        all_features.update({f'behavioral_{k}': v for k, v in behavioral_features.items()})
        all_features.update({f'graph_{k}': v for k, v in graph_features.items()})
        all_features.update({f'composite_{k}': v for k, v in composite_features.items()})
        all_features.update({f'reaction_{k}': v for k, v in reaction_features.items()})
        
        # Apply proper normalization to prevent values maxing at 1
        all_features = self._normalize_features(all_features)
        
        feature_labels = list(all_features.keys())
        feature_vector = [float(all_features[k]) for k in feature_labels]
        
        self._feature_names = feature_labels
        
        return feature_vector, feature_labels
    
    def extract_all_users(self, messages: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Extract features for all users in the conversation.
        
        Returns:
            Dictionary mapping user names to their feature data
        """
        participants = self.get_participants(messages)
        results = {}
        
        for user in participants:
            vector, labels = self.extract_for_user(messages, user)
            if vector:
                results[user] = {
                    'vector': vector,
                    'labels': labels,
                    'categories': self._group_by_category(labels, vector),
                    'message_count': len([m for m in messages if m.get('sender') == user])
                }
        
        return results
    
    def _group_by_category(self, labels: List[str], vector: List[float]) -> Dict[str, Dict[str, float]]:
        """Group features by category."""
        categories = {}
        for label, value in zip(labels, vector):
            parts = label.split('_', 1)
            if len(parts) == 2:
                category, name = parts
            else:
                category, name = 'other', label
            
            if category not in categories:
                categories[category] = {}
            categories[category][name] = value
        
        return categories
    
    def _normalize_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Apply proper normalization to features to prevent maxing out at 1.
        Uses sigmoid-based soft normalization for unbounded features.
        """
        normalized = {}
        
        # Define normalization strategies for different feature types
        # Features that should be in [0, 1] range naturally
        bounded_features = {
            'ratio', 'rate', 'frequency', 'score', 'index', 'level',
            'tendency', 'balance', 'consistency', 'matching', 'alignment'
        }
        
        # Features that can have larger ranges and need soft normalization
        unbounded_features = {
            'mean', 'std', 'variance', 'count', 'length', 'distance',
            'entropy', 'depth', 'density'
        }
        
        for key, value in features.items():
            if value is None or np.isnan(value) or np.isinf(value):
                normalized[key] = 0.0
                continue
            
            # Check if feature is naturally bounded
            is_bounded = any(b in key.lower() for b in bounded_features)
            is_unbounded = any(u in key.lower() for u in unbounded_features)
            
            if is_bounded and not is_unbounded:
                # Clip to [0, 1] for naturally bounded features
                normalized[key] = float(np.clip(value, 0.0, 1.0))
            elif is_unbounded or abs(value) > 1.0:
                # Apply soft sigmoid normalization for unbounded features
                # Maps any value to (0, 1) range smoothly
                normalized[key] = float(self._soft_normalize(value))
            else:
                # Keep value as-is if it's already in reasonable range
                normalized[key] = float(np.clip(value, -1.0, 1.0))
        
        return normalized
    
    def _soft_normalize(self, value: float, scale: float = 1.0) -> float:
        """
        Apply soft sigmoid normalization.
        Maps any real number to (0, 1) range.
        """
        # Use tanh-based normalization for smoother distribution
        # tanh maps to (-1, 1), we shift to (0, 1)
        return (np.tanh(value / scale) + 1) / 2
    
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
        names.extend([f'reaction_{n}' for n in self.reaction_extractor.get_feature_names()])
        
        return names
    
    def get_feature_count(self) -> int:
        """Get total number of features."""
        return len(self.get_feature_names())
    
    def get_user_summary(self, messages: List[Dict[str, Any]], target_user: str) -> Dict[str, float]:
        """Get summary scores for each feature category for a user."""
        vector, labels = self.extract_for_user(messages, target_user)
        
        if not vector:
            return {}
        
        categories = self._group_by_category(labels, vector)
        
        summary = {}
        for category, features in categories.items():
            values = list(features.values())
            valid_values = [v for v in values if not np.isnan(v) and not np.isinf(v)]
            if valid_values:
                summary[category] = float(np.mean(valid_values))
            else:
                summary[category] = 0.0
        
        return summary
