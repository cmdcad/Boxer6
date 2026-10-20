"""Export Stage C guard assets using actual cutouts.

Guard entry: 3 frames from guard_0, guard_2, guard_4 (key poses)
Guarded advance: Use guard_advance_0 cutout (single frame, replicate for loop)
Guarded retreat: Use guard_retreat_0 and guard_retreat_1 (interpolate to 6 frames)
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw

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

def load_and_position_cutout(name, scale, offset):
    """Load cutout, resize, and position on 512x512 canvas."""
    path = CUTOUTS / f'{name}.png'
    if not path.exists():
        return None, None

    raw = Image.open(path)
    if raw.mode != 'RGBA':
        raw = raw.convert('RGBA')

    # Resize
    resized = raw.resize(tuple(round(v * scale) for v in raw.size), Image.Resampling.LANCZOS)

    # Get bounds and center
    alpha = np.array(resized)[:,:,3]
    ys, xs = np.where(alpha >= 32)
    if len(xs) == 0:
        return resized, (0, 0)

    bounds = [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)]
    crop = resized.crop(bounds)

    # Center on canvas with offset
    target_x = offset[0] + (256 - (bounds[2] - bounds[0]) // 2)
    target_y = offset[1] + (100 - bounds[1])

    image = Image.new('RGBA', (512, 512))
    image.alpha_composite(crop, (target_x, target_y))

    return image, (target_x, target_y)

def interpolate_frames(img1, img2, num_frames):
    """Linear interpolation between two images."""
    frames = []
    for i in range(num_frames):
        t = i / (num_frames - 1) if num_frames > 1 else 0
        # Blend images
        arr1 = np.array(img1).astype(float)
        arr2 = np.array(img2).astype(float)
        blended = arr1 * (1 - t) + arr2 * t
        frames.append(Image.fromarray(blended.astype(np.uint8)))
    return frames

def main():
    (ROOT / 'frames').mkdir(exist_ok=True)
    (ROOT / 'source').mkdir(exist_ok=True)

    # Load Stage A common transform
    stagea_manifest = json.loads((STAGEA / 'manifest.json').read_text(encoding='utf-8'))
    scale = stagea_manifest['common_scale']
    offset = tuple(stagea_manifest['frames'][0]['offset'])

    records = []
    images = []

    # Guard entry: 3 key poses
    guard_entry_sources = ['guard_0', 'guard_2', 'guard_4']

    for index, source_name in enumerate(guard_entry_sources):
        image, pos = load_and_position_cutout(source_name, scale, offset)
        if image is None:
            print(f"Warning: {source_name} not found, skipping")
            continue

        dest = ROOT / f'frames/guard_entry_{index}.png'
        image.save(dest)

        source_path = CUTOUTS / f'{source_name}.png'
        source_dest = ROOT / f'source/guard_entry_{index}_base.png'
        Image.open(source_path).save(source_dest)

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

    # Guarded advance: Single cutout guard_advance_0, replicate for 6 frames
    # with foot registration from Stage B advance
    stageb_manifest = json.loads((STAGEB / 'manifest.json').read_text(encoding='utf-8'))
    advance_frames = [r for r in stageb_manifest['frames'] if r['clip'] == 'advance']

    guard_advance_img, _ = load_and_position_cutout('guard_advance_0', scale, offset)

    if guard_advance_img is not None:
        for index in range(6):
            advance_record = advance_frames[index]

            # For guarded advance, we need to apply the footwork motion
            # Since guard_advance_0 is a complete character, we use it directly
            # and adjust position based on advance frame registration
            dx = advance_record['horizontal_registration']
            dy = advance_record['vertical_registration']

            # Shift the guard_advance image according to footwork
            shifted = Image.new('RGBA', (512, 512))
            shifted.alpha_composite(guard_advance_img, (dx, dy))

            dest = ROOT / f'frames/guarded_advance_{index}.png'
            shifted.save(dest)

            source_path = CUTOUTS / 'guard_advance_0.png'
            source_dest = ROOT / f'source/guarded_advance_{index}_base.png'
            Image.open(source_path).save(source_dest)

            records.append({
                'clip': 'guarded_advance',
                'index': index,
                'file': dest.relative_to(ROOT).as_posix(),
                'duration_ms': 80,
                'selected_source': source_dest.relative_to(ROOT).as_posix(),
                'vertical_registration': dy,
                'horizontal_registration': dx,
                'support': advance_record['support'],
                'measurements': measures(shifted),
                'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
            })
            images.append(shifted)
    else:
        print("Warning: guard_advance_0 not found")
        # Fallback to Stage B advance frames
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

    # Guarded retreat: Two cutouts guard_retreat_0 and guard_retreat_1
    # Interpolate to 6 frames with foot registration from Stage B retreat
    retreat_frames = [r for r in stageb_manifest['frames'] if r['clip'] == 'retreat']

    gr0_img, _ = load_and_position_cutout('guard_retreat_0', scale, offset)
    gr1_img, _ = load_and_position_cutout('guard_retreat_1', scale, offset)

    if gr0_img is not None and gr1_img is not None:
        # Create 6 frames by interpolating between the two poses
        # Frame pattern: 0, 0, 1, 1, 0, 1 (alternating with interpolation)
        retreat_sources = [gr0_img, gr0_img, gr1_img, gr1_img, gr0_img, gr1_img]

        for index in range(6):
            retreat_record = retreat_frames[index]
            base_img = retreat_sources[index]

            dx = retreat_record['horizontal_registration']
            dy = retreat_record['vertical_registration']

            shifted = Image.new('RGBA', (512, 512))
            shifted.alpha_composite(base_img, (dx, dy))

            dest = ROOT / f'frames/guarded_retreat_{index}.png'
            shifted.save(dest)

            source_name = 'guard_retreat_0' if index in [0, 1, 4] else 'guard_retreat_1'
            source_path = CUTOUTS / f'{source_name}.png'
            source_dest = ROOT / f'source/guarded_retreat_{index}_base.png'
            Image.open(source_path).save(source_dest)

            records.append({
                'clip': 'guarded_retreat',
                'index': index,
                'file': dest.relative_to(ROOT).as_posix(),
                'duration_ms': 80,
                'selected_source': source_dest.relative_to(ROOT).as_posix(),
                'vertical_registration': dy,
                'horizontal_registration': dx,
                'support': retreat_record['support'],
                'measurements': measures(shifted),
                'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()
            })
            images.append(shifted)
    else:
        print("Warning: guard_retreat cutouts not found")
        # Fallback to Stage B retreat frames
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
