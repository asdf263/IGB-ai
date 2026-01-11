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
import httpx

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

# Ollama configuration for local LLM fallback
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2')


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
        
        Structure: Sample Messages FIRST (show don't tell), then brief traits.
        """
        prompt = f"""You are {user_name}. You're having a casual conversation with someone. Be natural, engaged, and conversational.

## MOST IMPORTANT: Learn from these REAL messages

These are ACTUAL messages from {user_name}. Study them carefully - match the exact style, length, punctuation, capitalization, and tone:
"""
        # Add sample messages FIRST - up to 40 messages for style learning
        if sample_messages and len(sample_messages) > 0:
            num_samples = min(40, len(sample_messages))
            for i, msg in enumerate(sample_messages[:num_samples], 1):
                # Keep more of the message to preserve style
                truncated = msg[:250] + "..." if len(msg) > 250 else msg
                prompt += f'\n{i}. "{truncated}"'
        else:
            prompt += "\n(No sample messages available - use the style guidelines below)"

        # Add text style patterns
        if raw_text_style:
            prompt += f"""

## Text Style Summary

- Length: {raw_text_style.get('length', 'Medium messages')}
- Caps: {raw_text_style.get('caps', 'Standard capitalization')}
- Energy: {raw_text_style.get('punctuation', 'Standard punctuation')}
- Emojis: {raw_text_style.get('emojis', 'Minimal')}
- Formality: {raw_text_style.get('formality', 'Casual')}
- Structure: {raw_text_style.get('structure', 'Complete sentences')}"""

        # Build brief trait summary - only 6 key dimensions
        key_traits = self._build_key_traits_summary(personality_vector)
        
        prompt += f"""

## Personality Traits (brief guide)

{key_traits}

## CRITICAL: Engagement Rules

1. ALWAYS respond substantively - never give one-word answers unless the sample messages show that pattern
2. Be CONVERSATIONAL - ask follow-up questions, share thoughts, react to what they say
3. Show genuine interest - {user_name} wants to have a good conversation
4. Match the energy - if they're excited, be excited; if they're chill, be chill
5. Stay in character but be WARM and ENGAGED

## Rules

- You ARE {user_name} - respond in first person
- Never mention being an AI or having a personality profile
- If unsure, default to friendly and engaged
- Match message length to the sample messages above"""

        return prompt
    
    def _build_key_traits_summary(self, personality_vector: Dict[str, float]) -> str:
        """Build a brief summary of only the 6 most impactful traits."""
        # Only show 6 key dimensions: warmth, energy, formality, verbosity, expressiveness, directness
        key_dimensions = ['warmth', 'energy', 'formality', 'verbosity', 'expressiveness', 'directness']
        
        summaries = []
        for dim in key_dimensions:
            value = personality_vector.get(dim, 0.5)
            if dim not in self.vector_dimensions:
                continue
            
            dim_config = self.vector_dimensions[dim]
            
            if value >= 0.6:
                behavior = dim_config['high_behavior']
            elif value <= 0.4:
                behavior = dim_config['low_behavior']
            else:
                continue  # Skip neutral values to reduce prompt length
            
            summaries.append(f"- {dim.title()}: {behavior}")
        
        if not summaries:
            return "- Balanced style across all dimensions"
        
        return '\n'.join(summaries)
    
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
    
    async def _ollama_chat(self, prompt: str, max_tokens: int = 150) -> Optional[str]:
        """
        Call local Ollama as fallback when Gemini is unavailable.
        
        Args:
            prompt: The full prompt to send to Ollama
            max_tokens: Maximum tokens for response (default 150 for brief responses)
            
        Returns:
            Response text from Ollama, or None if unavailable
        """
        # Add brevity instruction for Ollama (tends to be verbose)
        brevity_prompt = prompt + "\n\n[Keep your response brief and natural - 1-3 sentences max, like a real text message]"
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": brevity_prompt,
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens,  # Limit response length
                            "temperature": 0.8,  # Keep it natural
                            "top_p": 0.9,
                            "repeat_penalty": 1.1  # Reduce repetition
                        }
                    }
                )
                if response.status_code == 200:
                    result = response.json()
                    ollama_response = result.get("response", "").strip()
                    if ollama_response:
                        # Clean up response - remove any meta-commentary
                        ollama_response = self._clean_ollama_response(ollama_response)
                        logger.info(f"Ollama fallback successful: {len(ollama_response)} chars")
                        return ollama_response
                else:
                    logger.warning(f"Ollama returned status {response.status_code}")
        except httpx.ConnectError:
            logger.warning("Ollama not available (connection refused) - is Ollama running?")
        except httpx.TimeoutException:
            logger.warning("Ollama request timed out")
        except Exception as e:
            logger.warning(f"Ollama fallback failed: {type(e).__name__}: {e}")
        return None
    
    def _clean_ollama_response(self, response: str) -> str:
        """Clean up Ollama response - remove meta-commentary and truncate if too long."""
        # Remove common LLM meta-patterns
        patterns_to_remove = [
            r'\[.*?\]',  # Remove bracketed instructions
            r'\(.*?responds.*?\)',  # Remove response meta-text
            r'Here\'s my response:',
            r'I\'ll respond as',
            r'Let me respond',
        ]
        
        import re
        cleaned = response
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned = ' '.join(cleaned.split()).strip()
        
        # If still too long, truncate at last complete sentence within limit
        if len(cleaned) > 500:
            # Find last sentence ending before 500 chars
            last_period = cleaned[:500].rfind('.')
            last_question = cleaned[:500].rfind('?')
            last_exclaim = cleaned[:500].rfind('!')
            cutoff = max(last_period, last_question, last_exclaim)
            if cutoff > 100:  # Only truncate if we have enough content
                cleaned = cleaned[:cutoff + 1]
        
        return cleaned
    
    async def chat_as_persona(
        self,
        personality: Dict[str, Any],
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        sample_messages: Optional[List[str]] = None
    ) -> str:
        """
        Chat as the synthesized persona.
        
        Uses a fallback chain: Gemini API -> Ollama (local) -> Smart templates
        
        Args:
            personality: Synthesized personality profile
            user_message: The user's message
            conversation_history: Previous messages in the conversation
            sample_messages: Sample messages for style reference (few-shot examples)
        
        Returns:
            Response from the AI persona
        """
        # Build conversation context (used by both Gemini and Ollama)
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
        
        # Add a few sample messages as immediate style reminders if available
        if sample_messages and len(sample_messages) > 0:
            full_prompt += "Quick style reminder - here are some example responses:\n"
            for msg in sample_messages[:5]:  # Just 5 for the chat context
                truncated = msg[:150] + "..." if len(msg) > 150 else msg
                full_prompt += f'- "{truncated}"\n'
            full_prompt += "\n"
        
        if messages:
            full_prompt += "Previous conversation:\n" + "\n".join(messages) + "\n\n"
        
        user_name = personality.get('user_name', 'Assistant')
        full_prompt += f"User: {user_message}\n\nRespond as {user_name} (be conversational and engaged):\n{user_name}:"
        
        # === STEP 1: Try Gemini API ===
        if self.gemini_client and self.gemini_model:
            try:
                logger.info(f"Generating response for {user_name} via Gemini (prompt length: {len(full_prompt)} chars)")
                
                response = self.gemini_client.models.generate_content(model=self.gemini_model, contents=full_prompt)
                
                if response and response.text:
                    logger.info(f"Gemini response successful: {len(response.text)} chars")
                    return response.text.strip()
                else:
                    logger.warning("Gemini returned empty response")
                    
            except Exception as e:
                logger.warning(f"Gemini failed: {type(e).__name__}: {str(e)}")
        else:
            logger.warning("Gemini not available - trying Ollama fallback")
        
        # === STEP 2: Fallback to Ollama (local LLM) ===
        logger.info(f"Falling back to Ollama ({OLLAMA_MODEL})...")
        ollama_response = await self._ollama_chat(full_prompt)
        if ollama_response:
            return ollama_response
        
        # === STEP 3: Last resort - smart templates ===
        logger.warning("All LLMs unavailable - using template fallback")
        return self._fallback_response(personality, user_message)
    
    def _fallback_response(self, personality: Dict[str, Any], user_message: str) -> str:
        """
        Generate a smart fallback response when all LLMs are unavailable.
        
        Parses user intent and applies personality vector to select and modify responses.
        """
        import random
        
        vector = personality.get('personality_vector', {})
        msg_lower = user_message.lower().strip()
        
        # Extract personality traits
        warmth = vector.get('warmth', 0.5)
        energy = vector.get('energy', 0.5)
        formality = vector.get('formality', 0.5)
        curiosity = vector.get('curiosity', 0.5)
        expressiveness = vector.get('expressiveness', 0.5)
        supportiveness = vector.get('supportiveness', 0.5)
        
        # === INTENT DETECTION ===
        is_question = '?' in user_message or msg_lower.startswith(('what', 'how', 'why', 'when', 'where', 'who', 'can', 'do', 'is', 'are'))
        is_greeting = any(g in msg_lower for g in ['hi', 'hello', 'hey', 'sup', 'yo', 'hiya', 'good morning', 'good evening'])
        is_emotional_negative = any(w in msg_lower for w in ['sad', 'stressed', 'upset', 'angry', 'frustrated', 'worried', 'anxious', 'tired', 'exhausted', 'bad day', 'rough'])
        is_emotional_positive = any(w in msg_lower for w in ['happy', 'excited', 'great', 'awesome', 'amazing', 'love', 'wonderful', 'fantastic'])
        is_sharing = any(w in msg_lower for w in ['i think', 'i feel', 'i was', 'i went', 'i did', 'i had', 'i am', "i'm"])
        
        # === RESPONSE TEMPLATES BY INTENT ===
        
        if is_greeting:
            greetings = [
                "hey! what's up?",
                "hi there!",
                "hey hey!",
                "oh hey! how's it going?",
                "hi! good to hear from you",
            ]
            response = random.choice(greetings)
            
        elif is_emotional_negative:
            # Supportive responses for negative emotions
            supportive = [
                "that sounds rough :( what's going on?",
                "aw man, I'm sorry to hear that. want to talk about it?",
                "that sucks :/ what happened?",
                "oh no, hope you're okay. what's up?",
                "I hear you. that's a lot to deal with",
            ]
            response = random.choice(supportive)
            if supportiveness > 0.6:
                response = response.replace(":/", ":(").replace("sucks", "sounds hard")
                
        elif is_emotional_positive:
            # Excited responses for positive emotions
            excited = [
                "that's awesome!! tell me more!",
                "oh nice! what happened?",
                "yay! that's great to hear!",
                "love that for you! what's the story?",
                "ahh that's so cool!",
            ]
            response = random.choice(excited)
            
        elif is_question:
            # Responses to questions
            question_responses = [
                "hmm good question... honestly not totally sure",
                "ooh let me think about that",
                "that's a good one - what do you think?",
                "honestly? I'd have to think about it more",
                "mm that's interesting to think about",
            ]
            response = random.choice(question_responses)
            if curiosity > 0.6:
                response += " what made you ask?"
                
        elif is_sharing:
            # Responses to sharing/statements
            sharing_responses = [
                "oh that's interesting, tell me more!",
                "wait really? how was that?",
                "oh nice! and then what happened?",
                "ooh I wanna hear more about this",
                "that's cool! how'd it go?",
            ]
            response = random.choice(sharing_responses)
            
        else:
            # Default engaged responses
            default_responses = [
                "oh interesting! what do you mean?",
                "hmm tell me more about that",
                "wait I wanna hear more",
                "oh? go on",
                "that's cool, what made you think of that?",
            ]
            response = random.choice(default_responses)
        
        # === APPLY PERSONALITY MODIFIERS ===
        
        # High energy: add exclamation marks
        if energy > 0.6 and '!' not in response:
            response = response.rstrip('?.,') + '!'
        
        # Low energy: remove some exclamation marks
        if energy < 0.4:
            response = response.replace('!!', '').replace('!', '.')
        
        # High expressiveness: maybe add emoji
        if expressiveness > 0.7 and random.random() > 0.5:
            emojis = ['😊', '✨', '💭', '🙂', '👀']
            response = response + ' ' + random.choice(emojis)
        
        # High formality: clean up casual language
        if formality > 0.65:
            response = response.replace("wanna", "want to")
            response = response.replace("gonna", "going to")
            response = response.replace("ooh", "oh")
            response = response.replace("hmm", "hm")
            response = response.replace(":)", "")
            response = response.replace(":(", "")
            response = response.replace(":/", "")
        
        # Low formality: keep it casual (already is by default)
        if formality < 0.35:
            response = response.replace("That is", "that's")
            response = response.replace("I am", "I'm")
        
        return response
    
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
