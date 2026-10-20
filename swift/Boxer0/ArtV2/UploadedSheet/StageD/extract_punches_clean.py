"""Extract punch and recovery poses with proper checkerboard removal.

The source has a baked checkerboard pattern. We need to:
1. Detect and remove the checkerboard background
2. Extract individual poses with tight bounds
3. Avoid neighboring character fragments
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
    """Remove checkerboard background by detecting the pattern."""
    # Convert to numpy
    arr = np.array(img)

    # The checkerboard alternates between light and dark squares
    # We can detect it by looking at the pattern
    # A simple approach: if a pixel is close to the checkerboard colors, make it transparent

    # Get RGB channels
    rgb = arr[:,:,:3]

    # Define checkerboard colors (light gray and dark gray)
    light_check = np.array([220, 220, 220])
    dark_check = np.array([180, 180, 180])

    # Create mask for pixels close to checkerboard colors
    light_mask = np.sum(np.abs(rgb - light_check), axis=2) < 30
    dark_mask = np.sum(np.abs(rgb - dark_check), axis=2) < 30

    # Combine masks
    check_mask = light_mask | dark_mask

    # Also detect pure white/grey
    grey_mask = (rgb.max(2) - rgb.min(2) <= 20) & (rgb.min(2) >= 160)

    # Combine all background masks
    background_mask = check_mask | grey_mask

    # Set alpha to 0 for background pixels
    arr[background_mask, 3] = 0

    return Image.fromarray(arr)

def extract_poses_with_bounds(img, output_prefix, expected_count=None):
    """Extract individual poses using component analysis with proper bounds."""
    img_rgba = remove_checkerboard(img)

    arr = np.array(img_rgba)
    alpha = arr[:,:,3]

    h, w = alpha.shape

    # Find connected components
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

                if len(points) > 500:  # Minimum size filter
                    components.append(points)

    # Sort by x position (left to right)
    components.sort(key=lambda pts: min(x for y, x in pts))

    if expected_count and len(components) != expected_count:
        print(f"  Warning: Found {len(components)} components, expected {expected_count}")

    for i, points in enumerate(components):
        yy, xx = np.array(points).T
        left, top = int(xx.min()), int(yy.min())
        right, bottom = int(xx.max()) + 1, int(yy.max()) + 1

        # Skip if too small
        if bottom - top < 30 or right - left < 30:
            continue

        # Crop with some padding
        padding = 2
        left = max(0, left - padding)
        top = max(0, top - padding)
        right = min(w, right + padding)
        bottom = min(h, bottom + padding)

        pose_img = img_rgba.crop((left, top, right, bottom))
        pose_img.save(CUTOUTS / f'{output_prefix}_{i}.png')
        print(f'  {output_prefix}_{i}.png: {pose_img.size}')

    return len(components)

# Extract Jab
print("Extracting Jab poses:")
jab_region = sheet.crop((0, 489, 506, 645))
jab_count = extract_poses_with_bounds(jab_region, 'jab', expected_count=6)

# Extract Cross
print("\nExtracting Cross poses:")
cross_region = sheet.crop((510, 489, 1025, 645))
cross_count = extract_poses_with_bounds(cross_region, 'cross', expected_count=6)

# Extract Recovery
print("\nExtracting Recovery poses:")
recovery_region = sheet.crop((379, 709, 738, 855))
recovery_count = extract_poses_with_bounds(recovery_region, 'recovery', expected_count=2)

# Rename recovery files to specific names
if recovery_count >= 2:
    (CUTOUTS / 'recovery_0.png').rename(CUTOUTS / 'jab_recovery.png')
    (CUTOUTS / 'recovery_1.png').rename(CUTOUTS / 'cross_recovery.png')
    print("\nRenamed recovery_0.png -> jab_recovery.png")
    print("Renamed recovery_1.png -> cross_recovery.png")

print(f"\nExtraction complete. Check cutouts in {CUTOUTS}")
