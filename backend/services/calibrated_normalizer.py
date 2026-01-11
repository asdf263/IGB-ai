"""
Calibrated Feature Normalizer
Applies piecewise linear normalization functions derived from calibration data.
Uses 5-step normalization for features with good calibration quality.
"""
from typing import Dict


class CalibratedNormalizer:
    """Normalizes features using calibration-derived piecewise functions."""
    
    def __init__(self):
        pass
    
    def normalize(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Apply calibrated normalization to features.
        
        Args:
            features: Dictionary of feature names to raw values
            
        Returns:
            Dictionary of feature names to normalized [0, 1] values
        """
        normalized = {}
        
        for key, value in features.items():
            # Extract the base feature name (remove prefix like 'text_', 'behavioral_', etc.)
            parts = key.split('_', 1)
            if len(parts) == 2:
                feature_name = parts[1]
            else:
                feature_name = key
            
            # Try to normalize using calibrated function
            normalized_value = self._normalize_feature(feature_name, value)
            
            # If no calibrated function exists, return original value
            normalized[key] = normalized_value if normalized_value is not None else value
        
        return normalized
    
    def _normalize_feature(self, feature_name: str, value: float) -> float:
        """Apply calibrated normalization for a specific feature."""
        
        # PERFECT FEATURES (8 features with no violations)
        if feature_name == 'all_caps_word_ratio':
            return self._normalize_all_caps_word_ratio(value)
        elif feature_name == 'elaboration_score':
            return self._normalize_elaboration_score(value)
        elif feature_name == 'sentiment_max':
            return self._normalize_sentiment_max(value)
        elif feature_name == 'sentiment_mean':
            return self._normalize_sentiment_mean(value)
        elif feature_name == 'sentiment_skewness':
            return self._normalize_sentiment_skewness(value)
        elif feature_name == 'sentiment_std':
            return self._normalize_sentiment_std(value)
        elif feature_name == 'sentiment_trend':
            return self._normalize_sentiment_trend(value)
        elif feature_name == 'sentiment_volatility':
            return self._normalize_sentiment_volatility(value)
        
        # ADDITIONAL USABLE FEATURES (7 features with curves fitted, ignoring non-monotonic points)
        elif feature_name == 'digit_ratio':
            return self._normalize_digit_ratio(value)
        elif feature_name == 'emotional_intensity_mean':
            return self._normalize_emotional_intensity_mean(value)
        elif feature_name == 'sentiment_consistency':
            return self._normalize_sentiment_consistency(value)
        elif feature_name == 'question_frequency':
            return self._normalize_question_frequency(value)
        
        # CAN WORK FEATURES (17 features with 1-2 violations)
        elif feature_name == 'answer_frequency':
            return self._normalize_answer_frequency(value)
        elif feature_name == 'formality_score':
            return self._normalize_formality_score(value)
        elif feature_name == 'hapax_legomena_ratio':
            return self._normalize_hapax_legomena_ratio(value)
        elif feature_name == 'initiation_rate':
            return self._normalize_initiation_rate(value)
        elif feature_name == 'lexical_richness':
            return self._normalize_lexical_richness(value)
        elif feature_name == 'neutral_ratio':
            return self._normalize_neutral_ratio(value)
        elif feature_name == 'positive_ratio':
            return self._normalize_positive_ratio(value)
        elif feature_name == 'punctuation_ratio':
            return self._normalize_punctuation_ratio(value)
        elif feature_name == 'response_rate':
            return self._normalize_response_rate(value)
        elif feature_name == 'sentiment_min':
            return self._normalize_sentiment_min(value)
        elif feature_name == 'sentiment_range':
            return self._normalize_sentiment_range(value)
        elif feature_name == 'stopword_ratio':
            return self._normalize_stopword_ratio(value)
        elif feature_name == 'type_token_ratio':
            return self._normalize_type_token_ratio(value)
        elif feature_name == 'uppercase_ratio':
            return self._normalize_uppercase_ratio(value)
        elif feature_name == 'weekday_ratio':
            return self._normalize_weekday_ratio(value)
        elif feature_name == 'weekend_ratio':
            return self._normalize_weekend_ratio(value)
        elif feature_name == 'whitespace_ratio':
            return self._normalize_whitespace_ratio(value)
        
        # Feature not in calibration set - return None to use original value
        return None
    
    # ========================================================================
    # PERFECT FEATURES - No violations
    # ========================================================================
    
    def _normalize_all_caps_word_ratio(self, x: float) -> float:
        if x <= 0.095238:
            return 0.25 * (x - 0.000000) / (0.095238 - 0.000000) if 0.095238 != 0.000000 else 0.0
        elif x <= 0.409091:
            return 0.25 + 0.25 * (x - 0.095238) / (0.409091 - 0.095238)
        elif x <= 0.535714:
            return 0.50 + 0.25 * (x - 0.409091) / (0.535714 - 0.409091)
        else:
            return 0.75 + 0.25 * (x - 0.535714) / (1.000000 - 0.535714)
    
    def _normalize_elaboration_score(self, x: float) -> float:
        if x <= 0.056000:
            return 0.25 * (x - 0.020000) / (0.056000 - 0.020000)
        elif x <= 0.112000:
            return 0.25 + 0.25 * (x - 0.056000) / (0.112000 - 0.056000)
        elif x <= 0.172000:
            return 0.50 + 0.25 * (x - 0.112000) / (0.172000 - 0.112000)
        else:
            return 0.75 + 0.25 * (x - 0.172000) / (0.188000 - 0.172000)
    
    def _normalize_sentiment_max(self, x: float) -> float:
        if x <= 0.833333:
            return 0.50 * (x - 0.000000) / (0.833333 - 0.000000) if 0.833333 != 0.000000 else 0.0
        else:
            return 0.50 + 0.50 * (x - 0.833333) / (1.000000 - 0.833333)
    
    def _normalize_sentiment_mean(self, x: float) -> float:
        if x <= 0.253968:
            return 0.50 * (x - 0.000000) / (0.253968 - 0.000000) if 0.253968 != 0.000000 else 0.0
        else:
            return 0.50 + 0.50 * (x - 0.253968) / (1.000000 - 0.253968)
    
    def _normalize_sentiment_skewness(self, x: float) -> float:
        if x <= 0.000000:
            return 0.50 * (x - (-1.500000)) / (0.000000 - (-1.500000))
        else:
            return 0.50 + 0.50 * (x - 0.000000) / (1.500000 - 0.000000)
    
    def _normalize_sentiment_std(self, x: float) -> float:
        if x <= 0.661648:
            return 0.50 * (x - 0.333333) / (0.661648 - 0.333333)
        else:
            return 0.50 + 0.50 * (x - 0.661648) / (0.916515 - 0.661648)
    
    def _normalize_sentiment_trend(self, x: float) -> float:
        if x <= 0.000000:
            return 0.50 * (x - (-0.433333)) / (0.000000 - (-0.433333))
        else:
            return 0.50 + 0.50 * (x - 0.000000) / (0.477551 - 0.000000)
    
    def _normalize_sentiment_volatility(self, x: float) -> float:
        if x <= 0.500000:
            return 0.50 * (x - 0.000000) / (0.500000 - 0.000000) if 0.500000 != 0.000000 else 0.0
        else:
            return 0.50 + 0.50 * (x - 0.500000) / (2.000000 - 0.500000)
    
    # ========================================================================
    # CAN WORK FEATURES - 1-2 violations, non-monotonic points skipped
    # ========================================================================
    
    def _normalize_answer_frequency(self, x: float) -> float:
        if x <= 0.000000:
            return 0.0
        elif x <= 0.400000:
            return 0.75 * (x - 0.000000) / (0.400000 - 0.000000)
        else:
            return 0.75 + 0.25 * (x - 0.400000) / (0.600000 - 0.400000)
    
    def _normalize_formality_score(self, x: float) -> float:
        if x <= 0.468750:
            return 0.25 * (x - 0.346154) / (0.468750 - 0.346154)
        else:
            return 0.25 + 0.25 * (x - 0.468750) / (0.500000 - 0.468750)
    
    def _normalize_hapax_legomena_ratio(self, x: float) -> float:
        if x <= 0.333333:
            return 0.25 * (x - 0.000000) / (0.333333 - 0.000000) if 0.333333 != 0.000000 else 0.0
        elif x <= 0.941176:
            return 0.25 + 0.25 * (x - 0.333333) / (0.941176 - 0.333333)
        else:
            return 0.50 + 0.25 * (x - 0.941176) / (1.000000 - 0.941176)
    
    def _normalize_initiation_rate(self, x: float) -> float:
        if x <= 0.200000:
            return 0.25 * (x - 0.000000) / (0.200000 - 0.000000) if 0.200000 != 0.000000 else 0.0
        elif x <= 0.400000:
            return 0.25 + 0.25 * (x - 0.200000) / (0.400000 - 0.200000)
        else:
            return 0.50 + 0.50 * (x - 0.400000) / (1.000000 - 0.400000)
    
    def _normalize_lexical_richness(self, x: float) -> float:
        if x <= 0.666667:
            return 0.25 * (x - 0.600000) / (0.666667 - 0.600000)
        elif x <= 0.909091:
            return 0.25 + 0.25 * (x - 0.666667) / (0.909091 - 0.666667)
        else:
            return 0.50 + 0.50 * (x - 0.909091) / (0.935484 - 0.909091)
    
    def _normalize_neutral_ratio(self, x: float) -> float:
        if x <= 0.600000:
            return 0.25 * (x - 0.000000) / (0.600000 - 0.000000) if 0.600000 != 0.000000 else 0.0
        else:
            return 0.25 + 0.25 * (x - 0.600000) / (1.000000 - 0.600000)
    
    def _normalize_positive_ratio(self, x: float) -> float:
        if x <= 0.400000:
            return 0.25 * (x - 0.000000) / (0.400000 - 0.000000) if 0.400000 != 0.000000 else 0.0
        elif x <= 0.800000:
            return 0.25 + 0.25 * (x - 0.400000) / (0.800000 - 0.400000)
        else:
            return 0.50 + 0.50 * (x - 0.800000) / (1.000000 - 0.800000)
    
    def _normalize_punctuation_ratio(self, x: float) -> float:
        if x <= 0.022989:
            return 0.25 * (x - 0.000000) / (0.022989 - 0.000000) if 0.022989 != 0.000000 else 0.0
        else:
            return 0.25 + 0.25 * (x - 0.022989) / (0.073171 - 0.022989)
    
    def _normalize_response_rate(self, x: float) -> float:
        if x <= 0.750000:
            return 0.50 * (x - 0.000000) / (0.750000 - 0.000000) if 0.750000 != 0.000000 else 0.0
        else:
            return 0.50 + 0.25 * (x - 0.750000) / (1.000000 - 0.750000)
    
    def _normalize_sentiment_min(self, x: float) -> float:
        if x <= 0.000000:
            return 0.0
        else:
            return (x - 0.000000) / (1.000000 - 0.000000)
    
    def _normalize_sentiment_range(self, x: float) -> float:
        if x <= 0.833333:
            return 0.50 * (x - 1.000000) / (0.833333 - 1.000000)
        else:
            return 0.50 + 0.50 * (x - 0.833333) / (2.000000 - 0.833333)
    
    def _normalize_stopword_ratio(self, x: float) -> float:
        if x <= 0.352941:
            return 0.25 * (x - 0.000000) / (0.352941 - 0.000000) if 0.352941 != 0.000000 else 0.0
        elif x <= 0.666667:
            return 0.25 + 0.25 * (x - 0.352941) / (0.666667 - 0.352941)
        else:
            return 0.50 + 0.50 * (x - 0.666667) / (0.725275 - 0.666667)
    
    def _normalize_type_token_ratio(self, x: float) -> float:
        if x <= 0.187500:
            return 0.25 * (x - 0.083333) / (0.187500 - 0.083333)
        elif x <= 0.950000:
            return 0.25 + 0.25 * (x - 0.187500) / (0.950000 - 0.187500)
        else:
            return 0.50 + 0.25 * (x - 0.950000) / (1.000000 - 0.950000)
    
    def _normalize_uppercase_ratio(self, x: float) -> float:
        if x <= 0.049587:
            return 0.25 * (x - 0.000000) / (0.049587 - 0.000000) if 0.049587 != 0.000000 else 0.0
        elif x <= 0.160584:
            return 0.25 + 0.25 * (x - 0.049587) / (0.160584 - 0.049587)
        elif x <= 0.886364:
            return 0.50 + 0.25 * (x - 0.160584) / (0.886364 - 0.160584)
        else:
            return 0.75 + 0.25 * (x - 0.886364) / (1.000000 - 0.886364)
    
    def _normalize_weekday_ratio(self, x: float) -> float:
        if x <= 1.000000:
            return 0.25 * (x - 0.600000) / (1.000000 - 0.600000)
        else:
            return 0.25 + 0.75 * (x - 1.000000) / (0.800000 - 1.000000)
    
    def _normalize_weekend_ratio(self, x: float) -> float:
        if x <= 0.400000:
            return 0.25 * (x - 0.200000) / (0.400000 - 0.200000)
        else:
            return 0.25 + 0.50 * (x - 0.400000) / (0.400000 - 0.400000) if x <= 0.400000 else 0.75
    
    def _normalize_whitespace_ratio(self, x: float) -> float:
        if x <= 0.101852:
            return 0.25 * (x - 0.042553) / (0.101852 - 0.042553)
        elif x <= 0.140351:
            return 0.25 + 0.25 * (x - 0.101852) / (0.140351 - 0.101852)
        elif x <= 0.147465:
            return 0.50 + 0.25 * (x - 0.140351) / (0.147465 - 0.140351)
        else:
            return 0.75 + 0.25 * (x - 0.147465) / (0.754875 - 0.147465)
    
    # ========================================================================
    # ADDITIONAL USABLE FEATURES - Curves fitted ignoring non-monotonic points
    # ========================================================================
    
    def _normalize_digit_ratio(self, x: float) -> float:
        """
        digit_ratio: 3 violations (1 non-monotonic, 2 collapsed)
        Raw values: [0.0=0.000000, 0.25=0.056180, 0.5=0.045455, 0.75=0.066667, 1.0=1.000000]
        Using points: 0.0, 0.75, 1.0 (skipping non-monotonic 0.25 and 0.5)
        """
        if x <= 0.066667:
            return 0.75 * (x - 0.000000) / (0.066667 - 0.000000) if 0.066667 != 0.000000 else 0.0
        else:
            return 0.75 + 0.25 * (x - 0.066667) / (1.000000 - 0.066667)
    
    def _normalize_emotional_intensity_mean(self, x: float) -> float:
        """
        emotional_intensity_mean: 3 violations (1 non-monotonic, 2 collapsed)
        Raw values: [0.0=0.006250/0.000000, 0.25=0.055263, 0.5=0.009110/0.232495, 0.75=0.091071, 1.0=0.042500/1.000000]
        Using cleaner monotonic points: 0.0=0.000000, 0.5=0.232495, 1.0=1.000000
        """
        if x <= 0.232495:
            return 0.50 * (x - 0.000000) / (0.232495 - 0.000000) if 0.232495 != 0.000000 else 0.0
        else:
            return 0.50 + 0.50 * (x - 0.232495) / (1.000000 - 0.232495)
    
    def _normalize_sentiment_consistency(self, x: float) -> float:
        """
        sentiment_consistency: 3 collapsed violations
        Raw values: [0.0=0.559914/0.505103, 0.25=0.529607, 0.5=0.632436/0.671187, 0.75=0.688632, 1.0=0.671187/1.000000]
        Using cleaner points: 0.0=0.505103, 0.5=0.671187, 1.0=1.000000
        """
        if x <= 0.671187:
            return 0.50 * (x - 0.505103) / (0.671187 - 0.505103)
        else:
            return 0.50 + 0.50 * (x - 0.671187) / (1.000000 - 0.671187)
    
    def _normalize_question_frequency(self, x: float) -> float:
        """
        question_frequency: Recalibrated after fixing missing ? marks in data
        Raw values: [0.0=0.0, 0.25=0.0, 0.5=0.6, 0.75=0.6, 1.0=1.0]
        Using points: 0.0, 0.5, 1.0 (skipping collapsed 0.25 and 0.75)
        """
        if x <= 0.6:
            return 0.50 * (x - 0.0) / (0.6 - 0.0) if 0.6 != 0.0 else 0.0
        else:
            return 0.50 + 0.50 * (x - 0.6) / (1.0 - 0.6)
