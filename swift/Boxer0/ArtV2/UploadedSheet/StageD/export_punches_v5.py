"""Export Stage D with cleaned cutouts and fixed recovery timing.

Changes from v4:
- Use checkerboard-removed cutouts
- Cross: Use 6 illustrated poses only (transitions need manual artwork)
- Recovery timing: Jab 120ms, Cross 220ms (in GIFs)
- Add Idle frame after recovery in sequences
"""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
CUTOUTS = ROOT / 'cutouts'
STAGEA = ROOT.parent / 'StageA'

# Scale to match Stage A character height (~320px) from ~155px cutouts
SCALE = 2.05

def measures(image):
    """Measure foot positions and bounding box."""
    alpha = np.array(image)[:,:,3]
    ys, xs = np.where(alpha >= 32)
    if len(xs) == 0:
        return {'bounds': [0, 0, 0, 0], 'rear': {'sole_y': None, 'sole_x': None, 'ground_gap': None},
                'lead': {'sole_y': None, 'sole_x': None, 'ground_gap': None}}
    result = {'bounds': [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)]}
    for name, left, right in [('rear', 0, 256), ('lead', 256, 512)]:
        fy, fx = np.where(alpha[340:, left:right] >= 32)
        if len(fy) == 0:
            result[name] = {'sole_y': None, 'sole_x': None, 'ground_gap': None}
            continue
        bottom = int(fy.max() + 340)
        by, bx = np.where(alpha[bottom-2:bottom+1, left:right] >= 32)
        if len(bx) == 0:
            result[name] = {'sole_y': None, 'sole_x': None, 'ground_gap': None}
        else:
            result[name] = {'sole_y': bottom, 'sole_x': float((bx.min() + bx.max()) / 2 + left),
                           'ground_gap': 448 - bottom}
    return result

def scale_and_position(img, scale):
    """Scale cutout and position on 512x512 canvas at baseline."""
    scaled = img.resize(tuple(round(v * scale) for v in img.size), Image.Resampling.LANCZOS)

    alpha = np.array(scaled)[:,:,3]
    ys, xs = np.where(alpha >= 32)

    if len(xs) == 0:
        canvas = Image.new('RGBA', (512, 512))
        x = (512 - scaled.width) // 2
        y = (512 - scaled.height) // 2
        canvas.alpha_composite(scaled, (x, y))
        return canvas, {'dx': x, 'dy': y}

    bounds = [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)]
    bottom_y = bounds[3]
    target_y = 448 - bottom_y
    center_x = (bounds[0] + bounds[2]) // 2
    target_x = 256 - center_x

    canvas = Image.new('RGBA', (512, 512))
    canvas.alpha_composite(scaled, (target_x, target_y))

    return canvas, {'dx': target_x, 'dy': target_y}

def main():
    (ROOT / 'frames').mkdir(exist_ok=True)
    (ROOT / 'source').mkdir(exist_ok=True)

    records = []
    images = []

    # Jab: 6 frames
    for i in range(6):
        path = CUTOUTS / f'jab_{i}.png'
        if not path.exists():
            print(f"Warning: jab_{i}.png not found, skipping")
            continue

        raw = Image.open(path).convert('RGBA')
        image, pos = scale_and_position(raw, SCALE)

        dest = ROOT / f'frames/jab_{i}.png'
        image.save(dest)

        source_dest = ROOT / f'source/jab_{i}_base.png'
        shutil.copy(path, source_dest)

        meas = measures(image)

        records.append({
            'clip': 'jab',
            'index': i,
            'file': dest.relative_to(ROOT).as_posix(),
            'duration_ms': 50,
            'selected_source': source_dest.relative_to(ROOT).as_posix(),
            'vertical_registration': pos['dy'],
            'horizontal_registration': pos['dx'],
            'scale_factor': SCALE,
            'is_contact_frame': i == 3,
            'measurements': meas,
            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
        })
        images.append(image)

    # Cross: 6 illustrated poses only (transitions need manual artwork)
    for i in range(6):
        path = CUTOUTS / f'cross_{i}.png'
        if not path.exists():
            print(f"Warning: cross_{i}.png not found, skipping")
            continue

        raw = Image.open(path).convert('RGBA')
        image, pos = scale_and_position(raw, SCALE)

        dest = ROOT / f'frames/cross_{i}.png'
        image.save(dest)

        source_dest = ROOT / f'source/cross_{i}_base.png'
        shutil.copy(path, source_dest)

        meas = measures(image)

        records.append({
            'clip': 'cross',
            'index': i,
            'file': dest.relative_to(ROOT).as_posix(),
            'duration_ms': 60,
            'selected_source': source_dest.relative_to(ROOT).as_posix(),
            'vertical_registration': pos['dy'],
            'horizontal_registration': pos['dx'],
            'scale_factor': SCALE,
            'is_contact_frame': i == 4,
            'measurements': meas,
            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
        })
        images.append(image)

    # Recovery
    jab_recovery_path = CUTOUTS / 'jab_recovery.png'
    if jab_recovery_path.exists():
        raw = Image.open(jab_recovery_path).convert('RGBA')
        image, pos = scale_and_position(raw, SCALE)

        dest = ROOT / f'frames/jab_recovery.png'
        image.save(dest)

        source_dest = ROOT / f'source/jab_recovery_base.png'
        shutil.copy(jab_recovery_path, source_dest)

        meas = measures(image)

        records.append({
            'clip': 'jab_recovery',
            'index': 0,
            'file': dest.relative_to(ROOT).as_posix(),
            'duration_ms': 120,
            'selected_source': source_dest.relative_to(ROOT).as_posix(),
            'vertical_registration': pos['dy'],
            'horizontal_registration': pos['dx'],
            'scale_factor': SCALE,
            'measurements': meas,
            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
        })
        images.append(image)

    cross_recovery_path = CUTOUTS / 'cross_recovery.png'
    if cross_recovery_path.exists():
        raw = Image.open(cross_recovery_path).convert('RGBA')
        image, pos = scale_and_position(raw, SCALE)

        dest = ROOT / f'frames/cross_recovery.png'
        image.save(dest)

        source_dest = ROOT / f'source/cross_recovery_base.png'
        shutil.copy(cross_recovery_path, source_dest)

        meas = measures(image)

        records.append({
            'clip': 'cross_recovery',
            'index': 0,
            'file': dest.relative_to(ROOT).as_posix(),
            'duration_ms': 220,
            'selected_source': source_dest.relative_to(ROOT).as_posix(),
            'vertical_registration': pos['dy'],
            'horizontal_registration': pos['dx'],
            'scale_factor': SCALE,
            'measurements': meas,
            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
        })
        images.append(image)

    # Generate preview sheet
    sheet = Image.new('RGBA', (512 * 8, 550 * 2), (232, 238, 244, 255))
    draw = ImageDraw.Draw(sheet)

    # Jab row
    for i in range(6):
        rec = next((r for r in records if r['clip'] == 'jab' and r['index'] == i), None)
        if rec:
            x = i * 512
            y = 0
            img = Image.open(ROOT / rec['file'])
            sheet.alpha_composite(img, (x, y))
            draw.line((x, y + 448, x + 511, y + 448), fill=(210, 90, 70))
            draw.line((x + 256, y + 430, x + 256, y + 465), fill=(70, 130, 200))
            time_str = f"{i * 50} ms"
            if rec.get('is_contact_frame'):
                time_str += " CONTACT"
            draw.text((x + 12, y + 520), f'Jab {i + 1}: {time_str}', fill=(25, 42, 60))

    # Recovery in jab row slots 6-7
    for i in range(2):
        x = (6 + i) * 512
        y = 0
        if i == 0:
            img = Image.open(jab_recovery_path.parent.parent / 'frames/jab_recovery.png')
            sheet.alpha_composite(img, (x, y))
            draw.line((x, y + 448, x + 511, y + 448), fill=(210, 90, 70))
            draw.line((x + 256, y + 430, x + 256, y + 465), fill=(70, 130, 200))
            draw.text((x + 12, y + 520), 'Jab Recovery: 120ms', fill=(25, 42, 60))
        if i == 1:
            img = Image.open(cross_recovery_path.parent.parent / 'frames/cross_recovery.png')
            sheet.alpha_composite(img, (x, y))
            draw.line((x, y + 448, x + 511, y + 448), fill=(210, 90, 70))
            draw.line((x + 256, y + 430, x + 256, y + 465), fill=(70, 130, 200))
            draw.text((x + 12, y + 520), 'Cross Recovery: 220ms', fill=(25, 42, 60))

    # Cross row
    for i in range(6):
        rec = next((r for r in records if r['clip'] == 'cross' and r['index'] == i), None)
        if rec:
            x = i * 512
            y = 550
            img = Image.open(ROOT / rec['file'])
            sheet.alpha_composite(img, (x, y))
            draw.line((x, y + 448, x + 511, y + 448), fill=(210, 90, 70))
            draw.line((x + 256, y + 430, x + 256, y + 465), fill=(70, 130, 200))
            time_str = f"{i * 60} ms"
            if rec.get('is_contact_frame'):
                time_str += " CONTACT"
            draw.text((x + 12, y + 520), f'Cross {i + 1}: {time_str}', fill=(25, 42, 60))

    sheet.convert('RGB').save(ROOT / 'alignment_sheet.png')

    # Manifest
    manifest = {
        'canvas': [512, 512],
        'root': [256, 448],
        'baseline': 448,
        'facing': 'right',
        'scale_factor': SCALE,
        'note': 'Cross uses 6 illustrated poses only. Transitions require manual artwork creation.',
        'integrated': False,
        'clips': {
            'jab': {
                'frame_count': 6,
                'frame_duration_ms': 50,
                'total_ms': 300,
                'contact_frame': 3,
                'contact_ms': 150
            },
            'cross': {
                'frame_count': 6,
                'frame_duration_ms': 60,
                'total_ms': 360,
                'contact_frame': 4,
                'contact_ms': 240,
                'note': '6 illustrated poses only. Transitions not created - require manual artwork.'
            },
            'jab_recovery': {
                'frame_count': 1,
                'duration_ms': 120
            },
            'cross_recovery': {
                'frame_count': 1,
                'duration_ms': 220
            }
        },
        'frames': records
    }

    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'Exported Stage D: 6 Jab frames (300ms), 6 Cross frames (360ms - transitions require manual artwork), Jab recovery (120ms), Cross recovery (220ms).')
    print(f'Using scale {SCALE} to match Stage A character height. Alignment sheet saved to {ROOT}')

if __name__ == '__main__':
    main()
