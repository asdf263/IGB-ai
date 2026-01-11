"""
LLM Synthetic Feature Extraction Module
Generates high-level abstracted features from raw features for LLM personality synthesis.
These features are more interpretable and robust than raw features.
"""
import numpy as np
from typing import Dict, Any


class LLMSyntheticFeatureExtractor:
    """Generates synthetic features optimized for LLM personality understanding."""
    
    def __init__(self):
        self.feature_names = [
            'communication_warmth',
            'intellectual_engagement', 
            'social_dominance',
            'emotional_expressiveness',
            'conversational_energy',
            'linguistic_sophistication',
            'interpersonal_attunement',
            'self_focus_tendency',
            'humor_playfulness',
            'formality_level',
            'agreement_orientation',
            'emotional_stability',
            'curiosity_openness',
            'supportiveness',
            'directness_clarity',
            'verbosity_level',
            'positivity_bias',
            'engagement_consistency',
            'adaptive_communication',
            'conversational_initiative',
            # NEW: Text style and tempo features
            'typing_intensity',
            'message_brevity',
            'response_tempo',
            'text_expressiveness',
            'conversation_rhythm'
        ]
    
    def extract(self,
                text_features: Dict[str, float],
                linguistic_features: Dict[str, float],
                sentiment_features: Dict[str, float],
                behavioral_features: Dict[str, float],
                reaction_features: Dict[str, float],
                composite_features: Dict[str, float],
                emotion_features: Dict[str, float] = None,
                context_features: Dict[str, float] = None) -> Dict[str, float]:
        """
        Extract synthetic features from raw feature categories.
        
        All output features are normalized to 0-1 range.
        """
        # Use empty dicts if optional features not provided
        emotion_features = emotion_features or {}
        context_features = context_features or {}
        
        features = {}
        
        features['communication_warmth'] = self._compute_warmth(
            sentiment_features, behavioral_features, reaction_features
        )
        
        features['intellectual_engagement'] = self._compute_intellectual_engagement(
            text_features, linguistic_features, behavioral_features
        )
        
        features['social_dominance'] = self._compute_social_dominance(
            behavioral_features, reaction_features
        )
        
        features['emotional_expressiveness'] = self._compute_emotional_expressiveness(
            text_features, linguistic_features, sentiment_features
        )
        
        features['conversational_energy'] = self._compute_conversational_energy(
            text_features, behavioral_features, reaction_features
        )
        
        features['linguistic_sophistication'] = self._compute_linguistic_sophistication(
            text_features, linguistic_features
        )
        
        features['interpersonal_attunement'] = self._compute_interpersonal_attunement(
            reaction_features, behavioral_features
        )
        
        features['self_focus_tendency'] = self._compute_self_focus(
            linguistic_features, behavioral_features
        )
        
        features['humor_playfulness'] = self._compute_humor_playfulness(
            text_features, behavioral_features
        )
        
        features['formality_level'] = self._compute_formality(
            behavioral_features, linguistic_features, text_features
        )
        
        features['agreement_orientation'] = self._compute_agreement_orientation(
            behavioral_features, reaction_features
        )
        
        features['emotional_stability'] = self._compute_emotional_stability(
            sentiment_features, composite_features
        )
        
        features['curiosity_openness'] = self._compute_curiosity_openness(
            behavioral_features, reaction_features, text_features
        )
        
        features['supportiveness'] = self._compute_supportiveness(
            behavioral_features, reaction_features
        )
        
        features['directness_clarity'] = self._compute_directness(
            behavioral_features, linguistic_features
        )
        
        features['verbosity_level'] = self._compute_verbosity(
            text_features, behavioral_features
        )
        
        features['positivity_bias'] = self._compute_positivity_bias(
            sentiment_features
        )
        
        features['engagement_consistency'] = self._compute_engagement_consistency(
            reaction_features, composite_features
        )
        
        features['adaptive_communication'] = self._compute_adaptive_communication(
            reaction_features
        )
        
        features['conversational_initiative'] = self._compute_initiative(
            behavioral_features, reaction_features
        )
        
        # NEW: Text style and tempo features
        features['typing_intensity'] = self._compute_typing_intensity(
            text_features, linguistic_features
        )
        
        features['message_brevity'] = self._compute_message_brevity(
            text_features, behavioral_features
        )
        
        features['response_tempo'] = self._compute_response_tempo(
            text_features, context_features
        )
        
        features['text_expressiveness'] = self._compute_text_expressiveness(
            text_features, linguistic_features, emotion_features
        )
        
        features['conversation_rhythm'] = self._compute_conversation_rhythm(
            context_features, behavioral_features
        )
        
        return features
    
    def _safe_get(self, features: Dict[str, float], key: str, default: float = 0.5) -> float:
        """Safely get feature value with default."""
        val = features.get(key, default)
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return default
        return float(val)
    
    def _normalize(self, value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Normalize value to 0-1 range."""
        return float(max(0.0, min(1.0, (value - min_val) / (max_val - min_val + 0.001))))
    
    def _compute_warmth(self, sentiment: Dict, behavioral: Dict, reaction: Dict) -> float:
        """
        Communication Warmth: Overall friendliness and warmth in communication.
        High = friendly, supportive, positive; Low = cold, distant, neutral
        Boosted baseline to create more engaging personas.
        """
        sentiment_mean = self._safe_get(sentiment, 'sentiment_mean', 0)
        # Convert from -1,1 to 0,1
        sentiment_normalized = (sentiment_mean + 1) / 2
        
        positive_ratio = self._safe_get(sentiment, 'positive_ratio', 0.33)
        empathy = self._safe_get(behavioral, 'empathy_score', 0)
        support = self._safe_get(behavioral, 'support_ratio', 0)
        support_react = self._safe_get(reaction, 'support_reactivity', 0)
        
        raw_warmth = (
            sentiment_normalized * 0.25 +
            positive_ratio * 0.25 +
            empathy * 0.2 +
            support * 0.15 +
            support_react * 0.15
        )
        
        # Apply warmth boost - shift distribution upward to avoid cold personas
        # Maps 0.0-1.0 to 0.2-1.0 range (minimum 20% warmth)
        boosted_warmth = 0.2 + (raw_warmth * 0.8)
        
        return float(min(1.0, max(0.0, boosted_warmth)))
    
    def _compute_intellectual_engagement(self, text: Dict, linguistic: Dict, behavioral: Dict) -> float:
        """
        Intellectual Engagement: Depth of thought and analytical engagement.
        High = thoughtful, analytical, detailed; Low = surface-level, brief
        """
        lexical_richness = self._safe_get(text, 'lexical_richness', 0.5)
        question_mark_ratio = self._safe_get(text, 'question_mark_ratio', 0)  # Replaced question_frequency
        elaboration = self._safe_get(behavioral, 'elaboration_score', 0)
        readability = self._safe_get(linguistic, 'readability_score', 50) / 100
        avg_sentence_len = min(1.0, self._safe_get(linguistic, 'avg_sentence_length', 10) / 20)
        # Removed: pos_noun_ratio (useless - collapsed calibration)
        
        engagement = (
            lexical_richness * 0.3 +
            question_mark_ratio * 0.2 +
            elaboration * 0.25 +
            (1 - readability) * 0.15 +  # Lower readability = more complex
            avg_sentence_len * 0.1
        )
        return float(min(1.0, max(0.0, engagement)))
    
    def _compute_social_dominance(self, behavioral: Dict, reaction: Dict) -> float:
        """
        Social Dominance: Tendency to lead/control conversations.
        High = dominant, leading; Low = passive, following
        """
        initiation = self._safe_get(behavioral, 'initiation_rate', 0)
        dominance = self._safe_get(behavioral, 'dominance_score', 0.5)
        assertiveness = self._safe_get(behavioral, 'assertiveness_score', 0)
        topic_control = self._safe_get(behavioral, 'topic_control_ratio', 0)
        steering = self._safe_get(reaction, 'conversation_steering', 0)
        
        social_dom = (
            initiation * 0.25 +
            dominance * 0.25 +
            assertiveness * 0.2 +
            topic_control * 0.15 +
            steering * 0.15
        )
        return float(min(1.0, max(0.0, social_dom)))
    
    def _compute_emotional_expressiveness(self, text: Dict, linguistic: Dict, sentiment: Dict) -> float:
        """
        Emotional Expressiveness: How much emotion is displayed in communication.
        High = expressive, emotional; Low = reserved, neutral
        """
        emoji_density = min(1.0, self._safe_get(text, 'emoji_density', 0) * 10)
        exclamation = min(1.0, self._safe_get(linguistic, 'exclamation_ratio', 0))
        sentiment_range = self._safe_get(sentiment, 'sentiment_range', 0) / 2
        intensity = self._safe_get(sentiment, 'emotional_intensity_mean', 0)
        # Removed: pos_interjection_ratio (useless - collapsed calibration)
        uppercase = min(1.0, self._safe_get(text, 'uppercase_ratio', 0) * 5)
        
        expressiveness = (
            emoji_density * 0.3 +
            exclamation * 0.25 +
            sentiment_range * 0.2 +
            intensity * 0.15 +
            uppercase * 0.1
        )
        return float(min(1.0, max(0.0, expressiveness)))
    
    def _compute_conversational_energy(self, text: Dict, behavioral: Dict, reaction: Dict) -> float:
        """
        Conversational Energy: Overall energy and enthusiasm level.
        High = energetic, enthusiastic; Low = calm, measured
        """
        enthusiasm = self._safe_get(reaction, 'response_enthusiasm', 0)
        engagement = self._safe_get(behavioral, 'engagement_level', 0)
        word_count = min(1.0, self._safe_get(text, 'word_count_mean', 10) / 30)
        msg_length = min(1.0, self._safe_get(text, 'msg_length_mean', 50) / 150)
        
        energy = (
            enthusiasm * 0.35 +
            engagement * 0.3 +
            word_count * 0.2 +
            msg_length * 0.15
        )
        return float(min(1.0, max(0.0, energy)))
    
    def _compute_linguistic_sophistication(self, text: Dict, linguistic: Dict) -> float:
        """
        Linguistic Sophistication: Complexity and sophistication of language use.
        High = sophisticated, complex; Low = simple, basic
        """
        lexical_richness = self._safe_get(text, 'lexical_richness', 0.5)
        type_token = self._safe_get(text, 'type_token_ratio', 0.5)
        char_per_word = min(1.0, self._safe_get(text, 'char_per_word_mean', 4) / 8)
        readability = self._safe_get(linguistic, 'readability_score', 50) / 100
        subordinate = min(1.0, self._safe_get(linguistic, 'subordinate_clause_ratio', 0))
        dep_depth = min(1.0, self._safe_get(linguistic, 'avg_dependency_depth', 2) / 5)
        
        sophistication = (
            lexical_richness * 0.25 +
            type_token * 0.15 +
            char_per_word * 0.15 +
            (1 - readability) * 0.2 +  # Lower readability = more sophisticated
            subordinate * 0.15 +
            dep_depth * 0.1
        )
        return float(min(1.0, max(0.0, sophistication)))
    
    def _compute_interpersonal_attunement(self, reaction: Dict, behavioral: Dict) -> float:
        """
        Interpersonal Attunement: Responsiveness and adaptation to others.
        High = attuned, responsive; Low = self-focused, unresponsive
        """
        mirroring = self._safe_get(reaction, 'sentiment_mirroring', 0.5)
        formality_match = self._safe_get(reaction, 'formality_matching', 0.5)
        energy_match = self._safe_get(reaction, 'energy_matching', 0.5)
        responsiveness = self._safe_get(reaction, 'emotional_responsiveness', 0.5)
        alignment = self._safe_get(reaction, 'semantic_alignment', 0)
        response_rate = self._safe_get(behavioral, 'response_rate', 0)
        
        attunement = (
            mirroring * 0.2 +
            formality_match * 0.15 +
            energy_match * 0.15 +
            responsiveness * 0.2 +
            alignment * 0.15 +
            response_rate * 0.15
        )
        return float(min(1.0, max(0.0, attunement)))
    
    def _compute_self_focus(self, linguistic: Dict, behavioral: Dict) -> float:
        """
        Self-Focus Tendency: Tendency to focus on self vs others.
        High = self-focused; Low = other-focused
        """
        first_person = self._safe_get(linguistic, 'first_person_ratio', 0.5)
        self_disclosure = self._safe_get(behavioral, 'self_disclosure_level', 0)
        second_person = self._safe_get(linguistic, 'second_person_ratio', 0.3)
        
        # High first person and self-disclosure, low second person = self-focused
        self_focus = (
            first_person * 0.4 +
            self_disclosure * 0.3 +
            (1 - second_person) * 0.3
        )
        return float(min(1.0, max(0.0, self_focus)))
    
    def _compute_humor_playfulness(self, text: Dict, behavioral: Dict) -> float:
        """
        Humor/Playfulness: Use of humor and playful communication.
        High = humorous, playful; Low = serious, straightforward
        """
        humor_density = min(1.0, self._safe_get(behavioral, 'humor_density', 0) * 20)
        emoji = min(1.0, self._safe_get(text, 'emoji_density', 0) * 10)
        
        playfulness = (
            humor_density * 0.6 +
            emoji * 0.4
        )
        return float(min(1.0, max(0.0, playfulness)))
    
    def _compute_formality(self, behavioral: Dict, linguistic: Dict, text: Dict) -> float:
        """
        Formality Level: Formal vs casual communication style.
        High = formal; Low = casual
        """
        formality = self._safe_get(behavioral, 'formality_score', 0.5)
        # Removed: politeness_score (useless - collapsed calibration)
        # Contractions and emoji reduce formality
        emoji = min(1.0, self._safe_get(text, 'emoji_density', 0) * 10)
        stopword_ratio = self._safe_get(text, 'stopword_ratio', 0.5)  # More stopwords = more casual
        
        formal_level = (
            formality * 0.5 +
            (1 - stopword_ratio) * 0.3 +
            (1 - emoji) * 0.2
        )
        return float(min(1.0, max(0.0, formal_level)))
    
    def _compute_agreement_orientation(self, behavioral: Dict, reaction: Dict) -> float:
        """
        Agreement Orientation: Tendency to agree vs challenge.
        High = agreeable, affirming; Low = challenging, disagreeing
        """
        affirmation = self._safe_get(reaction, 'affirmation_tendency', 0)
        agreement = self._safe_get(behavioral, 'agreement_ratio', 0) * 10
        disagreement = self._safe_get(behavioral, 'disagreement_ratio', 0) * 10
        disagree_tend = self._safe_get(reaction, 'disagreement_tendency', 0)
        
        # High agreement, low disagreement = agreeable
        orientation = (
            affirmation * 0.3 +
            min(1.0, agreement) * 0.3 +
            (1 - min(1.0, disagreement)) * 0.2 +
            (1 - disagree_tend) * 0.2
        )
        return float(min(1.0, max(0.0, orientation)))
    
    def _compute_emotional_stability(self, sentiment: Dict, composite: Dict) -> float:
        """
        Emotional Stability: Consistency of emotional expression.
        High = stable, consistent; Low = volatile, variable
        """
        volatility = self._safe_get(sentiment, 'sentiment_volatility', 0)
        sentiment_std = self._safe_get(sentiment, 'sentiment_std', 0)
        consistency = self._safe_get(sentiment, 'sentiment_consistency', 0.5)
        composite_vol = self._safe_get(composite, 'emotional_volatility_index', 0)
        
        # Invert volatility measures
        stability = (
            (1 - volatility) * 0.3 +
            (1 - sentiment_std) * 0.25 +
            consistency * 0.25 +
            (1 - composite_vol) * 0.2
        )
        return float(min(1.0, max(0.0, stability)))
    
    def _compute_curiosity_openness(self, behavioral: Dict, reaction: Dict, text: Dict) -> float:
        """
        Curiosity/Openness: Interest in exploring new topics.
        High = curious, open; Low = closed, narrow
        """
        # Use question_mark_ratio instead of question_frequency (more reliable)
        question_mark = min(1.0, self._safe_get(text, 'question_mark_ratio', 0))
        topic_expansion = self._safe_get(reaction, 'topic_expansion_rate', 0)
        interest_signals = self._safe_get(reaction, 'interest_signal_rate', 0)
        
        curiosity = (
            question_mark * 0.4 +
            topic_expansion * 0.3 +
            interest_signals * 0.3
        )
        return float(min(1.0, max(0.0, curiosity)))
    
    def _compute_supportiveness(self, behavioral: Dict, reaction: Dict) -> float:
        """
        Supportiveness: Tendency to support and encourage others.
        High = supportive, encouraging; Low = neutral, unsupportive
        """
        support = self._safe_get(behavioral, 'support_ratio', 0)
        empathy = self._safe_get(behavioral, 'empathy_score', 0)
        support_react = self._safe_get(reaction, 'support_reactivity', 0)
        
        supportiveness = (
            support * 0.35 +
            empathy * 0.35 +
            support_react * 0.3
        )
        return float(min(1.0, max(0.0, supportiveness)))
    
    def _compute_directness(self, behavioral: Dict, linguistic: Dict) -> float:
        """
        Directness/Clarity: How direct and clear communication is.
        High = direct, clear; Low = indirect, hedged
        """
        directness = self._safe_get(behavioral, 'directness_score', 0.5)
        assertiveness = self._safe_get(behavioral, 'assertiveness_score', 0)
        
        direct_clarity = (
            directness * 0.5 +
            assertiveness * 0.5
        )
        return float(min(1.0, max(0.0, direct_clarity)))
    
    def _compute_verbosity(self, text: Dict, behavioral: Dict) -> float:
        """
        Verbosity Level: How much detail/length in responses.
        High = verbose, detailed; Low = concise, brief
        """
        word_count = min(1.0, self._safe_get(text, 'word_count_mean', 10) / 50)
        msg_length = min(1.0, self._safe_get(text, 'msg_length_mean', 50) / 200)
        elaboration = self._safe_get(behavioral, 'elaboration_score', 0)
        
        verbosity = (
            word_count * 0.35 +
            msg_length * 0.35 +
            elaboration * 0.3
        )
        return float(min(1.0, max(0.0, verbosity)))
    
    def _compute_positivity_bias(self, sentiment: Dict) -> float:
        """
        Positivity Bias: Overall positive vs negative tendency.
        High = positive; Low = negative
        Boosted baseline to avoid overly depressed personas.
        """
        sentiment_mean = self._safe_get(sentiment, 'sentiment_mean', 0)
        positive_ratio = self._safe_get(sentiment, 'positive_ratio', 0.33)
        
        # Convert sentiment_mean from -1,1 to 0,1
        sentiment_normalized = (sentiment_mean + 1) / 2
        
        # Base positivity calculation
        raw_positivity = (
            sentiment_normalized * 0.5 +
            positive_ratio * 0.5
        )
        
        # Apply positivity boost - shift distribution upward to avoid depressed personas
        # Maps 0.0-1.0 to 0.25-1.0 range (minimum 25% positivity)
        boosted_positivity = 0.25 + (raw_positivity * 0.75)
        
        return float(min(1.0, max(0.0, boosted_positivity)))
    
    def _compute_engagement_consistency(self, reaction: Dict, composite: Dict) -> float:
        """
        Engagement Consistency: How consistent engagement level is.
        High = consistent; Low = variable
        """
        attention = self._safe_get(reaction, 'attention_consistency', 0.5)
        personality_consistency = self._safe_get(composite, 'personality_consistency', 0.5)
        
        consistency = (
            attention * 0.5 +
            personality_consistency * 0.5
        )
        return float(min(1.0, max(0.0, consistency)))
    
    def _compute_adaptive_communication(self, reaction: Dict) -> float:
        """
        Adaptive Communication: How much style adapts to conversation partner.
        High = adaptive; Low = rigid
        """
        style_adapt = self._safe_get(reaction, 'style_adaptation', 0.5)
        formality_match = self._safe_get(reaction, 'formality_matching', 0.5)
        energy_match = self._safe_get(reaction, 'energy_matching', 0.5)
        vocab_convergence = self._safe_get(reaction, 'vocabulary_convergence', 0)
        
        adaptive = (
            style_adapt * 0.3 +
            formality_match * 0.25 +
            energy_match * 0.25 +
            vocab_convergence * 0.2
        )
        return float(min(1.0, max(0.0, adaptive)))
    
    def _compute_initiative(self, behavioral: Dict, reaction: Dict) -> float:
        """
        Conversational Initiative: Tendency to drive conversation forward.
        High = proactive; Low = reactive
        """
        initiation = self._safe_get(behavioral, 'initiation_rate', 0)
        topic_control = self._safe_get(behavioral, 'topic_control_ratio', 0)
        steering = self._safe_get(reaction, 'conversation_steering', 0)
        
        initiative = (
            initiation * 0.4 +
            topic_control * 0.3 +
            steering * 0.3
        )
        return float(min(1.0, max(0.0, initiative)))
    
    def _compute_typing_intensity(self, text: Dict, linguistic: Dict) -> float:
        """
        Typing Intensity: Use of caps, punctuation, emphasis markers.
        High = intense typing (CAPS, !!!, expressive); Low = calm, standard typing
        """
        uppercase = self._safe_get(text, 'uppercase_ratio', 0)
        punctuation = self._safe_get(text, 'punctuation_ratio', 0)
        exclamation = self._safe_get(linguistic, 'exclamation_ratio', 0)
        emoji = self._safe_get(text, 'emoji_density', 0)
        
        # Weight uppercase heavily as it's a strong stylistic signal
        intensity = (
            min(1.0, uppercase * 15) * 0.35 +  # Uppercase is rare, weight heavily
            min(1.0, punctuation * 8) * 0.25 +
            min(1.0, exclamation) * 0.25 +
            min(1.0, emoji * 5) * 0.15
        )
        return float(min(1.0, max(0.0, intensity)))
    
    def _compute_message_brevity(self, text: Dict, behavioral: Dict) -> float:
        """
        Message Brevity: Short, punchy messages vs long paragraphs.
        High = brief messages; Low = long, detailed messages
        """
        msg_length = self._safe_get(text, 'msg_length_mean', 50)
        word_count = self._safe_get(text, 'word_count_mean', 10)
        elaboration = self._safe_get(behavioral, 'elaboration_score', 0.5)
        
        # Invert - shorter messages = higher brevity
        # Normalize: 0-20 chars = very brief, 200+ = very long
        length_score = 1.0 - min(1.0, msg_length / 150)
        word_score = 1.0 - min(1.0, word_count / 30)
        
        brevity = (
            length_score * 0.4 +
            word_score * 0.4 +
            (1 - elaboration) * 0.2
        )
        return float(min(1.0, max(0.0, brevity)))
    
    def _compute_response_tempo(self, text: Dict, context: Dict) -> float:
        """
        Response Tempo: Speed and rhythm of responses.
        High = fast, rapid-fire responses; Low = slow, deliberate
        """
        # Use context features for turn-taking patterns
        turn_regularity = self._safe_get(context, 'turn_taking_regularity', 0.5)
        engagement_vol = self._safe_get(context, 'engagement_volatility', 0.5)
        
        # Shorter messages often correlate with faster tempo
        msg_length = self._safe_get(text, 'msg_length_mean', 50)
        length_factor = 1.0 - min(1.0, msg_length / 100)
        
        tempo = (
            turn_regularity * 0.4 +
            length_factor * 0.35 +
            engagement_vol * 0.25
        )
        return float(min(1.0, max(0.0, tempo)))
    
    def _compute_text_expressiveness(self, text: Dict, linguistic: Dict, emotion: Dict) -> float:
        """
        Text Expressiveness: How expressive the text style is.
        High = expressive (emojis, caps, punctuation); Low = plain text
        """
        emoji = self._safe_get(text, 'emoji_density', 0)
        uppercase = self._safe_get(text, 'uppercase_ratio', 0)
        exclamation = self._safe_get(linguistic, 'exclamation_ratio', 0)
        question = self._safe_get(text, 'question_mark_ratio', 0)
        # Removed: pos_interjection_ratio (useless - collapsed calibration)
        
        # Use emotion features if available
        emotion_intensity = self._safe_get(emotion, 'emotion_intensity_mean', 0.3)
        
        expressiveness = (
            min(1.0, emoji * 8) * 0.3 +
            min(1.0, uppercase * 12) * 0.2 +
            min(1.0, exclamation) * 0.2 +
            min(1.0, question) * 0.1 +
            emotion_intensity * 0.2
        )
        return float(min(1.0, max(0.0, expressiveness)))
    
    def _compute_conversation_rhythm(self, context: Dict, behavioral: Dict) -> float:
        """
        Conversation Rhythm: Pattern of conversation flow.
        High = dynamic, varied rhythm; Low = steady, consistent rhythm
        """
        momentum = self._safe_get(context, 'conversation_momentum', 0.5)
        engagement_vol = self._safe_get(context, 'engagement_volatility', 0.3)
        turn_regularity = self._safe_get(context, 'turn_taking_regularity', 0.5)
        monologue = self._safe_get(context, 'monologue_tendency', 0)
        
        # Dynamic rhythm = high volatility, varied patterns
        rhythm = (
            engagement_vol * 0.3 +
            (1 - turn_regularity) * 0.25 +  # Irregular = more dynamic
            monologue * 0.2 +
            abs(momentum - 0.5) * 0.25  # Deviation from neutral = more dynamic
        )
        return float(min(1.0, max(0.0, rhythm)))
    
    def get_feature_names(self) -> list:
        """Return list of feature names."""
        return self.feature_names.copy()
    
    def get_feature_descriptions(self) -> Dict[str, str]:
        """Return descriptions for each synthetic feature."""
        return {
            'communication_warmth': 'Overall friendliness and warmth (0=cold, 1=warm)',
            'intellectual_engagement': 'Depth of thought and analysis (0=surface, 1=deep)',
            'social_dominance': 'Tendency to lead conversations (0=passive, 1=dominant)',
            'emotional_expressiveness': 'How much emotion is displayed (0=reserved, 1=expressive)',
            'conversational_energy': 'Overall energy level (0=calm, 1=energetic)',
            'linguistic_sophistication': 'Language complexity (0=simple, 1=sophisticated)',
            'interpersonal_attunement': 'Responsiveness to others (0=unresponsive, 1=attuned)',
            'self_focus_tendency': 'Focus on self vs others (0=other-focused, 1=self-focused)',
            'humor_playfulness': 'Use of humor (0=serious, 1=playful)',
            'formality_level': 'Communication formality (0=casual, 1=formal)',
            'agreement_orientation': 'Tendency to agree (0=challenging, 1=agreeable)',
            'emotional_stability': 'Emotional consistency (0=volatile, 1=stable)',
            'curiosity_openness': 'Interest in new topics (0=closed, 1=curious)',
            'supportiveness': 'Tendency to support others (0=neutral, 1=supportive)',
            'directness_clarity': 'How direct communication is (0=indirect, 1=direct)',
            'verbosity_level': 'Amount of detail (0=concise, 1=verbose)',
            'positivity_bias': 'Overall sentiment tendency (0=negative, 1=positive)',
            'engagement_consistency': 'Consistency of engagement (0=variable, 1=consistent)',
            'adaptive_communication': 'Style adaptation to partner (0=rigid, 1=adaptive)',
            'conversational_initiative': 'Tendency to drive conversation (0=reactive, 1=proactive)',
            'typing_intensity': 'Use of caps, punctuation, emphasis (0=calm, 1=intense)',
            'message_brevity': 'Message length tendency (0=long paragraphs, 1=short bursts)',
            'response_tempo': 'Speed of conversation (0=slow/deliberate, 1=fast/rapid)',
            'text_expressiveness': 'Expressiveness in text style (0=plain, 1=expressive)',
            'conversation_rhythm': 'Conversation flow pattern (0=steady, 1=dynamic/varied)'
        }
