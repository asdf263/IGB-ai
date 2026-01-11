"""
Transformer-Based Emotion Detection Module
Uses HuggingFace emotion classification models for accurate emotion detection.
Replaces word-list based emotion detection with neural network classification.
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class EmotionTransformerExtractor:
    """Extracts emotion features using transformer-based classification."""
    
    # Emotion labels from common models (GoEmotions, etc.)
    EMOTION_CATEGORIES = [
        'joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust',
        'love', 'optimism', 'pessimism', 'trust', 'anticipation'
    ]
    
    # Mapping from model-specific labels to our standard categories
    EMOTION_MAPPING = {
        # From go_emotions model
        'admiration': 'love',
        'amusement': 'joy',
        'anger': 'anger',
        'annoyance': 'anger',
        'approval': 'trust',
        'caring': 'love',
        'confusion': 'surprise',
        'curiosity': 'anticipation',
        'desire': 'anticipation',
        'disappointment': 'sadness',
        'disapproval': 'disgust',
        'disgust': 'disgust',
        'embarrassment': 'fear',
        'excitement': 'joy',
        'fear': 'fear',
        'gratitude': 'love',
        'grief': 'sadness',
        'joy': 'joy',
        'love': 'love',
        'nervousness': 'fear',
        'optimism': 'optimism',
        'pride': 'joy',
        'realization': 'surprise',
        'relief': 'joy',
        'remorse': 'sadness',
        'sadness': 'sadness',
        'surprise': 'surprise',
        'neutral': 'neutral',
        # From emotion model
        'happy': 'joy',
        'sad': 'sadness',
        'angry': 'anger',
        'fearful': 'fear',
        'surprised': 'surprise',
        'disgusted': 'disgust',
    }
    
    def __init__(self, model_name: str = "SamLowe/roberta-base-go_emotions"):
        """
        Initialize emotion transformer.
        
        Args:
            model_name: HuggingFace model for emotion classification.
                       Options:
                       - "SamLowe/roberta-base-go_emotions" (27 emotions, recommended)
                       - "j-hartmann/emotion-english-distilroberta-base" (7 emotions)
                       - "bhadresh-savani/distilbert-base-uncased-emotion" (6 emotions)
        """
        self.model_name = model_name
        self.classifier = None
        self.model_available = False
        self._init_model()
        
        self.feature_names = [
            # Primary emotion scores (0-1)
            'joy_score',
            'sadness_score', 
            'anger_score',
            'fear_score',
            'surprise_score',
            'disgust_score',
            'love_score',
            'optimism_score',
            'trust_score',
            'anticipation_score',
            # Emotion dynamics
            'dominant_consistency',
            'diversity',
            'intensity_mean',
            'intensity_max',
            'positive_ratio',
            'negative_ratio',
            'transition_rate',
            'range',
            'entropy',
            'mixed_emotion_frequency'
        ]
    
    def _init_model(self):
        """Initialize the emotion classification model."""
        try:
            from transformers import pipeline
            self.classifier = pipeline(
                "text-classification",
                model=self.model_name,
                top_k=None,  # Return all labels with scores
                truncation=True,
                max_length=512
            )
            self.model_available = True
            logger.info(f"Emotion transformer loaded: {self.model_name}")
        except ImportError:
            logger.warning("transformers not installed, using fallback emotion detection")
            self.model_available = False
        except Exception as e:
            logger.warning(f"Failed to load emotion model: {e}, using fallback")
            self.model_available = False
    
    def _classify_emotion(self, text: str) -> Dict[str, float]:
        """
        Classify emotions in a single text.
        
        Returns:
            Dict mapping emotion categories to confidence scores (0-1)
        """
        if not text.strip():
            return {cat: 0.0 for cat in self.EMOTION_CATEGORIES}
        
        if not self.model_available:
            return self._fallback_emotion_detection(text)
        
        try:
            results = self.classifier(text)
            if isinstance(results, list) and len(results) > 0:
                if isinstance(results[0], list):
                    results = results[0]
                
                # Aggregate scores by our standard categories
                emotion_scores = {cat: 0.0 for cat in self.EMOTION_CATEGORIES}
                
                for item in results:
                    label = item['label'].lower()
                    score = item['score']
                    
                    # Map to standard category
                    if label in self.EMOTION_MAPPING:
                        mapped = self.EMOTION_MAPPING[label]
                        if mapped in emotion_scores:
                            emotion_scores[mapped] = max(emotion_scores[mapped], score)
                    elif label in emotion_scores:
                        emotion_scores[label] = max(emotion_scores[label], score)
                
                return emotion_scores
        except Exception as e:
            logger.debug(f"Emotion classification failed: {e}")
        
        return self._fallback_emotion_detection(text)
    
    def _fallback_emotion_detection(self, text: str) -> Dict[str, float]:
        """Fallback word-based emotion detection when model unavailable."""
        import re
        words = set(re.findall(r'\b\w+\b', text.lower()))
        
        emotion_words = {
            'joy': {'happy', 'joy', 'excited', 'thrilled', 'delighted', 'glad', 'pleased',
                   'cheerful', 'elated', 'wonderful', 'great', 'awesome', 'amazing', 'fantastic',
                   'love', 'fun', 'enjoy', 'laugh', 'smile', 'yay', 'woohoo', 'haha', 'lol'},
            'sadness': {'sad', 'unhappy', 'depressed', 'down', 'miserable', 'heartbroken',
                       'grief', 'lonely', 'hopeless', 'disappointed', 'sorry', 'miss', 'crying',
                       'tears', 'upset', 'hurt', 'pain', 'suffer', 'lost'},
            'anger': {'angry', 'furious', 'mad', 'irritated', 'annoyed', 'frustrated',
                     'outraged', 'hate', 'rage', 'pissed', 'livid', 'hostile', 'bitter',
                     'resentful', 'damn', 'hell', 'stupid', 'idiot'},
            'fear': {'afraid', 'scared', 'frightened', 'terrified', 'anxious', 'worried',
                    'nervous', 'panic', 'dread', 'horror', 'creepy', 'scary', 'threat',
                    'danger', 'risk', 'concern', 'stress', 'tense'},
            'surprise': {'surprised', 'amazed', 'astonished', 'shocked', 'stunned', 'wow',
                        'whoa', 'omg', 'unexpected', 'unbelievable', 'incredible', 'really',
                        'seriously', 'what', 'no way'},
            'disgust': {'disgusted', 'gross', 'nasty', 'yuck', 'ew', 'revolting', 'sick',
                       'vile', 'awful', 'terrible', 'horrible', 'worst', 'hate', 'loathe'},
            'love': {'love', 'adore', 'cherish', 'care', 'dear', 'sweetheart', 'darling',
                    'affection', 'fond', 'devoted', 'passionate', 'romantic', 'heart'},
            'optimism': {'hope', 'hopeful', 'optimistic', 'positive', 'confident', 'believe',
                        'faith', 'trust', 'expect', 'looking forward', 'excited', 'eager'},
            'trust': {'trust', 'believe', 'faith', 'reliable', 'honest', 'loyal', 'depend',
                     'confident', 'sure', 'certain', 'safe', 'secure'},
            'anticipation': {'anticipate', 'expect', 'await', 'eager', 'excited', 'curious',
                            'wonder', 'looking forward', 'can\'t wait', 'soon', 'planning'}
        }
        
        scores = {}
        for emotion, word_set in emotion_words.items():
            matches = len(words & word_set)
            scores[emotion] = min(1.0, matches * 0.3)  # Scale up matches
        
        return scores
    
    def _classify_batch(self, texts: List[str]) -> List[Dict[str, float]]:
        """Classify emotions for multiple texts."""
        if not self.model_available:
            return [self._fallback_emotion_detection(t) for t in texts]
        
        results = []
        for text in texts:
            results.append(self._classify_emotion(text))
        return results
    
    def extract(self, messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract emotion features from messages.
        
        Args:
            messages: List of message dicts with 'text' field
            
        Returns:
            Dict of emotion features
        """
        if not messages:
            return {name: 0.0 for name in self.feature_names}
        
        texts = [msg.get('text', '') for msg in messages if msg.get('text')]
        if not texts:
            return {name: 0.0 for name in self.feature_names}
        
        # Get emotion scores for each message
        all_emotions = self._classify_batch(texts)
        
        features = {}
        
        # Aggregate emotion scores across messages
        emotion_arrays = {cat: [] for cat in self.EMOTION_CATEGORIES}
        for emotions in all_emotions:
            for cat in self.EMOTION_CATEGORIES:
                emotion_arrays[cat].append(emotions.get(cat, 0.0))
        
        # Primary emotion scores (mean across messages)
        features['joy_score'] = float(np.mean(emotion_arrays['joy']))
        features['sadness_score'] = float(np.mean(emotion_arrays['sadness']))
        features['anger_score'] = float(np.mean(emotion_arrays['anger']))
        features['fear_score'] = float(np.mean(emotion_arrays['fear']))
        features['surprise_score'] = float(np.mean(emotion_arrays['surprise']))
        features['disgust_score'] = float(np.mean(emotion_arrays['disgust']))
        features['love_score'] = float(np.mean(emotion_arrays['love']))
        features['optimism_score'] = float(np.mean(emotion_arrays['optimism']))
        features['trust_score'] = float(np.mean(emotion_arrays['trust']))
        features['anticipation_score'] = float(np.mean(emotion_arrays['anticipation']))
        
        # Emotion dynamics
        features['dominant_consistency'] = self._compute_dominant_consistency(all_emotions)
        features['diversity'] = self._compute_emotion_diversity(all_emotions)
        features['intensity_mean'] = self._compute_intensity_mean(all_emotions)
        features['intensity_max'] = self._compute_intensity_max(all_emotions)
        features['positive_ratio'] = self._compute_positive_ratio(all_emotions)
        features['negative_ratio'] = self._compute_negative_ratio(all_emotions)
        features['transition_rate'] = self._compute_transition_rate(all_emotions)
        features['range'] = self._compute_emotional_range(all_emotions)
        features['entropy'] = self._compute_emotion_entropy(all_emotions)
        features['mixed_emotion_frequency'] = self._compute_mixed_emotion_freq(all_emotions)
        
        return features
    
    def _get_dominant_emotion(self, emotions: Dict[str, float]) -> Tuple[str, float]:
        """Get the dominant emotion and its score."""
        if not emotions:
            return 'neutral', 0.0
        max_emotion = max(emotions.items(), key=lambda x: x[1])
        return max_emotion
    
    def _compute_dominant_consistency(self, all_emotions: List[Dict[str, float]]) -> float:
        """How consistent is the dominant emotion across messages."""
        if len(all_emotions) < 2:
            return 1.0
        
        dominant_emotions = [self._get_dominant_emotion(e)[0] for e in all_emotions]
        most_common = max(set(dominant_emotions), key=dominant_emotions.count)
        consistency = dominant_emotions.count(most_common) / len(dominant_emotions)
        return float(consistency)
    
    def _compute_emotion_diversity(self, all_emotions: List[Dict[str, float]]) -> float:
        """How diverse are the emotions expressed."""
        if not all_emotions:
            return 0.0
        
        # Count emotions that appear with significant score
        significant_emotions = set()
        for emotions in all_emotions:
            for cat, score in emotions.items():
                if score > 0.2:
                    significant_emotions.add(cat)
        
        return float(len(significant_emotions) / len(self.EMOTION_CATEGORIES))
    
    def _compute_intensity_mean(self, all_emotions: List[Dict[str, float]]) -> float:
        """Average emotional intensity (max score per message)."""
        if not all_emotions:
            return 0.0
        
        intensities = [max(e.values()) if e else 0.0 for e in all_emotions]
        return float(np.mean(intensities))
    
    def _compute_intensity_max(self, all_emotions: List[Dict[str, float]]) -> float:
        """Maximum emotional intensity across all messages."""
        if not all_emotions:
            return 0.0
        
        max_scores = [max(e.values()) if e else 0.0 for e in all_emotions]
        return float(max(max_scores)) if max_scores else 0.0
    
    def _compute_positive_ratio(self, all_emotions: List[Dict[str, float]]) -> float:
        """Ratio of positive emotions."""
        positive_cats = {'joy', 'love', 'optimism', 'trust', 'anticipation'}
        negative_cats = {'sadness', 'anger', 'fear', 'disgust'}
        
        positive_sum = 0.0
        negative_sum = 0.0
        
        for emotions in all_emotions:
            for cat, score in emotions.items():
                if cat in positive_cats:
                    positive_sum += score
                elif cat in negative_cats:
                    negative_sum += score
        
        total = positive_sum + negative_sum
        if total == 0:
            return 0.5
        return float(positive_sum / total)
    
    def _compute_negative_ratio(self, all_emotions: List[Dict[str, float]]) -> float:
        """Ratio of negative emotions."""
        return 1.0 - self._compute_positive_ratio(all_emotions)
    
    def _compute_transition_rate(self, all_emotions: List[Dict[str, float]]) -> float:
        """How often does the dominant emotion change."""
        if len(all_emotions) < 2:
            return 0.0
        
        dominant_emotions = [self._get_dominant_emotion(e)[0] for e in all_emotions]
        transitions = sum(1 for i in range(len(dominant_emotions) - 1)
                         if dominant_emotions[i] != dominant_emotions[i + 1])
        return float(transitions / (len(dominant_emotions) - 1))
    
    def _compute_emotional_range(self, all_emotions: List[Dict[str, float]]) -> float:
        """Range of emotional intensity."""
        if not all_emotions:
            return 0.0
        
        max_scores = [max(e.values()) if e else 0.0 for e in all_emotions]
        return float(max(max_scores) - min(max_scores)) if max_scores else 0.0
    
    def _compute_emotion_entropy(self, all_emotions: List[Dict[str, float]]) -> float:
        """Entropy of emotion distribution."""
        if not all_emotions:
            return 0.0
        
        # Aggregate all emotion scores
        total_scores = {cat: 0.0 for cat in self.EMOTION_CATEGORIES}
        for emotions in all_emotions:
            for cat, score in emotions.items():
                if cat in total_scores:
                    total_scores[cat] += score
        
        # Normalize to probabilities
        total = sum(total_scores.values())
        if total == 0:
            return 0.0
        
        probs = [s / total for s in total_scores.values() if s > 0]
        entropy = -sum(p * np.log(p + 1e-10) for p in probs)
        
        # Normalize by max entropy
        max_entropy = np.log(len(self.EMOTION_CATEGORIES))
        return float(entropy / max_entropy) if max_entropy > 0 else 0.0
    
    def _compute_mixed_emotion_freq(self, all_emotions: List[Dict[str, float]]) -> float:
        """How often are multiple emotions expressed simultaneously."""
        if not all_emotions:
            return 0.0
        
        mixed_count = 0
        for emotions in all_emotions:
            significant = sum(1 for score in emotions.values() if score > 0.2)
            if significant >= 2:
                mixed_count += 1
        
        return float(mixed_count / len(all_emotions))
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names."""
        return self.feature_names.copy()
    
    def get_emotion_for_text(self, text: str) -> Dict[str, float]:
        """Get emotion scores for a single text (for debugging/analysis)."""
        return self._classify_emotion(text)
