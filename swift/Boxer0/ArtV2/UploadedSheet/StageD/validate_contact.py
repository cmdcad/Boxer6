"""Validate contact geometry against engine contracts.

Engine contact coordinates from PunchContact.swift:
- Jab center: (384.5, 189), radius: 20
- Cross center: (378, 186), radius: 18
- Defender target: (220, 127, 88, 173) [x, y, width, height]

This script overlays these coordinates on the exported frames to validate
that the glove positions align with the contact points.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'manifest.json'

# Engine contact geometry
CONTACT_GEOMETRY = {
    'jab': {'center': (384.5, 189), 'radius': 20},
    'cross': {'center': (378, 186), 'radius': 18},
    'defender_target': (220, 127, 88, 173)  # x, y, width, height
}

def analyze_glove_position(image, contact_center, contact_radius):
    """Analyze where the glove is in the image and compare to contact point."""
    alpha = np.array(image)[:,:,3]
    ys, xs = np.where(alpha >= 64)

    if len(xs) == 0:
        return {'glove_center': None, 'distance': None, 'overlap': False}

    # Find the glove by looking at the rightmost alpha pixels (extended arm)
    # For punches, the striking glove should be on the right side
    right_half_x = xs[xs > 256]
    right_half_y = ys[xs > 256]

    if len(right_half_x) == 0:
        return {'glove_center': None, 'distance': None, 'overlap': False}

    # Use rightmost alpha pixel cluster as glove position
    glove_x = float(right_half_x.max())
    glove_y = float(right_half_y[right_half_x.argmax()])

    # Calculate distance to contact point
    dx = glove_x - contact_center[0]
    dy = glove_y - contact_center[1]
    distance = (dx**2 + dy**2)**0.5

    # Check if glove is within reasonable range of contact point
    # Allow up to 2x radius for visual tolerance
    overlap = distance <= contact_radius * 2

    return {
        'glove_center': (glove_x, glove_y),
        'distance': distance,
        'overlap': overlap,
        'contact_center': contact_center,
        'contact_radius': contact_radius
    }

def create_contact_overlay(image, contact_center, contact_radius, glove_analysis):
    """Create a diagnostic overlay showing contact geometry."""
    overlay = image.copy()
    draw = ImageDraw.Draw(overlay)

    # Draw contact point circle (red)
    cx, cy = contact_center
    r = contact_radius
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 0, 0, 200), width=2)
    draw.point([cx, cy], fill=(255, 0, 0, 255))

    # Draw glove center if detected
    if glove_analysis['glove_center']:
        gx, gy = glove_analysis['glove_center']
        draw.point([gx, gy], fill=(0, 255, 0, 255))
        draw.ellipse([gx - 3, gy - 3, gx + 3, gy + 3], outline=(0, 255, 0, 200), width=2)

        # Draw line between glove and contact point
        draw.line([cx, cy, gx, gy], fill=(255, 255, 0, 150), width=1)

    return overlay

def main():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    records = manifest['frames']

    validation_results = []

    for rec in records:
        if rec['clip'] not in ['jab', 'cross']:
            continue

        image_path = ROOT / rec['file']
        image = Image.open(image_path)

        contact_info = CONTACT_GEOMETRY[rec['clip']]
        analysis = analyze_glove_position(image, contact_info['center'], contact_info['radius'])

        validation_results.append({
            'clip': rec['clip'],
            'index': rec['index'],
            'is_contact_frame': rec.get('is_contact_frame', False),
            'glove_analysis': analysis,
            'contact_aligned': analysis['overlap'] if analysis['glove_center'] else False
        })

        # Create diagnostic overlay for contact frames
        if rec.get('is_contact_frame'):
            overlay = create_contact_overlay(image, contact_info['center'], contact_info['radius'], analysis)
            overlay_path = ROOT / f'contact_overlay_{rec["clip"]}_frame{rec["index"]}.png'
            overlay.save(overlay_path)

    # Create comprehensive contact diagnostic sheet
    sheet = Image.new('RGBA', (512 * 6, 550 * 2), (232, 238, 244, 255))
    draw = ImageDraw.Draw(sheet)

    # Jab row
    jab_results = [r for r in validation_results if r['clip'] == 'jab']
    for i, res in enumerate(jab_results):
        x = i * 512
        y = 0
        image = Image.open(ROOT / f'frames/jab_{i}.png')

        # Apply contact overlay if it's the contact frame
        if res['is_contact_frame']:
            overlay = create_contact_overlay(image, CONTACT_GEOMETRY['jab']['center'],
                                             CONTACT_GEOMETRY['jab']['radius'], res['glove_analysis'])
            sheet.alpha_composite(overlay, (x, y))
        else:
            sheet.alpha_composite(image, (x, y))

        # Draw baseline and root
        draw.line((x, y + 448, x + 511, y + 448), fill=(210, 90, 70))
        draw.line((x + 256, y + 430, x + 256, y + 465), fill=(70, 130, 200))

        # Label
        label = f'Jab {i+1}'
        if res['is_contact_frame']:
            glove_dist = res['glove_analysis'].get('distance')
            aligned = res['contact_aligned']
            dist_str = f'{glove_dist:.1f}' if glove_dist is not None else 'N/A'
            label += f' CONTACT (dist: {dist_str}, aligned: {aligned})'
        draw.text((x + 12, y + 520), label, fill=(25, 42, 60))

    # Cross row
    cross_results = [r for r in validation_results if r['clip'] == 'cross']
    for i, res in enumerate(cross_results):
        x = i * 512
        y = 550
        image = Image.open(ROOT / f'frames/cross_{i}.png')

        if res['is_contact_frame']:
            overlay = create_contact_overlay(image, CONTACT_GEOMETRY['cross']['center'],
                                             CONTACT_GEOMETRY['cross']['radius'], res['glove_analysis'])
            sheet.alpha_composite(overlay, (x, y))
        else:
            sheet.alpha_composite(image, (x, y))

        draw.line((x, y + 448, x + 511, y + 448), fill=(210, 90, 70))
        draw.line((x + 256, y + 430, x + 256, y + 465), fill=(70, 130, 200))

        label = f'Cross {i+1}'
        if res['is_contact_frame']:
            glove_dist = res['glove_analysis'].get('distance')
            aligned = res['contact_aligned']
            dist_str = f'{glove_dist:.1f}' if glove_dist is not None else 'N/A'
            label += f' CONTACT (dist: {dist_str}, aligned: {aligned})'
        elif res.get('is_transition'):
            label += ' TRANSITION'
        draw.text((x + 12, y + 520), label, fill=(25, 42, 60))

    sheet.convert('RGB').save(ROOT / 'contact_diagnostic_sheet.png')

    # Save validation report
    report = {
        'contact_geometry': CONTACT_GEOMETRY,
        'validation_results': validation_results,
        'summary': {
            'jab_contact_aligned': next((r['contact_aligned'] for r in jab_results if r['is_contact_frame']), False),
            'cross_contact_aligned': next((r['contact_aligned'] for r in cross_results if r['is_contact_frame']), False)
        }
    }

    (ROOT / 'contact_validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    print(f'Contact validation complete.')
    print(f'Jab contact frame aligned: {report["summary"]["jab_contact_aligned"]}')
    print(f'Cross contact frame aligned: {report["summary"]["cross_contact_aligned"]}')
    print(f'Diagnostic sheet saved to {ROOT / "contact_diagnostic_sheet.png"}')
    print(f'Validation report saved to {ROOT / "contact_validation.json"}')

if __name__ == '__main__':
    main()
