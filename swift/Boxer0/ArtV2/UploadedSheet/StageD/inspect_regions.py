"""Extract full regions for visual inspection before manual bounds specification."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'uploaded_sprites_original.png'
CUTOUTS = ROOT / 'cutouts'

CUTOUTS.mkdir(exist_ok=True)

sheet = Image.open(SOURCE).convert('RGBA')

# Extract full regions for inspection
jab_region = sheet.crop((0, 489, 506, 645))
jab_region.save(CUTOUTS / 'jab_region_full.png')

cross_region = sheet.crop((510, 489, 1025, 645))
cross_region.save(CUTOUTS / 'cross_region_full.png')

recovery_region = sheet.crop((379, 709, 738, 855))
recovery_region.save(CUTOUTS / 'recovery_region_full.png')

print('Extracted full regions for inspection:')
print(f'  jab_region_full.png: {jab_region.size}')
print(f'  cross_region_full.png: {cross_region.size}')
print(f'  recovery_region_full.png: {recovery_region.size}')
