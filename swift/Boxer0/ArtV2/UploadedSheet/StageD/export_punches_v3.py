"""Export Stage D punch and recovery assets with correct scale.

Stage A scale 0.4056 was for 1254x1254 source images.
Our cutouts are ~84x156, so we need a larger scale to reach ~320px character height.
Target scale = 320 / 156 = 2.05
"""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
CUTOUTS = ROOT / 'cutouts'

# Calculate scale to match Stage A character height (~320px)
# Our cutouts are ~156px tall
SCALE = 2.05
OFFSET = (-2, 2)

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

def export_frame(img, dest, source_dest, clip, index, duration_ms, metadata):
    """Export a frame with scale and offset."""
    # Resize
    resized = img.resize(tuple(round(v * SCALE) for v in img.size), Image.Resampling.LANCZOS)

    # Composite with offset
    canvas = Image.new('RGBA', (512, 512))
    canvas.alpha_composite(resized, OFFSET)

    canvas.save(dest)

    meas = measures(canvas)

    return {
        'clip': clip,
        'index': index,
        'file': dest.relative_to(ROOT).as_posix(),
        'duration_ms': duration_ms,
        'selected_source': source_dest.relative_to(ROOT).as_posix(),
        'vertical_registration': OFFSET[1],
        'horizontal_registration': OFFSET[0],
        'scale_factor': SCALE,
        **metadata,
        'measurements': meas,
        'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
    }

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
        dest = ROOT / f'frames/jab_{i}.png'
        source_dest = ROOT / f'source/jab_{i}_base.png'
        shutil.copy(path, source_dest)

        rec = export_frame(raw, dest, source_dest, 'jab', i, 50,
                          {'is_contact_frame': i == 3})
        records.append(rec)
        images.append(Image.open(dest))

    # Cross: 6 illustrated + 2 transitions = 8 frames
    cross_sequence = []
    for i in range(6):
        path = CUTOUTS / f'cross_illustrated_{i}.png'
        if path.exists():
            cross_sequence.append(Image.open(path).convert('RGBA'))

    if len(cross_sequence) >= 6:
        # Create transition between pose 2 and 3
        if len(cross_sequence) > 2:
            transition1 = np.array(cross_sequence[2]).astype(float) * 0.5 + np.array(cross_sequence[3]).astype(float) * 0.5
            cross_sequence.insert(3, Image.fromarray(transition1.astype(np.uint8)))

        # Create transition between pose 4 and 5
        if len(cross_sequence) > 5:
            transition2 = np.array(cross_sequence[5]).astype(float) * 0.5 + np.array(cross_sequence[6] if len(cross_sequence) > 6 else cross_sequence[5]).astype(float) * 0.5
            cross_sequence.insert(6, Image.fromarray(transition2.astype(np.uint8)))

    for i, img in enumerate(cross_sequence[:8]):
        dest = ROOT / f'frames/cross_{i}.png'
        source_name = f'cross_illustrated_{min(i, 5)}.png'
        source_path = CUTOUTS / source_name
        source_dest = ROOT / f'source/cross_{i}_base.png'
        if source_path.exists():
            shutil.copy(source_path, source_dest)
        else:
            shutil.copy(CUTOUTS / f'cross_illustrated_{min(i, 5)}.png', source_dest)

        rec = export_frame(img, dest, source_dest, 'cross', i, 60,
                          {'is_contact_frame': i == 4, 'is_transition': i in [3, 6]})
        records.append(rec)
        images.append(Image.open(dest))

    # Recovery
    jab_recovery_path = CUTOUTS / 'recovery_0.png'
    if jab_recovery_path.exists():
        raw = Image.open(jab_recovery_path).convert('RGBA')
        dest = ROOT / f'frames/jab_recovery.png'
        source_dest = ROOT / f'source/jab_recovery_base.png'
        shutil.copy(jab_recovery_path, source_dest)

        rec = export_frame(raw, dest, source_dest, 'jab_recovery', 0, 120, {})
        records.append(rec)
        images.append(Image.open(dest))

    cross_recovery_path = CUTOUTS / 'recovery_1.png'
    if cross_recovery_path.exists():
        raw = Image.open(cross_recovery_path).convert('RGBA')
        dest = ROOT / f'frames/cross_recovery.png'
        source_dest = ROOT / f'source/cross_recovery_base.png'
        shutil.copy(cross_recovery_path, source_dest)

        rec = export_frame(raw, dest, source_dest, 'cross_recovery', 0, 220, {})
        records.append(rec)
        images.append(Image.open(dest))

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

    # Cross row
    for i in range(8):
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
            if rec.get('is_transition'):
                time_str += " TRANSITION"
            draw.text((x + 12, y + 520), f'Cross {i + 1}: {time_str}', fill=(25, 42, 60))

    sheet.convert('RGB').save(ROOT / 'alignment_sheet.png')

    # Generate preview GIFs
    jab_images = [Image.open(ROOT / r['file']) for r in records if r['clip'] == 'jab']
    if jab_images:
        jab_images[0].save(ROOT / 'jab_preview.png', save_all=True,
                           append_images=jab_images[1:], duration=50, loop=0, disposal=0, blend=0)

    cross_images = [Image.open(ROOT / r['file']) for r in records if r['clip'] == 'cross']
    if cross_images:
        cross_images[0].save(ROOT / 'cross_preview.png', save_all=True,
                            append_images=cross_images[1:], duration=60, loop=0, disposal=0, blend=0)

    # Manifest
    manifest = {
        'canvas': [512, 512],
        'root': [256, 448],
        'baseline': 448,
        'facing': 'right',
        'scale_factor': SCALE,
        'offset': list(OFFSET),
        'note': 'Cross includes 2 transition frames created from illustrated poses',
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
                'frame_count': 8,
                'frame_duration_ms': 60,
                'total_ms': 480,
                'contact_frame': 4,
                'contact_ms': 240,
                'transition_frames': [3, 6]
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
    print(f'Exported Stage D: 6 Jab frames (300ms), 8 Cross frames (480ms with 2 transitions), Jab recovery (120ms), Cross recovery (220ms).')
    print(f'Using scale {SCALE} and offset {OFFSET}. Alignment sheet saved to {ROOT}')

if __name__ == '__main__':
    main()
