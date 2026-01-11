"""
Personality Ecosystem Service
Manages a shared environment where AI personalities interact, comparing behavioral vectors,
computing compatibility scores, and measuring alignment in communication styles.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from scipy.spatial.distance import cosine, euclidean
from scipy.stats import pearsonr, spearmanr

logger = logging.getLogger(__name__)


class EcosystemService:
    """
    Manages the personality ecosystem where AI personas are compared and matched.
    Computes multi-dimensional compatibility scores based on behavioral vectors.
    """
    
    def __init__(self, storage_dir: str = "./data/ecosystem"):
        self.storage_dir = storage_dir
        self._ensure_storage_dir()
        self.personas: Dict[str, Dict[str, Any]] = {}
        self._load_personas()
        
        # Compatibility dimension weights
        self.compatibility_weights = {
            'emotional_alignment': 0.20,
            'conversation_rhythm': 0.15,
            'topic_affinity': 0.15,
            'social_energy_match': 0.15,
            'linguistic_similarity': 0.15,
            'trait_complementarity': 0.20,
        }
    
    def _ensure_storage_dir(self):
        """Create storage directory if needed."""
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def _load_personas(self):
        """Load all personas from storage."""
        try:
            personas_file = os.path.join(self.storage_dir, "personas.json")
            if os.path.exists(personas_file):
                with open(personas_file, 'r', encoding='utf-8') as f:
                    self.personas = json.load(f)
                logger.info(f"Loaded {len(self.personas)} personas")
        except Exception as e:
            logger.error(f"Failed to load personas: {e}")
            self.personas = {}
    
    def _save_personas(self):
        """Save all personas to storage."""
        try:
            personas_file = os.path.join(self.storage_dir, "personas.json")
            with open(personas_file, 'w', encoding='utf-8') as f:
                json.dump(self.personas, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save personas: {e}")
    
    def add_persona(
        self,
        persona_id: str,
        user_name: str,
        personality: Dict[str, Any],
        vector: List[float],
        source_analysis_id: Optional[str] = None,
        sample_messages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add a persona to the ecosystem.
        
        Args:
            persona_id: Unique identifier for the persona
            user_name: Display name
            personality: Synthesized personality profile
            vector: Feature vector
            source_analysis_id: ID of the source analysis
            sample_messages: Representative sample messages for style mimicry (up to 50)
        
        Returns:
            The added persona entry
        """
        # Store up to 50 sample messages for style reference
        stored_samples = []
        if sample_messages:
            stored_samples = sample_messages[:50]
        
        persona_entry = {
            'persona_id': persona_id,
            'user_name': user_name,
            'personality': personality,
            'vector': vector,
            'source_analysis_id': source_analysis_id,
            'sample_messages': stored_samples,
            'added_at': np.datetime64('now').astype(str),
            'interaction_count': 0,
        }
        
        self.personas[persona_id] = persona_entry
        self._save_personas()
        
        logger.info(f"Added persona: {user_name} ({persona_id})")
        return persona_entry
    
    def remove_persona(self, persona_id: str) -> bool:
        """Remove a persona from the ecosystem."""
        if persona_id in self.personas:
            del self.personas[persona_id]
            self._save_personas()
            return True
        return False
    
    def get_persona(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific persona."""
        return self.personas.get(persona_id)
    
    def list_personas(self) -> List[Dict[str, Any]]:
        """List all personas in the ecosystem."""
        return [
            {
                'persona_id': p['persona_id'],
                'user_name': p['user_name'],
                'added_at': p.get('added_at'),
                'interaction_count': p.get('interaction_count', 0),
                'metrics': p.get('personality', {}).get('metrics', {}),
            }
            for p in self.personas.values()
        ]
    
    def compute_compatibility(
        self,
        persona_id_1: str,
        persona_id_2: str
    ) -> Dict[str, Any]:
        """
        Compute detailed compatibility between two personas.
        
        Returns compatibility scores across multiple dimensions:
        - Emotional alignment
        - Conversation rhythm
        - Topic affinity
        - Social energy match
        - Linguistic similarity
        - Trait complementarity
        """
        persona1 = self.personas.get(persona_id_1)
        persona2 = self.personas.get(persona_id_2)
        
        if not persona1 or not persona2:
            raise ValueError("One or both personas not found")
        
        vec1 = np.array(persona1['vector'])
        vec2 = np.array(persona2['vector'])
        
        personality1 = persona1.get('personality', {})
        personality2 = persona2.get('personality', {})
        
        # Calculate each compatibility dimension
        scores = {}
        
        # 1. Emotional Alignment
        scores['emotional_alignment'] = self._compute_emotional_alignment(
            personality1, personality2, vec1, vec2
        )
        
        # 2. Conversation Rhythm
        scores['conversation_rhythm'] = self._compute_rhythm_compatibility(
            personality1, personality2, vec1, vec2
        )
        
        # 3. Topic Affinity
        scores['topic_affinity'] = self._compute_topic_affinity(
            personality1, personality2, vec1, vec2
        )
        
        # 4. Social Energy Match
        scores['social_energy_match'] = self._compute_social_energy_match(
            personality1, personality2
        )
        
        # 5. Linguistic Similarity
        scores['linguistic_similarity'] = self._compute_linguistic_similarity(
            personality1, personality2, vec1, vec2
        )
        
        # 6. Trait Complementarity
        scores['trait_complementarity'] = self._compute_trait_complementarity(
            personality1, personality2
        )
        
        # Calculate weighted overall score
        overall_score = sum(
            scores[dim] * weight
            for dim, weight in self.compatibility_weights.items()
        )
        
        # Generate insights
        insights = self._generate_compatibility_insights(scores, persona1, persona2)
        
        return {
            'persona1': persona1['user_name'],
            'persona2': persona2['user_name'],
            'overall_score': round(overall_score * 100, 1),
            'dimension_scores': {k: round(v * 100, 1) for k, v in scores.items()},
            'insights': insights,
            'strengths': self._identify_strengths(scores),
            'challenges': self._identify_challenges(scores),
            'recommendations': self._generate_recommendations(scores, personality1, personality2),
        }
    
    def _compute_emotional_alignment(
        self,
        p1: Dict, p2: Dict,
        vec1: np.ndarray, vec2: np.ndarray
    ) -> float:
        """Compute emotional alignment between personas."""
        metrics1 = p1.get('metrics', {})
        metrics2 = p2.get('metrics', {})
        
        # Compare emotional stability
        stability_diff = abs(
            metrics1.get('emotional_stability', 0.5) - 
            metrics2.get('emotional_stability', 0.5)
        )
        
        # Compare agreeableness
        agree_diff = abs(
            metrics1.get('agreeableness', 0.5) - 
            metrics2.get('agreeableness', 0.5)
        )
        
        # Similar emotional profiles are more compatible
        alignment = 1 - (stability_diff + agree_diff) / 2
        
        # Also check sentiment-related features in vectors
        # Assuming sentiment features are in a specific range
        sentiment_sim = self._vector_segment_similarity(vec1, vec2, 0.3, 0.4)
        
        return (alignment * 0.6 + sentiment_sim * 0.4)
    
    def _compute_rhythm_compatibility(
        self,
        p1: Dict, p2: Dict,
        vec1: np.ndarray, vec2: np.ndarray
    ) -> float:
        """Compute conversation rhythm compatibility."""
        traits1 = p1.get('traits', {})
        traits2 = p2.get('traits', {})
        
        rhythm1 = traits1.get('conversation_rhythm', 'steady')
        rhythm2 = traits2.get('conversation_rhythm', 'steady')
        
        # Same rhythm = good compatibility
        if rhythm1 == rhythm2:
            base_score = 0.9
        # Quick + thoughtful can complement
        elif set([rhythm1, rhythm2]) == {'quick', 'thoughtful'}:
            base_score = 0.6
        else:
            base_score = 0.7
        
        # Check temporal features similarity
        temporal_sim = self._vector_segment_similarity(vec1, vec2, 0, 0.1)
        
        return base_score * 0.7 + temporal_sim * 0.3
    
    def _compute_topic_affinity(
        self,
        p1: Dict, p2: Dict,
        vec1: np.ndarray, vec2: np.ndarray
    ) -> float:
        """Compute topic/semantic affinity."""
        # Use semantic features from vectors
        semantic_sim = self._vector_segment_similarity(vec1, vec2, 0.4, 0.6)
        
        # Check openness trait
        metrics1 = p1.get('metrics', {})
        metrics2 = p2.get('metrics', {})
        
        openness1 = metrics1.get('openness', 0.5)
        openness2 = metrics2.get('openness', 0.5)
        
        # High openness in both = more topic flexibility
        openness_bonus = (openness1 + openness2) / 4
        
        return min(1.0, semantic_sim + openness_bonus)
    
    def _compute_social_energy_match(self, p1: Dict, p2: Dict) -> float:
        """Compute social energy compatibility."""
        metrics1 = p1.get('metrics', {})
        metrics2 = p2.get('metrics', {})
        
        extraversion1 = metrics1.get('extraversion', 0.5)
        extraversion2 = metrics2.get('extraversion', 0.5)
        
        # Similar energy levels work well
        energy_diff = abs(extraversion1 - extraversion2)
        similarity_score = 1 - energy_diff
        
        # But complementary can also work (introvert + extrovert)
        if energy_diff > 0.4:
            # Check if it's a complementary match
            complementary_bonus = 0.2
        else:
            complementary_bonus = 0
        
        return min(1.0, similarity_score + complementary_bonus)
    
    def _compute_linguistic_similarity(
        self,
        p1: Dict, p2: Dict,
        vec1: np.ndarray, vec2: np.ndarray
    ) -> float:
        """Compute linguistic style similarity."""
        traits1 = p1.get('traits', {})
        traits2 = p2.get('traits', {})
        
        style1 = traits1.get('communication_style', 'balanced')
        style2 = traits2.get('communication_style', 'balanced')
        
        # Same style = high compatibility
        if style1 == style2:
            style_score = 0.9
        else:
            style_score = 0.6
        
        # Check linguistic features in vectors
        linguistic_sim = self._vector_segment_similarity(vec1, vec2, 0.2, 0.3)
        
        return style_score * 0.5 + linguistic_sim * 0.5
    
    def _compute_trait_complementarity(self, p1: Dict, p2: Dict) -> float:
        """Compute how well traits complement each other."""
        metrics1 = p1.get('metrics', {})
        metrics2 = p2.get('metrics', {})
        
        scores = []
        
        # Conscientiousness - similar is good
        consc_diff = abs(
            metrics1.get('conscientiousness', 0.5) - 
            metrics2.get('conscientiousness', 0.5)
        )
        scores.append(1 - consc_diff)
        
        # Agreeableness - at least one should be high
        agree_max = max(
            metrics1.get('agreeableness', 0.5),
            metrics2.get('agreeableness', 0.5)
        )
        scores.append(agree_max)
        
        # Openness - similar or both high is good
        open1 = metrics1.get('openness', 0.5)
        open2 = metrics2.get('openness', 0.5)
        openness_score = 1 - abs(open1 - open2) * 0.5 + (open1 + open2) * 0.25
        scores.append(min(1.0, openness_score))
        
        return np.mean(scores)
    
    def _vector_segment_similarity(
        self,
        vec1: np.ndarray,
        vec2: np.ndarray,
        start_ratio: float,
        end_ratio: float
    ) -> float:
        """Compute similarity for a segment of the vectors."""
        n = len(vec1)
        start = int(n * start_ratio)
        end = int(n * end_ratio)
        
        if start >= end or end > n:
            return 0.5
        
        seg1 = vec1[start:end]
        seg2 = vec2[start:end]
        
        # Use cosine similarity
        try:
            similarity = 1 - cosine(seg1, seg2)
            return max(0, min(1, similarity))
        except:
            return 0.5
    
    def _generate_compatibility_insights(
        self,
        scores: Dict[str, float],
        persona1: Dict,
        persona2: Dict
    ) -> List[str]:
        """Generate human-readable insights about compatibility."""
        insights = []
        name1 = persona1['user_name']
        name2 = persona2['user_name']
        
        # Emotional alignment insight
        if scores['emotional_alignment'] > 0.7:
            insights.append(f"{name1} and {name2} share similar emotional wavelengths, leading to natural understanding.")
        elif scores['emotional_alignment'] < 0.4:
            insights.append(f"Emotional expression styles differ significantly, which may require patience.")
        
        # Rhythm insight
        if scores['conversation_rhythm'] > 0.7:
            insights.append("Their conversation pacing naturally syncs up well.")
        elif scores['conversation_rhythm'] < 0.4:
            insights.append("Different conversation tempos may need adjustment.")
        
        # Social energy insight
        if scores['social_energy_match'] > 0.7:
            insights.append("Similar social energy levels create comfortable interaction.")
        
        # Linguistic insight
        if scores['linguistic_similarity'] > 0.7:
            insights.append("Communication styles are well-matched for easy understanding.")
        
        return insights
    
    def _identify_strengths(self, scores: Dict[str, float]) -> List[str]:
        """Identify relationship strengths."""
        strengths = []
        
        if scores['emotional_alignment'] > 0.7:
            strengths.append("Strong emotional understanding")
        if scores['conversation_rhythm'] > 0.7:
            strengths.append("Natural conversation flow")
        if scores['topic_affinity'] > 0.7:
            strengths.append("Shared interests and topics")
        if scores['social_energy_match'] > 0.7:
            strengths.append("Compatible energy levels")
        if scores['linguistic_similarity'] > 0.7:
            strengths.append("Similar communication styles")
        if scores['trait_complementarity'] > 0.7:
            strengths.append("Complementary personalities")
        
        return strengths if strengths else ["Potential for growth together"]
    
    def _identify_challenges(self, scores: Dict[str, float]) -> List[str]:
        """Identify potential challenges."""
        challenges = []
        
        if scores['emotional_alignment'] < 0.4:
            challenges.append("May need to work on emotional attunement")
        if scores['conversation_rhythm'] < 0.4:
            challenges.append("Conversation pacing differences")
        if scores['social_energy_match'] < 0.4:
            challenges.append("Different social energy needs")
        if scores['linguistic_similarity'] < 0.4:
            challenges.append("Communication style gaps")
        
        return challenges if challenges else ["No major challenges identified"]
    
    def _generate_recommendations(
        self,
        scores: Dict[str, float],
        p1: Dict,
        p2: Dict
    ) -> List[str]:
        """Generate recommendations for better interaction."""
        recommendations = []
        
        if scores['conversation_rhythm'] < 0.5:
            recommendations.append("Be patient with different response times")
        
        if scores['emotional_alignment'] < 0.5:
            recommendations.append("Express emotions clearly and check in often")
        
        if scores['linguistic_similarity'] < 0.5:
            recommendations.append("Adapt communication style when needed")
        
        if scores['social_energy_match'] < 0.5:
            recommendations.append("Respect different social energy needs")
        
        if not recommendations:
            recommendations.append("Continue building on your natural compatibility")
        
        return recommendations
    
    def find_best_matches(
        self,
        persona_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find the best matching personas for a given persona."""
        if persona_id not in self.personas:
            raise ValueError(f"Persona {persona_id} not found")
        
        matches = []
        
        for other_id in self.personas:
            if other_id == persona_id:
                continue
            
            try:
                compatibility = self.compute_compatibility(persona_id, other_id)
                matches.append({
                    'persona_id': other_id,
                    'user_name': self.personas[other_id]['user_name'],
                    'overall_score': compatibility['overall_score'],
                    'top_strength': compatibility['strengths'][0] if compatibility['strengths'] else None,
                })
            except Exception as e:
                logger.warning(f"Failed to compute compatibility with {other_id}: {e}")
        
        # Sort by score descending
        matches.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return matches[:top_k]
    
    def get_ecosystem_stats(self) -> Dict[str, Any]:
        """Get statistics about the ecosystem."""
        if not self.personas:
            return {
                'total_personas': 0,
                'avg_extraversion': 0,
                'avg_agreeableness': 0,
                'total_interactions': 0,
            }
        
        extraversions = []
        agreeableness = []
        total_interactions = 0
        
        for persona in self.personas.values():
            metrics = persona.get('personality', {}).get('metrics', {})
            extraversions.append(metrics.get('extraversion', 0.5))
            agreeableness.append(metrics.get('agreeableness', 0.5))
            total_interactions += persona.get('interaction_count', 0)
        
        return {
            'total_personas': len(self.personas),
            'avg_extraversion': round(np.mean(extraversions), 3),
            'avg_agreeableness': round(np.mean(agreeableness), 3),
            'total_interactions': total_interactions,
        }
    
    def increment_interaction(self, persona_id: str):
        """Increment interaction count for a persona."""
        if persona_id in self.personas:
            self.personas[persona_id]['interaction_count'] = \
                self.personas[persona_id].get('interaction_count', 0) + 1
            self._save_personas()
