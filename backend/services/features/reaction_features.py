"""
Reaction-Based Feature Extraction Module
Extracts features based on how a user reacts to the other person in a conversation.
Analyzes response patterns, sentiment shifts, engagement changes, and behavioral adaptations.
"""
import numpy as np
import re
from typing import List, Dict, Any, Tuple
from collections import defaultdict


class ReactionFeatureExtractor:
    """Extracts features based on user reactions to the other person's messages."""
    
    def __init__(self):
        self.feature_names = [
            # Response behavior features
            'response_enthusiasm',
            'response_length_ratio',
            'response_speed_consistency',
            'engagement_after_questions',
            'engagement_after_statements',
            
            # Sentiment reaction features
            'sentiment_mirroring',
            'sentiment_amplification',
            'sentiment_dampening',
            'emotional_responsiveness',
            'mood_influence_susceptibility',
            
            # Topic reaction features
            'topic_following_rate',
            'topic_expansion_rate',
            'topic_deflection_rate',
            'semantic_alignment',
            'conversation_steering',
            
            # Social reaction features
            'affirmation_tendency',
            'disagreement_tendency',
            'elaboration_on_partner_topics',
            'question_responsiveness',
            'support_reactivity',
            
            # Engagement dynamics
            'attention_consistency',
            'interest_signal_rate',
            'disengagement_signals',
            'reciprocity_balance',
            'conversation_investment',
            
            # Adaptive behavior
            'style_adaptation',
            'formality_matching',
            'energy_matching',
            'vocabulary_convergence',
            'communication_synchrony'
        ]
        
        self.positive_words = {
            'good', 'great', 'awesome', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'happy', 'glad', 'pleased', 'delighted', 'excited', 'thrilled',
            'perfect', 'beautiful', 'brilliant', 'outstanding', 'superb', 'terrific',
            'nice', 'fine', 'cool', 'best', 'better', 'fun', 'enjoy', 'thanks', 'thank'
        }
        
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'dislike', 'angry',
            'sad', 'upset', 'disappointed', 'frustrated', 'annoyed', 'irritated', 'furious',
            'depressed', 'miserable', 'unhappy', 'worried', 'anxious', 'stressed', 'nervous'
        }
        
        self.affirmations = {'yes', 'yeah', 'yep', 'sure', 'okay', 'ok', 'right', 'exactly',
                            'absolutely', 'definitely', 'certainly', 'agreed', 'true', 'correct'}
        
        self.disagreements = {'no', 'nope', 'disagree', 'wrong', 'incorrect', 'but', 'however',
                             'actually', 'not really', "don't think", 'doubt'}
        
        self.interest_signals = {'interesting', 'wow', 'really', 'tell me more', 'how', 'why',
                                'what', 'cool', 'amazing', 'fascinating', 'curious'}
        
        self.disengagement_signals = {'ok', 'k', 'sure', 'whatever', 'fine', 'mhm', 'hmm',
                                      'anyway', 'gtg', 'bye', 'later', 'busy'}
    
    def extract_for_user(self, messages: List[Dict[str, Any]], target_sender: str) -> Dict[str, float]:
        """
        Extract reaction features for a specific user based on how they react to the other person.
        
        Args:
            messages: List of all messages in conversation
            target_sender: The sender whose reactions we're analyzing
        """
        if not messages or len(messages) < 2:
            return {name: 0.0 for name in self.feature_names}
        
        # Separate messages and find reaction pairs
        reaction_pairs = self._find_reaction_pairs(messages, target_sender)
        
        if not reaction_pairs:
            return {name: 0.0 for name in self.feature_names}
        
        features = {}
        
        # Response behavior features
        features.update(self._compute_response_behavior(reaction_pairs))
        
        # Sentiment reaction features
        features.update(self._compute_sentiment_reactions(reaction_pairs))
        
        # Topic reaction features
        features.update(self._compute_topic_reactions(reaction_pairs))
        
        # Social reaction features
        features.update(self._compute_social_reactions(reaction_pairs))
        
        # Engagement dynamics
        features.update(self._compute_engagement_dynamics(reaction_pairs, messages, target_sender))
        
        # Adaptive behavior
        features.update(self._compute_adaptive_behavior(reaction_pairs))
        
        return features
    
    def _find_reaction_pairs(self, messages: List[Dict[str, Any]], target_sender: str) -> List[Tuple[Dict, Dict]]:
        """Find pairs of (other_person_message, target_user_response)."""
        pairs = []
        
        for i in range(1, len(messages)):
            current = messages[i]
            previous = messages[i-1]
            
            if current.get('sender') == target_sender and previous.get('sender') != target_sender:
                pairs.append((previous, current))
        
        return pairs
    
    def _compute_sentiment(self, text: str) -> float:
        """Compute sentiment score for text (-1 to 1)."""
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0
        
        positive_count = sum(1 for w in words if w in self.positive_words)
        negative_count = sum(1 for w in words if w in self.negative_words)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / len(words) * 5
    
    def _compute_response_behavior(self, pairs: List[Tuple[Dict, Dict]]) -> Dict[str, float]:
        """Compute response behavior features."""
        if not pairs:
            return {
                'response_enthusiasm': 0.0,
                'response_length_ratio': 0.0,
                'response_speed_consistency': 0.0,
                'engagement_after_questions': 0.0,
                'engagement_after_statements': 0.0
            }
        
        length_ratios = []
        enthusiasm_scores = []
        question_engagements = []
        statement_engagements = []
        
        for trigger, response in pairs:
            trigger_text = trigger.get('text', '')
            response_text = response.get('text', '')
            
            trigger_len = len(trigger_text.split())
            response_len = len(response_text.split())
            
            if trigger_len > 0:
                length_ratios.append(response_len / trigger_len)
            
            # Enthusiasm: exclamations, positive words, length
            exclamations = response_text.count('!')
            positive_count = sum(1 for w in response_text.lower().split() if w in self.positive_words)
            enthusiasm = min(1.0, (exclamations * 0.2 + positive_count * 0.1 + response_len * 0.01))
            enthusiasm_scores.append(enthusiasm)
            
            # Engagement based on trigger type
            engagement = response_len / 20  # Normalize by expected length
            if '?' in trigger_text:
                question_engagements.append(min(1.0, engagement))
            else:
                statement_engagements.append(min(1.0, engagement))
        
        return {
            'response_enthusiasm': float(np.mean(enthusiasm_scores)) if enthusiasm_scores else 0.0,
            'response_length_ratio': float(np.clip(np.mean(length_ratios), 0, 2) / 2) if length_ratios else 0.0,
            'response_speed_consistency': 0.5,  # Would need timestamps
            'engagement_after_questions': float(np.mean(question_engagements)) if question_engagements else 0.0,
            'engagement_after_statements': float(np.mean(statement_engagements)) if statement_engagements else 0.0
        }
    
    def _compute_sentiment_reactions(self, pairs: List[Tuple[Dict, Dict]]) -> Dict[str, float]:
        """Compute sentiment-based reaction features."""
        if not pairs:
            return {
                'sentiment_mirroring': 0.0,
                'sentiment_amplification': 0.0,
                'sentiment_dampening': 0.0,
                'emotional_responsiveness': 0.0,
                'mood_influence_susceptibility': 0.0
            }
        
        mirroring_scores = []
        amplification_scores = []
        dampening_scores = []
        responsiveness_scores = []
        
        for trigger, response in pairs:
            trigger_sentiment = self._compute_sentiment(trigger.get('text', ''))
            response_sentiment = self._compute_sentiment(response.get('text', ''))
            
            # Mirroring: how much response sentiment matches trigger
            if abs(trigger_sentiment) > 0.1:
                same_direction = (trigger_sentiment * response_sentiment) > 0
                mirroring_scores.append(1.0 if same_direction else 0.0)
                
                # Amplification vs dampening
                if same_direction:
                    if abs(response_sentiment) > abs(trigger_sentiment):
                        amplification_scores.append(min(1.0, abs(response_sentiment - trigger_sentiment)))
                    else:
                        dampening_scores.append(min(1.0, abs(trigger_sentiment - response_sentiment)))
            
            # Responsiveness: any sentiment response to emotional trigger
            if abs(trigger_sentiment) > 0.2:
                responsiveness_scores.append(min(1.0, abs(response_sentiment) * 2))
        
        # Mood influence: correlation between trigger and response sentiments
        if len(pairs) >= 3:
            trigger_sentiments = [self._compute_sentiment(p[0].get('text', '')) for p in pairs]
            response_sentiments = [self._compute_sentiment(p[1].get('text', '')) for p in pairs]
            correlation = np.corrcoef(trigger_sentiments, response_sentiments)[0, 1]
            mood_influence = (correlation + 1) / 2 if not np.isnan(correlation) else 0.5
        else:
            mood_influence = 0.5
        
        return {
            'sentiment_mirroring': float(np.mean(mirroring_scores)) if mirroring_scores else 0.5,
            'sentiment_amplification': float(np.mean(amplification_scores)) if amplification_scores else 0.0,
            'sentiment_dampening': float(np.mean(dampening_scores)) if dampening_scores else 0.0,
            'emotional_responsiveness': float(np.mean(responsiveness_scores)) if responsiveness_scores else 0.5,
            'mood_influence_susceptibility': float(mood_influence)
        }
    
    def _compute_topic_reactions(self, pairs: List[Tuple[Dict, Dict]]) -> Dict[str, float]:
        """Compute topic-based reaction features."""
        if not pairs:
            return {
                'topic_following_rate': 0.0,
                'topic_expansion_rate': 0.0,
                'topic_deflection_rate': 0.0,
                'semantic_alignment': 0.0,
                'conversation_steering': 0.0
            }
        
        following_scores = []
        expansion_scores = []
        deflection_scores = []
        steering_scores = []
        
        for trigger, response in pairs:
            trigger_words = set(re.findall(r'\b\w{4,}\b', trigger.get('text', '').lower()))
            response_words = set(re.findall(r'\b\w{4,}\b', response.get('text', '').lower()))
            
            if trigger_words:
                # Topic following: shared words
                overlap = len(trigger_words & response_words) / len(trigger_words)
                following_scores.append(overlap)
                
                # Topic expansion: new words added
                new_words = len(response_words - trigger_words)
                expansion_scores.append(min(1.0, new_words / 10))
                
                # Deflection: completely different topic
                if overlap < 0.1 and len(response_words) > 3:
                    deflection_scores.append(1.0)
                else:
                    deflection_scores.append(0.0)
            
            # Steering: asking questions to change direction
            if '?' in response.get('text', ''):
                steering_scores.append(1.0)
            else:
                steering_scores.append(0.0)
        
        # Semantic alignment: average word overlap
        semantic_alignment = float(np.mean(following_scores)) if following_scores else 0.0
        
        return {
            'topic_following_rate': float(np.mean(following_scores)) if following_scores else 0.0,
            'topic_expansion_rate': float(np.mean(expansion_scores)) if expansion_scores else 0.0,
            'topic_deflection_rate': float(np.mean(deflection_scores)) if deflection_scores else 0.0,
            'semantic_alignment': semantic_alignment,
            'conversation_steering': float(np.mean(steering_scores)) if steering_scores else 0.0
        }
    
    def _compute_social_reactions(self, pairs: List[Tuple[Dict, Dict]]) -> Dict[str, float]:
        """Compute social reaction features."""
        if not pairs:
            return {
                'affirmation_tendency': 0.0,
                'disagreement_tendency': 0.0,
                'elaboration_on_partner_topics': 0.0,
                'question_responsiveness': 0.0,
                'support_reactivity': 0.0
            }
        
        affirmation_scores = []
        disagreement_scores = []
        elaboration_scores = []
        question_response_scores = []
        support_scores = []
        
        support_words = {'help', 'support', 'understand', 'here for you', 'sorry to hear',
                        'that sounds', 'must be', 'hope', 'wish', 'care'}
        
        for trigger, response in pairs:
            response_text = response.get('text', '').lower()
            response_words = set(response_text.split())
            
            # Affirmation tendency
            affirm_count = len(response_words & self.affirmations)
            affirmation_scores.append(min(1.0, affirm_count / 2))
            
            # Disagreement tendency
            disagree_count = sum(1 for d in self.disagreements if d in response_text)
            disagreement_scores.append(min(1.0, disagree_count / 2))
            
            # Elaboration
            response_len = len(response_text.split())
            elaboration_scores.append(min(1.0, response_len / 30))
            
            # Question responsiveness
            if '?' in trigger.get('text', ''):
                # Good response to question: longer, no deflection
                quality = min(1.0, response_len / 15)
                question_response_scores.append(quality)
            
            # Support reactivity
            support_count = sum(1 for s in support_words if s in response_text)
            support_scores.append(min(1.0, support_count / 2))
        
        return {
            'affirmation_tendency': float(np.mean(affirmation_scores)),
            'disagreement_tendency': float(np.mean(disagreement_scores)),
            'elaboration_on_partner_topics': float(np.mean(elaboration_scores)),
            'question_responsiveness': float(np.mean(question_response_scores)) if question_response_scores else 0.5,
            'support_reactivity': float(np.mean(support_scores))
        }
    
    def _compute_engagement_dynamics(self, pairs: List[Tuple[Dict, Dict]], 
                                     messages: List[Dict[str, Any]], 
                                     target_sender: str) -> Dict[str, float]:
        """Compute engagement dynamics features."""
        if not pairs:
            return {
                'attention_consistency': 0.0,
                'interest_signal_rate': 0.0,
                'disengagement_signals': 0.0,
                'reciprocity_balance': 0.0,
                'conversation_investment': 0.0
            }
        
        response_lengths = []
        interest_counts = []
        disengage_counts = []
        
        for trigger, response in pairs:
            response_text = response.get('text', '').lower()
            response_len = len(response_text.split())
            response_lengths.append(response_len)
            
            # Interest signals
            interest_count = sum(1 for s in self.interest_signals if s in response_text)
            interest_counts.append(interest_count)
            
            # Disengagement signals
            disengage_count = sum(1 for s in self.disengagement_signals if s in response_text)
            if response_len < 3:
                disengage_count += 1
            disengage_counts.append(disengage_count)
        
        # Attention consistency: variance in response lengths
        attention_consistency = 1.0 / (1.0 + np.std(response_lengths) / 10) if response_lengths else 0.5
        
        # Reciprocity: balance of message counts
        user_msgs = [m for m in messages if m.get('sender') == target_sender]
        other_msgs = [m for m in messages if m.get('sender') != target_sender]
        if other_msgs:
            reciprocity = min(len(user_msgs), len(other_msgs)) / max(len(user_msgs), len(other_msgs))
        else:
            reciprocity = 0.0
        
        # Conversation investment: total words contributed
        total_words = sum(len(m.get('text', '').split()) for m in user_msgs)
        investment = min(1.0, total_words / 500)
        
        return {
            'attention_consistency': float(attention_consistency),
            'interest_signal_rate': float(np.mean(interest_counts) / 3) if interest_counts else 0.0,
            'disengagement_signals': float(np.mean(disengage_counts) / 3) if disengage_counts else 0.0,
            'reciprocity_balance': float(reciprocity),
            'conversation_investment': float(investment)
        }
    
    def _compute_adaptive_behavior(self, pairs: List[Tuple[Dict, Dict]]) -> Dict[str, float]:
        """Compute adaptive behavior features."""
        if not pairs:
            return {
                'style_adaptation': 0.0,
                'formality_matching': 0.0,
                'energy_matching': 0.0,
                'vocabulary_convergence': 0.0,
                'communication_synchrony': 0.0
            }
        
        formality_matches = []
        energy_matches = []
        vocab_convergences = []
        
        formal_words = {'therefore', 'however', 'furthermore', 'regarding', 'consequently'}
        informal_words = {'gonna', 'wanna', 'lol', 'haha', 'omg', 'btw', 'yeah', 'nope'}
        
        for trigger, response in pairs:
            trigger_text = trigger.get('text', '').lower()
            response_text = response.get('text', '').lower()
            
            # Formality matching
            trigger_formal = sum(1 for w in formal_words if w in trigger_text)
            trigger_informal = sum(1 for w in informal_words if w in trigger_text)
            response_formal = sum(1 for w in formal_words if w in response_text)
            response_informal = sum(1 for w in informal_words if w in response_text)
            
            trigger_formality = trigger_formal - trigger_informal
            response_formality = response_formal - response_informal
            formality_diff = abs(trigger_formality - response_formality)
            formality_matches.append(1.0 / (1.0 + formality_diff))
            
            # Energy matching (length and punctuation)
            trigger_energy = len(trigger_text) + trigger_text.count('!') * 10
            response_energy = len(response_text) + response_text.count('!') * 10
            if trigger_energy > 0:
                energy_ratio = min(response_energy, trigger_energy) / max(response_energy, trigger_energy)
                energy_matches.append(energy_ratio)
            
            # Vocabulary convergence
            trigger_words = set(trigger_text.split())
            response_words = set(response_text.split())
            if trigger_words:
                convergence = len(trigger_words & response_words) / len(trigger_words)
                vocab_convergences.append(convergence)
        
        # Style adaptation: average of all matching scores
        style_adaptation = np.mean([
            np.mean(formality_matches) if formality_matches else 0.5,
            np.mean(energy_matches) if energy_matches else 0.5,
            np.mean(vocab_convergences) if vocab_convergences else 0.5
        ])
        
        return {
            'style_adaptation': float(style_adaptation),
            'formality_matching': float(np.mean(formality_matches)) if formality_matches else 0.5,
            'energy_matching': float(np.mean(energy_matches)) if energy_matches else 0.5,
            'vocabulary_convergence': float(np.mean(vocab_convergences)) if vocab_convergences else 0.0,
            'communication_synchrony': float(style_adaptation)
        }
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names."""
        return self.feature_names.copy()
