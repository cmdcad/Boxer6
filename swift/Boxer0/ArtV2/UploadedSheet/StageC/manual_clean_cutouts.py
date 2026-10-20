"""Manually clean guard cutouts based on visual inspection of artifacts.

The current cutouts have:
1. Neighboring pose fragments (need to crop tighter)
2. Cut-off boots/legs (need to adjust bounds)

Strategy: Use the existing cutouts as a starting point, then clean each one.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
CUTOUTS = ROOT.parent / 'cutouts'
CLEAN = ROOT / 'clean_cutouts'

CLEAN.mkdir(exist_ok=True)

def clean_cutout(path, output_path, trim_pixels=5):
    """Clean a cutout by trimming transparent edges and removing artifacts."""
    img = Image.open(path).convert('RGBA')
    arr = np.array(img)

    # Find alpha bounds
    alpha = arr[:,:,3]
    ys, xs = np.where(alpha >= 32)

    if len(xs) == 0:
        return

    x_min, x_max = int(xs.min()), int(xs.max()) + 1
    y_min, y_max = int(ys.min()), int(ys.max()) + 1

    # Add small padding for edge safety
    x_min = max(0, x_min - trim_pixels)
    y_min = max(0, y_min - trim_pixels)
    x_max = min(img.width, x_max + trim_pixels)
    y_max = min(img.height, y_max + trim_pixels)

    # Crop to bounds
    cropped = img.crop((x_min, y_min, x_max, y_max))

    # Save
    cropped.save(output_path)
    print(f"Cleaned {path.name}: {img.size} -> {cropped.size}")

# Clean guard entry poses
for i in [0, 2, 4]:  # guard_0, guard_2, guard_4
    path = CUTOUTS / f'guard_{i}.png'
    if path.exists():
        clean_cutout(path, CLEAN / f'guard_entry_{i//2}.png', trim_pixels=8)

# For guard_advance and guard_retreat strips, we need to slice then clean each frame
def clean_strip(path, num_frames, output_prefix):
    """Slice a strip and clean each frame."""
    strip = Image.open(path).convert('RGBA')
    frame_width = strip.width // num_frames

    for i in range(num_frames):
        left = i * frame_width
        right = left + frame_width
        frame = strip.crop((left, 0, right, strip.height))

        # Clean this frame
        arr = np.array(frame)
        alpha = arr[:,:,3]
        ys, xs = np.where(alpha >= 32)

        if len(xs) > 0:
            x_min, x_max = int(xs.min()), int(xs.max()) + 1
            y_min, y_max = int(ys.min()), int(ys.max()) + 1

            # Trim
            x_min = max(0, x_min - 8)
            y_min = max(0, y_min - 8)
            x_max = min(frame.width, x_max + 8)
            y_max = min(frame.height, y_max + 8)

            cleaned = frame.crop((x_min, y_min, x_max, y_max))
        else:
            cleaned = frame

        cleaned.save(CLEAN / f'{output_prefix}_{i}.png')
        print(f"Cleaned {output_prefix}_{i}.png: {frame.size} -> {cleaned.size}")

# Clean guard_advance strip
guard_advance_path = CUTOUTS / 'guard_advance_0.png'
if guard_advance_path.exists():
    clean_strip(guard_advance_path, 6, 'guard_advance')

# Clean guard_retreat strip
guard_retreat_path = CUTOUTS / 'guard_retreat_1.png'
if guard_retreat_path.exists():
    clean_strip(guard_retreat_path, 5, 'guard_retreat')

    # Also clean guard_retreat_0
    gr0_path = CUTOUTS / 'guard_retreat_0.png'
    if gr0_path.exists():
        clean_cutout(gr0_path, CLEAN / 'guard_retreat_0.png', trim_pixels=8)

print(f"\nClean cutouts saved to {CLEAN}")
