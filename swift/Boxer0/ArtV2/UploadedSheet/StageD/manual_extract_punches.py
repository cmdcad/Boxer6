"""Manually extract punch and recovery poses with tight bounds to avoid clipping and neighboring fragments.

Based on Stage C's manual_bounds_extract.py approach - specify exact coordinates for each pose
to avoid the checkerboard background and overlapping characters in the source sheet.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'uploaded_sprites_original.png'
CUTOUTS = ROOT / 'cutouts'

CUTOUTS.mkdir(exist_ok=True)

# Load the uploaded sheet
sheet = Image.open(SOURCE).convert('RGBA')

# Based on extract_sheet.py, the regions are:
# Jab: (0,489,506,645) - this is a strip of 6 jab poses
# Cross: (510,489,1025,645) - this is a strip of 6 cross poses
# Recovery: (379,709,738,855) - contains recovery poses

# For manual extraction, I need to visually inspect and specify tight bounds
# around each individual pose to avoid the checkerboard and neighboring characters

# Jab strip is 506px wide, so each frame is ~84px
# But we need tighter bounds to avoid overlap
jab_bounds = [
    (10, 10, 75, 140),   # jab_0
    (94, 10, 160, 140),  # jab_1
    (178, 10, 245, 140), # jab_2
    (262, 10, 330, 140), # jab_3 (contact)
    (346, 10, 415, 140), # jab_4
    (430, 10, 495, 140), # jab_5
]

# Cross strip is 515px wide, each frame ~85px
cross_bounds = [
    (10, 10, 80, 140),   # cross_0
    (95, 10, 165, 140),  # cross_1
    (180, 10, 250, 140), # cross_2
    (265, 10, 335, 140), # cross_3
    (350, 10, 420, 140), # cross_4 (contact)
    (435, 10, 505, 140), # cross_5
]

# Extract Jab frames
jab_region = sheet.crop((0, 489, 506, 645))
for i, (left, top, right, bottom) in enumerate(jab_bounds):
    frame = jab_region.crop((left, top, right, bottom))
    frame.save(CUTOUTS / f'jab_{i}.png')
    print(f'jab_{i}.png: {frame.size}')

# Extract Cross frames
cross_region = sheet.crop((510, 489, 1025, 645))
for i, (left, top, right, bottom) in enumerate(cross_bounds):
    frame = cross_region.crop((left, top, right, bottom))
    frame.save(CUTOUTS / f'cross_{i}.png')
    print(f'cross_{i}.png: {frame.size}')

# Recovery region - extract individual poses manually
recovery_region = sheet.crop((379, 709, 738, 855))

# Based on visual inspection, recovery poses are at these positions
recovery_bounds = [
    (10, 10, 80, 140),   # jab recovery
    (95, 10, 165, 140),  # cross recovery
]

recovery_names = ['jab_recovery', 'cross_recovery']
for i, (left, top, right, bottom) in enumerate(recovery_bounds):
    frame = recovery_region.crop((left, top, right, bottom))
    frame.save(CUTOUTS / f'{recovery_names[i]}.png')
    print(f'{recovery_names[i]}.png: {frame.size}')

print(f'\nManually extracted cutouts to {CUTOUTS}')
