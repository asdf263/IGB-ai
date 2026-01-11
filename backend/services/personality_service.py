"""
AI Personality Synthesis Service
Generates custom LLM prompts that shape chatbot voice, tone, style, pacing, and quirks
based on extracted user features from conversation analysis.

Uses a Personality Vector approach where normalized numerical feature values
guide the LLM's generation style as weighted constraints.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)


class PersonalityService:
    """Synthesizes AI personalities from user behavioral features using vector-based prompts."""
    
    def __init__(self):
        self.gemini_model = None
        self._init_gemini()
        
        # Define core personality dimensions - streamlined to 12 most impactful traits
        # Focus on traits that directly affect mimicry quality without overwhelming the LLM
        # LOW behaviors are phrased positively - as personality styles, not deficits
        self.vector_dimensions = {
            # === CORE TONE (3 dimensions) ===
            'warmth': {
                'source_features': ['synthetic_communication_warmth', 'sentiment_positive_ratio', 'behavioral_empathy_score'],
                'interpretation': 'Friendliness and emotional warmth',
                'high_behavior': 'Be warm, friendly, and openly supportive',
                'low_behavior': 'Be professionally friendly, show care through actions not words'
            },
            'energy': {
                'source_features': ['synthetic_conversational_energy', 'reaction_response_enthusiasm', 'linguistic_exclamation_ratio'],
                'interpretation': 'Energy and enthusiasm level',
                'high_behavior': 'Show high energy and excitement!',
                'low_behavior': 'Be calm and thoughtfully engaged'
            },
            'formality': {
                'source_features': ['synthetic_formality_level', 'behavioral_formality_score'],
                'interpretation': 'Formal vs casual style',
                'high_behavior': 'Use formal language and proper grammar',
                'low_behavior': 'Use casual, relaxed language with contractions'
            },
            
            # === TEXT STYLE (4 dimensions) ===
            'verbosity': {
                'source_features': ['synthetic_verbosity_level', 'text_word_count_mean', 'behavioral_elaboration_score'],
                'interpretation': 'Message length and detail',
                'high_behavior': 'Write longer, detailed messages',
                'low_behavior': 'Keep messages short and punchy'
            },
            'typing_intensity': {
                'source_features': ['text_uppercase_ratio', 'text_all_caps_word_ratio', 'linguistic_exclamation_ratio'],
                'interpretation': 'CAPS and punctuation intensity',
                'high_behavior': 'Use CAPS for emphasis, multiple punctuation!!!',
                'low_behavior': 'Use standard capitalization, clean punctuation'
            },
            'expressiveness': {
                'source_features': ['synthetic_emotional_expressiveness', 'text_emoji_density', 'text_punctuation_ratio'],
                'interpretation': 'Emoji and emotional expression',
                'high_behavior': 'Use emojis and expressive punctuation freely',
                'low_behavior': 'Express through words rather than emojis'
            },
            'message_structure': {
                'source_features': ['text_sentence_count_mean', 'text_words_per_sentence_mean'],
                'interpretation': 'Short fragments vs paragraphs',
                'high_behavior': 'Write in complete paragraphs with multiple sentences',
                'low_behavior': 'Write quick, snappy messages'
            },
            
            # === SOCIAL DYNAMICS (3 dimensions) ===
            'curiosity': {
                'source_features': ['synthetic_curiosity_openness', 'behavioral_question_frequency', 'text_question_mark_ratio'],
                'interpretation': 'Question-asking tendency',
                'high_behavior': 'Ask questions frequently, show active curiosity',
                'low_behavior': 'Share thoughts and opinions confidently'
            },
            'supportiveness': {
                'source_features': ['synthetic_supportiveness', 'behavioral_support_ratio', 'behavioral_empathy_score'],
                'interpretation': 'Empathy and support',
                'high_behavior': 'Show empathy openly, offer support',
                'low_behavior': 'Be helpful through practical advice and solutions'
            },
            'directness': {
                'source_features': ['synthetic_directness_clarity', 'behavioral_directness_score'],
                'interpretation': 'Straightforward vs indirect',
                'high_behavior': 'Be direct and clear without hedging',
                'low_behavior': 'Use thoughtful, diplomatic language'
            },
            
            # === PERSONALITY QUIRKS (2 dimensions) ===
            'humor': {
                'source_features': ['synthetic_humor_playfulness', 'behavioral_humor_density'],
                'interpretation': 'Humor and playfulness',
                'high_behavior': 'Include humor and playful banter',
                'low_behavior': 'Keep a sincere, genuine tone'
            },
            'self_focus': {
                'source_features': ['synthetic_self_focus_tendency', 'linguistic_first_person_ratio'],
                'interpretation': 'Self vs other focus',
                'high_behavior': 'Share personal experiences freely, use "I" often',
                'low_behavior': 'Focus on the other person and shared topics'
            }
        }
    
    def _init_gemini(self):
        """Initialize Gemini model for chat."""
        if not GEMINI_AVAILABLE:
            logger.warning("google-genai not installed")
            return
            
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.warning("GEMINI_API_KEY not set")
            return
            
        try:
            # Initialize the client with the new google-genai package
            self.gemini_client = genai.Client(api_key=api_key)
            self.gemini_model = 'gemini-3-flash-preview'
            logger.info(f"Gemini model initialized for personality chat: {self.gemini_model}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.gemini_client = None
            self.gemini_model = None
    
    def synthesize_personality(
        self,
        user_name: str,
        user_features: Dict[str, Any],
        sample_messages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Synthesize a complete personality profile from user features.
        
        Args:
            user_name: Name of the person
            user_features: Extracted features including categories and vector
            sample_messages: Optional sample messages for style reference
        
        Returns:
            Personality profile with personality vector, system prompt, and metadata
        """
        categories = user_features.get('categories', {})
        
        # Build the personality vector from extracted features
        personality_vector = self._build_personality_vector(categories)
        
        # Extract raw text style features for direct LLM guidance (not abstracted)
        raw_text_style = self._extract_raw_text_style(categories)
        
        # Build the vector-based system prompt with raw style features
        system_prompt = self._build_vector_system_prompt(user_name, personality_vector, sample_messages, raw_text_style)
        
        # Calculate personality metrics (Big Five)
        metrics = self._calculate_personality_metrics(categories)
        
        return {
            'user_name': user_name,
            'personality_vector': personality_vector,
            'system_prompt': system_prompt,
            'metrics': metrics,
            'feature_summary': self._summarize_features(categories)
        }
    
    def _build_personality_vector(self, categories: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Build a personality vector from extracted feature categories.
        Maps raw features to normalized personality dimensions.
        """
        vector = {}
        
        for dim_name, dim_config in self.vector_dimensions.items():
            source_features = dim_config['source_features']
            values = []
            
            for feature_name in source_features:
                value = self._find_feature_value(categories, feature_name)
                if value is not None:
                    # Handle inverted features
                    if 'hedging' in feature_name or 'contraction' in feature_name:
                        value = 1 - value  # Invert
                    values.append(value)
            
            if values:
                # Average the source features
                vector[dim_name] = round(np.mean(values), 2)
            else:
                # Default to neutral
                vector[dim_name] = 0.5
        
        return vector
    
    def _extract_raw_text_style(self, categories: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Extract only the most critical observable text patterns for LLM mimicry.
        Focus on 6 key patterns that have the highest impact on perceived authenticity.
        """
        text = categories.get('text', {})
        linguistic = categories.get('linguistic', {})
        behavioral = categories.get('behavioral', {})
        
        style = {}
        
        # 1. MESSAGE LENGTH - Most visible pattern
        avg_words = text.get('word_count_mean', 10)
        if avg_words < 5:
            style['length'] = f'Very short ({int(avg_words)} words avg) - fragments and brief responses'
        elif avg_words < 15:
            style['length'] = f'Short ({int(avg_words)} words avg) - concise messages'
        elif avg_words < 30:
            style['length'] = f'Medium ({int(avg_words)} words avg) - balanced messages'
        else:
            style['length'] = f'Long ({int(avg_words)} words avg) - detailed paragraphs'
        
        # 2. CAPS USAGE - Highly distinctive
        uppercase_ratio = text.get('uppercase_ratio', 0)
        all_caps_ratio = text.get('all_caps_word_ratio', 0)
        if uppercase_ratio > 0.2 or all_caps_ratio > 0.1:
            style['caps'] = f'HEAVY CAPS usage ({uppercase_ratio:.0%}) - uses CAPS for EMPHASIS'
        elif uppercase_ratio > 0.1 or all_caps_ratio > 0.05:
            style['caps'] = f'Moderate caps ({uppercase_ratio:.0%}) - occasional EMPHASIS'
        else:
            style['caps'] = f'Standard caps ({uppercase_ratio:.0%}) - normal capitalization'
        
        # 3. PUNCTUATION INTENSITY - Exclamations and questions
        exclamation_ratio = linguistic.get('exclamation_ratio', 0)
        question_ratio = text.get('question_mark_ratio', 0)
        if exclamation_ratio > 0.2:
            style['punctuation'] = f'High energy! Uses lots of exclamation marks! ({exclamation_ratio:.0%})'
        elif exclamation_ratio > 0.1:
            style['punctuation'] = f'Moderate energy with regular exclamations ({exclamation_ratio:.0%})'
        else:
            style['punctuation'] = f'Calm punctuation. Minimal exclamations ({exclamation_ratio:.0%})'
        
        if question_ratio > 0.2:
            style['punctuation'] += f' Asks many questions? ({question_ratio:.0%})'
        
        # 4. EMOJI USAGE - Emotional expressiveness
        emoji_density = text.get('emoji_density', 0)
        if emoji_density > 0.15:
            style['emojis'] = f'Heavy emoji user 😊✨ ({emoji_density:.1%} density)'
        elif emoji_density > 0.05:
            style['emojis'] = f'Moderate emoji use 😊 ({emoji_density:.1%} density)'
        elif emoji_density > 0.01:
            style['emojis'] = f'Rare emojis ({emoji_density:.1%} density)'
        else:
            style['emojis'] = 'No emojis'
        
        # 5. FORMALITY - Contractions and casual language
        formality = behavioral.get('formality_score', 0.5)
        if formality > 0.65:
            style['formality'] = 'Formal - proper grammar, no contractions (do not, cannot)'
        elif formality > 0.35:
            style['formality'] = "Casual - uses contractions (don't, can't, won't)"
        else:
            style['formality'] = 'Very casual - relaxed grammar, slang, abbreviations (u, ur, gonna)'
        
        # 6. SENTENCE STRUCTURE - Fragments vs complete
        sentences_per_msg = text.get('sentence_count_mean', 1)
        if sentences_per_msg < 1.2:
            style['structure'] = 'Single-sentence messages or fragments'
        elif sentences_per_msg < 2.5:
            style['structure'] = 'Short messages with 1-2 sentences'
        else:
            style['structure'] = f'Multi-sentence messages ({sentences_per_msg:.1f} sentences avg)'
        
        return style
    
    def _find_feature_value(self, categories: Dict, feature_name: str) -> Optional[float]:
        """Find a feature value across all categories."""
        for cat_name, features in categories.items():
            if isinstance(features, dict):
                # Try exact match
                if feature_name in features:
                    return features[feature_name]
                # Try partial match (feature name contains or is contained)
                for fname, fval in features.items():
                    if feature_name in fname or fname in feature_name:
                        if isinstance(fval, (int, float)) and not np.isnan(fval):
                            return fval
        return None
    
    def _build_vector_system_prompt(
        self,
        user_name: str,
        personality_vector: Dict[str, float],
        sample_messages: Optional[List[str]] = None,
        raw_text_style: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a vector-based system prompt that instructs the LLM to use
        the personality vector as weighted stylistic constraints.
        """
        # Format the vector as JSON
        vector_json = json.dumps(personality_vector, indent=2)
        
        # Build interpretation rules
        interpretation_rules = self._build_interpretation_rules(personality_vector)
        
        prompt = f"""You are embodying {user_name}'s personality and texting style. You have been given a personality profile extracted from their real messages.

## Core Principle
Bring {user_name} to life as a warm, engaged conversationalist. Even if some metrics are low, interpret them as personality quirks rather than negativity. This person WANTS to connect and communicate.

## Personality Profile (0.0=low, 1.0=high)

{vector_json}

## How to Apply These Traits

{interpretation_rules}

## Tone Guidelines
- Default to FRIENDLY and ENGAGED - assume {user_name} enjoys this conversation
- Low warmth = reserved/professional, NOT cold or dismissive
- Low energy = calm/thoughtful, NOT bored or disinterested  
- Low expressiveness = subtle/understated, NOT emotionless
- Always show genuine interest in the conversation topic

## Rules
- Respond AS {user_name}, not about them
- Never mention AI, vectors, or personality modeling
- Match their style naturally throughout the conversation
- When in doubt, lean toward warmth and engagement"""

        # Add simplified text style patterns
        if raw_text_style:
            prompt += f"""

## CRITICAL: Text Style Patterns to Match EXACTLY

{raw_text_style.get('length', 'Medium messages')}
{raw_text_style.get('caps', 'Standard capitalization')}
{raw_text_style.get('punctuation', 'Standard punctuation')}
{raw_text_style.get('emojis', 'No emojis')}
{raw_text_style.get('formality', 'Casual style')}
{raw_text_style.get('structure', 'Complete sentences')}

Match these patterns EXACTLY in your responses."""

        # Add sample messages if available
        if sample_messages and len(sample_messages) > 0:
            prompt += f"""

## Reference Messages from {user_name}

Study these EXACT messages carefully and replicate the style, punctuation, capitalization, and emoji patterns:
"""
            for i, msg in enumerate(sample_messages[:10], 1):
                # Keep more of the message to preserve style
                truncated = msg[:300] + "..." if len(msg) > 300 else msg
                prompt += f'\n{i}. "{truncated}"'

        prompt += f"""

Remember: You ARE {user_name} for this conversation. Match their EXACT texting style - same punctuation patterns, same capitalization habits, same emoji usage, same message length tendencies."""

        return prompt
    
    def _build_interpretation_rules(self, personality_vector: Dict[str, float]) -> str:
        """Build concise interpretation rules based on vector values."""
        rules = []
        
        for dim_name, value in personality_vector.items():
            if dim_name not in self.vector_dimensions:
                continue
                
            dim_config = self.vector_dimensions[dim_name]
            
            # Only include rules for non-neutral values (saves tokens)
            if value >= 0.65:
                behavior = dim_config['high_behavior']
                rules.append(f"• {dim_name.replace('_', ' ').title()} ({value}): {behavior}")
            elif value <= 0.35:
                behavior = dim_config['low_behavior']
                rules.append(f"• {dim_name.replace('_', ' ').title()} ({value}): {behavior}")
        
        # If all values are neutral, provide a baseline
        if not rules:
            rules.append("• Balanced, moderate style across all dimensions")
        
        return '\n'.join(rules)
    
    def _calculate_personality_metrics(
        self,
        categories: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """Calculate Big Five personality metrics from features."""
        metrics = {}
        
        # Extraversion (social energy, enthusiasm)
        extraversion_features = [
            self._find_feature_value(categories, 'initiation_rate'),
            self._find_feature_value(categories, 'response_enthusiasm'),
            self._find_feature_value(categories, 'exclamation_ratio'),
            self._find_feature_value(categories, 'engagement'),
        ]
        valid = [v for v in extraversion_features if v is not None]
        metrics['extraversion'] = np.mean(valid) if valid else 0.5
        
        # Agreeableness (cooperation, empathy)
        agree_features = [
            self._find_feature_value(categories, 'affirmation_tendency'),
            self._find_feature_value(categories, 'sentiment_mirroring'),
            self._find_feature_value(categories, 'support_reactivity'),
            self._find_feature_value(categories, 'empathy'),
        ]
        valid = [v for v in agree_features if v is not None]
        metrics['agreeableness'] = np.mean(valid) if valid else 0.5
        
        # Openness (curiosity, creativity)
        open_features = [
            self._find_feature_value(categories, 'topic_expansion_rate'),
            self._find_feature_value(categories, 'vocabulary_richness'),
            self._find_feature_value(categories, 'semantic_diversity'),
            self._find_feature_value(categories, 'question_ratio'),
        ]
        valid = [v for v in open_features if v is not None]
        metrics['openness'] = np.mean(valid) if valid else 0.5
        
        # Emotional Stability (inverse of neuroticism)
        stability_features = [
            self._find_feature_value(categories, 'sentiment_volatility'),
            self._find_feature_value(categories, 'emotional_volatility'),
        ]
        valid = [v for v in stability_features if v is not None]
        metrics['emotional_stability'] = 1 - np.mean(valid) if valid else 0.5
        
        # Conscientiousness (organization, dependability)
        consc_features = [
            self._find_feature_value(categories, 'formality'),
            self._find_feature_value(categories, 'response_rate'),
            self._find_feature_value(categories, 'consistency'),
        ]
        valid = [v for v in consc_features if v is not None]
        metrics['conscientiousness'] = np.mean(valid) if valid else 0.5
        
        return {k: round(v, 3) for k, v in metrics.items()}
    
    def _summarize_features(self, categories: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Create a summary of key features by category."""
        summary = {}
        
        for cat_name, features in categories.items():
            if isinstance(features, dict):
                values = [v for v in features.values() if isinstance(v, (int, float)) and not np.isnan(v)]
                if values:
                    summary[cat_name] = round(np.mean(values), 3)
        
        return summary
    
    async def chat_as_persona(
        self,
        personality: Dict[str, Any],
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Chat as the synthesized persona.
        
        Args:
            personality: Synthesized personality profile
            user_message: The user's message
            conversation_history: Previous messages in the conversation
        
        Returns:
            Response from the AI persona
        """
        if not self.gemini_client or not self.gemini_model:
            logger.warning("Gemini model not initialized - using fallback response. Check GEMINI_API_KEY environment variable.")
            return self._fallback_response(personality, user_message)
        
        try:
            # Build conversation context
            messages = []
            
            # Add system prompt
            system_prompt = personality.get('system_prompt', '')
            if not system_prompt:
                logger.warning("No system prompt found in personality profile")
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    messages.append(f"{role}: {content}")
            
            # Build the full prompt
            full_prompt = f"{system_prompt}\n\n"
            if messages:
                full_prompt += "Previous conversation:\n" + "\n".join(messages) + "\n\n"
            full_prompt += f"User: {user_message}\n\n{personality['user_name']}:"
            
            logger.info(f"Generating response for {personality['user_name']} (prompt length: {len(full_prompt)} chars)")
            
            # Generate response using the new google-genai API
            response = self.gemini_client.models.generate_content(model=self.gemini_model, contents=full_prompt)
            
            if not response or not response.text:
                logger.error("Gemini returned empty response")
                return self._fallback_response(personality, user_message)
            
            logger.info(f"Successfully generated response: {len(response.text)} chars")
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Chat error: {type(e).__name__}: {str(e)}", exc_info=True)
            return self._fallback_response(personality, user_message)
    
    def _fallback_response(self, personality: Dict[str, Any], user_message: str) -> str:
        """Generate a fallback response when Gemini is unavailable."""
        user_name = personality.get('user_name', 'Unknown')
        vector = personality.get('personality_vector', {})
        
        # Generate a simple response based on personality vector
        # Check sentiment baseline
        sentiment = vector.get('sentiment_baseline', 0.5)
        formality = vector.get('formality', 0.5)
        enthusiasm = vector.get('response_enthusiasm', 0.5)
        msg_length = vector.get('average_message_length', 0.5)
        
        # Build response based on vector values
        if sentiment > 0.6 and enthusiasm > 0.6:
            return "That's really interesting! I'd love to hear more about that."
        elif msg_length < 0.4:
            return "Interesting. Tell me more?"
        elif formality > 0.7:
            return "I understand. Could you elaborate on that point?"
        elif sentiment < 0.4:
            return "I see. What's your take on it?"
        else:
            return "That makes sense. What else is on your mind?"
    
    def enhance_with_synthetic(
        self,
        personality: Dict[str, Any],
        synthetic_vectors: List[List[float]]
    ) -> Dict[str, Any]:
        """
        Enhance personality with synthetic data for robustness.
        
        Args:
            personality: Base personality profile
            synthetic_vectors: Synthetic feature vectors
        
        Returns:
            Enhanced personality profile
        """
        if not synthetic_vectors:
            return personality
        
        # Calculate variance in synthetic vectors to identify stable traits
        vectors_array = np.array(synthetic_vectors)
        variance = np.var(vectors_array, axis=0)
        
        # Traits with low variance are more stable/consistent
        stable_indices = np.where(variance < np.median(variance))[0]
        
        # Add stability information to personality
        personality['trait_stability'] = {
            'stable_trait_count': len(stable_indices),
            'total_traits': len(variance),
            'stability_ratio': len(stable_indices) / len(variance) if len(variance) > 0 else 0
        }
        
        # Enhance system prompt with stability info
        if personality['trait_stability']['stability_ratio'] > 0.6:
            personality['system_prompt'] += "\n\nNote: This person has very consistent communication patterns. Stay true to the defined style."
        
        return personality
