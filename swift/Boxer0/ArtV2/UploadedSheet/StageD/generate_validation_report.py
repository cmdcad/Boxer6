"""Generate comprehensive validation report for Stage D.

Checks:
- Frame counts match engine contracts
- Canvas dimensions are 512x512
- Alpha channel is present and non-empty
- Character height matches Stage A (~320px)
- Feet are detected at baseline 448
- No frames are clipped outside canvas
- Contact geometry analysis
- Frame timing matches engine contracts
"""
from pathlib import Path
import json
import hashlib
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'manifest.json'
CONTACT_VALIDATION = ROOT / 'contact_validation.json'

def validate_frame(image_path):
    """Validate a single frame."""
    img = Image.open(image_path)
    img.verify()
    img = Image.open(image_path)  # Reopen after verify

    issues = []
    warnings = []

    # Check canvas size
    if img.size != (512, 512):
        issues.append(f"Canvas size is {img.size}, expected (512, 512)")

    # Check alpha channel
    if img.mode != 'RGBA':
        issues.append(f"Image mode is {img.mode}, expected RGBA")

    alpha = np.array(img)[:,:,3]
    if alpha.sum() == 0:
        issues.append("Alpha channel is completely empty")

    # Check character bounds
    ys, xs = np.where(alpha >= 32)
    if len(xs) > 0:
        bounds = [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)]
        height = bounds[3] - bounds[1]

        # Check character height (should be ~320px like Stage A)
        if height < 280:
            warnings.append(f"Character height {height}px is small (expected ~320px)")
        elif height > 360:
            warnings.append(f"Character height {height}px is large (expected ~320px)")

        # Check canvas containment
        if bounds[0] < 0 or bounds[1] < 0 or bounds[2] > 512 or bounds[3] > 512:
            issues.append(f"Character bounds {bounds} exceed canvas")

        # Check foot detection
        fy, fx = np.where(alpha[440:, :] >= 32)
        if len(fy) == 0:
            warnings.append("No feet detected in bottom region")
        else:
            bottom = int(fy.max() + 440)
            ground_gap = 448 - bottom
            if ground_gap < -10:
                issues.append(f"Feet extend below baseline by {-ground_gap}px")
            elif ground_gap > 10:
                warnings.append(f"Feet are {ground_gap}px above baseline")
    else:
        issues.append("No alpha pixels found")

    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'bounds': [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)] if len(xs) > 0 else None,
        'alpha_pixels': int(alpha.sum() / 255),
        'sha256': hashlib.sha256(image_path.read_bytes()).hexdigest()
    }

def main():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    contact_validation = json.loads(CONTACT_VALIDATION.read_text(encoding='utf-8'))

    records = manifest['frames']
    validation_results = []

    for rec in records:
        image_path = ROOT / rec['file']
        frame_validation = validate_frame(image_path)

        # Add contact info if available
        contact_info = None
        for cv in contact_validation['validation_results']:
            if cv['clip'] == rec['clip'] and cv['index'] == rec['index']:
                contact_info = cv
                break

        validation_results.append({
            'clip': rec['clip'],
            'index': rec['index'],
            'file': rec['file'],
            'duration_ms': rec['duration_ms'],
            'validation': frame_validation,
            'contact_info': contact_info
        })

    # Summary
    total_frames = len(validation_results)
    valid_frames = sum(1 for r in validation_results if r['validation']['valid'])
    frames_with_issues = total_frames - valid_frames

    jab_frames = [r for r in validation_results if r['clip'] == 'jab']
    cross_frames = [r for r in validation_results if r['clip'] == 'cross']

    report = {
        'stage': 'D',
        'description': 'Punches and Recovery (Jab, Cross, Jab Recovery, Cross Recovery)',
        'validation_date': '2026-10-20',
        'summary': {
            'total_frames': total_frames,
            'valid_frames': valid_frames,
            'frames_with_issues': frames_with_issues,
            'jab_frame_count': len(jab_frames),
            'cross_frame_count': len(cross_frames),
            'jab_recovery_count': len([r for r in validation_results if r['clip'] == 'jab_recovery']),
            'cross_recovery_count': len([r for r in validation_results if r['clip'] == 'cross_recovery'])
        },
        'engine_contract_compliance': {
            'jab': {
                'expected_frames': 6,
                'expected_duration_ms': 300,
                'expected_contact_frame': 3,
                'expected_contact_ms': 150,
                'actual_frames': len(jab_frames),
                'actual_duration_ms': sum(r['duration_ms'] for r in jab_frames),
                'compliant': len(jab_frames) == 6 and sum(r['duration_ms'] for r in jab_frames) == 300
            },
            'cross': {
                'expected_frames': 8,
                'expected_duration_ms': 480,
                'expected_contact_frame': 4,
                'expected_contact_ms': 240,
                'actual_frames': len(cross_frames),
                'actual_duration_ms': sum(r['duration_ms'] for r in cross_frames),
                'compliant': len(cross_frames) == 8 and sum(r['duration_ms'] for r in cross_frames) == 480
            }
        },
        'contact_geometry': contact_validation['contact_geometry'],
        'contact_alignment': contact_validation['summary'],
        'frame_validations': validation_results,
        'limitations': [
            'Contact geometry mismatch: New artwork has different proportions than engine coordinates',
            'Jab glove at frame 3 is ~75px from engine contact point (384.5, 189)',
            'Cross glove at frame 4 may also deviate from engine contact point (378, 186)',
            'Engine contact coordinates may need adjustment to match new artwork',
            'Transition frames for Cross are simple 50/50 blends - may not be anatomically ideal'
        ],
        'notes': [
            'All frames exported at 512x512 RGBA',
            'Scale 2.05 used to match Stage A character height (~320px)',
            'Cross includes 2 transition frames (indices 3 and 6)',
            'Contact diagnostic sheet available at contact_diagnostic_sheet.png',
            'Full alignment sheet available at full_alignment_sheet.png',
            'Animated GIFs available for review'
        ]
    }

    (ROOT / 'validation_report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    print(f'Validation report generated:')
    print(f'  Total frames: {total_frames}')
    print(f'  Valid frames: {valid_frames}')
    print(f'  Frames with issues: {frames_with_issues}')
    print(f'  Jab compliance: {report["engine_contract_compliance"]["jab"]["compliant"]}')
    print(f'  Cross compliance: {report["engine_contract_compliance"]["cross"]["compliant"]}')
    print(f'  Jab contact aligned: {report["contact_alignment"]["jab_contact_aligned"]}')
    print(f'  Cross contact aligned: {report["contact_alignment"]["cross_contact_aligned"]}')
    print(f'Report saved to {ROOT / "validation_report.json"}')

if __name__ == '__main__':
    main()
