"""
Compatibility Score Service
Uses Google's Gemini API to calculate compatibility scores between users
based on their extracted behavior features.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class CompatibilityService:
    """Calculates compatibility scores using Gemini LLM."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        self._init_model()
    
    def _init_model(self):
        """Initialize Gemini model."""
        if not self.api_key:
            logger.warning("No Gemini API key provided. Compatibility scoring will use fallback method.")
            return
        
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.model = 'gemini-3-flash-preview'
            logger.info(f"Gemini model initialized successfully: {self.model}")
        except ImportError:
            logger.warning("google-genai not installed. Install with: pip install google-genai")
            self.client = None
            self.model = None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            self.client = None
            self.model = None
    
    async def calculate_compatibility(
        self,
        user1_features: Dict[str, Any],
        user2_features: Dict[str, Any],
        user1_name: str = "User 1",
        user2_name: str = "User 2"
    ) -> Dict[str, Any]:
        """
        Calculate compatibility score between two users based on their features.
        
        Args:
            user1_features: Feature dictionary for user 1
            user2_features: Feature dictionary for user 2
            user1_name: Display name for user 1
            user2_name: Display name for user 2
            
        Returns:
            Dictionary with compatibility score and analysis
        """
        if self.client is None or self.model is None:
            return self._fallback_compatibility(user1_features, user2_features, user1_name, user2_name)
        
        try:
            return await self._gemini_compatibility(user1_features, user2_features, user1_name, user2_name)
        except Exception as e:
            logger.error(f"Gemini compatibility calculation failed: {e}")
            return self._fallback_compatibility(user1_features, user2_features, user1_name, user2_name)
    
    async def _gemini_compatibility(
        self,
        user1_features: Dict[str, Any],
        user2_features: Dict[str, Any],
        user1_name: str,
        user2_name: str
    ) -> Dict[str, Any]:
        """Calculate compatibility using Gemini."""
        # Prepare feature summaries for the prompt
        user1_summary = self._prepare_feature_summary(user1_features, user1_name)
        user2_summary = self._prepare_feature_summary(user2_features, user2_name)
        
        prompt = f"""Analyze the communication compatibility between two people based on their conversation behavior profiles.

{user1_name}'s Communication Profile:
{user1_summary}

{user2_name}'s Communication Profile:
{user2_summary}

Based on these behavioral profiles, provide a compatibility analysis in the following JSON format:
{{
    "overall_score": <number between 0-100>,
    "communication_style_match": <number between 0-100>,
    "emotional_compatibility": <number between 0-100>,
    "engagement_balance": <number between 0-100>,
    "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
    "challenges": ["<challenge 1>", "<challenge 2>"],
    "recommendations": ["<recommendation 1>", "<recommendation 2>"],
    "summary": "<2-3 sentence summary of compatibility>"
}}

Consider factors like:
- Communication style alignment (formality, directness, expressiveness)
- Emotional responsiveness and sentiment patterns
- Engagement levels and reciprocity
- Topic handling and conversation flow
- Adaptive behaviors and synchrony

Return ONLY the JSON object, no additional text."""

        try:
            response = self.client.models.generate_content(model=self.model, contents=prompt)
            result_text = response.text.strip()
            
            # Clean up response if needed
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            result = json.loads(result_text.strip())
            result['method'] = 'gemini'
            result['user1'] = user1_name
            result['user2'] = user2_name
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            return self._fallback_compatibility(user1_features, user2_features, user1_name, user2_name)
        except Exception as e:
            logger.error(f"Gemini compatibility calculation failed: {e}")
            return self._fallback_compatibility(user1_features, user2_features, user1_name, user2_name)
    
    def _prepare_feature_summary(self, features: Dict[str, Any], user_name: str) -> str:
        """Prepare a human-readable summary of user features for the prompt."""
        categories = features.get('categories', {})
        
        summary_parts = []
        
        # Sentiment profile
        if 'sentiment' in categories:
            sent = categories['sentiment']
            sentiment_mean = sent.get('mean', sent.get('sentiment_mean', 0))
            positive_ratio = sent.get('positive_ratio', 0)
            volatility = sent.get('volatility', sent.get('sentiment_volatility', 0))
            
            mood = "positive" if sentiment_mean > 0.1 else "negative" if sentiment_mean < -0.1 else "neutral"
            summary_parts.append(f"- Emotional tone: Generally {mood} (positivity: {positive_ratio:.0%})")
            summary_parts.append(f"- Emotional stability: {'Stable' if volatility < 0.3 else 'Variable'}")
        
        # Communication style
        if 'behavioral' in categories:
            beh = categories['behavioral']
            formality = beh.get('formality_score', 0.5)
            directness = beh.get('directness_score', 0.5)
            assertiveness = beh.get('assertiveness_score', 0.5)
            
            style = "formal" if formality > 0.6 else "casual" if formality < 0.4 else "balanced"
            summary_parts.append(f"- Communication style: {style.capitalize()}")
            summary_parts.append(f"- Directness: {'Direct' if directness > 0.6 else 'Indirect' if directness < 0.4 else 'Moderate'}")
            summary_parts.append(f"- Assertiveness: {'High' if assertiveness > 0.6 else 'Low' if assertiveness < 0.4 else 'Moderate'}")
        
        # Engagement patterns
        if 'behavioral' in categories:
            beh = categories['behavioral']
            engagement = beh.get('engagement_level', 0.5)
            response_rate = beh.get('response_rate', 0.5)
            
            summary_parts.append(f"- Engagement level: {'High' if engagement > 0.6 else 'Low' if engagement < 0.4 else 'Moderate'}")
            summary_parts.append(f"- Responsiveness: {response_rate:.0%}")
        
        # Reaction patterns
        if 'reaction' in categories:
            react = categories['reaction']
            mirroring = react.get('sentiment_mirroring', 0.5)
            support = react.get('support_reactivity', 0)
            adaptation = react.get('style_adaptation', 0.5)
            
            summary_parts.append(f"- Emotional mirroring: {'High' if mirroring > 0.6 else 'Low' if mirroring < 0.4 else 'Moderate'}")
            summary_parts.append(f"- Supportiveness: {'High' if support > 0.3 else 'Low' if support < 0.1 else 'Moderate'}")
            summary_parts.append(f"- Adaptability: {'High' if adaptation > 0.6 else 'Low' if adaptation < 0.4 else 'Moderate'}")
        
        # Composite scores
        if 'composite' in categories:
            comp = categories['composite']
            eq = comp.get('emotional_intelligence_proxy', 0.5)
            coherence = comp.get('topic_coherence_score', 0.5)
            
            summary_parts.append(f"- Emotional intelligence: {'High' if eq > 0.6 else 'Low' if eq < 0.4 else 'Moderate'}")
            summary_parts.append(f"- Topic coherence: {'High' if coherence > 0.6 else 'Low' if coherence < 0.4 else 'Moderate'}")
        
        return '\n'.join(summary_parts) if summary_parts else "Limited data available"
    
    def _fallback_compatibility(
        self,
        user1_features: Dict[str, Any],
        user2_features: Dict[str, Any],
        user1_name: str,
        user2_name: str
    ) -> Dict[str, Any]:
        """Calculate compatibility using algorithmic fallback when Gemini is unavailable."""
        import numpy as np
        
        # Extract vectors
        vec1 = user1_features.get('vector', [])
        vec2 = user2_features.get('vector', [])
        
        if not vec1 or not vec2:
            return {
                'overall_score': 50,
                'communication_style_match': 50,
                'emotional_compatibility': 50,
                'engagement_balance': 50,
                'strengths': ['Insufficient data for detailed analysis'],
                'challenges': ['More conversation data needed'],
                'recommendations': ['Continue conversing to build a better profile'],
                'summary': 'Not enough data to determine compatibility accurately.',
                'method': 'fallback',
                'user1': user1_name,
                'user2': user2_name
            }
        
        # Ensure same length
        min_len = min(len(vec1), len(vec2))
        vec1 = np.array(vec1[:min_len])
        vec2 = np.array(vec2[:min_len])
        
        # Calculate various compatibility metrics
        
        # 1. Cosine similarity (overall similarity)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 > 0 and norm2 > 0:
            cosine_sim = np.dot(vec1, vec2) / (norm1 * norm2)
        else:
            cosine_sim = 0
        
        # 2. Complementarity score (some differences are good)
        diff = np.abs(vec1 - vec2)
        complementarity = 1 - np.mean(diff)
        
        # 3. Category-specific scores
        cat1 = user1_features.get('categories', {})
        cat2 = user2_features.get('categories', {})
        
        # Communication style match
        style_match = self._calculate_style_match(cat1, cat2)
        
        # Emotional compatibility
        emotional_compat = self._calculate_emotional_compatibility(cat1, cat2)
        
        # Engagement balance
        engagement_balance = self._calculate_engagement_balance(cat1, cat2)
        
        # Overall score (weighted average)
        overall = (
            cosine_sim * 0.2 +
            complementarity * 0.2 +
            style_match * 0.25 +
            emotional_compat * 0.2 +
            engagement_balance * 0.15
        ) * 100
        
        # Generate insights
        strengths, challenges, recommendations = self._generate_insights(
            cat1, cat2, style_match, emotional_compat, engagement_balance
        )
        
        return {
            'overall_score': round(max(0, min(100, overall))),
            'communication_style_match': round(style_match * 100),
            'emotional_compatibility': round(emotional_compat * 100),
            'engagement_balance': round(engagement_balance * 100),
            'strengths': strengths,
            'challenges': challenges,
            'recommendations': recommendations,
            'summary': self._generate_summary(overall, style_match, emotional_compat),
            'method': 'algorithmic',
            'user1': user1_name,
            'user2': user2_name
        }
    
    def _calculate_style_match(self, cat1: Dict, cat2: Dict) -> float:
        """Calculate communication style match."""
        beh1 = cat1.get('behavioral', {})
        beh2 = cat2.get('behavioral', {})
        
        formality_diff = abs(beh1.get('formality_score', 0.5) - beh2.get('formality_score', 0.5))
        directness_diff = abs(beh1.get('directness_score', 0.5) - beh2.get('directness_score', 0.5))
        
        return 1 - (formality_diff + directness_diff) / 2
    
    def _calculate_emotional_compatibility(self, cat1: Dict, cat2: Dict) -> float:
        """Calculate emotional compatibility."""
        sent1 = cat1.get('sentiment', {})
        sent2 = cat2.get('sentiment', {})
        react1 = cat1.get('reaction', {})
        react2 = cat2.get('reaction', {})
        
        # Similar positivity levels
        pos_diff = abs(sent1.get('positive_ratio', 0.5) - sent2.get('positive_ratio', 0.5))
        
        # Emotional responsiveness
        resp1 = react1.get('emotional_responsiveness', 0.5)
        resp2 = react2.get('emotional_responsiveness', 0.5)
        avg_responsiveness = (resp1 + resp2) / 2
        
        # Support reactivity
        support1 = react1.get('support_reactivity', 0)
        support2 = react2.get('support_reactivity', 0)
        avg_support = (support1 + support2) / 2
        
        return (1 - pos_diff) * 0.4 + avg_responsiveness * 0.3 + avg_support * 0.3
    
    def _calculate_engagement_balance(self, cat1: Dict, cat2: Dict) -> float:
        """Calculate engagement balance."""
        beh1 = cat1.get('behavioral', {})
        beh2 = cat2.get('behavioral', {})
        react1 = cat1.get('reaction', {})
        react2 = cat2.get('reaction', {})
        
        # Reciprocity
        recip1 = react1.get('reciprocity_balance', 0.5)
        recip2 = react2.get('reciprocity_balance', 0.5)
        
        # Engagement levels
        eng1 = beh1.get('engagement_level', 0.5)
        eng2 = beh2.get('engagement_level', 0.5)
        eng_diff = abs(eng1 - eng2)
        
        return ((recip1 + recip2) / 2) * 0.5 + (1 - eng_diff) * 0.5
    
    def _generate_insights(
        self,
        cat1: Dict,
        cat2: Dict,
        style_match: float,
        emotional_compat: float,
        engagement_balance: float
    ) -> tuple:
        """Generate strengths, challenges, and recommendations."""
        strengths = []
        challenges = []
        recommendations = []
        
        if style_match > 0.7:
            strengths.append("Similar communication styles")
        elif style_match < 0.4:
            challenges.append("Different communication styles may cause misunderstandings")
            recommendations.append("Be mindful of communication style differences")
        
        if emotional_compat > 0.7:
            strengths.append("Strong emotional connection potential")
        elif emotional_compat < 0.4:
            challenges.append("Emotional wavelengths may not always align")
            recommendations.append("Practice active listening and emotional validation")
        
        if engagement_balance > 0.7:
            strengths.append("Balanced conversation dynamics")
        elif engagement_balance < 0.4:
            challenges.append("Uneven engagement levels")
            recommendations.append("Ensure both parties have equal opportunity to contribute")
        
        # Add default if empty
        if not strengths:
            strengths.append("Potential for growth through differences")
        if not challenges:
            challenges.append("No major challenges identified")
        if not recommendations:
            recommendations.append("Continue building on your communication strengths")
        
        return strengths[:3], challenges[:2], recommendations[:2]
    
    def _generate_summary(self, overall: float, style_match: float, emotional_compat: float) -> str:
        """Generate a summary statement."""
        if overall >= 75:
            return "Excellent compatibility! Your communication styles and emotional patterns complement each other well."
        elif overall >= 60:
            return "Good compatibility with room for growth. You share common ground in communication."
        elif overall >= 45:
            return "Moderate compatibility. Some differences exist but can be bridged with understanding."
        else:
            return "Compatibility requires effort. Focus on understanding each other's communication needs."
