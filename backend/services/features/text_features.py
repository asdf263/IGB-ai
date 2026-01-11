"""
Text Metrics Feature Extraction Module
Extracts ~25 text structure and metrics features from chat messages
"""
import numpy as np
import re
import math
from typing import List, Dict, Any
from collections import Counter


class TextFeatureExtractor:
    """Extracts text structure and metrics features from chat messages."""
    
    def __init__(self):
        self.feature_names = [
            'msg_length_mean',
            'msg_length_std',
            'msg_length_min',
            'msg_length_max',
            'msg_length_median',
            'word_count_mean',
            'word_count_std',
            'char_per_word_mean',
            'sentence_count_mean',
            'words_per_sentence_mean',
            'lexical_richness',
            'type_token_ratio',
            'hapax_legomena_ratio',
            'shannon_entropy',
            'char_entropy',
            'stopword_ratio',
            'uppercase_ratio',
            'digit_ratio',
            'punctuation_ratio',
            'whitespace_ratio',
            'emoji_density',
            'url_density',
            'mention_density',
            'hashtag_density',
            'question_mark_ratio',
            'all_caps_word_ratio'
        ]
        
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
            'dare', 'ought', 'used', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our',
            'their', 'this', 'that', 'these', 'those', 'what', 'which', 'who',
            'whom', 'whose', 'when', 'where', 'why', 'how', 'all', 'each', 'every',
            'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
            'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just'
        }
        
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        self.mention_pattern = re.compile(r'@\w+')
        self.hashtag_pattern = re.compile(r'#\w+')
    
    def extract(self, messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract all text features from messages."""
        if not messages:
            return {name: 0.0 for name in self.feature_names}
        
        texts = [msg.get('text', '') for msg in messages if msg.get('text')]
        if not texts:
            return {name: 0.0 for name in self.feature_names}
        
        features = {}
        
        # Message length features
        lengths = [len(t) for t in texts]
        features['msg_length_mean'] = float(np.mean(lengths))
        features['msg_length_std'] = float(np.std(lengths))
        features['msg_length_min'] = float(np.min(lengths))
        features['msg_length_max'] = float(np.max(lengths))
        features['msg_length_median'] = float(np.median(lengths))
        
        # Word count features
        word_counts = [len(t.split()) for t in texts]
        features['word_count_mean'] = float(np.mean(word_counts))
        features['word_count_std'] = float(np.std(word_counts))
        
        # Characters per word
        all_words = ' '.join(texts).split()
        if all_words:
            features['char_per_word_mean'] = float(np.mean([len(w) for w in all_words]))
        else:
            features['char_per_word_mean'] = 0.0
        
        # Sentence features
        sentence_counts = [len(re.split(r'[.!?]+', t)) for t in texts]
        features['sentence_count_mean'] = float(np.mean(sentence_counts))
        
        words_per_sentence = []
        for t in texts:
            sentences = re.split(r'[.!?]+', t)
            for s in sentences:
                words = s.split()
                if words:
                    words_per_sentence.append(len(words))
        features['words_per_sentence_mean'] = float(np.mean(words_per_sentence)) if words_per_sentence else 0.0
        
        # Lexical features
        all_text = ' '.join(texts).lower()
        words = re.findall(r'\b\w+\b', all_text)
        
        if words:
            unique_words = set(words)
            word_freq = Counter(words)
            
            features['lexical_richness'] = len(unique_words) / len(words)
            features['type_token_ratio'] = len(unique_words) / len(words)
            
            hapax = sum(1 for w, c in word_freq.items() if c == 1)
            features['hapax_legomena_ratio'] = hapax / len(unique_words) if unique_words else 0.0
            
            features['shannon_entropy'] = self._compute_word_entropy(words)
            
            stopword_count = sum(1 for w in words if w in self.stopwords)
            features['stopword_ratio'] = stopword_count / len(words)
        else:
            features['lexical_richness'] = 0.0
            features['type_token_ratio'] = 0.0
            features['hapax_legomena_ratio'] = 0.0
            features['shannon_entropy'] = 0.0
            features['stopword_ratio'] = 0.0
        
        # Character-level entropy
        features['char_entropy'] = self._compute_char_entropy(all_text)
        
        # Character type ratios - use ORIGINAL text (not lowercased) for uppercase detection
        all_text_original = ' '.join(texts)  # Keep original case
        
        # Count non-whitespace characters for ratio calculations (excluding whitespace)
        non_whitespace_chars = [c for c in all_text_original if not c.isspace()]
        total_non_whitespace = len(non_whitespace_chars) if non_whitespace_chars else 1
        
        features['uppercase_ratio'] = sum(1 for c in non_whitespace_chars if c.isupper()) / total_non_whitespace
        features['digit_ratio'] = sum(1 for c in non_whitespace_chars if c.isdigit()) / total_non_whitespace
        features['punctuation_ratio'] = sum(1 for c in non_whitespace_chars if c in '.,!?;:\'"-()[]{}') / total_non_whitespace
        
        # Whitespace ratio uses total chars (including whitespace) as denominator
        total_chars_with_whitespace = len(all_text_original) if all_text_original else 1
        features['whitespace_ratio'] = sum(1 for c in all_text_original if c.isspace()) / total_chars_with_whitespace
        
        # Special pattern densities - use original text for patterns that don't need lowercasing
        total_words = len(words) if words else 1
        
        # Emojis don't have case, but use original to be safe
        emoji_count = len(self.emoji_pattern.findall(all_text_original))
        features['emoji_density'] = emoji_count / total_words
        
        # URLs, mentions, hashtags - use original text
        url_count = len(self.url_pattern.findall(all_text_original))
        features['url_density'] = url_count / total_words
        
        mention_count = len(self.mention_pattern.findall(all_text_original))
        features['mention_density'] = mention_count / total_words
        
        hashtag_count = len(self.hashtag_pattern.findall(all_text_original))
        features['hashtag_density'] = hashtag_count / total_words
        
        question_count = all_text.count('?')
        features['question_mark_ratio'] = question_count / len(texts)
        
        # All-caps words detection (words with 2+ chars that are entirely uppercase)
        # Use original text to preserve case
        original_words = re.findall(r'\b[A-Za-z]+\b', all_text_original)
        all_caps_words = [w for w in original_words if len(w) >= 2 and w.isupper()]
        total_alpha_words = len(original_words) if original_words else 1
        
        features['all_caps_word_ratio'] = len(all_caps_words) / total_alpha_words
        
        return features
    
    def _compute_word_entropy(self, words: List[str]) -> float:
        """Compute Shannon entropy of word distribution."""
        if not words:
            return 0.0
        
        word_freq = Counter(words)
        total = len(words)
        entropy = 0.0
        
        for count in word_freq.values():
            prob = count / total
            if prob > 0:
                entropy -= prob * math.log2(prob)
        
        return float(entropy)
    
    def _compute_char_entropy(self, text: str) -> float:
        """Compute Shannon entropy of character distribution."""
        if not text:
            return 0.0
        
        char_freq = Counter(text.lower())
        total = len(text)
        entropy = 0.0
        
        for count in char_freq.values():
            prob = count / total
            if prob > 0:
                entropy -= prob * math.log2(prob)
        
        return float(entropy)
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names."""
        return self.feature_names.copy()
