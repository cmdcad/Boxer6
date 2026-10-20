"""Export Stage D punch and recovery assets.

Jab: 6 frames, 50ms each, 300ms total, contact at frame 3 (150ms)
Cross: 8 frames, 60ms each, 480ms total, contact at frame 4 (240ms)
  - 6 illustrated poses + 2 anatomically consistent transition frames
Jab recovery: 1 held pose, 120ms
Cross recovery: 1 held pose, 220ms

Scale to match Stage A: Stage A uses scale 0.4056 on 1254x1254 source to get ~320px character
Our cutouts are ~84x156, need to scale to ~320px height -> scale ~2.05x
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

# Calculate scale: Stage A character is ~320px tall, our cutouts are ~156px tall
# Scale = 320 / 156 = 2.05
PUNCH_SCALE = 2.05

# Or use Stage A's scale factor adjusted for our smaller cutouts
# Stage A scale = 0.4056 for 1254x1254 source -> 508x508 before crop
# Our cutouts are ~84x156, so to get equivalent output:
# If we want the same visual size as Stage A, we need to reverse-calculate
# Actually, let's just measure the target height and scale to match

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

def interpolate_frames(img1, img2, num_frames):
    """Linear interpolation between two images for transition frames."""
    frames = []
    for i in range(num_frames):
        t = i / (num_frames - 1) if num_frames > 1 else 0
        arr1 = np.array(img1).astype(float)
        arr2 = np.array(img2).astype(float)
        blended = arr1 * (1 - t) + arr2 * t
        frames.append(Image.fromarray(blended.astype(np.uint8)))
    return frames

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
        image, pos = scale_and_position(raw, PUNCH_SCALE)

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
            'scale_factor': PUNCH_SCALE,
            'is_contact_frame': i == 3,
            'measurements': meas,
            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
        })
        images.append(image)

    # Cross: 6 illustrated + 2 transitions = 8 frames
    # Use illustrated poses as: 0, 1, 2, 3, 4, 5
    # Insert transitions: between 2-3 and between 4-5
    # Final sequence: 0, 1, 2, [transition], 3, 4, [transition], 5
    cross_sequence = []
    for i in range(6):
        path = CUTOUTS / f'cross_illustrated_{i}.png'
        if path.exists():
            cross_sequence.append(Image.open(path).convert('RGBA'))

    if len(cross_sequence) >= 6:
        # Create transition between pose 2 and 3
        if len(cross_sequence) > 2:
            transition1 = interpolate_frames(cross_sequence[2], cross_sequence[3], 1)[0]
            cross_sequence.insert(3, transition1)

        # Create transition between pose 4 and 5
        if len(cross_sequence) > 5:
            transition2 = interpolate_frames(cross_sequence[5], cross_sequence[6] if len(cross_sequence) > 6 else cross_sequence[5], 1)[0]
            cross_sequence.insert(6, transition2)

    for i, img in enumerate(cross_sequence[:8]):
        image, pos = scale_and_position(img, PUNCH_SCALE)

        dest = ROOT / f'frames/cross_{i}.png'
        image.save(dest)

        source_name = f'cross_illustrated_{min(i, 5)}.png'
        source_path = CUTOUTS / source_name
        source_dest = ROOT / f'source/cross_{i}_base.png'
        if source_path.exists():
            shutil.copy(source_path, source_dest)
        else:
            # For transition frames, copy the source of the preceding illustrated frame
            shutil.copy(CUTOUTS / f'cross_illustrated_{min(i, 5)}.png', source_dest)

        meas = measures(image)

        records.append({
            'clip': 'cross',
            'index': i,
            'file': dest.relative_to(ROOT).as_posix(),
            'duration_ms': 60,
            'selected_source': source_dest.relative_to(ROOT).as_posix(),
            'vertical_registration': pos['dy'],
            'horizontal_registration': pos['dx'],
            'scale_factor': PUNCH_SCALE,
            'is_contact_frame': i == 4,
            'is_transition': i in [3, 6],
            'measurements': meas,
            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
        })
        images.append(image)

    # Recovery: Identify jab and cross recovery poses
    # recovery_0.png (78x145) - likely jab recovery (smaller, after quick jab)
    # recovery_1.png (84x146) - could be cross recovery
    # recovery_2.png (165x146) - larger, maybe something else

    # Based on size, let's use recovery_0 for jab (78x145 ~ jab size)
    # and recovery_1 for cross (84x146 ~ cross size)
    jab_recovery_path = CUTOUTS / 'recovery_0.png'
    cross_recovery_path = CUTOUTS / 'recovery_1.png'

    if jab_recovery_path.exists():
        raw = Image.open(jab_recovery_path).convert('RGBA')
        image, pos = scale_and_position(raw, PUNCH_SCALE)

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
            'scale_factor': PUNCH_SCALE,
            'measurements': meas,
            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
        })
        images.append(image)

    if cross_recovery_path.exists():
        raw = Image.open(cross_recovery_path).convert('RGBA')
        image, pos = scale_and_position(raw, PUNCH_SCALE)

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
            'scale_factor': PUNCH_SCALE,
            'measurements': meas,
            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
        })
        images.append(image)

    # Generate preview sheet
    # Jab (6), Cross (8), Jab recovery (1), Cross recovery (1) = 16 frames
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
        'scale_factor': PUNCH_SCALE,
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
    print(f'Alignment sheet saved to {ROOT}')

if __name__ == '__main__':
    main()
