from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

p = Path(__file__).resolve().parent
idle = Image.open(p.parent/'StageA/frames/idle_a_0.png').convert('RGBA')
files = sorted((p/'source/repaired').glob('*.png'))
sheet = Image.new('RGB', (512*8, 550*2), '#e8eef4')
for i, f in enumerate(files):
    im = Image.open(f).convert('RGBA').resize((512, 512), Image.Resampling.LANCZOS)
    a = np.array(im.getchannel('A'))
    y, x = np.where(a >= 32)
    c = Image.new('RGBA', (512, 512))
    c.alpha_composite(im, (0, 448-int(y.max())))
    c.paste(idle.crop((0, 260, 512, 512)), (0, 260))
    col, row = i % 8, i // 8
    sheet.paste(c, (col*512, row*550), c)
    ImageDraw.Draw(sheet).text((col*512+12, row*550+518), f.stem, fill='#183249')
sheet.save(p/'source/repaired/waist_join_review.png')
print('Saved waist join review.')
