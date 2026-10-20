"""Extract Jab, Cross, and Recovery poses from uploaded sheet.

Jab region: (0,489,506,645) - likely contains multiple jab poses
Cross region: (510,489,1025,645) - contains 6 illustrated poses, need to create 2 transitions for 8 total
Recovery region: (379,709,738,855) - contains recovery poses
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from collections import deque

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'uploaded_sprites_original.png'
CUTOUTS = ROOT / 'cutouts'

CUTOUTS.mkdir(exist_ok=True)

# Load the uploaded sheet
sheet = Image.open(SOURCE).convert('RGBA')

# Region coordinates from extract_sheet.py
jab_region = (0, 489, 506, 645)
cross_region = (510, 489, 1025, 645)
recovery_region = (379, 709, 738, 855)

# Extract full regions
jab_crop = sheet.crop(jab_region)
cross_crop = sheet.crop(cross_region)
recovery_crop = sheet.crop(recovery_region)

# Save region crops for inspection
jab_crop.save(CUTOUTS / 'jab_region.png')
cross_crop.save(CUTOUTS / 'cross_region.png')
recovery_crop.save(CUTOUTS / 'recovery_region.png')

print(f"Extracted regions:")
print(f"  Jab: {jab_crop.size}")
print(f"  Cross: {cross_crop.size}")
print(f"  Recovery: {recovery_crop.size}")

# Now extract individual poses using the extraction script's component logic
def components(mask, min_size=100):
    """Find connected components in mask."""
    h, w = mask.shape
    seen = np.zeros_like(mask)
    result = []

    for y in range(h):
        for x in range(w):
            if mask[y, x] and not seen[y, x]:
                q = deque([(y, x)])
                seen[y, x] = True
                points = []

                while q:
                    cy, cx = q.popleft()
                    points.append((cy, cx))

                    for yy, xx in [(cy-1, cx), (cy+1, cx), (cy, cx-1), (cy, cx+1)]:
                        if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not seen[yy, xx]:
                            seen[yy, xx] = True
                            q.append((yy, xx))

                if len(points) > min_size:
                    result.append(points)

    return sorted(result, key=lambda pts: min(x for y, x in pts))

def extract_poses_from_region(crop, output_prefix):
    """Extract individual poses from a region crop."""
    rgb = np.array(crop.convert('RGB'))
    h, w = rgb.shape[:2]

    # Create mask: light colors (high values) that aren't white
    grey = (rgb.max(2).astype(int) - rgb.min(2).astype(int) <= 16) & (rgb.min(2) >= 155)

    # Flood-fill from edges to find background
    outside = np.zeros((h, w), dtype=bool)
    q = deque()

    for y in range(h):
        for x in [0, w-1]:
            if grey[y, x]:
                outside[y, x] = True
                q.append((y, x))

    for x in range(w):
        for y in [0, h-1]:
            if grey[y, x] and not outside[y, x]:
                outside[y, x] = True
                q.append((y, x))

    while q:
        y, x = q.popleft()
        for yy, xx in [(y-1, x), (y+1, x), (y, x-1), (y, x+1)]:
            if 0 <= yy < h and 0 <= xx < w and grey[yy, xx] and not outside[yy, xx]:
                outside[yy, xx] = True
                q.append((yy, xx))

    # Find components (the actual character poses)
    poses = components(~outside, min_size=500)

    print(f"  Found {len(poses)} poses")

    for i, points in enumerate(poses):
        yy, xx = np.array(points).T
        left, top = int(xx.min()), int(yy.min())
        right, bottom = int(xx.max()) + 1, int(yy.max()) + 1

        if bottom - top < 30:
            continue

        # Create RGBA with alpha
        alpha = np.zeros((h, w), dtype=np.uint8)
        alpha[yy, xx] = 255
        rgba = np.dstack([rgb, alpha])
        rgba[alpha == 0, :3] = 0

        pose_img = Image.fromarray(rgba).crop((left, top, right, bottom))
        pose_img.save(CUTOUTS / f'{output_prefix}_{i}.png')
        print(f"    {output_prefix}_{i}.png: {pose_img.size}")

# Extract poses from each region
print("\nExtracting Jab poses:")
extract_poses_from_region(jab_crop, 'jab')

print("\nExtracting Cross poses:")
extract_poses_from_region(cross_crop, 'cross')

print("\nExtracting Recovery poses:")
extract_poses_from_region(recovery_crop, 'recovery')

print(f"\nAll cutouts saved to {CUTOUTS}")
