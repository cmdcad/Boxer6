"""Extract punch poses by slicing the sprite strips first, then removing checkerboard.

The Jab and Cross regions are sprite strips with 6 poses each in a row.
We slice them first, then clean each individual frame.
"""
from pathlib import Path
import numpy as np
from PIL import Image
from collections import deque

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'uploaded_sprites_original.png'
CUTOUTS = ROOT / 'cutouts'

CUTOUTS.mkdir(exist_ok=True)

sheet = Image.open(SOURCE).convert('RGBA')

def remove_checkerboard(img):
    """Remove checkerboard background."""
    arr = np.array(img)
    rgb = arr[:,:,:3]

    # Define checkerboard colors
    light_check = np.array([220, 220, 220])
    dark_check = np.array([180, 180, 180])

    # Create masks
    light_mask = np.sum(np.abs(rgb - light_check), axis=2) < 30
    dark_mask = np.sum(np.abs(rgb - dark_check), axis=2) < 30
    grey_mask = (rgb.max(2) - rgb.min(2) <= 20) & (rgb.min(2) >= 160)

    background_mask = light_mask | dark_mask | grey_mask
    arr[background_mask, 3] = 0

    return Image.fromarray(arr)

def tighten_bounds(img):
    """Crop to actual content bounds."""
    arr = np.array(img)
    alpha = arr[:,:,3]
    ys, xs = np.where(alpha >= 64)

    if len(xs) == 0:
        return img

    left, top = int(xs.min()), int(ys.min())
    right, bottom = int(xs.max()) + 1, int(ys.max()) + 1

    # Add small padding
    padding = 3
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(img.width, right + padding)
    bottom = min(img.height, bottom + padding)

    return img.crop((left, top, right, bottom))

# Jab: 6 frames in a 506px strip -> ~84px each
print("Extracting Jab frames:")
jab_region = sheet.crop((0, 489, 506, 645))
jab_frame_width = jab_region.width // 6

for i in range(6):
    left = i * jab_frame_width
    right = left + jab_frame_width
    frame = jab_region.crop((left, 0, right, jab_region.height))

    # Remove checkerboard
    frame_clean = remove_checkerboard(frame)

    # Tighten bounds
    frame_tight = tighten_bounds(frame_clean)

    frame_tight.save(CUTOUTS / f'jab_{i}.png')
    print(f'  jab_{i}.png: {frame_tight.size}')

# Cross: 6 frames in a 515px strip -> ~85px each
print("\nExtracting Cross frames:")
cross_region = sheet.crop((510, 489, 1025, 645))
cross_frame_width = cross_region.width // 6

for i in range(6):
    left = i * cross_frame_width
    right = left + cross_frame_width
    frame = cross_region.crop((left, 0, right, cross_region.height))

    frame_clean = remove_checkerboard(frame)
    frame_tight = tighten_bounds(frame_clean)

    frame_tight.save(CUTOUTS / f'cross_{i}.png')
    print(f'  cross_{i}.png: {frame_tight.size}')

# Recovery: extract with component analysis
print("\nExtracting Recovery frames:")
recovery_region = sheet.crop((379, 709, 738, 855))
recovery_clean = remove_checkerboard(recovery_region)

# Use component analysis for recovery
arr = np.array(recovery_clean)
alpha = arr[:,:,3]
h, w = alpha.shape

seen = np.zeros((h, w), dtype=bool)
components = []

for y in range(h):
    for x in range(w):
        if alpha[y, x] >= 64 and not seen[y, x]:
            q = deque([(y, x)])
            seen[y, x] = True
            points = []

            while q:
                cy, cx = q.popleft()
                points.append((cy, cx))

                for yy, xx in [(cy-1, cx), (cy+1, cx), (cy, cx-1), (cy, cx+1)]:
                    if 0 <= yy < h and 0 <= xx < w and alpha[yy, xx] >= 64 and not seen[yy, xx]:
                        seen[yy, xx] = True
                        q.append((yy, xx))

            if len(points) > 200:
                components.append(points)

components.sort(key=lambda pts: min(x for y, x in pts))

for i, points in enumerate(components[:2]):
    yy, xx = np.array(points).T
    left, top = int(xx.min()), int(yy.min())
    right, bottom = int(xx.max()) + 1, int(yy.max()) + 1

    padding = 3
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(w, right + padding)
    bottom = min(h, bottom + padding)

    pose_img = recovery_clean.crop((left, top, right, bottom))
    pose_img.save(CUTOUTS / f'recovery_{i}.png')
    print(f'  recovery_{i}.png: {pose_img.size}')

# Rename recovery files
(CUTOUTS / 'recovery_0.png').rename(CUTOUTS / 'jab_recovery.png')
(CUTOUTS / 'recovery_1.png').rename(CUTOUTS / 'cross_recovery.png')
print("\nRenamed recovery_0.png -> jab_recovery.png")
print("Renamed recovery_1.png -> cross_recovery.png")

print(f"\nExtraction complete with checkerboard removal.")
