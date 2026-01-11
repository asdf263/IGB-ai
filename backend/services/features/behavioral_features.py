"""
Behavioral Pattern Feature Extraction Module
Extracts ~25 conversational behavior and social signal features from chat messages
"""
import numpy as np
import re
from typing import List, Dict, Any
from collections import Counter


class BehavioralFeatureExtractor:
    """Extracts behavioral pattern features from chat messages."""
    
    def __init__(self):
        self.feature_names = [
            'response_rate',
            'initiation_rate',
            'avg_turn_length',
            'turn_length_variance',
            'question_frequency',
            'answer_frequency',
            'affirmation_frequency',
            'elaboration_score',
            'politeness_score',
            'formality_score',
            'humor_density',
            'sarcasm_probability',
            'empathy_score',
            'directness_score',
            'assertiveness_score',
            'engagement_level',
            'reciprocity_index',
            'dominance_score',
            'topic_control_ratio',
            'interruption_proxy',
            'agreement_ratio',
            'disagreement_ratio',
            'support_ratio',
            'criticism_ratio',
            'self_disclosure_level'
        ]
        
        self.affirmations = {'yes', 'yeah', 'yep', 'sure', 'okay', 'ok', 'right', 'exactly',
                            'absolutely', 'definitely', 'certainly', 'agreed', 'true', 'correct'}
        self.politeness_markers = {'please', 'thank', 'thanks', 'sorry', 'excuse', 'pardon',
                                   'appreciate', 'grateful', 'kindly', 'would you', 'could you'}
        self.formal_markers = {'therefore', 'however', 'furthermore', 'moreover', 'regarding',
                              'consequently', 'accordingly', 'hence', 'thus', 'nevertheless'}
        self.informal_markers = {'gonna', 'wanna', 'gotta', 'kinda', 'sorta', 'yeah', 'nope',
                                'cool', 'awesome', 'lol', 'haha', 'omg', 'btw', 'idk'}
        self.humor_markers = {'lol', 'haha', 'hehe', 'rofl', 'lmao', 'joke', 'funny', 'hilarious',
                             'kidding', 'jk', 'humor', '😂', '🤣', '😄', '😆'}
        self.empathy_markers = {'understand', 'feel', 'sorry', 'sympathize', 'care', 'support',
                               'here for you', 'tough', 'difficult', 'hard', 'hope', 'wish'}
        self.assertive_markers = {'must', 'should', 'need', 'have to', 'definitely', 'certainly',
                                 'absolutely', 'clearly', 'obviously', 'undoubtedly'}
        self.hedge_markers = {'maybe', 'perhaps', 'possibly', 'might', 'could', 'seem', 'think',
                             'believe', 'guess', 'suppose', 'probably', 'somewhat'}
        self.agreement_markers = {'agree', 'right', 'exactly', 'true', 'correct', 'yes', 'same',
                                 'absolutely', 'definitely', 'totally'}
        self.disagreement_markers = {'disagree', 'wrong', 'incorrect', 'no', 'nope', 'but',
                                    'however', 'actually', 'not really', 'don\'t think'}
        self.support_markers = {'help', 'support', 'encourage', 'great job', 'well done', 'proud',
                               'amazing', 'awesome', 'fantastic', 'keep going', 'you can'}
        self.criticism_markers = {'wrong', 'bad', 'poor', 'terrible', 'mistake', 'error', 'fail',
                                 'shouldn\'t', 'why did you', 'you always', 'you never'}
        self.self_disclosure = {'i feel', 'i think', 'i believe', 'my opinion', 'personally',
                               'to be honest', 'honestly', 'i\'m', 'my life', 'my experience'}
    
    def extract(self, messages: List[Dict[str, Any]], target_user: str = None) -> Dict[str, float]:
        """
        Extract all behavioral features from messages.
        
        Args:
            messages: All messages in the conversation
            target_user: The user to extract features for (if None, defaults to 'user' for backward compatibility)
        """
        if not messages:
            return {name: 0.0 for name in self.feature_names}
        
        # Default to 'user' for backward compatibility
        if target_user is None:
            target_user = 'user'
        
        # Get all participants
        participants = list(set(m.get('sender') for m in messages if m.get('sender')))
        
        # Filter messages for target user and others
        user_messages = [m for m in messages if m.get('sender') == target_user]
        other_messages = [m for m in messages if m.get('sender') != target_user]
        
        # Get the "other" participant (for 2-person conversations)
        other_user = None
        if len(participants) == 2:
            other_user = [p for p in participants if p != target_user][0]
        
        features = {}
        
        # Response and initiation patterns
        features['response_rate'] = self._compute_response_rate(messages, target_user, other_user)
        features['initiation_rate'] = self._compute_initiation_rate(messages, target_user)
        
        # Turn length features
        turn_features = self._compute_turn_features(messages, target_user)
        features.update(turn_features)
        
        # Question and answer patterns
        qa_features = self._compute_qa_features(user_messages)
        features.update(qa_features)
        
        # Communication style features
        style_features = self._compute_style_features(user_messages)
        features.update(style_features)
        
        # Social behavior features
        social_features = self._compute_social_features(user_messages)
        features.update(social_features)
        
        # Interaction dynamics
        dynamics_features = self._compute_dynamics_features(messages, user_messages, target_user, other_user)
        features.update(dynamics_features)
        
        return features
    
    def _compute_response_rate(self, messages: List[Dict[str, Any]], target_user: str, other_user: str = None) -> float:
        """Compute how often target_user responds to other person's messages."""
        if len(messages) < 2 or not other_user:
            return 0.0
        
        responses = 0
        opportunities = 0
        
        for i in range(1, len(messages)):
            if messages[i-1].get('sender') == other_user:
                opportunities += 1
                if messages[i].get('sender') == target_user:
                    responses += 1
        
        return responses / opportunities if opportunities > 0 else 0.0
    
    def _compute_initiation_rate(self, messages: List[Dict[str, Any]], target_user: str) -> float:
        """Compute how often target_user initiates conversation."""
        if not messages:
            return 0.0
        
        user_messages = [m for m in messages if m.get('sender') == target_user]
        if not user_messages:
            return 0.0
        
        initiations = 0
        for i, msg in enumerate(messages):
            if msg.get('sender') == target_user:
                if i == 0 or messages[i-1].get('sender') == target_user:
                    initiations += 1
        
        return initiations / len(user_messages)
    
    def _compute_turn_features(self, messages: List[Dict[str, Any]], target_user: str, other_user: str = None) -> Dict[str, float]:
        """Compute turn-taking features."""
        user_turns = []
        current_turn = []
        prev_sender = None
        
        for msg in messages:
            sender = msg.get('sender')
            if sender != prev_sender:
                if current_turn and prev_sender == target_user:
                    user_turns.append(current_turn)
                current_turn = [msg]
                prev_sender = sender
            else:
                current_turn.append(msg)
        
        if current_turn:
            user_turns.append(current_turn)
        
        if not user_turns:
            return {'avg_turn_length': 0.0, 'turn_length_variance': 0.0}
        
        turn_lengths = [len(turn) for turn in user_turns]
        return {
            'avg_turn_length': float(np.mean(turn_lengths)),
            'turn_length_variance': float(np.var(turn_lengths))
        }
    
    def _compute_qa_features(self, user_messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """Compute question and answer frequency features."""
        if not user_messages:
            return {
                'question_frequency': 0.0,
                'answer_frequency': 0.0,
                'affirmation_frequency': 0.0,
                'elaboration_score': 0.0
            }
        
        texts = [m.get('text', '') for m in user_messages]
        total = len(texts)
        
        question_count = sum(1 for t in texts if '?' in t)
        
        answer_starters = {'yes', 'no', 'yeah', 'nope', 'sure', 'okay', 'because', 'well'}
        answer_count = sum(1 for t in texts 
                          if t.lower().split()[0] in answer_starters if t.split())
        
        affirmation_count = sum(1 for t in texts 
                               for w in t.lower().split() if w in self.affirmations)
        
        avg_length = np.mean([len(t.split()) for t in texts])
        elaboration = min(1.0, avg_length / 50)
        
        return {
            'question_frequency': question_count / total,
            'answer_frequency': answer_count / total,
            'affirmation_frequency': affirmation_count / total,
            'elaboration_score': float(elaboration)
        }
    
    def _compute_style_features(self, user_messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """Compute communication style features."""
        if not user_messages:
            return {
                'politeness_score': 0.0,
                'formality_score': 0.0,
                'humor_density': 0.0,
                'sarcasm_probability': 0.0
            }
        
        all_text = ' '.join(m.get('text', '') for m in user_messages).lower()
        words = all_text.split()
        total_words = len(words) if words else 1
        
        politeness = sum(1 for w in words if w in self.politeness_markers)
        formal = sum(1 for w in words if w in self.formal_markers)
        informal = sum(1 for w in words if w in self.informal_markers)
        humor = sum(1 for w in words if w in self.humor_markers)
        
        formality_score = (formal - informal) / total_words if total_words > 0 else 0
        formality_score = (formality_score + 1) / 2
        
        sarcasm_indicators = all_text.count('...') + all_text.count('right...') + \
                            all_text.count('sure') + all_text.count('totally')
        sarcasm_prob = min(1.0, sarcasm_indicators / max(len(user_messages), 1) * 0.2)
        
        return {
            'politeness_score': min(1.0, politeness / total_words * 10),
            'formality_score': float(max(0, min(1, formality_score))),
            'humor_density': humor / total_words,
            'sarcasm_probability': float(sarcasm_prob)
        }
    
    def _compute_social_features(self, user_messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """Compute social behavior features."""
        if not user_messages:
            return {
                'empathy_score': 0.0,
                'directness_score': 0.0,
                'assertiveness_score': 0.0,
                'agreement_ratio': 0.0,
                'disagreement_ratio': 0.0,
                'support_ratio': 0.0,
                'criticism_ratio': 0.0,
                'self_disclosure_level': 0.0
            }
        
        all_text = ' '.join(m.get('text', '') for m in user_messages).lower()
        words = all_text.split()
        total_words = len(words) if words else 1
        total_messages = len(user_messages)
        
        empathy = sum(1 for phrase in self.empathy_markers if phrase in all_text)
        assertive = sum(1 for w in words if w in self.assertive_markers)
        hedge = sum(1 for w in words if w in self.hedge_markers)
        agreement = sum(1 for w in words if w in self.agreement_markers)
        disagreement = sum(1 for w in words if w in self.disagreement_markers)
        support = sum(1 for phrase in self.support_markers if phrase in all_text)
        criticism = sum(1 for phrase in self.criticism_markers if phrase in all_text)
        disclosure = sum(1 for phrase in self.self_disclosure if phrase in all_text)
        
        directness = 1.0 - (hedge / total_words * 10) if total_words > 0 else 0.5
        assertiveness = assertive / total_words * 10 if total_words > 0 else 0
        
        return {
            'empathy_score': min(1.0, empathy / total_messages),
            'directness_score': float(max(0, min(1, directness))),
            'assertiveness_score': float(min(1.0, assertiveness)),
            'agreement_ratio': agreement / total_words,
            'disagreement_ratio': disagreement / total_words,
            'support_ratio': min(1.0, support / total_messages),
            'criticism_ratio': min(1.0, criticism / total_messages),
            'self_disclosure_level': min(1.0, disclosure / total_messages)
        }
    
    def _compute_dynamics_features(self, messages: List[Dict[str, Any]], 
                                   user_messages: List[Dict[str, Any]],
                                   target_user: str,
                                   other_user: str = None) -> Dict[str, float]:
        """Compute interaction dynamics features."""
        if not messages or not user_messages:
            return {
                'engagement_level': 0.0,
                'reciprocity_index': 0.0,
                'dominance_score': 0.0,
                'topic_control_ratio': 0.0,
                'interruption_proxy': 0.0
            }
        
        user_count = len(user_messages)
        other_count = len(messages) - user_count
        total = len(messages)
        
        user_words = sum(len(m.get('text', '').split()) for m in user_messages)
        other_words = sum(len(m.get('text', '').split()) for m in messages if m.get('sender') == other_user) if other_user else 0
        
        engagement = min(1.0, user_count / max(total, 1) * 2)
        
        reciprocity = 1.0 - abs(user_words - other_words) / max(user_words + other_words, 1) if other_user else 0.5
        
        total_words = user_words + other_words
        dominance = (user_words - other_words) / max(user_words + other_words, 1) if other_user else 0.0
        
        question_initiations = sum(1 for m in user_messages if '?' in m.get('text', ''))
        topic_control = question_initiations / max(user_count, 1)
        
        short_responses = sum(1 for m in user_messages if len(m.get('text', '').split()) < 3)
        interruption_proxy = short_responses / max(user_count, 1)
        
        return {
            'engagement_level': float(engagement),
            'reciprocity_index': float(reciprocity),
            'dominance_score': float(dominance),
            'topic_control_ratio': float(topic_control),
            'interruption_proxy': float(interruption_proxy)
        }
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names."""
        return self.feature_names.copy()
