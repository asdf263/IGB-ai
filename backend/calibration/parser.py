"""
Parser for calibration target markdown files.
Extracts JSON conversation samples from files like SENTIMENT_CALIBRATION_DATA.md
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from .models import CalibrationSample


class CalibrationDataParser:
    """Parses calibration markdown files to extract conversation samples."""
    
    def __init__(self):
        self.json_pattern = re.compile(r'```json\s*\n({[\s\S]*?})\s*\n```', re.MULTILINE)
        self.vector_pattern = re.compile(r'###\s*VECTOR_NAME:\s*(\S+)')
        self.intensity_pattern = re.compile(r'###\s*INTENSITY:\s*([\d.]+)')
    
    def parse_file(self, filepath: Path) -> List[CalibrationSample]:
        """Parse a single calibration markdown file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> List[CalibrationSample]:
        """Parse markdown content and extract calibration samples."""
        samples = []
        
        # Split by section headers (## N. feature_name)
        sections = re.split(r'\n## \d+\.', content)
        
        for section in sections:
            section_samples = self._parse_section(section)
            samples.extend(section_samples)
        
        return samples
    
    def _parse_section(self, section: str) -> List[CalibrationSample]:
        """Parse a single section containing one or more intensity samples."""
        samples = []
        
        # Split by intensity blocks (### VECTOR_NAME:)
        blocks = re.split(r'\n---\n', section)
        
        for block in blocks:
            sample = self._parse_block(block)
            if sample:
                samples.append(sample)
        
        return samples
    
    def _parse_block(self, block: str) -> Optional[CalibrationSample]:
        """Parse a single intensity block."""
        # Extract vector name
        vector_match = self.vector_pattern.search(block)
        if not vector_match:
            return None
        vector_name = vector_match.group(1)
        
        # Extract intensity
        intensity_match = self.intensity_pattern.search(block)
        if not intensity_match:
            return None
        intensity = float(intensity_match.group(1))
        
        # Extract JSON conversation
        json_match = self.json_pattern.search(block)
        if not json_match:
            return None
        
        try:
            data = json.loads(json_match.group(1))
            messages = data.get('messages', [])
        except json.JSONDecodeError:
            return None
        
        if not messages:
            return None
        
        return CalibrationSample(
            vector_name=vector_name,
            intensity=intensity,
            messages=messages
        )
    
    def parse_directory(self, directory: Path) -> Dict[str, List[CalibrationSample]]:
        """Parse all calibration files in a directory."""
        samples_by_category = {}
        
        for filepath in directory.glob('*_CALIBRATION_DATA.md'):
            # Extract category from filename (e.g., SENTIMENT from SENTIMENT_CALIBRATION_DATA.md)
            category = filepath.stem.replace('_CALIBRATION_DATA', '')
            
            samples = self.parse_file(filepath)
            if samples:
                samples_by_category[category] = samples
        
        return samples_by_category
    
    def group_by_vector(self, samples: List[CalibrationSample]) -> Dict[str, List[CalibrationSample]]:
        """Group samples by vector name."""
        grouped = {}
        for sample in samples:
            if sample.vector_name not in grouped:
                grouped[sample.vector_name] = []
            grouped[sample.vector_name].append(sample)
        return grouped
