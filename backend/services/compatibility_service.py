"""
Compatibility Score Service
Uses Google's Gemini API to calculate compatibility scores between users
based on their extracted behavior features.

Fallback chain: Gemini -> Ollama (local) -> Algorithmic
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger(__name__)

# Ollama configuration for local LLM fallback
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2')


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
        user2_name: str = "User 2",
        messages: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calculate compatibility score between two users based on their features.
        
        Fallback chain: Gemini -> Ollama (local) -> Algorithmic
        
        Args:
            user1_features: Feature dictionary for user 1
            user2_features: Feature dictionary for user 2
            user1_name: Display name for user 1
            user2_name: Display name for user 2
            messages: Optional list of conversation messages for context
            
        Returns:
            Dictionary with compatibility score and analysis
        """
        # === STEP 1: Try Gemini API ===
        if self.client is not None and self.model is not None:
            try:
                result = await self._gemini_compatibility(user1_features, user2_features, user1_name, user2_name, messages)
                return result
            except Exception as e:
                logger.warning(f"Gemini compatibility failed: {e}, trying Ollama...")
        
        # === STEP 2: Fallback to Ollama (local LLM) ===
        logger.info(f"Falling back to Ollama ({OLLAMA_MODEL}) for compatibility...")
        ollama_result = await self._ollama_compatibility(user1_features, user2_features, user1_name, user2_name, messages)
        if ollama_result:
            return ollama_result
        
        # === STEP 3: Algorithmic fallback ===
        logger.warning("All LLMs unavailable - using algorithmic fallback")
        return self._fallback_compatibility(user1_features, user2_features, user1_name, user2_name)
    
    async def _gemini_compatibility(
        self,
        user1_features: Dict[str, Any],
        user2_features: Dict[str, Any],
        user1_name: str,
        user2_name: str,
        messages: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Calculate compatibility using Gemini."""
        prompt = self._build_compatibility_prompt(user1_features, user2_features, user1_name, user2_name, messages)

        try:
            response = self.client.models.generate_content(model=self.model, contents=prompt)
            result_text = response.text.strip()
            
            parsed = self._parse_llm_response(result_text, user1_name, user2_name, 'gemini')
            if parsed:
                return parsed
            else:
                raise ValueError("Failed to parse Gemini response as JSON")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            raise  # Re-raise to trigger fallback chain
        except Exception as e:
            logger.error(f"Gemini compatibility calculation failed: {e}")
            raise  # Re-raise to trigger fallback chain
    
    def _build_compatibility_prompt(
        self,
        user1_features: Dict[str, Any],
        user2_features: Dict[str, Any],
        user1_name: str,
        user2_name: str,
        messages: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Build the compatibility analysis prompt for LLMs."""
        user1_summary = self._prepare_feature_summary(user1_features, user1_name)
        user2_summary = self._prepare_feature_summary(user2_features, user2_name)
        
        # Prepare message snippet (~100 messages)
        message_snippet = ""
        if messages and len(messages) > 0:
            snippet_messages = messages[-100:] if len(messages) > 100 else messages
            message_snippet = "\n\n## Conversation Sample (~100 messages)\n\n"
            for msg in snippet_messages:
                sender = msg.get('sender', 'Unknown')
                text = msg.get('text', '')
                if len(text) > 200:
                    text = text[:200] + "..."
                message_snippet += f"{sender}: {text}\n"
        
        return f"""Analyze the communication compatibility between two people based on their conversation behavior profiles and actual conversation examples.

{user1_name}'s Communication Profile:
{user1_summary}

{user2_name}'s Communication Profile:
{user2_summary}
{message_snippet}

Based on these behavioral profiles and the conversation examples above, provide a compatibility analysis in the following JSON format:
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
    
    def _parse_llm_response(self, result_text: str, user1_name: str, user2_name: str, method: str) -> Optional[Dict[str, Any]]:
        """Parse LLM response and return compatibility result.
        
        Attempts multiple parsing strategies to handle varied LLM output formats.
        """
        import re
        
        # Clean up response if needed
        result_text = result_text.strip()
        
        # Remove markdown code blocks
        if result_text.startswith('```json'):
            result_text = result_text[7:]
        if result_text.startswith('```'):
            result_text = result_text[3:]
        if result_text.endswith('```'):
            result_text = result_text[:-3]
        result_text = result_text.strip()
        
        # Strategy 1: Try direct JSON parse
        try:
            result = json.loads(result_text)
            result['method'] = method
            result['user1'] = user1_name
            result['user2'] = user2_name
            return result
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Try to find JSON object in the text using regex
        json_match = re.search(r'\{[\s\S]*"overall_score"[\s\S]*\}', result_text)
        if json_match:
            try:
                result = json.loads(json_match.group())
                result['method'] = method
                result['user1'] = user1_name
                result['user2'] = user2_name
                return result
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Try to extract key values manually for a partial result
        try:
            # Extract overall_score
            score_match = re.search(r'"overall_score"\s*:\s*(\d+)', result_text)
            style_match = re.search(r'"communication_style_match"\s*:\s*(\d+)', result_text)
            emotional_match = re.search(r'"emotional_compatibility"\s*:\s*(\d+)', result_text)
            engagement_match = re.search(r'"engagement_balance"\s*:\s*(\d+)', result_text)
            summary_match = re.search(r'"summary"\s*:\s*"([^"]*)"', result_text)
            
            if score_match:
                result = {
                    'overall_score': int(score_match.group(1)),
                    'communication_style_match': int(style_match.group(1)) if style_match else 50,
                    'emotional_compatibility': int(emotional_match.group(1)) if emotional_match else 50,
                    'engagement_balance': int(engagement_match.group(1)) if engagement_match else 50,
                    'strengths': ['LLM analysis available'],
                    'challenges': ['Partial analysis due to parsing'],
                    'recommendations': ['Consider retrying for full analysis'],
                    'summary': summary_match.group(1) if summary_match else 'Compatibility analysis completed.',
                    'method': f'{method}_partial',
                    'user1': user1_name,
                    'user2': user2_name
                }
                logger.info(f"Used partial parsing for {method} response")
                return result
        except Exception as e:
            logger.warning(f"Partial parsing failed for {method}: {e}")
        
        logger.error(f"Failed to parse {method} response after all strategies")
        return None
    
    async def _ollama_compatibility(
        self,
        user1_features: Dict[str, Any],
        user2_features: Dict[str, Any],
        user1_name: str,
        user2_name: str,
        messages: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate compatibility using local Ollama as fallback.
        
        Args:
            user1_features: Feature dictionary for user 1
            user2_features: Feature dictionary for user 2
            user1_name: Display name for user 1
            user2_name: Display name for user 2
            messages: Optional list of conversation messages for context
            
        Returns:
            Compatibility result dict, or None if Ollama is unavailable
        """
        prompt = self._build_compatibility_prompt(user1_features, user2_features, user1_name, user2_name, messages)
        
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": 1024
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ollama_response = result.get("response", "").strip()
                    
                    if ollama_response:
                        logger.info(f"Ollama compatibility response: {len(ollama_response)} chars")
                        parsed = self._parse_llm_response(ollama_response, user1_name, user2_name, 'ollama')
                        if parsed:
                            return parsed
                        else:
                            logger.warning("Failed to parse Ollama response as JSON")
                else:
                    logger.warning(f"Ollama returned status {response.status_code}")
                    
        except httpx.ConnectError:
            logger.warning("Ollama not available (connection refused) - is Ollama running?")
        except httpx.TimeoutException:
            logger.warning("Ollama request timed out (90s)")
        except Exception as e:
            logger.warning(f"Ollama compatibility failed: {type(e).__name__}: {e}")
        
        return None
    
    def _prepare_feature_summary(self, features: Dict[str, Any], user_name: str) -> str:
        """Prepare a human-readable summary of user features for the prompt."""
        categories = features.get('categories', {})
        
        # Helper to safely get numeric value (handles numpy types)
        def safe_float(val, default=0):
            if val is None:
                return default
            if hasattr(val, 'item'):
                return float(val.item())
            try:
                return float(val)
            except (TypeError, ValueError):
                return default
        
        summary_parts = []
        
        # Sentiment profile
        if 'sentiment' in categories:
            sent = categories['sentiment']
            sentiment_mean = safe_float(sent.get('mean', sent.get('sentiment_mean', 0)))
            positive_ratio = safe_float(sent.get('positive_ratio', 0))
            volatility = safe_float(sent.get('volatility', sent.get('sentiment_volatility', 0)))
            
            mood = "positive" if sentiment_mean > 0.1 else "negative" if sentiment_mean < -0.1 else "neutral"
            summary_parts.append(f"- Emotional tone: Generally {mood} (positivity: {positive_ratio:.0%})")
            summary_parts.append(f"- Emotional stability: {'Stable' if volatility < 0.3 else 'Variable'}")
        
        # Communication style
        if 'behavioral' in categories:
            beh = categories['behavioral']
            formality = safe_float(beh.get('formality_score', 0.5), 0.5)
            directness = safe_float(beh.get('directness_score', 0.5), 0.5)
            assertiveness = safe_float(beh.get('assertiveness_score', 0.5), 0.5)
            
            style = "formal" if formality > 0.6 else "casual" if formality < 0.4 else "balanced"
            summary_parts.append(f"- Communication style: {style.capitalize()}")
            summary_parts.append(f"- Directness: {'Direct' if directness > 0.6 else 'Indirect' if directness < 0.4 else 'Moderate'}")
            summary_parts.append(f"- Assertiveness: {'High' if assertiveness > 0.6 else 'Low' if assertiveness < 0.4 else 'Moderate'}")
        
        # Engagement patterns
        if 'behavioral' in categories:
            beh = categories['behavioral']
            engagement = safe_float(beh.get('engagement_level', 0.5), 0.5)
            response_rate = safe_float(beh.get('response_rate', 0.5), 0.5)
            
            summary_parts.append(f"- Engagement level: {'High' if engagement > 0.6 else 'Low' if engagement < 0.4 else 'Moderate'}")
            summary_parts.append(f"- Responsiveness: {response_rate:.0%}")
        
        # Reaction patterns
        if 'reaction' in categories:
            react = categories['reaction']
            mirroring = safe_float(react.get('sentiment_mirroring', 0.5), 0.5)
            support = safe_float(react.get('support_reactivity', 0), 0)
            adaptation = safe_float(react.get('style_adaptation', 0.5), 0.5)
            
            summary_parts.append(f"- Emotional mirroring: {'High' if mirroring > 0.6 else 'Low' if mirroring < 0.4 else 'Moderate'}")
            summary_parts.append(f"- Supportiveness: {'High' if support > 0.3 else 'Low' if support < 0.1 else 'Moderate'}")
            summary_parts.append(f"- Adaptability: {'High' if adaptation > 0.6 else 'Low' if adaptation < 0.4 else 'Moderate'}")
        
        # Composite scores
        if 'composite' in categories:
            comp = categories['composite']
            eq = safe_float(comp.get('emotional_intelligence_proxy', 0.5), 0.5)
            coherence = safe_float(comp.get('topic_coherence_score', 0.5), 0.5)
            
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
        
        # Extract vectors and convert to Python lists if needed
        vec1 = user1_features.get('vector', [])
        vec2 = user2_features.get('vector', [])
        
        # Convert to list if numpy array
        if hasattr(vec1, 'tolist'):
            vec1 = vec1.tolist()
        if hasattr(vec2, 'tolist'):
            vec2 = vec2.tolist()
        
        # Check for empty or invalid vectors
        if not vec1 or not vec2 or (hasattr(vec1, '__len__') and len(vec1) == 0):
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
    
    def _safe_float(self, val, default=0.5):
        """Safely convert a value to float, handling numpy types."""
        if val is None:
            return default
        if hasattr(val, 'item'):
            return float(val.item())
        try:
            return float(val)
        except (TypeError, ValueError):
            return default
    
    def _calculate_style_match(self, cat1: Dict, cat2: Dict) -> float:
        """Calculate communication style match."""
        beh1 = cat1.get('behavioral', {})
        beh2 = cat2.get('behavioral', {})
        
        formality_diff = abs(self._safe_float(beh1.get('formality_score', 0.5)) - self._safe_float(beh2.get('formality_score', 0.5)))
        directness_diff = abs(self._safe_float(beh1.get('directness_score', 0.5)) - self._safe_float(beh2.get('directness_score', 0.5)))
        
        return 1 - (formality_diff + directness_diff) / 2
    
    def _calculate_emotional_compatibility(self, cat1: Dict, cat2: Dict) -> float:
        """Calculate emotional compatibility."""
        sent1 = cat1.get('sentiment', {})
        sent2 = cat2.get('sentiment', {})
        react1 = cat1.get('reaction', {})
        react2 = cat2.get('reaction', {})
        
        # Similar positivity levels
        pos_diff = abs(self._safe_float(sent1.get('positive_ratio', 0.5)) - self._safe_float(sent2.get('positive_ratio', 0.5)))
        
        # Emotional responsiveness
        resp1 = self._safe_float(react1.get('emotional_responsiveness', 0.5))
        resp2 = self._safe_float(react2.get('emotional_responsiveness', 0.5))
        avg_responsiveness = (resp1 + resp2) / 2
        
        # Support reactivity
        support1 = self._safe_float(react1.get('support_reactivity', 0), 0)
        support2 = self._safe_float(react2.get('support_reactivity', 0), 0)
        avg_support = (support1 + support2) / 2
        
        return (1 - pos_diff) * 0.4 + avg_responsiveness * 0.3 + avg_support * 0.3
    
    def _calculate_engagement_balance(self, cat1: Dict, cat2: Dict) -> float:
        """Calculate engagement balance."""
        beh1 = cat1.get('behavioral', {})
        beh2 = cat2.get('behavioral', {})
        react1 = cat1.get('reaction', {})
        react2 = cat2.get('reaction', {})
        
        # Reciprocity
        recip1 = self._safe_float(react1.get('reciprocity_balance', 0.5))
        recip2 = self._safe_float(react2.get('reciprocity_balance', 0.5))
        
        # Engagement levels
        eng1 = self._safe_float(beh1.get('engagement_level', 0.5))
        eng2 = self._safe_float(beh2.get('engagement_level', 0.5))
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
