"""
Calibration Pipeline
Processes synthetic chat logs, extracts features, normalizes values, and validates consistency.
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from .models import CalibrationSample, DiagnosticReport, CalibrationResult


class CalibrationPipeline:
    """Pipeline for calibrating vector component values using synthetic data."""
    
    def __init__(self, feature_extractor=None):
        """
        Initialize pipeline.
        
        Args:
            feature_extractor: Optional UserFeatureExtractor instance.
                              If None, will be created on first use.
        """
        self._feature_extractor = feature_extractor
    
    @property
    def feature_extractor(self):
        """Lazy load feature extractor."""
        if self._feature_extractor is None:
            from services.user_feature_extractor import UserFeatureExtractor
            self._feature_extractor = UserFeatureExtractor()
        return self._feature_extractor
    
    def extract_text(self, messages: List[Dict], sender_filter: str = 'user') -> str:
        """Concatenate text from specified sender."""
        texts = [
            msg['text'] 
            for msg in messages 
            if msg.get('sender') == sender_filter
        ]
        return '\n'.join(texts)
    
    def extract_features(self, messages: List[Dict], target_user: str = 'user') -> Dict[str, float]:
        """Extract all features from messages."""
        feature_vector, feature_names = self.feature_extractor.extract_for_user(
            messages, target_user
        )
        return dict(zip(feature_names, feature_vector))
    
    def get_component_value(
        self, 
        features: Dict[str, float], 
        vector_name: str
    ) -> Optional[float]:
        """Get the value for a specific vector component."""
        # Try exact match first
        if vector_name in features:
            return features[vector_name]
        
        # Try with common prefixes
        prefixes = ['sentiment_', 'text_', 'behavioral_', 'linguistic_', 
                    'temporal_', 'semantic_', 'composite_', 'synthetic_',
                    'reaction_', 'emotion_', 'context_']
        
        for prefix in prefixes:
            key = f"{prefix}{vector_name}"
            if key in features:
                return features[key]
        
        # Try partial match
        for key in features:
            if vector_name in key:
                return features[key]
        
        return None
    
    def normalize_value(
        self,
        raw_value: float,
        anchor_low: float,
        anchor_high: float
    ) -> float:
        """Scale raw value to 0-1 using anchor points."""
        if anchor_high == anchor_low:
            return 0.5  # Degenerate case
        
        normalized = (raw_value - anchor_low) / (anchor_high - anchor_low)
        return max(0.0, min(1.0, normalized))
    
    def validate_monotonicity(
        self,
        samples: List[CalibrationSample]
    ) -> Tuple[bool, List[str]]:
        """Check if normalized values increase with intensity."""
        sorted_samples = sorted(samples, key=lambda s: s.intensity)
        violations = []
        
        for i in range(1, len(sorted_samples)):
            prev = sorted_samples[i - 1]
            curr = sorted_samples[i]
            
            if prev.normalized_value is None or curr.normalized_value is None:
                continue
            
            # Check monotonic increase
            if curr.normalized_value < prev.normalized_value - 0.01:  # Small tolerance
                violations.append(
                    f"Non-monotonic: intensity {prev.intensity:.2f} -> {curr.intensity:.2f}, "
                    f"but value {prev.normalized_value:.4f} -> {curr.normalized_value:.4f}"
                )
            
            # Check for collapsed values (too similar)
            if abs(curr.normalized_value - prev.normalized_value) < 0.05:
                if curr.intensity - prev.intensity >= 0.25:
                    violations.append(
                        f"Collapsed: intensities {prev.intensity:.2f} and {curr.intensity:.2f} "
                        f"have similar values {prev.normalized_value:.4f} and {curr.normalized_value:.4f}"
                    )
        
        return len(violations) == 0, violations
    
    def run(
        self,
        samples_by_vector: Dict[str, List[CalibrationSample]]
    ) -> Tuple[List[CalibrationResult], List[DiagnosticReport]]:
        """
        Execute full calibration pipeline.
        
        Args:
            samples_by_vector: Dictionary mapping vector names to their samples
        
        Returns:
            results: List of calibration results
            reports: List of diagnostic reports
        """
        results = []
        reports = []
        
        for vector_name, samples in samples_by_vector.items():
            print(f"Processing vector: {vector_name}")
            
            # Extract features for each sample
            for sample in samples:
                try:
                    features = self.extract_features(sample.messages)
                    sample.raw_value = self.get_component_value(features, vector_name)
                    
                    if sample.raw_value is None:
                        print(f"  Warning: Could not find feature for {vector_name}")
                        sample.raw_value = 0.0
                except Exception as e:
                    print(f"  Error extracting features: {e}")
                    sample.raw_value = 0.0
            
            # Find anchor points (intensity 0.0, 0.5, and 1.0)
            samples_with_values = [s for s in samples if s.raw_value is not None]
            
            if not samples_with_values:
                print(f"  Skipping {vector_name}: no valid samples")
                continue
            
            anchor_low = next(
                (s.raw_value for s in samples if s.intensity == 0.0 and s.raw_value is not None),
                min(s.raw_value for s in samples_with_values)
            )
            anchor_mid = next(
                (s.raw_value for s in samples if s.intensity == 0.5 and s.raw_value is not None),
                None
            )
            anchor_high = next(
                (s.raw_value for s in samples if s.intensity == 1.0 and s.raw_value is not None),
                max(s.raw_value for s in samples_with_values)
            )
            
            # If no 0.5 sample, estimate as midpoint
            if anchor_mid is None:
                anchor_mid = (anchor_low + anchor_high) / 2
            
            # Normalize all samples
            for sample in samples:
                if sample.raw_value is not None:
                    sample.normalized_value = self.normalize_value(
                        sample.raw_value, anchor_low, anchor_high
                    )
                    
                    results.append(CalibrationResult(
                        id=f"{sample.vector_name}_{sample.intensity}",
                        vector_name=sample.vector_name,
                        intensity=sample.intensity,
                        raw_value=sample.raw_value,
                        normalized_value=sample.normalized_value
                    ))
            
            # Validate
            is_valid, violations = self.validate_monotonicity(samples)
            
            report = DiagnosticReport(
                vector_name=vector_name,
                is_valid=is_valid,
                violations=violations,
                samples=samples,
                anchor_low=anchor_low,
                anchor_mid=anchor_mid,
                anchor_high=anchor_high,
                flagged_for_review=not is_valid
            )
            reports.append(report)
            
            status = "✓" if is_valid else "✗"
            print(f"  {status} {vector_name}: anchor_range=[{anchor_low:.4f}, {anchor_high:.4f}]")
            if violations:
                for v in violations:
                    print(f"    - {v}")
        
        return results, reports
