"""
Convert batch JSON files to calibration markdown format.
"""

import json
from pathlib import Path


def convert_batch_to_markdown(batch_file: Path, output_file: Path):
    """Convert a batch JSON file to calibration markdown format."""
    
    with open(batch_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    lines = []
    lines.append(f"# {batch_file.stem.upper()} Calibration Data")
    lines.append("")
    lines.append("Synthetic conversational data for calibrating vector components.")
    lines.append("")
    
    feature_idx = 1
    for feature_name, intensity_data in data.items():
        lines.append("---")
        lines.append("")
        lines.append(f"## {feature_idx}. {feature_name}")
        lines.append("")
        
        # Process each intensity level
        for intensity_str, sample_data in sorted(intensity_data.items(), key=lambda x: float(x[0])):
            intensity = float(intensity_str)
            messages = sample_data.get('messages', [])
            
            if not messages:
                continue
            
            lines.append(f"### VECTOR_NAME: {feature_name}")
            lines.append(f"### INTENSITY: {intensity}")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps({"messages": messages}, indent=2))
            lines.append("```")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        feature_idx += 1
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"Converted {batch_file.name} -> {output_file.name}")


def main():
    """Convert all batch files."""
    calibration_dir = Path(__file__).parent
    targets_dir = calibration_dir / 'calibrationtargets'
    targets_dir.mkdir(exist_ok=True)
    
    # Find all batch JSON files
    batch_files = sorted(calibration_dir.glob('batch*.json'))
    
    if not batch_files:
        print("No batch files found!")
        return
    
    print(f"Found {len(batch_files)} batch files")
    print()
    
    for batch_file in batch_files:
        # Create output filename
        output_name = f"{batch_file.stem.upper()}_CALIBRATION_DATA.md"
        output_file = targets_dir / output_name
        
        convert_batch_to_markdown(batch_file, output_file)
    
    print()
    print(f"Converted {len(batch_files)} files to {targets_dir}")


if __name__ == '__main__':
    main()
