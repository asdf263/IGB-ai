"""
Sentiment and Emotion Feature Extraction Module
Extracts ~20 sentiment and emotional dynamics features from chat messages
"""
import numpy as np
import re
from typing import List, Dict, Any
from collections import Counter


class SentimentFeatureExtractor:
    """Extracts sentiment and emotion features from chat messages."""
    
    def __init__(self):
        self.feature_names = [
            'sentiment_mean',
            'sentiment_std',
            'sentiment_min',
            'sentiment_max',
            'sentiment_range',
            'sentiment_skewness',
            'positive_ratio',
            'negative_ratio',
            'neutral_ratio',
            'sentiment_volatility',
            'sentiment_trend',
            'emotional_intensity_mean',
            'emotional_shift_frequency',
            'sentiment_consistency'
        ]
        
        self.positive_words = {
            'good', 'great', 'awesome', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'happy', 'glad', 'pleased', 'delighted', 'excited', 'thrilled',
            'perfect', 'beautiful', 'brilliant', 'outstanding', 'superb', 'terrific',
            'nice', 'fine', 'cool', 'best', 'better', 'fun', 'enjoy', 'enjoyed', 'enjoying',
            'thanks', 'thank', 'appreciate', 'grateful', 'blessed', 'fortunate', 'lucky',
            'hope', 'hopeful', 'optimistic', 'confident', 'proud', 'successful', 'win'
        }
        
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'dislike', 'angry',
            'sad', 'upset', 'disappointed', 'frustrated', 'annoyed', 'irritated', 'furious',
            'depressed', 'miserable', 'unhappy', 'worried', 'anxious', 'stressed', 'nervous',
            'afraid', 'scared', 'frightened', 'terrified', 'disgusted', 'sick', 'tired',
            'bored', 'lonely', 'hurt', 'pain', 'suffer', 'fail', 'failed', 'failure',
            'wrong', 'mistake', 'error', 'problem', 'issue', 'trouble', 'difficult', 'hard'
        }
        
        self.joy_words = {'happy', 'joy', 'joyful', 'excited', 'thrilled', 'delighted', 'elated',
                         'cheerful', 'merry', 'glad', 'pleased', 'content', 'satisfied', 'blissful'}
        self.sadness_words = {'sad', 'unhappy', 'depressed', 'melancholy', 'sorrowful', 'gloomy',
                             'miserable', 'heartbroken', 'grief', 'mourning', 'lonely', 'hopeless'}
        self.anger_words = {'angry', 'furious', 'enraged', 'irritated', 'annoyed', 'frustrated',
                           'mad', 'outraged', 'hostile', 'bitter', 'resentful', 'hate'}
        self.fear_words = {'afraid', 'scared', 'frightened', 'terrified', 'anxious', 'worried',
                          'nervous', 'panicked', 'horrified', 'dread', 'fearful', 'uneasy'}
        self.surprise_words = {'surprised', 'amazed', 'astonished', 'shocked', 'stunned',
                              'startled', 'unexpected', 'wow', 'whoa', 'omg', 'unbelievable'}
        self.disgust_words = {'disgusted', 'revolted', 'repulsed', 'gross', 'nasty', 'yuck',
                             'ew', 'sick', 'vile', 'loathe', 'detest', 'abhor'}
        
        self.intensifiers = {'very', 'really', 'extremely', 'incredibly', 'absolutely', 'totally',
                            'completely', 'utterly', 'so', 'too', 'super', 'highly'}
    
    def extract(self, messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract all sentiment features from messages."""
        if not messages:
            return {name: 0.0 for name in self.feature_names}
        
        texts = [msg.get('text', '') for msg in messages if msg.get('text')]
        if not texts:
            return {name: 0.0 for name in self.feature_names}
        
        sentiments = [self._compute_sentiment(t) for t in texts]
        emotions = [self._compute_emotions(t) for t in texts]
        
        features = {}
        
        # Sentiment statistics
        sentiments_arr = np.array(sentiments)
        features['sentiment_mean'] = float(np.mean(sentiments_arr))
        features['sentiment_std'] = float(np.std(sentiments_arr))
        features['sentiment_min'] = float(np.min(sentiments_arr))
        features['sentiment_max'] = float(np.max(sentiments_arr))
        features['sentiment_range'] = float(np.max(sentiments_arr) - np.min(sentiments_arr))
        features['sentiment_skewness'] = self._compute_skewness(sentiments)
        
        # Sentiment category ratios
        positive_count = sum(1 for s in sentiments if s > 0.1)
        negative_count = sum(1 for s in sentiments if s < -0.1)
        neutral_count = len(sentiments) - positive_count - negative_count
        total = len(sentiments)
        
        features['positive_ratio'] = positive_count / total
        features['negative_ratio'] = negative_count / total
        features['neutral_ratio'] = neutral_count / total
        
        # Sentiment dynamics
        features['sentiment_volatility'] = self._compute_volatility(sentiments)
        features['sentiment_trend'] = self._compute_trend(sentiments)
        features['sentiment_consistency'] = self._compute_consistency(sentiments)
        
        # Emotional intensity and shifts
        intensities = [self._compute_intensity(t) for t in texts]
        features['emotional_intensity_mean'] = float(np.mean(intensities))
        features['emotional_shift_frequency'] = self._compute_shift_frequency(sentiments)
        
        return features
    
    def _compute_sentiment(self, text: str) -> float:
        """Compute sentiment score for a single text (-1 to 1)."""
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0
        
        positive_count = sum(1 for w in words if w in self.positive_words)
        negative_count = sum(1 for w in words if w in self.negative_words)
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0
        
        score = (positive_count - negative_count) / len(words)
        return max(-1.0, min(1.0, score * 5))
    
    def _compute_emotions(self, text: str) -> Dict[str, int]:
        """Compute emotion counts for a single text."""
        words = set(re.findall(r'\b\w+\b', text.lower()))
        
        return {
            'joy': len(words & self.joy_words),
            'sadness': len(words & self.sadness_words),
            'anger': len(words & self.anger_words),
            'fear': len(words & self.fear_words),
            'surprise': len(words & self.surprise_words),
            'disgust': len(words & self.disgust_words)
        }
    
    def _aggregate_emotions(self, emotions: List[Dict[str, int]]) -> Dict[str, int]:
        """Aggregate emotion counts across all messages."""
        totals = Counter()
        for e in emotions:
            totals.update(e)
        return dict(totals)
    
    def _compute_intensity(self, text: str) -> float:
        """Compute emotional intensity based on intensifiers and punctuation."""
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0
        
        intensifier_count = sum(1 for w in words if w in self.intensifiers)
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        
        intensity = (intensifier_count / len(words)) + (exclamation_count * 0.1) + (caps_ratio * 0.5)
        return min(1.0, intensity)
    
    def _compute_skewness(self, data: List[float]) -> float:
        """Compute skewness of data."""
        if len(data) < 3:
            return 0.0
        arr = np.array(data)
        mean = np.mean(arr)
        std = np.std(arr)
        if std == 0:
            return 0.0
        return float(np.mean(((arr - mean) / std) ** 3))
    
    def _compute_volatility(self, sentiments: List[float]) -> float:
        """Compute sentiment volatility (average absolute change)."""
        if len(sentiments) < 2:
            return 0.0
        changes = [abs(sentiments[i+1] - sentiments[i]) for i in range(len(sentiments)-1)]
        return float(np.mean(changes))
    
    def _compute_trend(self, sentiments: List[float]) -> float:
        """Compute sentiment trend (slope of linear fit)."""
        if len(sentiments) < 2:
            return 0.0
        x = np.arange(len(sentiments))
        coeffs = np.polyfit(x, sentiments, 1)
        return float(coeffs[0])
    
    def _compute_consistency(self, sentiments: List[float]) -> float:
        """Compute sentiment consistency (1 - normalized std)."""
        if len(sentiments) < 2:
            return 1.0
        std = np.std(sentiments)
        return float(1.0 / (1.0 + std))
    
    def _compute_shift_frequency(self, sentiments: List[float], threshold: float = 0.3) -> float:
        """Compute frequency of significant sentiment shifts."""
        if len(sentiments) < 2:
            return 0.0
        shifts = sum(1 for i in range(len(sentiments)-1) 
                    if abs(sentiments[i+1] - sentiments[i]) > threshold)
        return float(shifts / (len(sentiments) - 1))
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names."""
        return self.feature_names.copy()
