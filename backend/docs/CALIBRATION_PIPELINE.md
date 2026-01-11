# Vector Component Calibration Pipeline

Pipeline for processing synthetic JSON chat logs, extracting embeddings, deriving vector-component values, normalizing to 0–1, and flagging inconsistencies.

---

## Pipeline Steps

### Step 1: Load Synthetic Data
Load multiple JSON files containing conversations at known intensity levels.

```
Input: Directory of JSON files named by pattern: {vector_name}_{intensity}.json
Output: List of (vector_name, intensity, messages) tuples
```

### Step 2: Extract Text
Concatenate user messages from each conversation into a single text block for embedding.

```
Input: messages array
Output: concatenated_text (user messages only, joined by newline)
```

### Step 3: Generate Embeddings
Call embedding model to produce vector representation.

```
Input: concatenated_text
Output: embedding vector (float array)
```

### Step 4: Extract Component Activation
Derive single scalar value for the target vector component using one of:
- **Direct dimension**: Select specific index from embedding
- **Projection**: Dot product with learned direction vector
- **Similarity**: Cosine similarity to prototype embedding

```
Input: embedding, component_config
Output: raw_value (float)
```

### Step 5: Normalize to 0–1
Use synthetic anchor points (known 0.0 and 1.0 samples) to scale raw values.

```
Input: raw_value, anchor_low (from intensity=0.0), anchor_high (from intensity=1.0)
Output: normalized_value = (raw_value - anchor_low) / (anchor_high - anchor_low)
```

### Step 6: Validate Monotonicity
Verify that increasing intensity produces increasing (or decreasing, if inverted) normalized values.

```
Input: List of (intensity, normalized_value) pairs
Output: is_monotonic (bool), violations (list)
```

### Step 7: Flag and Document Failures
Generate diagnostic report for any component with issues.

```
Input: validation results
Output: diagnostic_report
```

---

## Pseudo-Code

```python
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
import json
import os

@dataclass
class CalibrationSample:
    vector_name: str
    intensity: float
    messages: List[Dict]
    raw_value: float = None
    normalized_value: float = None

@dataclass
class DiagnosticReport:
    vector_name: str
    is_valid: bool
    violations: List[str]
    samples: List[CalibrationSample]

# Step 1: Load synthetic data
def load_calibration_data(data_dir: str) -> Dict[str, List[CalibrationSample]]:
    """Load JSON files grouped by vector component."""
    samples_by_vector = {}
    
    for filename in os.listdir(data_dir):
        if not filename.endswith('.json'):
            continue
        
        # Parse filename: {vector_name}_{intensity}.json
        parts = filename.replace('.json', '').rsplit('_', 1)
        vector_name = parts[0]
        intensity = float(parts[1])
        
        with open(os.path.join(data_dir, filename)) as f:
            data = json.load(f)
        
        sample = CalibrationSample(
            vector_name=vector_name,
            intensity=intensity,
            messages=data['messages']
        )
        
        if vector_name not in samples_by_vector:
            samples_by_vector[vector_name] = []
        samples_by_vector[vector_name].append(sample)
    
    return samples_by_vector

# Step 2: Extract text from messages
def extract_text(messages: List[Dict], sender_filter: str = 'user') -> str:
    """Concatenate text from specified sender."""
    texts = [
        msg['text'] 
        for msg in messages 
        if msg.get('sender') == sender_filter
    ]
    return '\n'.join(texts)

# Step 3: Generate embedding (abstract API)
def get_embedding(text: str, model: Any) -> List[float]:
    """Call embedding model API."""
    # Abstract: replace with actual embedding call
    # e.g., model.encode(text) or openai.embeddings.create(...)
    return model.encode(text)

# Step 4: Extract component activation
def extract_component_value(
    embedding: List[float],
    method: str,
    config: Dict
) -> float:
    """Extract scalar value for target component."""
    
    if method == 'dimension':
        # Direct dimension selection
        return embedding[config['dimension_index']]
    
    elif method == 'projection':
        # Dot product with direction vector
        direction = config['direction_vector']
        return sum(e * d for e, d in zip(embedding, direction))
    
    elif method == 'similarity':
        # Cosine similarity to prototype
        prototype = config['prototype_embedding']
        dot = sum(e * p for e, p in zip(embedding, prototype))
        norm_e = sum(e**2 for e in embedding) ** 0.5
        norm_p = sum(p**2 for p in prototype) ** 0.5
        return dot / (norm_e * norm_p + 1e-8)
    
    else:
        raise ValueError(f"Unknown method: {method}")

# Step 5: Normalize using anchors
def normalize_value(
    raw_value: float,
    anchor_low: float,
    anchor_high: float
) -> float:
    """Scale raw value to 0-1 using anchor points."""
    if anchor_high == anchor_low:
        return 0.5  # Degenerate case
    
    normalized = (raw_value - anchor_low) / (anchor_high - anchor_low)
    return max(0.0, min(1.0, normalized))  # Clip to [0, 1]

# Step 6: Validate monotonicity
def validate_monotonicity(
    samples: List[CalibrationSample]
) -> Tuple[bool, List[str]]:
    """Check if normalized values increase with intensity."""
    sorted_samples = sorted(samples, key=lambda s: s.intensity)
    violations = []
    
    for i in range(1, len(sorted_samples)):
        prev = sorted_samples[i - 1]
        curr = sorted_samples[i]
        
        # Check monotonic increase
        if curr.normalized_value < prev.normalized_value:
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

# Step 7: Generate diagnostic report
def generate_report(
    vector_name: str,
    samples: List[CalibrationSample],
    is_valid: bool,
    violations: List[str]
) -> DiagnosticReport:
    """Create diagnostic report for vector component."""
    return DiagnosticReport(
        vector_name=vector_name,
        is_valid=is_valid,
        violations=violations,
        samples=samples
    )

# Main pipeline
def run_calibration_pipeline(
    data_dir: str,
    embedding_model: Any,
    extraction_config: Dict[str, Dict]
) -> Tuple[List[Dict], List[DiagnosticReport]]:
    """
    Execute full calibration pipeline.
    
    Args:
        data_dir: Directory containing calibration JSON files
        embedding_model: Model for generating embeddings
        extraction_config: Per-vector config for component extraction
    
    Returns:
        results: List of normalized results per conversation
        reports: List of diagnostic reports per vector
    """
    # Load data
    samples_by_vector = load_calibration_data(data_dir)
    
    results = []
    reports = []
    
    for vector_name, samples in samples_by_vector.items():
        config = extraction_config.get(vector_name, {})
        method = config.get('method', 'dimension')
        
        # Process each sample
        for sample in samples:
            text = extract_text(sample.messages)
            embedding = get_embedding(text, embedding_model)
            sample.raw_value = extract_component_value(embedding, method, config)
        
        # Find anchor points (intensity 0.0 and 1.0)
        anchor_low = next(
            (s.raw_value for s in samples if s.intensity == 0.0),
            min(s.raw_value for s in samples)
        )
        anchor_high = next(
            (s.raw_value for s in samples if s.intensity == 1.0),
            max(s.raw_value for s in samples)
        )
        
        # Normalize all samples
        for sample in samples:
            sample.normalized_value = normalize_value(
                sample.raw_value, anchor_low, anchor_high
            )
            
            results.append({
                'id': f"{sample.vector_name}_{sample.intensity}",
                'vector_name': sample.vector_name,
                'intensity': sample.intensity,
                'raw_value': sample.raw_value,
                'normalized_value': sample.normalized_value
            })
        
        # Validate
        is_valid, violations = validate_monotonicity(samples)
        report = generate_report(vector_name, samples, is_valid, violations)
        reports.append(report)
    
    return results, reports
```

---

## Validation Rules

### 1. Monotonicity Test
```
For sorted intensities [i_0, i_1, ..., i_n]:
  normalized[i_k] <= normalized[i_{k+1}] for all k
```
**Failure**: Non-monotonic ordering indicates embedding doesn't capture the feature correctly.

### 2. Separation Test
```
For intensity gap >= 0.25:
  |normalized[i_high] - normalized[i_low]| >= 0.05
```
**Failure**: Collapsed values indicate insufficient feature discrimination.

### 3. Anchor Validity Test
```
anchor_high > anchor_low + epsilon (epsilon = 0.01)
```
**Failure**: Degenerate anchors indicate feature not captured at all.

### 4. Boundary Test
```
For intensity = 0.0: normalized_value in [0.0, 0.15]
For intensity = 1.0: normalized_value in [0.85, 1.0]
```
**Failure**: Anchor samples don't produce expected boundary values.

### 5. Linearity Test (Optional)
```
For intensity = 0.5: normalized_value in [0.35, 0.65]
```
**Failure**: Non-linear scaling may indicate feature saturation.

---

## Output Formats

### Normalized Results (JSON)
```json
{
  "results": [
    {
      "id": "sentiment_mean_0.0",
      "vector_name": "sentiment_mean",
      "intensity": 0.0,
      "raw_value": -0.8234,
      "normalized_value": 0.0
    },
    {
      "id": "sentiment_mean_0.5",
      "vector_name": "sentiment_mean",
      "intensity": 0.5,
      "raw_value": 0.0123,
      "normalized_value": 0.4876
    },
    {
      "id": "sentiment_mean_1.0",
      "vector_name": "sentiment_mean",
      "intensity": 1.0,
      "raw_value": 0.8567,
      "normalized_value": 1.0
    }
  ]
}
```

### Diagnostic Report (JSON)
```json
{
  "reports": [
    {
      "vector_name": "sentiment_mean",
      "is_valid": true,
      "violations": [],
      "sample_count": 3,
      "anchor_low": -0.8234,
      "anchor_high": 0.8567,
      "flagged_for_review": false
    },
    {
      "vector_name": "sentiment_volatility",
      "is_valid": false,
      "violations": [
        "Non-monotonic: intensity 0.50 -> 0.75, but value 0.6234 -> 0.5891",
        "Collapsed: intensities 0.25 and 0.50 have similar values 0.6012 and 0.6234"
      ],
      "sample_count": 5,
      "anchor_low": 0.1234,
      "anchor_high": 0.7891,
      "flagged_for_review": true
    }
  ]
}
```

### Summary Report (Markdown)
```markdown
# Calibration Summary

## Passed: 12/14 vectors
| Vector | Samples | Anchor Range | Status |
|--------|---------|--------------|--------|
| sentiment_mean | 3 | [-0.82, 0.86] | ✓ |
| positive_ratio | 3 | [0.00, 1.00] | ✓ |
| ... | ... | ... | ... |

## Failed: 2/14 vectors
| Vector | Issue | Action Required |
|--------|-------|-----------------|
| sentiment_volatility | Non-monotonic at 0.50-0.75 | Review synthetic data |
| emotional_shift_frequency | Collapsed values | Increase feature contrast |
```

---

## Integration with Existing Pipeline

To integrate with `@c:\Users\Ghesh\Documents\IGB-ai\backend\services\user_feature_extractor.py`:

```python
# In user_feature_extractor.py, add calibration support:

class UserFeatureExtractor:
    def __init__(self, calibration_file: str = None):
        # ... existing init ...
        self.calibration = None
        if calibration_file:
            self.calibration = self._load_calibration(calibration_file)
    
    def _load_calibration(self, filepath: str) -> Dict:
        """Load normalization anchors from calibration results."""
        with open(filepath) as f:
            data = json.load(f)
        return {
            r['vector_name']: {
                'anchor_low': r['anchor_low'],
                'anchor_high': r['anchor_high']
            }
            for r in data['reports']
            if r['is_valid']
        }
    
    def normalize_with_calibration(self, features: Dict) -> Dict:
        """Apply calibration-based normalization."""
        if not self.calibration:
            return features
        
        normalized = {}
        for name, value in features.items():
            if name in self.calibration:
                cal = self.calibration[name]
                normalized[name] = (value - cal['anchor_low']) / (
                    cal['anchor_high'] - cal['anchor_low'] + 1e-8
                )
                normalized[name] = max(0.0, min(1.0, normalized[name]))
            else:
                normalized[name] = value
        
        return normalized
```

---

## File Structure

```
backend/
├── calibration/
│   ├── data/                    # Synthetic JSON files
│   │   ├── sentiment_mean_0.0.json
│   │   ├── sentiment_mean_0.5.json
│   │   ├── sentiment_mean_1.0.json
│   │   └── ...
│   ├── results/                 # Pipeline outputs
│   │   ├── normalized_results.json
│   │   └── diagnostic_reports.json
│   └── run_calibration.py       # Pipeline script
└── docs/
    ├── CALIBRATION_PIPELINE.md  # This document
    └── SENTIMENT_CALIBRATION_DATA.md
```
