"""
Data models for calibration pipeline.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class CalibrationSample:
    """Represents a single calibration conversation sample."""
    vector_name: str
    intensity: float
    messages: List[Dict[str, Any]]
    raw_value: Optional[float] = None
    normalized_value: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            'vector_name': self.vector_name,
            'intensity': self.intensity,
            'message_count': len(self.messages),
            'raw_value': self.raw_value,
            'normalized_value': self.normalized_value
        }


@dataclass
class DiagnosticReport:
    """Diagnostic report for a vector component."""
    vector_name: str
    is_valid: bool
    violations: List[str] = field(default_factory=list)
    samples: List[CalibrationSample] = field(default_factory=list)
    anchor_low: Optional[float] = None
    anchor_mid: Optional[float] = None
    anchor_high: Optional[float] = None
    flagged_for_review: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'vector_name': self.vector_name,
            'is_valid': self.is_valid,
            'violations': self.violations,
            'sample_count': len(self.samples),
            'anchor_low': self.anchor_low,
            'anchor_mid': self.anchor_mid,
            'anchor_high': self.anchor_high,
            'flagged_for_review': self.flagged_for_review
        }
    
    def get_normalization_formula(self) -> str:
        """Generate normalization formula for this vector."""
        v0 = self.anchor_low if self.anchor_low is not None else 0.0
        v05 = self.anchor_mid if self.anchor_mid is not None else (v0 + (self.anchor_high or 1.0)) / 2
        v1 = self.anchor_high if self.anchor_high is not None else 1.0
        
        formula = f"""
# Normalization Formula for {self.vector_name}
# Anchor Points:
#   v_0   (intensity=0.0) = {v0:.6f}
#   v_0.5 (intensity=0.5) = {v05:.6f}
#   v_1   (intensity=1.0) = {v1:.6f}

def normalize_{self.vector_name.replace('.', '_')}(x):
    v_0 = {v0:.6f}
    v_05 = {v05:.6f}
    v_1 = {v1:.6f}
    
    # Piecewise linear interpolation
    if x <= v_05:
        if v_05 == v_0:
            normalized = 0.0
        else:
            normalized = 0.5 * (x - v_0) / (v_05 - v_0)
    else:
        if v_1 == v_05:
            normalized = 1.0
        else:
            normalized = 0.5 + 0.5 * (x - v_05) / (v_1 - v_05)
    
    return max(0.0, min(1.0, normalized))
"""
        return formula


@dataclass
class CalibrationResult:
    """Result for a single calibration sample."""
    id: str
    vector_name: str
    intensity: float
    raw_value: float
    normalized_value: float
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'vector_name': self.vector_name,
            'intensity': self.intensity,
            'raw_value': self.raw_value,
            'normalized_value': self.normalized_value
        }
