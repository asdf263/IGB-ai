"""
Conversation Context Feature Extraction Module
Extracts features about conversation flow, topic transitions, and dialogue dynamics.
Captures the structure and progression of conversations beyond individual messages.
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import re
from collections import Counter


class ConversationContextExtractor:
    """Extracts features about conversation flow and context."""
    
    def __init__(self):
        self.feature_names = [
            # Topic flow features
            'topic_continuity_score',
            'topic_introduction_rate',
            'topic_depth_score',
            'topic_breadth_score',
            'topic_return_frequency',
            
            # Conversation structure
            'exchange_balance',
            'conversation_momentum',
            'dialogue_density',
            'response_relevance_mean',
            'tangent_frequency',
            
            # Turn dynamics
            'turn_taking_regularity',
            'monologue_tendency',
            'interruption_pattern',
            'conversation_dominance_shift',
            'speaking_time_variance',
            
            # Engagement patterns
            'engagement_trajectory',
            'attention_decay_rate',
            're_engagement_frequency',
            'peak_engagement_timing',
            'engagement_volatility',
            
            # Conversation phases
            'opening_warmth',
            'closing_warmth',
            'mid_conversation_depth',
            'phase_transition_smoothness',
            'conversation_arc_completeness'
        ]
        
        # Topic indicators for detecting topic changes
        self.topic_shift_markers = {
            'anyway', 'speaking of', 'by the way', 'btw', 'oh', 'also',
            'another thing', 'on another note', 'changing topic', 'random but',
            'unrelated', 'off topic', 'so anyway', 'moving on'
        }
        
        self.topic_continuation_markers = {
            'yeah', 'yes', 'exactly', 'right', 'true', 'agreed', 'same',
            'and', 'also', 'plus', 'moreover', 'furthermore', 'additionally',
            'about that', 'regarding', 'on that note', 'speaking of which'
        }
        
        self.engagement_markers = {
            'interesting', 'wow', 'really', 'tell me more', 'how', 'why',
            'what', 'cool', 'amazing', 'fascinating', 'curious', '?',
            'love', 'great', 'awesome', '!', 'haha', 'lol'
        }
        
        self.disengagement_markers = {
            'ok', 'k', 'sure', 'whatever', 'fine', 'mhm', 'hmm',
            'anyway', 'gtg', 'bye', 'later', 'busy', 'brb', 'ttyl'
        }
    
    def extract(self, messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract conversation context features.
        
        Args:
            messages: List of message dicts with 'text' and 'sender' fields
            
        Returns:
            Dict of conversation context features
        """
        if not messages or len(messages) < 2:
            return {name: 0.0 for name in self.feature_names}
        
        features = {}
        
        # Topic flow features
        topic_features = self._extract_topic_flow(messages)
        features.update(topic_features)
        
        # Conversation structure features
        structure_features = self._extract_structure(messages)
        features.update(structure_features)
        
        # Turn dynamics features
        turn_features = self._extract_turn_dynamics(messages)
        features.update(turn_features)
        
        # Engagement pattern features
        engagement_features = self._extract_engagement_patterns(messages)
        features.update(engagement_features)
        
        # Conversation phase features
        phase_features = self._extract_phase_features(messages)
        features.update(phase_features)
        
        return features
    
    def _get_message_words(self, msg: Dict[str, Any]) -> set:
        """Extract words from a message."""
        text = msg.get('text', '')
        return set(re.findall(r'\b\w{3,}\b', text.lower()))
    
    def _compute_message_similarity(self, msg1: Dict, msg2: Dict) -> float:
        """Compute word overlap similarity between two messages."""
        words1 = self._get_message_words(msg1)
        words2 = self._get_message_words(msg2)
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0
    
    def _extract_topic_flow(self, messages: List[Dict]) -> Dict[str, float]:
        """Extract topic flow features."""
        n = len(messages)
        
        # Topic continuity: average similarity between consecutive messages
        continuity_scores = []
        for i in range(1, n):
            sim = self._compute_message_similarity(messages[i-1], messages[i])
            continuity_scores.append(sim)
        
        topic_continuity = np.mean(continuity_scores) if continuity_scores else 0.0
        
        # Topic introduction rate: how often new topics are introduced
        topic_shifts = 0
        for i, msg in enumerate(messages):
            text = msg.get('text', '').lower()
            if any(marker in text for marker in self.topic_shift_markers):
                topic_shifts += 1
            elif i > 0 and self._compute_message_similarity(messages[i-1], msg) < 0.1:
                topic_shifts += 1
        
        topic_intro_rate = topic_shifts / n if n > 0 else 0.0
        
        # Topic depth: how long topics are sustained
        topic_lengths = []
        current_length = 1
        for i in range(1, n):
            if self._compute_message_similarity(messages[i-1], messages[i]) > 0.15:
                current_length += 1
            else:
                topic_lengths.append(current_length)
                current_length = 1
        topic_lengths.append(current_length)
        
        topic_depth = np.mean(topic_lengths) / 5 if topic_lengths else 0.0  # Normalize
        topic_depth = min(1.0, topic_depth)
        
        # Topic breadth: number of distinct topic clusters
        all_words = []
        for msg in messages:
            all_words.extend(self._get_message_words(msg))
        unique_topics = len(set(all_words))
        topic_breadth = min(1.0, unique_topics / (n * 5)) if n > 0 else 0.0
        
        # Topic return frequency: how often we return to previous topics
        topic_returns = 0
        for i in range(2, n):
            for j in range(i - 2):
                if self._compute_message_similarity(messages[i], messages[j]) > 0.3:
                    topic_returns += 1
                    break
        
        topic_return_freq = topic_returns / (n - 2) if n > 2 else 0.0
        
        return {
            'topic_continuity_score': float(topic_continuity),
            'topic_introduction_rate': float(min(1.0, topic_intro_rate)),
            'topic_depth_score': float(topic_depth),
            'topic_breadth_score': float(topic_breadth),
            'topic_return_frequency': float(topic_return_freq)
        }
    
    def _extract_structure(self, messages: List[Dict]) -> Dict[str, float]:
        """Extract conversation structure features."""
        n = len(messages)
        
        # Get senders
        senders = [msg.get('sender', 'unknown') for msg in messages]
        unique_senders = list(set(senders))
        
        # Exchange balance: how balanced is the conversation
        if len(unique_senders) >= 2:
            sender_counts = Counter(senders)
            counts = list(sender_counts.values())
            exchange_balance = min(counts) / max(counts) if max(counts) > 0 else 0.0
        else:
            exchange_balance = 0.0
        
        # Conversation momentum: are messages getting longer/shorter
        lengths = [len(msg.get('text', '').split()) for msg in messages]
        if len(lengths) >= 2:
            momentum = np.corrcoef(range(len(lengths)), lengths)[0, 1]
            momentum = (momentum + 1) / 2 if not np.isnan(momentum) else 0.5
        else:
            momentum = 0.5
        
        # Dialogue density: average message length relative to conversation
        avg_length = np.mean(lengths) if lengths else 0
        dialogue_density = min(1.0, avg_length / 30)  # Normalize by ~30 words
        
        # Response relevance: how relevant are responses to triggers
        relevance_scores = []
        for i in range(1, n):
            if senders[i] != senders[i-1]:  # Different sender = response
                relevance = self._compute_message_similarity(messages[i-1], messages[i])
                relevance_scores.append(relevance)
        
        response_relevance = np.mean(relevance_scores) if relevance_scores else 0.5
        
        # Tangent frequency: how often does conversation go off-topic
        tangent_count = 0
        for i in range(2, n):
            prev_sim = self._compute_message_similarity(messages[i-2], messages[i-1])
            curr_sim = self._compute_message_similarity(messages[i-1], messages[i])
            if prev_sim > 0.2 and curr_sim < 0.1:
                tangent_count += 1
        
        tangent_freq = tangent_count / (n - 2) if n > 2 else 0.0
        
        return {
            'exchange_balance': float(exchange_balance),
            'conversation_momentum': float(momentum),
            'dialogue_density': float(dialogue_density),
            'response_relevance_mean': float(response_relevance),
            'tangent_frequency': float(min(1.0, tangent_freq))
        }
    
    def _extract_turn_dynamics(self, messages: List[Dict]) -> Dict[str, float]:
        """Extract turn-taking dynamics features."""
        n = len(messages)
        senders = [msg.get('sender', 'unknown') for msg in messages]
        
        # Turn taking regularity: how regular is the alternation
        alternations = sum(1 for i in range(1, n) if senders[i] != senders[i-1])
        regularity = alternations / (n - 1) if n > 1 else 0.0
        
        # Monologue tendency: consecutive messages by same sender
        monologue_lengths = []
        current_length = 1
        for i in range(1, n):
            if senders[i] == senders[i-1]:
                current_length += 1
            else:
                monologue_lengths.append(current_length)
                current_length = 1
        monologue_lengths.append(current_length)
        
        monologue_tendency = (np.mean(monologue_lengths) - 1) / 3 if monologue_lengths else 0.0
        monologue_tendency = min(1.0, max(0.0, monologue_tendency))
        
        # Interruption pattern: short responses after long messages
        interruption_count = 0
        for i in range(1, n):
            if senders[i] != senders[i-1]:
                prev_len = len(messages[i-1].get('text', '').split())
                curr_len = len(messages[i].get('text', '').split())
                if prev_len > 20 and curr_len < 5:
                    interruption_count += 1
        
        interruption_pattern = interruption_count / (n - 1) if n > 1 else 0.0
        
        # Dominance shift: how much does dominance change over conversation
        unique_senders = list(set(senders))
        if len(unique_senders) >= 2:
            first_half = senders[:n//2]
            second_half = senders[n//2:]
            
            first_dom = first_half.count(unique_senders[0]) / len(first_half) if first_half else 0.5
            second_dom = second_half.count(unique_senders[0]) / len(second_half) if second_half else 0.5
            dominance_shift = abs(first_dom - second_dom)
        else:
            dominance_shift = 0.0
        
        # Speaking time variance: variance in message lengths by sender
        sender_lengths = {}
        for msg, sender in zip(messages, senders):
            if sender not in sender_lengths:
                sender_lengths[sender] = []
            sender_lengths[sender].append(len(msg.get('text', '').split()))
        
        variances = [np.var(lengths) for lengths in sender_lengths.values() if len(lengths) > 1]
        speaking_variance = np.mean(variances) if variances else 0.0
        speaking_variance = min(1.0, speaking_variance / 100)  # Normalize
        
        return {
            'turn_taking_regularity': float(regularity),
            'monologue_tendency': float(monologue_tendency),
            'interruption_pattern': float(min(1.0, interruption_pattern * 5)),
            'conversation_dominance_shift': float(dominance_shift),
            'speaking_time_variance': float(speaking_variance)
        }
    
    def _compute_engagement_score(self, msg: Dict) -> float:
        """Compute engagement score for a single message."""
        text = msg.get('text', '').lower()
        words = set(text.split())
        
        engagement = 0.0
        
        # Check engagement markers
        for marker in self.engagement_markers:
            if marker in text:
                engagement += 0.2
        
        # Check disengagement markers
        for marker in self.disengagement_markers:
            if marker in words:
                engagement -= 0.15
        
        # Message length contributes to engagement
        word_count = len(text.split())
        engagement += min(0.3, word_count / 30)
        
        # Questions show engagement
        engagement += text.count('?') * 0.15
        
        return max(0.0, min(1.0, engagement))
    
    def _extract_engagement_patterns(self, messages: List[Dict]) -> Dict[str, float]:
        """Extract engagement pattern features."""
        n = len(messages)
        
        # Compute engagement scores for each message
        engagement_scores = [self._compute_engagement_score(msg) for msg in messages]
        
        # Engagement trajectory: is engagement increasing or decreasing
        if len(engagement_scores) >= 2:
            trajectory = np.corrcoef(range(len(engagement_scores)), engagement_scores)[0, 1]
            trajectory = (trajectory + 1) / 2 if not np.isnan(trajectory) else 0.5
        else:
            trajectory = 0.5
        
        # Attention decay rate: how quickly does engagement drop
        if len(engagement_scores) >= 3:
            first_third = np.mean(engagement_scores[:n//3]) if n//3 > 0 else 0
            last_third = np.mean(engagement_scores[-n//3:]) if n//3 > 0 else 0
            decay_rate = max(0, first_third - last_third)
        else:
            decay_rate = 0.0
        
        # Re-engagement frequency: how often does engagement spike after dip
        re_engagements = 0
        for i in range(2, n):
            if engagement_scores[i-1] < 0.3 and engagement_scores[i] > 0.5:
                re_engagements += 1
        
        re_engagement_freq = re_engagements / (n - 2) if n > 2 else 0.0
        
        # Peak engagement timing: when is engagement highest (0=start, 1=end)
        if engagement_scores:
            peak_idx = np.argmax(engagement_scores)
            peak_timing = peak_idx / (n - 1) if n > 1 else 0.5
        else:
            peak_timing = 0.5
        
        # Engagement volatility: how much does engagement fluctuate
        if len(engagement_scores) >= 2:
            volatility = np.std(engagement_scores)
        else:
            volatility = 0.0
        
        return {
            'engagement_trajectory': float(trajectory),
            'attention_decay_rate': float(min(1.0, decay_rate)),
            're_engagement_frequency': float(min(1.0, re_engagement_freq * 5)),
            'peak_engagement_timing': float(peak_timing),
            'engagement_volatility': float(min(1.0, volatility * 2))
        }
    
    def _extract_phase_features(self, messages: List[Dict]) -> Dict[str, float]:
        """Extract conversation phase features."""
        n = len(messages)
        
        # Split conversation into thirds
        third = max(1, n // 3)
        opening = messages[:third]
        middle = messages[third:2*third]
        closing = messages[2*third:]
        
        # Opening warmth: positive sentiment in opening
        opening_warmth = self._compute_phase_warmth(opening)
        
        # Closing warmth: positive sentiment in closing
        closing_warmth = self._compute_phase_warmth(closing)
        
        # Mid-conversation depth: engagement in middle
        mid_depth = np.mean([self._compute_engagement_score(m) for m in middle]) if middle else 0.5
        
        # Phase transition smoothness: how smooth are transitions between phases
        if opening and middle:
            open_mid_sim = self._compute_message_similarity(opening[-1], middle[0]) if middle else 0.5
        else:
            open_mid_sim = 0.5
        
        if middle and closing:
            mid_close_sim = self._compute_message_similarity(middle[-1], closing[0]) if closing else 0.5
        else:
            mid_close_sim = 0.5
        
        transition_smoothness = (open_mid_sim + mid_close_sim) / 2
        
        # Conversation arc completeness: does it have proper opening and closing
        has_greeting = any(
            any(g in msg.get('text', '').lower() for g in ['hi', 'hello', 'hey', 'good morning', 'good evening'])
            for msg in opening
        )
        has_closing = any(
            any(c in msg.get('text', '').lower() for c in ['bye', 'goodbye', 'see you', 'later', 'take care', 'goodnight'])
            for msg in closing
        )
        
        arc_completeness = (0.5 if has_greeting else 0.0) + (0.5 if has_closing else 0.0)
        
        return {
            'opening_warmth': float(opening_warmth),
            'closing_warmth': float(closing_warmth),
            'mid_conversation_depth': float(mid_depth),
            'phase_transition_smoothness': float(transition_smoothness),
            'conversation_arc_completeness': float(arc_completeness)
        }
    
    def _compute_phase_warmth(self, messages: List[Dict]) -> float:
        """Compute warmth score for a conversation phase."""
        if not messages:
            return 0.5
        
        warm_words = {
            'hi', 'hello', 'hey', 'thanks', 'thank', 'please', 'love', 'great',
            'awesome', 'wonderful', 'nice', 'good', 'happy', 'glad', 'appreciate',
            'welcome', 'care', 'hope', 'best', 'friend', 'dear', 'sweet'
        }
        
        cold_words = {
            'whatever', 'fine', 'ok', 'k', 'busy', 'later', 'no', 'stop',
            'leave', 'annoying', 'bother', 'hate', 'worst', 'terrible'
        }
        
        warm_count = 0
        cold_count = 0
        
        for msg in messages:
            words = set(msg.get('text', '').lower().split())
            warm_count += len(words & warm_words)
            cold_count += len(words & cold_words)
        
        total = warm_count + cold_count
        if total == 0:
            return 0.5
        
        return float(warm_count / total)
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names."""
        return self.feature_names.copy()
