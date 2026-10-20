"""Re-extract guard poses using the extraction script's logic.

Looking at the extraction_review.png, I can see the guard poses are laid out.
Let me use the original extraction script's approach but manually specify bounds.
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

# Based on the extraction script coordinates:
# guard: (0,264,505,417) - 6 guard poses
# guard_advance: (508,264,1024,417) - 6 frames
# guard_retreat: (1026,264,1536,417) - 6 frames

# Let me inspect the guard region visually and estimate tighter bounds
# The guard region is 505px wide with 6 poses = ~84px per pose
# Starting from x=0, poses are at approximately:
# 0-84, 84-168, 168-252, 252-336, 336-420, 420-505

# Guard entry - use poses that show progression
# Looking at the extraction, I need to pick 3 that show: idle -> raising -> raised
guard_indices = [0, 2, 4]  # Use 0, 2, 4 for clearer progression

# Guard advance - all 6 frames
guard_advance_start_x = 508
guard_advance_width = 516
guard_advance_frame_width = guard_advance_width // 6  # ~86px

# Guard retreat - all 6 frames
guard_retreat_start_x = 1026
guard_retreat_width = 510
guard_retreat_frame_width = guard_retreat_width // 6  # ~85px

def extract_frame(region_x, frame_index, frame_width, output_name):
    """Extract a single frame from a region."""
    x = region_x + frame_index * frame_width
    y = 264
    h = 153

    # Add some padding to avoid cutting off edges
    padding = 5
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = frame_width + padding * 2
    h = h + padding * 2

    crop = sheet.crop((x, y, x + w, y + h))

    # Alpha-trim
    arr = np.array(crop)
    alpha = arr[:,:,3]
    ys, xs = np.where(alpha >= 32)

    if len(xs) > 0:
        x_min, x_max = int(xs.min()), int(xs.max()) + 1
        y_min, y_max = int(ys.min()), int(ys.max()) + 1

        cleaned = crop.crop((x_min, y_min, x_max, y_max))
    else:
        cleaned = crop

    cleaned.save(CLEAN / output_name)
    print(f"Extracted {output_name}: {crop.size} -> {cleaned.size}")

# Extract guard entry poses (from guard region)
for i, idx in enumerate(guard_indices):
    x = idx * 84
    extract_frame(0, idx, 84, f'guard_entry_{i}.png')

# Extract guard advance frames
for i in range(6):
    extract_frame(guard_advance_start_x, i, guard_advance_frame_width, f'guard_advance_{i}.png')

# Extract guard retreat frames
for i in range(6):
    extract_frame(guard_retreat_start_x, i, guard_retreat_frame_width, f'guard_retreat_{i}.png')

print(f"\nRe-extracted guard poses to {CLEAN}")
