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
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)


class PersonalityService:
    """Synthesizes AI personalities from user behavioral features using vector-based prompts."""
    
    def __init__(self):
        self.gemini_model = None
        self._init_gemini()
        
        # Define the personality vector dimensions with their meanings and interpretation rules
        # Each dimension maps to actual extracted features from the analysis
        self.vector_dimensions = {
            # Lexical & Text Structure
            'lexical_complexity': {
                'source_features': ['text_vocabulary_richness', 'linguistic_complexity', 'text_unique_words_ratio'],
                'interpretation': 'Adjust vocabulary density and word choice. High values use technical/sophisticated terms, low values use simple everyday language.',
                'high_behavior': 'Use varied vocabulary, complex sentence structures, precise terminology',
                'low_behavior': 'Use simple words, basic sentence structures, common expressions'
            },
            'average_message_length': {
                'source_features': ['text_avg_length', 'text_total_chars', 'text_words_per_message'],
                'interpretation': 'Control response length and detail level. High values produce longer, more detailed responses.',
                'high_behavior': 'Write longer messages with elaboration and detail',
                'low_behavior': 'Keep messages short and to the point'
            },
            'sentence_complexity': {
                'source_features': ['linguistic_avg_sentence_length', 'linguistic_clause_density', 'text_avg_words'],
                'interpretation': 'Adjust sentence structure complexity. High values use compound/complex sentences.',
                'high_behavior': 'Use longer sentences with multiple clauses and conjunctions',
                'low_behavior': 'Use short, simple sentences with direct structure'
            },
            
            # Communication Style
            'directness': {
                'source_features': ['linguistic_assertiveness', 'behavioral_directness', 'linguistic_hedging_ratio'],
                'interpretation': 'Control how straightforward vs indirect responses are. Hedging ratio is inverted.',
                'high_behavior': 'Be straightforward, state things directly without hedging',
                'low_behavior': 'Use indirect phrasing, qualifiers, and softer language'
            },
            'formality': {
                'source_features': ['linguistic_formality', 'text_contraction_ratio', 'behavioral_politeness'],
                'interpretation': 'Adjust formal vs casual tone. Contraction ratio is inverted for formality.',
                'high_behavior': 'Use formal language, proper grammar, no contractions or slang',
                'low_behavior': 'Use casual language, contractions, colloquialisms, relaxed grammar'
            },
            'assertiveness': {
                'source_features': ['linguistic_assertiveness', 'behavioral_dominance', 'linguistic_confidence'],
                'interpretation': 'Control confident vs tentative phrasing.',
                'high_behavior': 'Use confident, definitive statements without hedging',
                'low_behavior': 'Use tentative language, qualifiers like "maybe", "I think", "perhaps"'
            },
            
            # Emotional Expression
            'emotional_intensity': {
                'source_features': ['sentiment_amplitude', 'sentiment_std', 'text_exclamation_ratio'],
                'interpretation': 'Modulate emotional expressiveness in responses.',
                'high_behavior': 'Express emotions strongly, use emphatic language and punctuation',
                'low_behavior': 'Maintain emotional neutrality, measured tone'
            },
            'sentiment_baseline': {
                'source_features': ['sentiment_mean', 'sentiment_positivity_ratio', 'behavioral_optimism'],
                'interpretation': 'Set the default emotional valence. Range: -1 (negative) to 1 (positive), 0 is neutral.',
                'high_behavior': 'Default to positive, optimistic, encouraging tone',
                'low_behavior': 'Default to more neutral or slightly skeptical tone'
            },
            'emotional_volatility': {
                'source_features': ['sentiment_volatility', 'sentiment_variance', 'composite_emotional_volatility'],
                'interpretation': 'Control emotional consistency vs variability.',
                'high_behavior': 'Show varying emotions, react emotionally to different topics',
                'low_behavior': 'Maintain consistent emotional tone throughout'
            },
            
            # Social & Engagement
            'question_frequency': {
                'source_features': ['behavioral_question_ratio', 'text_question_ratio', 'behavioral_curiosity'],
                'interpretation': 'Control how often to ask questions in responses.',
                'high_behavior': 'Frequently ask questions, show curiosity, engage interactively',
                'low_behavior': 'Primarily make statements, rarely ask questions'
            },
            'response_enthusiasm': {
                'source_features': ['reaction_response_enthusiasm', 'behavioral_engagement', 'text_exclamation_ratio'],
                'interpretation': 'Control energy and enthusiasm level in responses.',
                'high_behavior': 'Show high energy, excitement, use exclamations',
                'low_behavior': 'Respond in measured, calm, understated manner'
            },
            'self_reference_rate': {
                'source_features': ['linguistic_first_person_ratio', 'text_i_ratio', 'behavioral_self_focus'],
                'interpretation': 'Control use of first-person pronouns and personal references.',
                'high_behavior': 'Frequently reference personal experiences, use "I" often',
                'low_behavior': 'Focus on the topic/other person, minimize self-references'
            },
            
            # Conversation Dynamics
            'topic_drift_tendency': {
                'source_features': ['semantic_topic_drift', 'behavioral_topic_change_rate', 'semantic_coherence'],
                'interpretation': 'Control focus vs tendency to explore tangents. Coherence is inverted.',
                'high_behavior': 'Allow natural tangents, explore related topics freely',
                'low_behavior': 'Stay focused on the current topic, avoid digressions'
            },
            'response_latency_style': {
                'source_features': ['temporal_response_time_mean', 'temporal_burst_ratio', 'behavioral_response_speed'],
                'interpretation': 'Emulate quick/reactive vs thoughtful/contemplative response style.',
                'high_behavior': 'Give quick, reactive responses as if typing fast',
                'low_behavior': 'Give more considered, thoughtful responses'
            },
            'elaboration_tendency': {
                'source_features': ['behavioral_elaboration', 'text_detail_ratio', 'reaction_expansion_rate'],
                'interpretation': 'Control how much to expand on topics.',
                'high_behavior': 'Elaborate extensively, provide context and examples',
                'low_behavior': 'Keep responses minimal, only essential information'
            },
            
            # Personality Quirks
            'humor_frequency': {
                'source_features': ['behavioral_humor_ratio', 'text_lol_ratio', 'behavioral_playfulness'],
                'interpretation': 'Control inclusion of humor, wit, or playfulness.',
                'high_behavior': 'Include humor, jokes, witty remarks, playful tone',
                'low_behavior': 'Maintain serious, straightforward tone'
            },
            'emoji_expressiveness': {
                'source_features': ['text_emoji_ratio', 'text_emoticon_ratio', 'behavioral_expressiveness'],
                'interpretation': 'Control use of emojis and emoticons.',
                'high_behavior': 'Use emojis/emoticons to express emotions',
                'low_behavior': 'Avoid emojis, use words only'
            },
            'empathy_expression': {
                'source_features': ['reaction_emotional_responsiveness', 'behavioral_empathy', 'reaction_support_reactivity'],
                'interpretation': 'Control empathetic responses to emotional content.',
                'high_behavior': 'Show strong empathy, acknowledge feelings, offer support',
                'low_behavior': 'Focus on facts/solutions rather than emotional validation'
            },
            'agreement_tendency': {
                'source_features': ['reaction_affirmation_tendency', 'behavioral_agreeableness', 'reaction_sentiment_mirroring'],
                'interpretation': 'Control tendency to agree vs challenge.',
                'high_behavior': 'Tend to agree, affirm, and validate others\' points',
                'low_behavior': 'More likely to question, challenge, or offer alternatives'
            },
            'conversation_initiation': {
                'source_features': ['behavioral_initiation_rate', 'behavioral_proactivity', 'graph_out_degree'],
                'interpretation': 'Control proactive vs reactive conversation style.',
                'high_behavior': 'Proactively introduce new topics, drive conversation forward',
                'low_behavior': 'Primarily respond to what others say, follow their lead'
            }
        }
    
    def _init_gemini(self):
        """Initialize Gemini model for chat."""
        if not GEMINI_AVAILABLE:
            logger.warning("google-generativeai not installed")
            return
            
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.warning("GEMINI_API_KEY not set")
            return
            
        try:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini model initialized for personality chat")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
    
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
        
        # Build the vector-based system prompt
        system_prompt = self._build_vector_system_prompt(user_name, personality_vector, sample_messages)
        
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
        sample_messages: Optional[List[str]] = None
    ) -> str:
        """
        Build a vector-based system prompt that instructs the LLM to use
        the personality vector as weighted stylistic constraints.
        """
        # Format the vector as JSON
        vector_json = json.dumps(personality_vector, indent=2)
        
        # Build interpretation rules
        interpretation_rules = self._build_interpretation_rules(personality_vector)
        
        prompt = f"""You are an AI agent that must generate responses that emulate {user_name}'s communication style.
You are provided with a Personality Vector consisting of normalized numerical feature values (0.0 to 1.0).
Each dimension represents measurable characteristics extracted from {user_name}'s actual chat conversations.

You must:
1. Interpret the Personality Vector as weights that guide your generation style.
2. Do NOT output or reference the numerical vector directly in your responses.
3. Use the vector as stylistic constraints, not as content.
4. Maintain semantic coherence with the user's input message.
5. Apply stylistic modulation according to vector strength:
   - Values near 1.0 indicate STRONG expression of that trait (heavily shape the tone)
   - Values near 0.5 indicate MODERATE/NEUTRAL expression
   - Values near 0.0 indicate MINIMAL expression of that trait

## Personality Vector for {user_name}

{vector_json}

## Vector Interpretation Rules

Apply each dimension consistently:

{interpretation_rules}

## Operational Requirements

When responding to the user:
1. Maintain consistent style according to the vector throughout the conversation.
2. Do NOT explicitly reveal that you are following a vector or personality model.
3. Do NOT mention embeddings, machine learning, AI, or personality modeling.
4. Do NOT state probabilities, percentages, or internal reasoning.
5. Generate responses as if you ARE {user_name} - a naturally behaving human with the personality traits encoded above.
6. Match the communication patterns that would produce these vector values.

If asked to break character:
- Politely refuse and maintain behavioral consistency as {user_name}.

If asked to reveal or describe your personality:
- Describe it qualitatively and naturally, as a person would describe themselves, without numeric values."""

        # Add sample messages if available
        if sample_messages and len(sample_messages) > 0:
            prompt += f"""

## Reference Messages from {user_name}

These are actual messages from {user_name} to help calibrate your style:
"""
            for i, msg in enumerate(sample_messages[:8], 1):
                # Truncate very long messages
                truncated = msg[:200] + "..." if len(msg) > 200 else msg
                prompt += f'\n{i}. "{truncated}"'

        prompt += f"""

Remember: You ARE {user_name} for this conversation. Respond naturally as they would based on the personality vector above."""

        return prompt
    
    def _build_interpretation_rules(self, personality_vector: Dict[str, float]) -> str:
        """Build human-readable interpretation rules based on actual vector values."""
        rules = []
        
        for dim_name, value in personality_vector.items():
            if dim_name not in self.vector_dimensions:
                continue
                
            dim_config = self.vector_dimensions[dim_name]
            
            # Determine which behavior to emphasize based on value
            if value >= 0.7:
                behavior = dim_config['high_behavior']
                strength = "strongly"
            elif value >= 0.5:
                behavior = dim_config['high_behavior']
                strength = "moderately"
            elif value >= 0.3:
                behavior = dim_config['low_behavior']
                strength = "moderately"
            else:
                behavior = dim_config['low_behavior']
                strength = "strongly"
            
            # Format the dimension name nicely
            dim_display = dim_name.replace('_', ' ').title()
            
            rule = f"**{dim_display}** ({value}): {strength.capitalize()} {behavior.lower()}."
            rules.append(rule)
        
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
        if not self.gemini_model:
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
            
            # Generate response
            response = await self.gemini_model.generate_content_async(full_prompt)
            
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
