"""Aggressively clean cutouts by removing small disconnected fragments.

Remove:
1. Small alpha fragments (likely from neighboring poses)
2. Expand bounds to ensure no cut-off limbs
"""
from pathlib import Path
import shutil
import numpy as np
from PIL import Image, ImageDraw
from collections import deque

ROOT = Path(__file__).resolve().parent
CUTOUTS = ROOT.parent / 'cutouts'
CLEAN = ROOT / 'clean_cutouts'

CLEAN.mkdir(exist_ok=True)

def find_components(mask, min_size=100):
    """Find connected components in mask."""
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    components = []

    for y in range(h):
        for x in range(w):
            if mask[y, x] and not seen[y, x]:
                # BFS to find component
                q = deque([(y, x)])
                seen[y, x] = True
                points = []

                while q:
                    cy, cx = q.popleft()
                    points.append((cy, cx))

                    for ny, nx in [(cy-1, cx), (cy+1, cx), (cy, cx-1), (cy, cx+1)]:
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            q.append((ny, nx))

                if len(points) >= min_size:
                    components.append(points)

    return components

def clean_image(img_path, output_path):
    """Clean an image by removing small fragments."""
    img = Image.open(img_path).convert('RGBA')
    arr = np.array(img)

    # Get alpha mask
    alpha = arr[:,:,3] >= 32

    # Find all components
    components = find_components(alpha, min_size=50)

    if not components:
        print(f"No components found in {img_path.name}")
        img.save(output_path)
        return

    # Keep only the largest component (the main character)
    components.sort(key=len, reverse=True)
    main_component = components[0]

    # Create mask with only main component
    clean_mask = np.zeros_like(alpha, dtype=bool)
    for y, x in main_component:
        clean_mask[y, x] = True

    # Apply mask
    cleaned_arr = arr.copy()
    cleaned_arr[~clean_mask, 3] = 0  # Set alpha to 0 for removed pixels

    # Crop to bounds of main component
    ys, xs = np.where(clean_mask)
    if len(xs) > 0:
        y_min, y_max = int(ys.min()), int(ys.max()) + 1
        x_min, x_max = int(xs.min()), int(xs.max()) + 1

        # Add small padding
        padding = 3
        y_min = max(0, y_min - padding)
        y_max = min(img.height, y_max + padding)
        x_min = max(0, x_min - padding)
        x_max = min(img.width, x_max + padding)

        cleaned_img = Image.fromarray(cleaned_arr).crop((x_min, y_min, x_max, y_max))
    else:
        cleaned_img = Image.fromarray(cleaned_arr)

    cleaned_img.save(output_path)
    print(f"Cleaned {img_path.name}: {img.size} -> {cleaned_img.size}, removed {len(components)-1} fragments")

# Clean guard entry poses
for i in range(3):
    # Use guard_0, guard_2, guard_4 from original cutouts
    idx = [0, 2, 4][i]
    path = CUTOUTS / f'guard_{idx}.png'
    if path.exists():
        clean_image(path, CLEAN / f'guard_entry_{i}.png')

# Clean guard advance frames
for i in range(6):
    # The guard_advance_0 is a strip, need to slice first
    strip_path = CUTOUTS / 'guard_advance_0.png'
    if strip_path.exists():
        strip = Image.open(strip_path).convert('RGBA')
        frame_width = strip.width // 6
        frame = strip.crop((i * frame_width, 0, (i + 1) * frame_width, strip.height))

        # Save temp, clean, then save final
        temp_path = CLEAN / f'temp_ga_{i}.png'
        frame.save(temp_path)
        clean_image(temp_path, CLEAN / f'guard_advance_{i}.png')
        temp_path.unlink()

# Clean guard retreat frames
# guard_retreat_1 is a strip
strip_path = CUTOUTS / 'guard_retreat_1.png'
if strip_path.exists():
    strip = Image.open(strip_path).convert('RGBA')
    frame_width = strip.width // 5
    for i in range(5):
        frame = strip.crop((i * frame_width, 0, (i + 1) * frame_width, strip.height))
        temp_path = CLEAN / f'temp_gr_{i}.png'
        frame.save(temp_path)
        clean_image(temp_path, CLEAN / f'guard_retreat_{i}.png')
        temp_path.unlink()

# Also clean guard_retreat_0
gr0_path = CUTOUTS / 'guard_retreat_0.png'
if gr0_path.exists():
    clean_image(gr0_path, CLEAN / 'guard_retreat_0.png')

# Pad retreat to 6 frames by duplicating last
last = CLEAN / 'guard_retreat_4.png'
if last.exists():
    shutil.copy(last, CLEAN / 'guard_retreat_5.png')

print(f"\nAggressively cleaned cutouts saved to {CLEAN}")
