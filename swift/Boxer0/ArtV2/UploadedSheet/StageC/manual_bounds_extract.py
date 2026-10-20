"""Extract guard poses with manually tuned tight bounds.

Based on visual inspection of the sheet, specify exact bounds for each pose
to avoid neighboring pose fragments and cut-off limbs.
"""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'uploaded_sprites_original.png'
CLEAN = ROOT / 'clean_cutouts'

CLEAN.mkdir(exist_ok=True)

sheet = Image.open(SOURCE).convert('RGBA')

# Manually tuned bounds (x, y, width, height) for each pose
# These are conservative estimates to avoid fragments

# Guard row: y=264-417
# Guard poses at x=0-505 region
guard_entry_bounds = [
    (20, 275, 65, 135),  # guard_0 - idle pose
    (100, 275, 65, 135), # guard_1 - low raise
    (180, 275, 65, 135), # guard_2 - mid raise
    (260, 275, 65, 135), # guard_3 - high raise
    (340, 275, 68, 135), # guard_4 - fully raised
    (420, 275, 75, 135), # guard_5 - guard hold
]

# Guard advance: x=508-1024 region
guard_advance_bounds = [
    (525, 275, 75, 135),
    (605, 275, 75, 135),
    (685, 275, 75, 135),
    (765, 275, 75, 135),
    (845, 275, 75, 135),
    (925, 275, 75, 135),
]

# Guard retreat: x=1026-1536 region
guard_retreat_bounds = [
    (1040, 275, 72, 133),
    (1120, 275, 75, 133),
    (1200, 275, 75, 133),
    (1280, 275, 75, 133),
    (1360, 275, 75, 133),
    (1440, 275, 75, 133),
]

def extract(bounds, output_name):
    """Extract with given bounds."""
    x, y, w, h = bounds
    crop = sheet.crop((x, y, x + w, y + h))
    crop.save(CLEAN / output_name)
    print(f"Extracted {output_name}: {crop.size}")

# Extract guard entry (use 0, 2, 4 for progression)
extract(guard_entry_bounds[0], 'guard_entry_0.png')
extract(guard_entry_bounds[2], 'guard_entry_1.png')
extract(guard_entry_bounds[4], 'guard_entry_2.png')

# Extract guard advance
for i in range(6):
    extract(guard_advance_bounds[i], f'guard_advance_{i}.png')

# Extract guard retreat
for i in range(6):
    extract(guard_retreat_bounds[i], f'guard_retreat_{i}.png')

print(f"\nManually extracted guard poses to {CLEAN}")
