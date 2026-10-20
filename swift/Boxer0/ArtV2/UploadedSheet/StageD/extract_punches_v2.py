"""Extract Jab, Cross, and Recovery poses from uploaded sheet.

Jab and Cross are sprite strips with multiple poses on one character.
Need to slice them horizontally to get individual frames.
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

# Based on the production plan:
# Jab: 6 frames at 50ms each = 300ms total
# Cross: 8 frames at 60ms each = 480ms total (6 illustrated + 2 created transitions)
# Recovery: separate poses for jab and cross

# Jab region is 506px wide, likely has ~6 poses -> ~84px per pose
jab_frames = 6
jab_frame_width = jab_crop.width // jab_frames

print(f"Jab region: {jab_crop.size}, frame width: {jab_frame_width}")
for i in range(jab_frames):
    left = i * jab_frame_width
    right = left + jab_frame_width
    frame = jab_crop.crop((left, 0, right, jab_crop.height))
    frame.save(CUTOUTS / f'jab_{i}.png')
    print(f"  jab_{i}.png: {frame.size}")

# Cross region is 515px wide, has 6 illustrated poses
# Need to extract 6, then create 2 transition frames
cross_illustrated = 6
cross_frame_width = cross_crop.width // cross_illustrated

print(f"\nCross region: {cross_crop.size}, frame width: {cross_frame_width}")
for i in range(cross_illustrated):
    left = i * cross_frame_width
    right = left + cross_frame_width
    frame = cross_crop.crop((left, 0, right, cross_crop.height))
    frame.save(CUTOUTS / f'cross_illustrated_{i}.png')
    print(f"  cross_illustrated_{i}.png: {frame.size}")

# Recovery region - extract all poses found
print(f"\nRecovery region: {recovery_crop.size}")
# Use component extraction for recovery since they're separate characters
rgb = np.array(recovery_crop.convert('RGB'))
h, w = rgb.shape[:2]

grey = (rgb.max(2).astype(int) - rgb.min(2).astype(int) <= 16) & (rgb.min(2) >= 155)

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

poses = components(~outside, min_size=200)

print(f"  Found {len(poses)} recovery poses")
for i, points in enumerate(poses):
    yy, xx = np.array(points).T
    left, top = int(xx.min()), int(yy.min())
    right, bottom = int(xx.max()) + 1, int(yy.max()) + 1

    if bottom - top < 30:
        continue

    alpha = np.zeros((h, w), dtype=np.uint8)
    alpha[yy, xx] = 255
    rgba = np.dstack([rgb, alpha])
    rgba[alpha == 0, :3] = 0

    pose_img = Image.fromarray(rgba).crop((left, top, right, bottom))
    pose_img.save(CUTOUTS / f'recovery_{i}.png')
    print(f"    recovery_{i}.png: {pose_img.size}")

print(f"\nAll cutouts saved to {CUTOUTS}")
