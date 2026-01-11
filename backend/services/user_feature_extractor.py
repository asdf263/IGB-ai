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
from .features.sentiment_features import SentimentFeatureExtractor
from .features.behavioral_features import BehavioralFeatureExtractor
from .features.composite_features import CompositeFeatureExtractor
from .features.reaction_features import ReactionFeatureExtractor
from .features.llm_synthetic_features import LLMSyntheticFeatureExtractor
from .features.emotion_transformer import EmotionTransformerExtractor
from .features.conversation_context_features import ConversationContextExtractor
from .calibrated_normalizer import CalibratedNormalizer


class UserFeatureExtractor:
    """Extracts behavior vectors for individual users in a conversation."""
    
    def __init__(self, use_gpu: bool = False):
        self.temporal_extractor = TemporalFeatureExtractor()
        self.text_extractor = TextFeatureExtractor()
        self.linguistic_extractor = LinguisticFeatureExtractorSpacy()
        self.sentiment_extractor = SentimentFeatureExtractor()
        self.behavioral_extractor = BehavioralFeatureExtractor()
        self.composite_extractor = CompositeFeatureExtractor()
        self.reaction_extractor = ReactionFeatureExtractor()
        self.llm_synthetic_extractor = LLMSyntheticFeatureExtractor()
        self.emotion_extractor = EmotionTransformerExtractor()
        self.context_extractor = ConversationContextExtractor()
        self.calibrated_normalizer = CalibratedNormalizer()
        
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
        sentiment_features = self.sentiment_extractor.extract(user_messages)
        behavioral_features = self.behavioral_extractor.extract(messages, target_user)  # Needs full context
        
        # Extract transformer-based emotion features (replaces word-list emotions)
        emotion_features = self.emotion_extractor.extract(user_messages)
        
        # Extract conversation context features (flow and topic transitions)
        context_features = self.context_extractor.extract(messages)  # Needs full context
        
        # Extract reaction features (how user reacts to the other person)
        reaction_features = self.reaction_extractor.extract_for_user(messages, target_user)
        
        # Compute composite features
        composite_features = self.composite_extractor.extract(
            temporal_features=temporal_features,
            text_features=text_features,
            linguistic_features=linguistic_features,
            semantic_features={},
            sentiment_features=sentiment_features,
            behavioral_features=behavioral_features,
            graph_features={}
        )
        
        # Compute LLM synthetic features (high-level abstractions for personality)
        llm_synthetic_features = self.llm_synthetic_extractor.extract(
            text_features=text_features,
            linguistic_features=linguistic_features,
            sentiment_features=sentiment_features,
            behavioral_features=behavioral_features,
            reaction_features=reaction_features,
            composite_features=composite_features,
            emotion_features=emotion_features,
            context_features=context_features
        )
        
        # Combine all features with proper normalization
        all_features = {}
        all_features.update({f'temporal_{k}': v for k, v in temporal_features.items()})
        all_features.update({f'text_{k}': v for k, v in text_features.items()})
        all_features.update({f'linguistic_{k}': v for k, v in linguistic_features.items()})
        all_features.update({f'sentiment_{k}': v for k, v in sentiment_features.items()})
        all_features.update({f'behavioral_{k}': v for k, v in behavioral_features.items()})
        all_features.update({f'composite_{k}': v for k, v in composite_features.items()})
        all_features.update({f'reaction_{k}': v for k, v in reaction_features.items()})
        all_features.update({f'emotion_{k}': v for k, v in emotion_features.items()})
        all_features.update({f'context_{k}': v for k, v in context_features.items()})
        all_features.update({f'synthetic_{k}': v for k, v in llm_synthetic_features.items()})
        
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
        Normalize features using calibrated piecewise functions where available,
        falling back to heuristic normalization for other features.
        """
        # First, apply calibrated normalization
        normalized = self.calibrated_normalizer.normalize(features)
        
        # For features not in calibration set, apply fallback normalization
        bounded_keywords = {
            'ratio', 'density', 'richness', 'consistency', 'matching', 
            'alignment', 'balance', 'tendency'
        }
        
        soft_bounded_keywords = {
            'score', 'index', 'level', 'frequency', 'rate'
        }
        
        raw_keywords = {
            'mean', 'std', 'min', 'max', 'median', 'count', 'length',
            'entropy', 'depth', 'readability', 'latency', 'session'
        }
        
        for key, value in normalized.items():
            # Handle invalid values
            if value is None or (isinstance(value, float) and (np.isnan(value) or np.isinf(value))):
                normalized[key] = 0.0
                continue
            
            # If value was already normalized by calibration (changed from original), keep it
            if key in features and value != features[key]:
                # Calibrated normalization was applied, clip to [0, 1] for safety
                normalized[key] = float(np.clip(value, 0.0, 1.0))
                continue
            
            # Apply fallback normalization for non-calibrated features
            key_lower = key.lower()
            
            is_bounded = any(b in key_lower for b in bounded_keywords)
            is_soft_bounded = any(b in key_lower for b in soft_bounded_keywords)
            is_raw = any(r in key_lower for r in raw_keywords)
            
            if is_bounded:
                normalized[key] = float(np.clip(value, 0.0, 1.0))
            elif is_soft_bounded:
                normalized[key] = float(np.clip(value, 0.0, 1.0))
            elif is_raw:
                normalized[key] = float(max(0.0, value))
            else:
                if 0.0 <= value <= 1.0:
                    normalized[key] = float(value)
                else:
                    normalized[key] = float(value)
        
        return normalized
    
    def get_feature_names(self) -> List[str]:
        """Get list of all feature names."""
        if self._feature_names:
            return self._feature_names.copy()
        
        names = []
        names.extend([f'temporal_{n}' for n in self.temporal_extractor.get_feature_names()])
        names.extend([f'text_{n}' for n in self.text_extractor.get_feature_names()])
        names.extend([f'linguistic_{n}' for n in self.linguistic_extractor.get_feature_names()])
        names.extend([f'sentiment_{n}' for n in self.sentiment_extractor.get_feature_names()])
        names.extend([f'behavioral_{n}' for n in self.behavioral_extractor.get_feature_names()])
        names.extend([f'composite_{n}' for n in self.composite_extractor.get_feature_names()])
        names.extend([f'reaction_{n}' for n in self.reaction_extractor.get_feature_names()])
        names.extend([f'emotion_{n}' for n in self.emotion_extractor.get_feature_names()])
        names.extend([f'context_{n}' for n in self.context_extractor.get_feature_names()])
        names.extend([f'synthetic_{n}' for n in self.llm_synthetic_extractor.get_feature_names()])
        
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
