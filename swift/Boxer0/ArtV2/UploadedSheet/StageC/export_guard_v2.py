"""Export Stage C guard assets with proper compositing.

Guard entry: Start from Stage A idle, transition guard arms up through 3 poses.
Guarded movement: Composite guard arm positions over Stage B footwork frames.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageChops

ROOT = Path(__file__).resolve().parent
CUTOUTS = ROOT.parent / 'cutouts'
STAGEA = ROOT.parent / 'StageA'
STAGEB = ROOT.parent / 'StageB'

def measures(image):
    """Measure foot positions and bounding box."""
    alpha = np.array(image)[:,:,3]
    ys, xs = np.where(alpha >= 32)
    if len(xs) == 0:
        return {'bounds': [0, 0, 0, 0], 'rear': {'sole_y': 448, 'sole_x': 207.0, 'ground_gap': 0},
                'lead': {'sole_y': 448, 'sole_x': 309.5, 'ground_gap': 0}}
    result = {'bounds': [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)]}
    for name, left, right in [('rear', 0, 256), ('lead', 256, 512)]:
        fy, fx = np.where(alpha[340:, left:right] >= 32)
        if len(fy) == 0:
            result[name] = {'sole_y': 448, 'sole_x': (left + right) / 2, 'ground_gap': 0}
            continue
        bottom = int(fy.max() + 340)
        by, bx = np.where(alpha[bottom-2:bottom+1, left:right] >= 32)
        if len(bx) == 0:
            result[name] = {'sole_y': 448, 'sole_x': (left + right) / 2, 'ground_gap': 0}
        else:
            result[name] = {'sole_y': bottom, 'sole_x': float((bx.min() + bx.max()) / 2 + left),
                           'ground_gap': 448 - bottom}
    return result

def load_cutout(name):
    """Load a cutout image."""
    path = CUTOUTS / f'{name}.png'
    if not path.exists():
        return None
    raw = Image.open(path)
    if raw.mode != 'RGBA':
        raw = raw.convert('RGBA')
    return raw

def composite_guard_over_footwork(footwork_img, guard_img, scale, offset):
    """Composite guard pose over footwork frame."""
    # Resize guard to match scale
    guard_resized = guard_img.resize(tuple(round(v * scale) for v in guard_img.size), Image.Resampling.LANCZOS)

    # Get bounds of guard to center it
    guard_alpha = np.array(guard_resized)[:,:,3]
    guard_ys, guard_xs = np.where(guard_alpha >= 32)
    if len(guard_xs) == 0:
        return footwork_img

    guard_bounds = [int(guard_xs.min()), int(guard_ys.min()), int(guard_xs.max()+1), int(guard_ys.max()+1)]
    guard_width = guard_bounds[2] - guard_bounds[0]
    guard_height = guard_bounds[3] - guard_bounds[1]

    # Extract just the guard character from its canvas
    guard_crop = guard_resized.crop(guard_bounds)

    # Position guard over footwork - align torso roughly to center
    target_x = offset[0] + (256 - guard_width // 2)
    target_y = offset[1] + (100 - guard_bounds[1])  # Align shoulders area

    result = Image.new('RGBA', (512, 512))
    result.alpha_composite(footwork_img, (0, 0))
    result.alpha_composite(guard_crop, (target_x, target_y))

    return result

def main():
    (ROOT / 'frames').mkdir(exist_ok=True)
    (ROOT / 'source').mkdir(exist_ok=True)

    # Load Stage A common transform
    stagea_manifest = json.loads((STAGEA / 'manifest.json').read_text(encoding='utf-8'))
    scale = stagea_manifest['common_scale']
    offset = tuple(stagea_manifest['frames'][0]['offset'])

    records = []
    images = []

    # Guard entry: Use the 3 best guard poses from cutouts
    # guard_0 (lower), guard_2 (mid), guard_4 (raised)
    guard_entry_sources = ['guard_0', 'guard_2', 'guard_4']

    for index, source_name in enumerate(guard_entry_sources):
        guard_raw = load_cutout(source_name)
        if guard_raw is None:
            print(f"Warning: {source_name} not found, skipping")
            continue

        # Resize and position on canvas
        guard_resized = guard_raw.resize(tuple(round(v * scale) for v in guard_raw.size), Image.Resampling.LANCZOS)

        # Get bounds
        guard_alpha = np.array(guard_resized)[:,:,3]
        guard_ys, guard_xs = np.where(guard_alpha >= 32)
        if len(guard_xs) > 0:
            guard_bounds = [int(guard_xs.min()), int(guard_ys.min()), int(guard_xs.max()+1), int(guard_ys.max()+1)]
            guard_crop = guard_resized.crop(guard_bounds)

            # Center on canvas
            target_x = offset[0] + (256 - (guard_bounds[2] - guard_bounds[0]) // 2)
            target_y = offset[1] + (100 - guard_bounds[1])

            image = Image.new('RGBA', (512, 512))
            image.alpha_composite(guard_crop, (target_x, target_y))
        else:
            image = guard_resized

        dest = ROOT / f'frames/guard_entry_{index}.png'
        image.save(dest)

        source_dest = ROOT / f'source/guard_entry_{index}_base.png'
        guard_raw.save(source_dest)

        records.append({
            'clip': 'guard_entry',
            'index': index,
            'file': dest.relative_to(ROOT).as_posix(),
            'duration_ms': 40,
            'selected_source': source_dest.relative_to(ROOT).as_posix(),
            'vertical_registration': 0,
            'horizontal_registration': 0,
            'measurements': measures(image),
            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
        })
        images.append(image)

    # Guarded advance: Composite guard_4 (raised guard) over each advance frame
    stageb_manifest = json.loads((STAGEB / 'manifest.json').read_text(encoding='utf-8'))
    advance_frames = [r for r in stageb_manifest['frames'] if r['clip'] == 'advance']
    guard_raised = load_cutout('guard_4')

    if guard_raised is not None:
        for index in range(6):
            advance_record = advance_frames[index]
            advance_path = STAGEB / advance_record['file']
            advance_base = Image.open(advance_path).convert('RGBA')

            # Composite guard over advance
            image = composite_guard_over_footwork(advance_base, guard_raised, scale, offset)

            dest = ROOT / f'frames/guarded_advance_{index}.png'
            image.save(dest)

            source_dest = ROOT / f'source/guarded_advance_{index}_base.png'
            guard_raised.save(source_dest)

            records.append({
                'clip': 'guarded_advance',
                'index': index,
                'file': dest.relative_to(ROOT).as_posix(),
                'duration_ms': 80,
                'selected_source': source_dest.relative_to(ROOT).as_posix(),
                'vertical_registration': advance_record['vertical_registration'],
                'horizontal_registration': advance_record['horizontal_registration'],
                'support': advance_record['support'],
                'measurements': measures(image),
                'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
            })
            images.append(image)
    else:
        print("Warning: guard_4 not found, using Stage B advance frames directly")
        for index in range(6):
            advance_record = advance_frames[index]
            advance_path = STAGEB / advance_record['file']
            advance_base = Image.open(advance_path).convert('RGBA')

            dest = ROOT / f'frames/guarded_advance_{index}.png'
            advance_base.save(dest)

            records.append({
                'clip': 'guarded_advance',
                'index': index,
                'file': dest.relative_to(ROOT).as_posix(),
                'duration_ms': 80,
                'selected_source': advance_record['selected_source'],
                'vertical_registration': advance_record['vertical_registration'],
                'horizontal_registration': advance_record['horizontal_registration'],
                'support': advance_record['support'],
                'measurements': measures(advance_base),
                'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
            })
            images.append(advance_base)

    # Guarded retreat: Composite guard_4 over each retreat frame
    retreat_frames = [r for r in stageb_manifest['frames'] if r['clip'] == 'retreat']

    if guard_raised is not None:
        for index in range(6):
            retreat_record = retreat_frames[index]
            retreat_path = STAGEB / retreat_record['file']
            retreat_base = Image.open(retreat_path).convert('RGBA')

            image = composite_guard_over_footwork(retreat_base, guard_raised, scale, offset)

            dest = ROOT / f'frames/guarded_retreat_{index}.png'
            image.save(dest)

            source_dest = ROOT / f'source/guarded_retreat_{index}_base.png'
            guard_raised.save(source_dest)

            records.append({
                'clip': 'guarded_retreat',
                'index': index,
                'file': dest.relative_to(ROOT).as_posix(),
                'duration_ms': 80,
                'selected_source': source_dest.relative_to(ROOT).as_posix(),
                'vertical_registration': retreat_record['vertical_registration'],
                'horizontal_registration': retreat_record['horizontal_registration'],
                'support': retreat_record['support'],
                'measurements': measures(image),
                'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
            })
            images.append(image)
    else:
        print("Warning: guard_4 not found, using Stage B retreat frames directly")
        for index in range(6):
            retreat_record = retreat_frames[index]
            retreat_path = STAGEB / retreat_record['file']
            retreat_base = Image.open(retreat_path).convert('RGBA')

            dest = ROOT / f'frames/guarded_retreat_{index}.png'
            retreat_base.save(dest)

            records.append({
                'clip': 'guarded_retreat',
                'index': index,
                'file': dest.relative_to(ROOT).as_posix(),
                'duration_ms': 80,
                'selected_source': retreat_record['selected_source'],
                'vertical_registration': retreat_record['vertical_registration'],
                'horizontal_registration': retreat_record['horizontal_registration'],
                'support': retreat_record['support'],
                'measurements': measures(retreat_base),
                'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
            })
            images.append(retreat_base)

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
            draw.text((x + 12, y + 520), f'{clip_name.replace("_", " ").title()} {i + 1}: {time_str}', fill=(25, 42, 60))
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
        'common_scale': scale,
        'common_offset': list(offset),
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
    print(f'Alignment sheet and preview GIFs saved to {ROOT}')

if __name__ == '__main__':
    main()
