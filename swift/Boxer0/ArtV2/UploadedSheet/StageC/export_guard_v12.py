"""Export Stage C guard assets using cleaned cutouts.

Guard entry: 3 frames from clean guard_entry_0, guard_entry_1, guard_entry_2
Guarded advance: 6 frames from clean guard_advance_0-5
Guarded retreat: 6 frames from clean guard_retreat_0-5

Scale: 2.133x to match Stage A character height (~320px)
"""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
CLEAN = ROOT / 'clean_cutouts'
GUARD_SCALE = 2.133

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

    # Guard entry: 3 clean frames
    for index in range(3):
        path = CLEAN / f'guard_entry_{index}.png'
        if not path.exists():
            print(f"Warning: guard_entry_{index}.png not found, skipping")
            continue

        raw = Image.open(path).convert('RGBA')
        image, pos = scale_and_position(raw, GUARD_SCALE)

        dest = ROOT / f'frames/guard_entry_{index}.png'
        image.save(dest)

        source_dest = ROOT / f'source/guard_entry_{index}_base.png'
        shutil.copy(path, source_dest)

        meas = measures(image)

        records.append({
            'clip': 'guard_entry',
            'index': index,
            'file': dest.relative_to(ROOT).as_posix(),
            'duration_ms': 40,
            'selected_source': source_dest.relative_to(ROOT).as_posix(),
            'vertical_registration': pos['dy'],
            'horizontal_registration': pos['dx'],
            'scale_factor': GUARD_SCALE,
            'measurements': meas,
            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
        })
        images.append(image)

    # Guarded advance: 6 clean frames
    for index in range(6):
        path = CLEAN / f'guard_advance_{index}.png'
        if not path.exists():
            print(f"Warning: guard_advance_{index}.png not found, skipping")
            continue

        raw = Image.open(path).convert('RGBA')
        image, pos = scale_and_position(raw, GUARD_SCALE)

        dest = ROOT / f'frames/guarded_advance_{index}.png'
        image.save(dest)

        source_dest = ROOT / f'source/guarded_advance_{index}_base.png'
        shutil.copy(path, source_dest)

        meas = measures(image)

        records.append({
            'clip': 'guarded_advance',
            'index': index,
            'file': dest.relative_to(ROOT).as_posix(),
            'duration_ms': 80,
            'selected_source': source_dest.relative_to(ROOT).as_posix(),
            'scale_factor': GUARD_SCALE,
            'measurements': meas,
            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
        })
        images.append(image)

    # Guarded retreat: 6 clean frames
    for index in range(6):
        path = CLEAN / f'guard_retreat_{index}.png'
        if not path.exists():
            print(f"Warning: guard_retreat_{index}.png not found, skipping")
            continue

        raw = Image.open(path).convert('RGBA')
        image, pos = scale_and_position(raw, GUARD_SCALE)

        dest = ROOT / f'frames/guarded_retreat_{index}.png'
        image.save(dest)

        source_dest = ROOT / f'source/guarded_retreat_{index}_base.png'
        shutil.copy(path, source_dest)

        meas = measures(image)

        records.append({
            'clip': 'guarded_retreat',
            'index': index,
            'file': dest.relative_to(ROOT).as_posix(),
            'duration_ms': 80,
            'selected_source': source_dest.relative_to(ROOT).as_posix(),
            'scale_factor': GUARD_SCALE,
            'measurements': meas,
            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
        })
        images.append(image)

    # Generate preview sheet
    sheet = Image.new('RGBA', (512 * 6, 550 * 3), (232, 238, 244, 255))
    draw = ImageDraw.Draw(sheet)

    clip_start = 0
    for clip_name in ['guard_entry', 'guarded_advance', 'guarded_retreat']:
        clip_records = [r for r in records if r['clip'] == clip_name]
        for i, rec in enumerate(clip_records):
            x = i * 512
            y = clip_start * 550
            img = Image.open(ROOT / rec['file'])
            sheet.alpha_composite(img, (x, y))
            draw.line((x, y + 448, x + 511, y + 448), fill=(210, 90, 70))
            draw.line((x + 256, y + 430, x + 256, y + 465), fill=(70, 130, 200))
            time_str = f"{i * (40 if clip_name == 'guard_entry' else 80)} ms"
            meas = rec['measurements']
            foot_info = ""
            if meas['rear']['sole_y'] is not None:
                foot_info = f"R:{meas['rear']['sole_y']:.0f} L:{meas['lead']['sole_y']:.0f}"
            else:
                foot_info = "NO FEET"
            draw.text((x + 12, y + 520), f'{clip_name.replace("_", " ").title()} {i + 1}: {time_str} [{foot_info}]', fill=(25, 42, 60))
        clip_start += 1

    sheet.convert('RGB').save(ROOT / 'alignment_sheet.png')

    # Generate preview GIFs
    for clip_name in ['guard_entry', 'guarded_advance', 'guarded_retreat']:
        clip_images = [Image.open(ROOT / r['file']) for r in records if r['clip'] == clip_name]
        if clip_images:
            duration = 40 if clip_name == 'guard_entry' else 80
            clip_images[0].save(ROOT / f'{clip_name}_preview.png', save_all=True,
                               append_images=clip_images[1:], duration=duration, loop=0, disposal=0, blend=0)

    # Manifest
    manifest = {
        'canvas': [512, 512],
        'root': [256, 448],
        'baseline': 448,
        'facing': 'right',
        'scale_factor': GUARD_SCALE,
        'note': 'Using re-extracted clean cutouts without neighboring pose fragments',
        'integrated': False,
        'clips': {
            'guard_entry': {
                'frame_count': 3,
                'frame_duration_ms': 40,
                'entry_duration_ms': 120,
                'effective_at_ms': 120,
                'hold_final': True
            },
            'guarded_advance': {
                'frame_count': 6,
                'frame_duration_ms': 80,
                'loop_ms': 480,
                'movement_driven': True
            },
            'guarded_retreat': {
                'frame_count': 6,
                'frame_duration_ms': 80,
                'loop_ms': 480,
                'movement_driven': True
            }
        },
        'frames': records
    }

    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'Exported Stage C: 3 guard entry frames (120ms), 6 guarded advance (480ms), 6 guarded retreat (480ms).')
    print(f'Using clean cutouts without fragments. Alignment sheet saved to {ROOT}')

if __name__ == '__main__':
    main()
