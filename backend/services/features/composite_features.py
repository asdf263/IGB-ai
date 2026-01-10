"""
Composite and Synthetic Feature Extraction Module
Extracts ~15 derived composite behavior signals from other features
"""
import numpy as np
from typing import List, Dict, Any


class CompositeFeatureExtractor:
    """Extracts composite derived features from other feature categories."""
    
    def __init__(self):
        self.feature_names = [
            'social_energy_index',
            'emotional_volatility_index',
            'attentiveness_index',
            'confidence_index',
            'expressiveness_index',
            'topic_coherence_score',
            'communication_efficiency',
            'engagement_quality',
            'personality_consistency',
            'interaction_rhythm_score',
            'semantic_richness',
            'conversational_depth',
            'responsiveness_quality',
            'emotional_intelligence_proxy',
            'overall_behavior_score'
        ]
    
    def extract(self, 
                temporal_features: Dict[str, float],
                text_features: Dict[str, float],
                linguistic_features: Dict[str, float],
                semantic_features: Dict[str, float],
                sentiment_features: Dict[str, float],
                behavioral_features: Dict[str, float],
                graph_features: Dict[str, float]) -> Dict[str, float]:
        """Extract all composite features from other feature categories."""
        
        features = {}
        
        features['social_energy_index'] = self._compute_social_energy(
            text_features, temporal_features, sentiment_features
        )
        
        features['emotional_volatility_index'] = self._compute_emotional_volatility(
            sentiment_features, temporal_features
        )
        
        features['attentiveness_index'] = self._compute_attentiveness(
            behavioral_features, temporal_features
        )
        
        features['confidence_index'] = self._compute_confidence(
            linguistic_features, behavioral_features
        )
        
        features['expressiveness_index'] = self._compute_expressiveness(
            text_features, sentiment_features
        )
        
        features['topic_coherence_score'] = self._compute_topic_coherence(
            semantic_features
        )
        
        features['communication_efficiency'] = self._compute_communication_efficiency(
            text_features, behavioral_features
        )
        
        features['engagement_quality'] = self._compute_engagement_quality(
            behavioral_features, temporal_features, sentiment_features
        )
        
        features['personality_consistency'] = self._compute_personality_consistency(
            linguistic_features, behavioral_features
        )
        
        features['interaction_rhythm_score'] = self._compute_interaction_rhythm(
            temporal_features, graph_features
        )
        
        features['semantic_richness'] = self._compute_semantic_richness(
            text_features, semantic_features
        )
        
        features['conversational_depth'] = self._compute_conversational_depth(
            linguistic_features, semantic_features, behavioral_features
        )
        
        features['responsiveness_quality'] = self._compute_responsiveness_quality(
            temporal_features, behavioral_features
        )
        
        features['emotional_intelligence_proxy'] = self._compute_emotional_intelligence(
            sentiment_features, behavioral_features
        )
        
        features['overall_behavior_score'] = self._compute_overall_score(features)
        
        return features
    
    def _safe_get(self, features: Dict[str, float], key: str, default: float = 0.0) -> float:
        """Safely get feature value with default."""
        return features.get(key, default)
    
    def _compute_social_energy(self, text_features: Dict[str, float],
                               temporal_features: Dict[str, float],
                               sentiment_features: Dict[str, float]) -> float:
        """Compute social energy index: message_length × frequency × sentiment."""
        msg_length = self._safe_get(text_features, 'msg_length_mean', 50) / 100
        frequency = self._safe_get(temporal_features, 'avg_messages_per_hour', 1) / 10
        sentiment = (self._safe_get(sentiment_features, 'sentiment_mean', 0) + 1) / 2
        
        energy = msg_length * frequency * sentiment
        return float(min(1.0, max(0.0, energy)))
    
    def _compute_emotional_volatility(self, sentiment_features: Dict[str, float],
                                      temporal_features: Dict[str, float]) -> float:
        """Compute emotional volatility: sentiment_variance × reply_latency_variance."""
        sentiment_var = self._safe_get(sentiment_features, 'sentiment_std', 0)
        latency_var = min(1.0, self._safe_get(temporal_features, 'std_response_latency', 0) / 3600)
        
        volatility = sentiment_var * latency_var
        return float(min(1.0, max(0.0, volatility * 2)))
    
    def _compute_attentiveness(self, behavioral_features: Dict[str, float],
                               temporal_features: Dict[str, float]) -> float:
        """Compute attentiveness: question_frequency × response_speed."""
        question_freq = self._safe_get(behavioral_features, 'question_frequency', 0)
        response_rate = self._safe_get(behavioral_features, 'response_rate', 0)
        
        avg_latency = self._safe_get(temporal_features, 'avg_response_latency', 60)
        speed_score = 1.0 / (1.0 + avg_latency / 60)
        
        attentiveness = (question_freq + response_rate + speed_score) / 3
        return float(min(1.0, max(0.0, attentiveness)))
    
    def _compute_confidence(self, linguistic_features: Dict[str, float],
                           behavioral_features: Dict[str, float]) -> float:
        """Compute confidence: assertive_statements / hedges."""
        assertive = self._safe_get(linguistic_features, 'assertive_word_ratio', 0)
        hedge = self._safe_get(linguistic_features, 'hedge_word_ratio', 0.01)
        assertiveness = self._safe_get(behavioral_features, 'assertiveness_score', 0)
        
        confidence = (assertive / (hedge + 0.01) + assertiveness) / 2
        return float(min(1.0, max(0.0, confidence)))
    
    def _compute_expressiveness(self, text_features: Dict[str, float],
                                sentiment_features: Dict[str, float]) -> float:
        """Compute expressiveness: emoji_density × sentiment_amplitude."""
        emoji_density = self._safe_get(text_features, 'emoji_density', 0)
        sentiment_range = self._safe_get(sentiment_features, 'sentiment_range', 0)
        intensity = self._safe_get(sentiment_features, 'emotional_intensity_mean', 0)
        
        expressiveness = (emoji_density * 10 + sentiment_range + intensity) / 3
        return float(min(1.0, max(0.0, expressiveness)))
    
    def _compute_topic_coherence(self, semantic_features: Dict[str, float]) -> float:
        """Compute topic coherence: topic_stability / entropy."""
        coherence = self._safe_get(semantic_features, 'semantic_coherence', 0.5)
        concentration = self._safe_get(semantic_features, 'topic_concentration', 0.5)
        
        score = (coherence + concentration) / 2
        return float(min(1.0, max(0.0, score)))
    
    def _compute_communication_efficiency(self, text_features: Dict[str, float],
                                         behavioral_features: Dict[str, float]) -> float:
        """Compute communication efficiency: information density per message."""
        lexical_richness = self._safe_get(text_features, 'lexical_richness', 0.5)
        elaboration = self._safe_get(behavioral_features, 'elaboration_score', 0.5)
        
        msg_length = self._safe_get(text_features, 'msg_length_mean', 50)
        length_penalty = 1.0 / (1.0 + msg_length / 200)
        
        efficiency = (lexical_richness + elaboration) / 2 * (1 - length_penalty * 0.5)
        return float(min(1.0, max(0.0, efficiency)))
    
    def _compute_engagement_quality(self, behavioral_features: Dict[str, float],
                                    temporal_features: Dict[str, float],
                                    sentiment_features: Dict[str, float]) -> float:
        """Compute engagement quality score."""
        engagement = self._safe_get(behavioral_features, 'engagement_level', 0.5)
        response_rate = self._safe_get(behavioral_features, 'response_rate', 0.5)
        positive_ratio = self._safe_get(sentiment_features, 'positive_ratio', 0.33)
        
        quality = (engagement + response_rate + positive_ratio) / 3
        return float(min(1.0, max(0.0, quality)))
    
    def _compute_personality_consistency(self, linguistic_features: Dict[str, float],
                                        behavioral_features: Dict[str, float]) -> float:
        """Compute personality consistency score."""
        formality = self._safe_get(behavioral_features, 'formality_score', 0.5)
        directness = self._safe_get(behavioral_features, 'directness_score', 0.5)
        
        consistency = 1.0 - abs(formality - directness)
        return float(min(1.0, max(0.0, consistency)))
    
    def _compute_interaction_rhythm(self, temporal_features: Dict[str, float],
                                    graph_features: Dict[str, float]) -> float:
        """Compute interaction rhythm score."""
        burstiness = self._safe_get(temporal_features, 'burstiness_score', 0)
        social_balance = self._safe_get(graph_features, 'social_balance', 0.5)
        
        rhythm = (1 - abs(burstiness) + social_balance) / 2
        return float(min(1.0, max(0.0, rhythm)))
    
    def _compute_semantic_richness(self, text_features: Dict[str, float],
                                   semantic_features: Dict[str, float]) -> float:
        """Compute semantic richness score."""
        entropy = self._safe_get(text_features, 'shannon_entropy', 0) / 10
        diversity = self._safe_get(semantic_features, 'topic_diversity', 0)
        
        richness = (entropy + diversity) / 2
        return float(min(1.0, max(0.0, richness)))
    
    def _compute_conversational_depth(self, linguistic_features: Dict[str, float],
                                      semantic_features: Dict[str, float],
                                      behavioral_features: Dict[str, float]) -> float:
        """Compute conversational depth score."""
        clause_depth = self._safe_get(linguistic_features, 'avg_clause_depth', 1) / 3
        elaboration = self._safe_get(behavioral_features, 'elaboration_score', 0.5)
        abstraction = self._safe_get(semantic_features, 'abstraction_level', 0.5)
        
        depth = (clause_depth + elaboration + abstraction) / 3
        return float(min(1.0, max(0.0, depth)))
    
    def _compute_responsiveness_quality(self, temporal_features: Dict[str, float],
                                        behavioral_features: Dict[str, float]) -> float:
        """Compute responsiveness quality score."""
        avg_latency = self._safe_get(temporal_features, 'avg_response_latency', 60)
        speed_score = 1.0 / (1.0 + avg_latency / 120)
        
        response_rate = self._safe_get(behavioral_features, 'response_rate', 0.5)
        
        quality = (speed_score + response_rate) / 2
        return float(min(1.0, max(0.0, quality)))
    
    def _compute_emotional_intelligence(self, sentiment_features: Dict[str, float],
                                        behavioral_features: Dict[str, float]) -> float:
        """Compute emotional intelligence proxy score."""
        empathy = self._safe_get(behavioral_features, 'empathy_score', 0)
        support = self._safe_get(behavioral_features, 'support_ratio', 0)
        sentiment_consistency = self._safe_get(sentiment_features, 'sentiment_consistency', 0.5)
        
        eq = (empathy + support + sentiment_consistency) / 3
        return float(min(1.0, max(0.0, eq)))
    
    def _compute_overall_score(self, features: Dict[str, float]) -> float:
        """Compute overall behavior score from all composite features."""
        values = [v for k, v in features.items() if k != 'overall_behavior_score']
        if not values:
            return 0.5
        return float(np.mean(values))
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names."""
        return self.feature_names.copy()
