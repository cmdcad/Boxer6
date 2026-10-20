"""Re-extract guard poses with manual bounds to avoid fragments.

Based on the extraction coordinates:
- guard row: y=264 to 417 (height 153)
- guard: x=0 to 505 (width 505) - contains 6 guard poses
- guard_advance: x=508 to 1024 (width 516) - contains 6 frames
- guard_retreat: x=1026 to 1536 (width 510) - contains 6 frames

Manual bounds for each pose to avoid fragments:
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'uploaded_sprites_original.png'
CLEAN = ROOT / 'clean_cutouts'

CLEAN.mkdir(exist_ok=True)

# Load the uploaded sheet
sheet = Image.open(SOURCE).convert('RGBA')

# Guard row coordinates
guard_row_y = (264, 417)
guard_x = (0, 505)
guard_advance_x = (508, 1024)
guard_retreat_x = (1026, 1536)

# Manual bounds for each guard pose (x, y, width, height) on the full sheet
# Guard region: x=0-505, y=264-417
# These are spaced ~83px apart
guard_bounds = [
    # Guard entry poses (using guard_0, guard_2, guard_4 as the 3 key poses)
    (15, 270, 70, 140),  # guard_0
    (95, 270, 70, 140),  # guard_1
    (175, 270, 70, 140), # guard_2
    (255, 270, 70, 140), # guard_3
    (335, 270, 73, 140), # guard_4
    (415, 270, 80, 140), # guard_5
]

# Guard advance region: x=508-1024, y=264-417
guard_advance_bounds = [
    (518, 270, 80, 140),
    (600, 270, 80, 140),
    (682, 270, 80, 140),
    (764, 270, 80, 140),
    (846, 270, 80, 140),
    (928, 270, 80, 140),
]

# Guard retreat region: x=1026-1536, y=264-417
guard_retreat_bounds = [
    (1036, 270, 78, 138),
    (1118, 270, 80, 138),
    (1200, 270, 80, 138),
    (1282, 270, 80, 138),
    (1364, 270, 80, 138),
    (1446, 270, 80, 138),
]

def extract_and_clean(bounds, output_name):
    """Extract with given bounds and clean edges."""
    x, y, w, h = bounds
    crop = sheet.crop((x, y, x + w, y + h))

    # Alpha-trim to remove any remaining edge artifacts
    arr = np.array(crop)
    alpha = arr[:,:,3]
    ys, xs = np.where(alpha >= 32)

    if len(xs) > 0:
        x_min, x_max = int(xs.min()), int(xs.max()) + 1
        y_min, y_max = int(ys.min()), int(ys.max()) + 1

        # Small padding
        x_min = max(0, x_min - 2)
        y_min = max(0, y_min - 2)
        x_max = min(crop.width, x_max + 2)
        y_max = min(crop.height, y_max + 2)

        cleaned = crop.crop((x_min, y_min, x_max, y_max))
    else:
        cleaned = crop

    cleaned.save(CLEAN / output_name)
    print(f"Extracted {output_name}: {crop.size} -> {cleaned.size}")
    return cleaned

# Extract guard entry poses using 0, 1, 4 for better progression
# guard_0 = idle pose, guard_1 = mid-raise, guard_4 = fully raised
extract_and_clean(guard_bounds[0], 'guard_entry_0.png')
extract_and_clean(guard_bounds[1], 'guard_entry_1.png')
extract_and_clean(guard_bounds[4], 'guard_entry_2.png')

# Extract guard advance frames
for i in range(6):
    extract_and_clean(guard_advance_bounds[i], f'guard_advance_{i}.png')

# Extract guard retreat frames
for i in range(6):
    extract_and_clean(guard_retreat_bounds[i], f'guard_retreat_{i}.png')

print(f"\nRe-extracted guard poses to {CLEAN}")
