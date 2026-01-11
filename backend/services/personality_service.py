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
        
        # Define the personality vector dimensions with their meanings and interpretation rules
        # Uses SYNTHETIC features (from llm_synthetic_features.py) as primary source - these are
        # pre-computed abstractions that are more robust and interpretable for the LLM.
        # Falls back to raw features when synthetic not available.
        self.vector_dimensions = {
            # Core Communication Style (from synthetic features)
            'warmth': {
                'source_features': ['synthetic_communication_warmth', 'behavioral_empathy_score', 'sentiment_positive_ratio'],
                'interpretation': 'Overall friendliness and warmth in communication.',
                'high_behavior': 'Be warm, friendly, supportive, and encouraging',
                'low_behavior': 'Be more neutral, reserved, and matter-of-fact'
            },
            'energy': {
                'source_features': ['synthetic_conversational_energy', 'reaction_response_enthusiasm', 'behavioral_engagement_level'],
                'interpretation': 'Overall energy and enthusiasm level.',
                'high_behavior': 'Show high energy, excitement, enthusiasm in responses',
                'low_behavior': 'Respond in calm, measured, understated manner'
            },
            'formality': {
                'source_features': ['synthetic_formality_level', 'behavioral_formality_score', 'behavioral_politeness_score'],
                'interpretation': 'Formal vs casual communication style.',
                'high_behavior': 'Use formal language, proper grammar, professional tone',
                'low_behavior': 'Use casual language, contractions, relaxed grammar'
            },
            'directness': {
                'source_features': ['synthetic_directness_clarity', 'behavioral_directness_score', 'behavioral_assertiveness_score'],
                'interpretation': 'How straightforward vs indirect responses are.',
                'high_behavior': 'Be straightforward, state things directly without hedging',
                'low_behavior': 'Use indirect phrasing, qualifiers, softer language'
            },
            
            # Emotional Expression
            'emotional_expressiveness': {
                'source_features': ['synthetic_emotional_expressiveness', 'text_emoji_density', 'linguistic_exclamation_ratio'],
                'interpretation': 'How much emotion is displayed in communication.',
                'high_behavior': 'Express emotions openly, use emphatic language and emojis',
                'low_behavior': 'Maintain emotional neutrality, measured tone'
            },
            'positivity': {
                'source_features': ['synthetic_positivity_bias', 'sentiment_positive_ratio', 'sentiment_sentiment_mean'],
                'interpretation': 'Default emotional valence (positive vs negative).',
                'high_behavior': 'Default to positive, optimistic, encouraging tone',
                'low_behavior': 'Default to more neutral or slightly skeptical tone'
            },
            'emotional_stability': {
                'source_features': ['synthetic_emotional_stability', 'sentiment_sentiment_consistency', 'sentiment_sentiment_volatility'],
                'interpretation': 'Emotional consistency vs variability.',
                'high_behavior': 'Maintain consistent emotional tone throughout',
                'low_behavior': 'Show varying emotions, react emotionally to different topics'
            },
            
            # Social & Engagement
            'curiosity': {
                'source_features': ['synthetic_curiosity_openness', 'behavioral_question_frequency', 'text_question_mark_ratio'],
                'interpretation': 'Interest in exploring topics and asking questions.',
                'high_behavior': 'Frequently ask questions, show curiosity, explore topics',
                'low_behavior': 'Primarily make statements, rarely ask questions'
            },
            'supportiveness': {
                'source_features': ['synthetic_supportiveness', 'behavioral_support_ratio', 'behavioral_empathy_score'],
                'interpretation': 'Tendency to support and encourage others.',
                'high_behavior': 'Show strong empathy, acknowledge feelings, offer support',
                'low_behavior': 'Focus on facts/solutions rather than emotional validation'
            },
            'agreement_orientation': {
                'source_features': ['synthetic_agreement_orientation', 'reaction_affirmation_tendency', 'behavioral_agreement_ratio'],
                'interpretation': 'Tendency to agree vs challenge.',
                'high_behavior': 'Tend to agree, affirm, and validate others\' points',
                'low_behavior': 'More likely to question, challenge, or offer alternatives'
            },
            
            # Communication Patterns
            'verbosity': {
                'source_features': ['synthetic_verbosity_level', 'text_word_count_mean', 'behavioral_elaboration_score'],
                'interpretation': 'How much detail and length in responses.',
                'high_behavior': 'Write longer messages with elaboration and detail',
                'low_behavior': 'Keep messages short and to the point'
            },
            'sophistication': {
                'source_features': ['synthetic_linguistic_sophistication', 'text_lexical_richness', 'linguistic_readability_score'],
                'interpretation': 'Language complexity and sophistication.',
                'high_behavior': 'Use varied vocabulary, complex sentence structures',
                'low_behavior': 'Use simple words, basic sentence structures'
            },
            'humor': {
                'source_features': ['synthetic_humor_playfulness', 'behavioral_humor_density', 'text_emoji_density'],
                'interpretation': 'Use of humor and playfulness.',
                'high_behavior': 'Include humor, jokes, witty remarks, playful tone',
                'low_behavior': 'Maintain serious, straightforward tone'
            },
            
            # Interpersonal Dynamics
            'self_focus': {
                'source_features': ['synthetic_self_focus_tendency', 'linguistic_first_person_ratio', 'behavioral_self_disclosure_level'],
                'interpretation': 'Focus on self vs others.',
                'high_behavior': 'Frequently reference personal experiences, use "I" often',
                'low_behavior': 'Focus on the topic/other person, minimize self-references'
            },
            'social_dominance': {
                'source_features': ['synthetic_social_dominance', 'behavioral_dominance_score', 'behavioral_initiation_rate'],
                'interpretation': 'Tendency to lead vs follow in conversations.',
                'high_behavior': 'Proactively introduce topics, drive conversation forward',
                'low_behavior': 'Primarily respond to what others say, follow their lead'
            },
            'adaptiveness': {
                'source_features': ['synthetic_adaptive_communication', 'reaction_style_adaptation', 'reaction_formality_matching'],
                'interpretation': 'How much style adapts to conversation partner.',
                'high_behavior': 'Adapt communication style to match the other person',
                'low_behavior': 'Maintain consistent personal style regardless of partner'
            },
            'attunement': {
                'source_features': ['synthetic_interpersonal_attunement', 'reaction_sentiment_mirroring', 'reaction_emotional_responsiveness'],
                'interpretation': 'Responsiveness and sensitivity to others.',
                'high_behavior': 'Be highly responsive to emotional cues, mirror sentiment',
                'low_behavior': 'Respond based on content rather than emotional cues'
            },
            
            # Text Style & Tempo (NEW - weighted higher for stylistic accuracy)
            'message_tempo': {
                'source_features': ['temporal_burstiness_score', 'temporal_avg_response_latency', 'text_msg_length_mean'],
                'interpretation': 'Speed and rhythm of communication. Fast responders with short messages vs slow, deliberate responses.',
                'high_behavior': 'Send quick, short bursts of messages. Respond rapidly. Use brief, punchy sentences.',
                'low_behavior': 'Take time to compose longer, more thoughtful responses. Write in complete paragraphs.'
            },
            'typing_intensity': {
                'source_features': ['text_uppercase_ratio', 'text_punctuation_ratio', 'linguistic_exclamation_ratio'],
                'interpretation': 'Intensity of typing style - caps, punctuation, emphasis.',
                'high_behavior': 'Use CAPS for emphasis, multiple punctuation marks!!, expressive typing style',
                'low_behavior': 'Use standard capitalization, minimal punctuation, calm typing style'
            },
            'message_structure': {
                'source_features': ['text_msg_length_mean', 'text_words_per_sentence_mean', 'text_sentence_count_mean'],
                'interpretation': 'How messages are structured - short fragments vs long paragraphs.',
                'high_behavior': 'Write longer messages with multiple sentences and detailed explanations',
                'low_behavior': 'Write short, fragmented messages. One thought per message. Brief responses.'
            },
            'response_speed': {
                'source_features': ['temporal_avg_response_latency', 'temporal_burstiness_score', 'context_turn_taking_regularity'],
                'interpretation': 'How quickly responses come and conversation pacing.',
                'high_behavior': 'Respond quickly, maintain rapid back-and-forth conversation flow',
                'low_behavior': 'Take time before responding, more deliberate pacing'
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
        Extract raw, visible text style features that the LLM should directly mimic.
        These are NOT abstracted - they represent exact observable patterns.
        """
        text = categories.get('text', {})
        linguistic = categories.get('linguistic', {})
        sentiment = categories.get('sentiment', {})
        behavioral = categories.get('behavioral', {})
        
        style = {}
        
        # Punctuation patterns
        exclamation_ratio = linguistic.get('exclamation_ratio', 0)
        style['exclamation_ratio'] = exclamation_ratio
        if exclamation_ratio > 0.3:
            style['exclamation_level'] = 'HEAVY - frequently uses exclamation marks!'
        elif exclamation_ratio > 0.15:
            style['exclamation_level'] = 'Moderate - uses exclamation marks regularly'
        elif exclamation_ratio > 0.05:
            style['exclamation_level'] = 'Light - occasional exclamation marks'
        else:
            style['exclamation_level'] = 'Minimal - rarely uses exclamation marks'
        
        question_ratio = text.get('question_mark_ratio', 0)
        style['question_ratio'] = question_ratio
        if question_ratio > 0.3:
            style['question_level'] = 'High - asks many questions'
        elif question_ratio > 0.15:
            style['question_level'] = 'Moderate - asks questions regularly'
        else:
            style['question_level'] = 'Low - mostly makes statements'
        
        # Check for multiple punctuation (!!!, ???)
        punctuation_ratio = text.get('punctuation_ratio', 0)
        style['uses_multiple_punctuation'] = punctuation_ratio > 0.1 and exclamation_ratio > 0.2
        
        # Capitalization patterns
        uppercase_ratio = text.get('uppercase_ratio', 0)
        style['uppercase_ratio'] = uppercase_ratio
        if uppercase_ratio > 0.3:
            style['caps_level'] = 'HEAVY - frequently uses ALL CAPS for emphasis'
            style['caps_style'] = 'Uses CAPS LOCK for emphasis and excitement'
        elif uppercase_ratio > 0.15:
            style['caps_level'] = 'Moderate - sometimes uses CAPS for emphasis'
            style['caps_style'] = 'Occasionally capitalizes words for EMPHASIS'
        elif uppercase_ratio > 0.05:
            style['caps_level'] = 'Light - minimal caps beyond sentence starts'
            style['caps_style'] = 'Standard capitalization with rare emphasis'
        else:
            style['caps_level'] = 'Minimal - standard capitalization only'
            style['caps_style'] = 'Standard capitalization'
        
        # Emoji patterns
        emoji_density = text.get('emoji_density', 0)
        style['emoji_density'] = emoji_density
        if emoji_density > 0.2:
            style['emoji_level'] = 'HEAVY - uses emojis very frequently 😊🎉'
            style['common_emojis'] = 'Uses many emojis throughout messages'
        elif emoji_density > 0.1:
            style['emoji_level'] = 'Moderate - uses emojis regularly'
            style['common_emojis'] = 'Sprinkles emojis in messages'
        elif emoji_density > 0.02:
            style['emoji_level'] = 'Light - occasional emoji use'
            style['common_emojis'] = 'Rare emoji use'
        else:
            style['emoji_level'] = 'None - does not use emojis'
            style['common_emojis'] = 'No emojis'
        
        # Message structure
        avg_words = text.get('word_count_mean', 10)
        style['avg_words'] = avg_words
        if avg_words < 5:
            style['sentence_style'] = 'Very short, fragmented messages'
        elif avg_words < 10:
            style['sentence_style'] = 'Brief, concise messages'
        elif avg_words < 20:
            style['sentence_style'] = 'Medium-length messages'
        else:
            style['sentence_style'] = 'Long, detailed messages with multiple sentences'
        
        # Formality and diction
        formality = behavioral.get('formality_score', 0.5)
        if formality > 0.7:
            style['formality_description'] = 'Formal - proper grammar and vocabulary'
            style['uses_contractions'] = False
        elif formality > 0.4:
            style['formality_description'] = 'Casual - relaxed but clear'
            style['uses_contractions'] = True
        else:
            style['formality_description'] = 'Very casual - informal, conversational'
            style['uses_contractions'] = True
        
        # Abbreviations and slang
        lexical_richness = text.get('lexical_richness', 0.5)
        if lexical_richness < 0.3:
            style['uses_abbreviations'] = 'Uses abbreviations (u, ur, lol, omg, etc.)'
            style['filler_words'] = 'Uses fillers like "like", "um", "ya know"'
        elif lexical_richness < 0.5:
            style['uses_abbreviations'] = 'Occasional abbreviations'
            style['filler_words'] = 'Some casual expressions'
        else:
            style['uses_abbreviations'] = 'Standard spelling'
            style['filler_words'] = 'Minimal filler words'
        
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

        # Add raw text style features for direct mimicry (not abstracted)
        if raw_text_style:
            prompt += f"""

## CRITICAL: Visible Text Style Features

These are the EXACT observable text patterns from {user_name}'s messages. You MUST replicate these patterns precisely:

### Punctuation & Emphasis
- **Exclamation usage**: {raw_text_style.get('exclamation_level', 'moderate')} ({raw_text_style.get('exclamation_ratio', 0):.0%} of sentences end with !)
- **Question frequency**: {raw_text_style.get('question_level', 'moderate')} ({raw_text_style.get('question_ratio', 0):.0%} of messages are questions)
- **Multiple punctuation**: {"YES - uses !!!, ???, etc." if raw_text_style.get('uses_multiple_punctuation', False) else "No - single punctuation marks"}

### Capitalization
- **CAPS usage**: {raw_text_style.get('caps_level', 'none')} ({raw_text_style.get('uppercase_ratio', 0):.0%} uppercase letters)
- **Style**: {raw_text_style.get('caps_style', 'Standard capitalization')}

### Emoji & Expressiveness  
- **Emoji frequency**: {raw_text_style.get('emoji_level', 'none')} ({raw_text_style.get('emoji_density', 0):.1%} emoji density)
- **Common emojis**: {raw_text_style.get('common_emojis', 'None detected')}

### Message Structure
- **Average message length**: {raw_text_style.get('avg_words', 0):.0f} words per message
- **Sentence structure**: {raw_text_style.get('sentence_style', 'Complete sentences')}
- **Abbreviations/slang**: {raw_text_style.get('uses_abbreviations', 'Standard spelling')}

### Diction & Vocabulary
- **Formality**: {raw_text_style.get('formality_description', 'Neutral')}
- **Contractions**: {"Uses contractions (don't, can't, won't)" if raw_text_style.get('uses_contractions', False) else "Formal (do not, cannot)"}
- **Filler words**: {raw_text_style.get('filler_words', 'None detected')}

YOU MUST MATCH THESE PATTERNS EXACTLY. If they use "!!!" you use "!!!". If they use CAPS for emphasis, you use CAPS. If they use emojis, you use similar emojis."""

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
