"""
Calibration Runner Script
Parses calibration target files from calibration/calibrationtargets/ and runs the calibration pipeline.

Usage:
    python run_calibration.py
    python run_calibration.py --targets-dir ./calibrationtargets
    python run_calibration.py --output ./results/calibration_results.txt
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from calibration.parser import CalibrationDataParser
from calibration.pipeline import CalibrationPipeline
from calibration.models import CalibrationResult, DiagnosticReport


def format_results_text(
    results: list,
    reports: list,
    execution_time: float
) -> str:
    """Format results as a text report."""
    lines = []
    
    # Header
    lines.append("=" * 80)
    lines.append("CALIBRATION PIPELINE RESULTS")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Execution Time: {execution_time:.2f} seconds")
    lines.append("=" * 80)
    lines.append("")
    
    # Summary
    total_vectors = len(reports)
    passed_vectors = sum(1 for r in reports if r.is_valid)
    failed_vectors = total_vectors - passed_vectors
    
    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append(f"Total Vectors Processed: {total_vectors}")
    lines.append(f"Passed: {passed_vectors}")
    lines.append(f"Failed: {failed_vectors}")
    lines.append(f"Pass Rate: {(passed_vectors/total_vectors*100) if total_vectors > 0 else 0:.1f}%")
    lines.append("")
    
    # Detailed Results by Vector
    lines.append("DETAILED RESULTS BY VECTOR")
    lines.append("-" * 40)
    
    for report in sorted(reports, key=lambda r: r.vector_name):
        status = "PASS" if report.is_valid else "FAIL"
        lines.append(f"\n[{status}] {report.vector_name}")
        lines.append(f"  Anchor Low (0.0):  {report.anchor_low:.6f}" if report.anchor_low is not None else "  Anchor Low (0.0):  N/A")
        lines.append(f"  Anchor Mid (0.5):  {report.anchor_mid:.6f}" if report.anchor_mid is not None else "  Anchor Mid (0.5):  N/A")
        lines.append(f"  Anchor High (1.0): {report.anchor_high:.6f}" if report.anchor_high is not None else "  Anchor High (1.0): N/A")
        lines.append(f"  Sample Count: {len(report.samples)}")
        
        if report.violations:
            lines.append("  Violations:")
            for v in report.violations:
                lines.append(f"    - {v}")
        
        # Show sample values
        lines.append("  Samples:")
        for sample in sorted(report.samples, key=lambda s: s.intensity):
            raw = f"{sample.raw_value:.6f}" if sample.raw_value is not None else "N/A"
            norm = f"{sample.normalized_value:.6f}" if sample.normalized_value is not None else "N/A"
            lines.append(f"    intensity={sample.intensity:.2f}: raw={raw}, normalized={norm}")
    
    lines.append("")
    
    # Normalized Results Table
    lines.append("NORMALIZED RESULTS TABLE")
    lines.append("-" * 40)
    lines.append(f"{'ID':<40} {'Intensity':<10} {'Raw Value':<15} {'Normalized':<15}")
    lines.append("-" * 80)
    
    for result in sorted(results, key=lambda r: (r.vector_name, r.intensity)):
        lines.append(f"{result.id:<40} {result.intensity:<10.2f} {result.raw_value:<15.6f} {result.normalized_value:<15.6f}")
    
    lines.append("")
    
    # Failed Vectors Summary
    if failed_vectors > 0:
        lines.append("FAILED VECTORS REQUIRING REVIEW")
        lines.append("-" * 40)
        for report in reports:
            if not report.is_valid:
                lines.append(f"\n{report.vector_name}:")
                for v in report.violations:
                    lines.append(f"  - {v}")
    
    lines.append("")
    
    # Normalization Formulas
    lines.append("=" * 80)
    lines.append("NORMALIZATION FORMULAS (3-Point Piecewise Linear)")
    lines.append("=" * 80)
    lines.append("")
    lines.append("For each feature, use the following formula to normalize raw values to [0, 1]:")
    lines.append("")
    
    for report in sorted(reports, key=lambda r: r.vector_name):
        lines.append(report.get_normalization_formula())
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def format_results_json(results: list, reports: list) -> str:
    """Format results as JSON."""
    return json.dumps({
        'generated': datetime.now().isoformat(),
        'summary': {
            'total_vectors': len(reports),
            'passed': sum(1 for r in reports if r.is_valid),
            'failed': sum(1 for r in reports if not r.is_valid)
        },
        'results': [r.to_dict() for r in results],
        'reports': [r.to_dict() for r in reports]
    }, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Run calibration pipeline on synthetic data')
    parser.add_argument(
        '--targets-dir',
        type=str,
        default='calibrationtargets',
        help='Directory containing calibration target .md files'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='calibration_results.txt',
        help='Output file path for results'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['text', 'json'],
        default='text',
        help='Output format (text or json)'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    script_dir = Path(__file__).parent
    targets_dir = script_dir / args.targets_dir
    output_path = script_dir / args.output
    
    print(f"Calibration Pipeline Runner")
    print(f"=" * 40)
    print(f"Targets Directory: {targets_dir}")
    print(f"Output File: {output_path}")
    print()
    
    # Check targets directory exists
    if not targets_dir.exists():
        print(f"Creating targets directory: {targets_dir}")
        targets_dir.mkdir(parents=True, exist_ok=True)
        print(f"Please add calibration target files (e.g., SENTIMENT_CALIBRATION_DATA.md) to:")
        print(f"  {targets_dir}")
        return 1
    
    # Find calibration files
    calibration_files = list(targets_dir.glob('*_CALIBRATION_DATA.md'))
    
    if not calibration_files:
        print(f"No calibration files found in {targets_dir}")
        print(f"Expected files matching pattern: *_CALIBRATION_DATA.md")
        print(f"\nYou can copy the calibration data from docs/SENTIMENT_CALIBRATION_DATA.md")
        return 1
    
    print(f"Found {len(calibration_files)} calibration file(s):")
    for f in calibration_files:
        print(f"  - {f.name}")
    print()
    
    # Parse calibration files
    print("Parsing calibration files...")
    data_parser = CalibrationDataParser()
    
    all_samples = []
    for filepath in calibration_files:
        samples = data_parser.parse_file(filepath)
        all_samples.extend(samples)
        print(f"  {filepath.name}: {len(samples)} samples")
    
    if not all_samples:
        print("No valid samples found in calibration files")
        return 1
    
    # Group by vector
    samples_by_vector = data_parser.group_by_vector(all_samples)
    print(f"\nTotal: {len(all_samples)} samples across {len(samples_by_vector)} vectors")
    print()
    
    # Run pipeline
    print("Running calibration pipeline...")
    print("-" * 40)
    
    start_time = datetime.now()
    
    pipeline = CalibrationPipeline()
    results, reports = pipeline.run(samples_by_vector)
    
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()
    
    print()
    print("-" * 40)
    print(f"Pipeline completed in {execution_time:.2f} seconds")
    print()
    
    # Format and save results
    if args.format == 'json':
        output_content = format_results_json(results, reports)
        if not output_path.suffix:
            output_path = output_path.with_suffix('.json')
    else:
        output_content = format_results_text(results, reports, execution_time)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"Results saved to: {output_path}")
    
    # Print summary
    passed = sum(1 for r in reports if r.is_valid)
    failed = len(reports) - passed
    
    print()
    print("=" * 40)
    print(f"SUMMARY: {passed}/{len(reports)} vectors passed")
    if failed > 0:
        print(f"FAILED VECTORS:")
        for r in reports:
            if not r.is_valid:
                print(f"  - {r.vector_name}")
    print("=" * 40)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
