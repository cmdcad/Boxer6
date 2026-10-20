"""Clean guard cutouts by re-extracting from the uploaded sheet with better bounds.

The current cutouts have neighboring pose fragments and cut-off limbs.
We'll re-extract with tighter bounds and manual cleanup.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
CUTOUTS = ROOT.parent / 'cutouts'
SOURCE = ROOT.parent / 'uploaded_sprites_original.png'
CLEAN = ROOT / 'clean_cutouts'

CLEAN.mkdir(exist_ok=True)

# Load the uploaded sheet
sheet = Image.open(SOURCE).convert('RGBA')
sheet_np = np.array(sheet)

# Guard poses appear to be in a row - let me identify their approximate positions
# Based on the cutout sizes (75-86px wide, 150-152px tall), they're probably
# arranged horizontally on the sheet

# Manual extraction coordinates (will need adjustment based on visual inspection)
# These are estimated - need to check the actual sheet layout
guard_positions = [
    # [x, y, width, height] for each guard pose
    # These are placeholders - will need to be adjusted
]

# Since I can't see the exact coordinates, let me create a helper to find
# non-transparent regions that might be the guard poses

def find_regions(image_np, min_width=50, min_height=100, max_width=100, max_height=200):
    """Find connected regions in the image."""
    alpha = image_np[:,:,3]
    ys, xs = np.where(alpha >= 32)

    if len(xs) == 0:
        return []

    # Simple bounding box clustering
    regions = []
    # Sort by x coordinate
    points = sorted(zip(xs, ys))

    # Group points by x proximity
    current_group = []
    last_x = None

    for x, y in points:
        if last_x is None or x - last_x > 20:
            if current_group:
                xs_group = [p[0] for p in current_group]
                ys_group = [p[1] for p in current_group]
                regions.append({
                    'x': min(xs_group),
                    'y': min(ys_group),
                    'w': max(xs_group) - min(xs_group) + 1,
                    'h': max(ys_group) - min(ys_group) + 1
                })
            current_group = [(x, y)]
        else:
            current_group.append((x, y))
        last_x = x

    if current_group:
        xs_group = [p[0] for p in current_group]
        ys_group = [p[1] for p in current_group]
        regions.append({
            'x': min(xs_group),
            'y': min(ys_group),
            'w': max(xs_group) - min(xs_group) + 1,
            'h': max(ys_group) - min(ys_group) + 1
        })

    # Filter by size
    filtered = [r for r in regions if min_width <= r['w'] <= max_width and min_height <= r['h'] <= max_height]

    return filtered

# Find guard regions
regions = find_regions(sheet_np, min_width=50, min_height=100, max_width=120, max_height=200)

print(f"Found {len(regions)} potential guard regions:")
for i, r in enumerate(regions):
    print(f"  Region {i}: x={r['x']}, y={r['y']}, w={r['w']}, h={r['h']}")

# Extract and save
for i, r in enumerate(regions[:6]):  # Take first 6 regions
    crop = sheet.crop((r['x'], r['y'], r['x'] + r['w'], r['y'] + r['h']))
    crop.save(CLEAN / f'guard_{i}.png')
    print(f"Saved guard_{i}.png")

print(f"Clean cutouts saved to {CLEAN}")
