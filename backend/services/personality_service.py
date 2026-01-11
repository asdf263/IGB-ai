"""
AI Personality Synthesis Service
Generates custom LLM prompts that shape chatbot voice, tone, style, pacing, and quirks
based on extracted user features from conversation analysis.
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
    """Synthesizes AI personalities from user behavioral features."""
    
    def __init__(self):
        self.gemini_model = None
        self._init_gemini()
        
        # Personality trait mappings from features
        self.trait_mappings = {
            'communication_style': {
                'text_avg_length': ('verbose', 'concise'),
                'text_vocabulary_richness': ('eloquent', 'simple'),
                'linguistic_formality': ('formal', 'casual'),
                'behavioral_question_ratio': ('inquisitive', 'declarative'),
            },
            'emotional_profile': {
                'sentiment_mean': ('positive', 'neutral', 'negative'),
                'sentiment_volatility': ('expressive', 'steady'),
                'reaction_emotional_responsiveness': ('empathetic', 'reserved'),
                'reaction_sentiment_mirroring': ('adaptive', 'independent'),
            },
            'social_dynamics': {
                'behavioral_response_rate': ('engaged', 'selective'),
                'behavioral_initiation_rate': ('proactive', 'reactive'),
                'reaction_reciprocity_balance': ('balanced', 'asymmetric'),
                'graph_centrality': ('central', 'peripheral'),
            },
            'conversation_rhythm': {
                'temporal_response_time_mean': ('quick', 'thoughtful'),
                'temporal_burst_ratio': ('bursty', 'steady'),
                'reaction_response_enthusiasm': ('enthusiastic', 'measured'),
            },
            'personality_quirks': {
                'text_emoji_ratio': ('expressive', 'minimal'),
                'text_exclamation_ratio': ('excitable', 'calm'),
                'linguistic_hedging_ratio': ('tentative', 'assertive'),
                'behavioral_humor_ratio': ('playful', 'serious'),
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
            Personality profile with traits, prompt, and metadata
        """
        categories = user_features.get('categories', {})
        
        # Extract personality traits from features
        traits = self._extract_traits(categories)
        
        # Generate communication style description
        style_description = self._generate_style_description(traits, categories)
        
        # Generate quirks and mannerisms
        quirks = self._extract_quirks(categories, sample_messages)
        
        # Build the system prompt
        system_prompt = self._build_system_prompt(
            user_name, traits, style_description, quirks, sample_messages
        )
        
        # Calculate personality metrics
        metrics = self._calculate_personality_metrics(categories)
        
        return {
            'user_name': user_name,
            'traits': traits,
            'style_description': style_description,
            'quirks': quirks,
            'system_prompt': system_prompt,
            'metrics': metrics,
            'feature_summary': self._summarize_features(categories)
        }
    
    def _extract_traits(self, categories: Dict[str, Dict[str, float]]) -> Dict[str, str]:
        """Extract personality traits from feature categories."""
        traits = {}
        
        for trait_category, feature_mappings in self.trait_mappings.items():
            trait_scores = []
            
            for feature_name, labels in feature_mappings.items():
                # Find the feature value
                value = self._find_feature_value(categories, feature_name)
                if value is not None:
                    trait_scores.append((feature_name, value, labels))
            
            if trait_scores:
                # Determine dominant trait based on average
                avg_value = np.mean([s[1] for s in trait_scores])
                
                # Map to trait label
                if len(trait_scores[0][2]) == 2:
                    # Binary trait
                    traits[trait_category] = trait_scores[0][2][0] if avg_value > 0.5 else trait_scores[0][2][1]
                else:
                    # Ternary trait
                    if avg_value > 0.6:
                        traits[trait_category] = trait_scores[0][2][0]
                    elif avg_value < 0.4:
                        traits[trait_category] = trait_scores[0][2][2]
                    else:
                        traits[trait_category] = trait_scores[0][2][1]
        
        return traits
    
    def _find_feature_value(self, categories: Dict, feature_name: str) -> Optional[float]:
        """Find a feature value across all categories."""
        for cat_name, features in categories.items():
            if isinstance(features, dict):
                # Try exact match
                if feature_name in features:
                    return features[feature_name]
                # Try partial match
                for fname, fval in features.items():
                    if feature_name in fname or fname in feature_name:
                        return fval
        return None
    
    def _generate_style_description(
        self,
        traits: Dict[str, str],
        categories: Dict[str, Dict[str, float]]
    ) -> str:
        """Generate a natural language description of communication style."""
        descriptions = []
        
        # Communication style
        comm_style = traits.get('communication_style', 'balanced')
        if comm_style == 'verbose':
            descriptions.append("tends to write longer, detailed messages")
        elif comm_style == 'concise':
            descriptions.append("prefers short, to-the-point messages")
        
        # Emotional profile
        emotional = traits.get('emotional_profile', 'neutral')
        if emotional == 'positive':
            descriptions.append("generally upbeat and positive in tone")
        elif emotional == 'expressive':
            descriptions.append("emotionally expressive with varying moods")
        
        # Social dynamics
        social = traits.get('social_dynamics', 'balanced')
        if social == 'proactive':
            descriptions.append("often initiates conversations and topics")
        elif social == 'engaged':
            descriptions.append("highly responsive and engaged in conversation")
        
        # Conversation rhythm
        rhythm = traits.get('conversation_rhythm', 'steady')
        if rhythm == 'quick':
            descriptions.append("responds quickly with rapid-fire messages")
        elif rhythm == 'bursty':
            descriptions.append("sends messages in bursts followed by pauses")
        
        # Personality quirks
        quirks = traits.get('personality_quirks', 'balanced')
        if quirks == 'expressive':
            descriptions.append("uses emojis and exclamation marks frequently")
        elif quirks == 'playful':
            descriptions.append("incorporates humor and playfulness")
        
        if descriptions:
            return "This person " + ", ".join(descriptions) + "."
        return "This person has a balanced, adaptable communication style."
    
    def _extract_quirks(
        self,
        categories: Dict[str, Dict[str, float]],
        sample_messages: Optional[List[str]] = None
    ) -> List[str]:
        """Extract specific quirks and mannerisms."""
        quirks = []
        
        # Check emoji usage
        emoji_ratio = self._find_feature_value(categories, 'emoji_ratio')
        if emoji_ratio and emoji_ratio > 0.3:
            quirks.append("Uses emojis frequently to express emotions")
        
        # Check question asking
        question_ratio = self._find_feature_value(categories, 'question_ratio')
        if question_ratio and question_ratio > 0.3:
            quirks.append("Often asks questions to engage others")
        
        # Check humor
        humor_ratio = self._find_feature_value(categories, 'humor_ratio')
        if humor_ratio and humor_ratio > 0.2:
            quirks.append("Incorporates humor and wit into conversations")
        
        # Check formality
        formality = self._find_feature_value(categories, 'formality')
        if formality:
            if formality > 0.7:
                quirks.append("Maintains formal language and proper grammar")
            elif formality < 0.3:
                quirks.append("Uses casual, informal language with abbreviations")
        
        # Check enthusiasm
        enthusiasm = self._find_feature_value(categories, 'enthusiasm')
        if enthusiasm and enthusiasm > 0.6:
            quirks.append("Shows enthusiasm through exclamations and energy")
        
        # Analyze sample messages for patterns
        if sample_messages:
            patterns = self._analyze_message_patterns(sample_messages)
            quirks.extend(patterns)
        
        return quirks[:8]  # Limit to 8 quirks
    
    def _analyze_message_patterns(self, messages: List[str]) -> List[str]:
        """Analyze sample messages for recurring patterns."""
        patterns = []
        
        if not messages:
            return patterns
        
        # Check for common phrases
        all_text = ' '.join(messages).lower()
        
        # Check greeting styles
        if 'hey' in all_text or 'hi' in all_text:
            patterns.append("Uses casual greetings like 'hey' or 'hi'")
        elif 'hello' in all_text:
            patterns.append("Uses more formal greetings like 'hello'")
        
        # Check for filler words
        fillers = ['like', 'um', 'uh', 'you know', 'basically', 'literally']
        for filler in fillers:
            if all_text.count(filler) > len(messages) * 0.1:
                patterns.append(f"Tends to use '{filler}' as a filler word")
                break
        
        # Check for laughter expressions
        if 'haha' in all_text or 'lol' in all_text or 'lmao' in all_text:
            patterns.append("Expresses laughter through text (haha, lol)")
        
        return patterns
    
    def _build_system_prompt(
        self,
        user_name: str,
        traits: Dict[str, str],
        style_description: str,
        quirks: List[str],
        sample_messages: Optional[List[str]] = None
    ) -> str:
        """Build the complete system prompt for the AI persona."""
        
        prompt_parts = [
            f"You are roleplaying as {user_name}. Your goal is to communicate exactly like {user_name} would, "
            f"based on their actual conversation patterns and personality.",
            "",
            "## Personality Profile",
            style_description,
            "",
            "## Key Traits"
        ]
        
        for trait_type, trait_value in traits.items():
            prompt_parts.append(f"- {trait_type.replace('_', ' ').title()}: {trait_value}")
        
        if quirks:
            prompt_parts.extend([
                "",
                "## Communication Quirks & Mannerisms"
            ])
            for quirk in quirks:
                prompt_parts.append(f"- {quirk}")
        
        if sample_messages:
            prompt_parts.extend([
                "",
                "## Example Messages (for style reference)",
                "Here are some actual messages from this person to help you match their style:"
            ])
            for msg in sample_messages[:5]:
                prompt_parts.append(f'- "{msg}"')
        
        prompt_parts.extend([
            "",
            "## Instructions",
            "1. Match the communication style, vocabulary, and tone shown above",
            "2. Use similar message lengths and formatting patterns",
            "3. Incorporate the quirks and mannerisms naturally",
            "4. Stay in character - respond as this person would",
            "5. Be authentic to their personality, not generic",
            "6. If asked about being an AI, stay in character as the person",
            "",
            "Remember: You ARE this person for the duration of this conversation. "
            "Respond naturally as they would, not as a helpful AI assistant."
        ])
        
        return '\n'.join(prompt_parts)
    
    def _calculate_personality_metrics(
        self,
        categories: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """Calculate high-level personality metrics."""
        metrics = {}
        
        # Extraversion (social energy)
        extraversion_features = [
            self._find_feature_value(categories, 'initiation_rate'),
            self._find_feature_value(categories, 'response_enthusiasm'),
            self._find_feature_value(categories, 'exclamation_ratio'),
        ]
        valid = [v for v in extraversion_features if v is not None]
        metrics['extraversion'] = np.mean(valid) if valid else 0.5
        
        # Agreeableness
        agree_features = [
            self._find_feature_value(categories, 'affirmation_tendency'),
            self._find_feature_value(categories, 'sentiment_mirroring'),
            self._find_feature_value(categories, 'support_reactivity'),
        ]
        valid = [v for v in agree_features if v is not None]
        metrics['agreeableness'] = np.mean(valid) if valid else 0.5
        
        # Openness
        open_features = [
            self._find_feature_value(categories, 'topic_expansion_rate'),
            self._find_feature_value(categories, 'vocabulary_richness'),
            self._find_feature_value(categories, 'semantic_diversity'),
        ]
        valid = [v for v in open_features if v is not None]
        metrics['openness'] = np.mean(valid) if valid else 0.5
        
        # Emotional stability
        stability_features = [
            self._find_feature_value(categories, 'sentiment_volatility'),
            self._find_feature_value(categories, 'mood_influence_susceptibility'),
        ]
        valid = [v for v in stability_features if v is not None]
        # Invert because high volatility = low stability
        metrics['emotional_stability'] = 1 - np.mean(valid) if valid else 0.5
        
        # Conscientiousness
        consc_features = [
            self._find_feature_value(categories, 'formality'),
            self._find_feature_value(categories, 'response_rate'),
            self._find_feature_value(categories, 'attention_consistency'),
        ]
        valid = [v for v in consc_features if v is not None]
        metrics['conscientiousness'] = np.mean(valid) if valid else 0.5
        
        return {k: round(v, 3) for k, v in metrics.items()}
    
    def _summarize_features(self, categories: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Create a summary of key features."""
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
            return self._fallback_response(personality, user_message)
        
        try:
            # Build conversation context
            messages = []
            
            # Add system prompt
            system_prompt = personality.get('system_prompt', '')
            
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
            
            # Generate response
            response = await self.gemini_model.generate_content_async(full_prompt)
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return self._fallback_response(personality, user_message)
    
    def _fallback_response(self, personality: Dict[str, Any], user_message: str) -> str:
        """Generate a fallback response when Gemini is unavailable."""
        traits = personality.get('traits', {})
        user_name = personality.get('user_name', 'Unknown')
        
        # Generate a simple response based on traits
        if traits.get('emotional_profile') == 'positive':
            return f"Hey! That's interesting. Tell me more about that!"
        elif traits.get('communication_style') == 'concise':
            return "Got it. What else?"
        else:
            return f"I see what you mean. What do you think about it?"
    
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
