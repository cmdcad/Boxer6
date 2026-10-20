"""Export isolated imagegen edits; canvas resampling/registration only.

No body-part painting, masks, per-character fitting or gameplay changes.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent


def measure(im):
    a = np.array(im.getchannel('A'))
    y, x = np.where(a >= 32)
    assert len(x), 'Empty sprite'
    out = {'bounds': [int(x.min()), int(y.min()), int(x.max()+1), int(y.max()+1)]}
    for name, l, r in [('rear', 0, 256), ('lead', 256, 512)]:
        sy, sx = np.where(a[340:, l:r] >= 32)
        assert len(sx), f'Missing {name} foot'
        bottom = int(sy.max()+340)
        by, bx = np.where(a[bottom-2:bottom+1, l:r] >= 32)
        out[name] = {'sole_y': bottom, 'sole_x': float((bx.min()+bx.max())/2+l),
                     'ground_gap': 448-bottom}
    return out


def main():
    records, clips = [], {}
    for clip, count, ms in [('guard_entry', 3, 40), ('guarded_advance', 6, 80), ('guarded_retreat', 6, 80)]:
        images = []
        for i in range(count):
            if clip == 'guard_entry' and i == 0:
                src = ROOT.parent/'StageA/frames/idle_a_0.png'
            else:
                src = ROOT/f'source/repaired/{clip}_{i}.png'
            raw = Image.open(src).convert('RGBA')
            assert raw.width == raw.height, (src, raw.size)
            # Resample the full canvas, never fit the character's bounding box.
            im = raw.resize((512, 512), Image.Resampling.LANCZOS)
            before = measure(im)
            dy = 448-max(before[f]['sole_y'] for f in ['rear', 'lead'])
            assert abs(dy) <= 16, (src, 'Excessive baseline correction', dy)
            canvas = Image.new('RGBA', (512, 512))
            canvas.alpha_composite(im, (0, dy))
            dest = ROOT/f'frames/{clip}_{i}.png'
            canvas.save(dest)
            m = measure(canvas)
            assert 8 < m['bounds'][0] < m['bounds'][2] < 504
            assert 280 <= m['bounds'][3]-m['bounds'][1] <= 345, (src, m)
            assert max(m[f]['sole_y'] for f in ['rear', 'lead']) == 448
            records.append({'clip': clip, 'index': i, 'file': dest.relative_to(ROOT).as_posix(),
                            'selected_source': str(src.relative_to(ROOT.parent)),
                            'source_canvas': list(raw.size), 'duration_ms': ms,
                            'vertical_registration': dy, 'measurements': m,
                            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()})
            images.append(canvas)
        clips[clip] = images
        images[0].save(ROOT/f'{clip}_preview.png', save_all=True,
                       append_images=images[1:], duration=ms, loop=0, disposal=0, blend=0)
    sheet = Image.new('RGB', (512*6, 550*3), '#e8eef4')
    draw = ImageDraw.Draw(sheet)
    for row, (clip, ims) in enumerate(clips.items()):
        for i, im in enumerate(ims):
            x, y = i*512, row*550
            sheet.paste(im, (x, y), im)
            draw.line((x, y+448, x+511, y+448), fill='#cb7367')
            draw.line((x+256, y+430, x+256, y+465), fill='#639ac1')
            draw.text((x+12, y+518), f'{clip} {i+1}', fill='#183249')
    sheet.save(ROOT/'alignment_sheet.png')
    # Gameplay-size previews, no synthetic root motion or foot-lock claims.
    for clip, ims in clips.items():
        preview = []
        for im in ims:
            bg = Image.new('RGB', (320, 280), '#e8eef4')
            small = im.resize((256, 256), Image.Resampling.LANCZOS)
            bg.paste(small, (32, 0), small)
            ImageDraw.Draw(bg).line((12, 224, 308, 224), fill='#a4b3c1')
            preview.append(bg)
        times = [40, 40, 640] if clip == 'guard_entry' else [80]*6
        preview[0].save(ROOT/f'{clip}_gameplay.gif', save_all=True,
                        append_images=preview[1:], duration=times, loop=0, disposal=2)
    paired = []
    for i in range(6):
        bg = Image.new('RGB', (640, 280), '#e8eef4')
        d = ImageDraw.Draw(bg)
        for column, clip in enumerate(['guarded_advance', 'guarded_retreat']):
            small = clips[clip][i].resize((256, 256), Image.Resampling.LANCZOS)
            bg.paste(small, (column*320+32, 0), small)
            d.text((column*320+20, 253), clip.replace('_', ' ').title(), fill='#183249')
            d.line((column*320+12, 224, column*320+308, 224), fill='#a4b3c1')
        paired.append(bg)
    paired[0].save(ROOT/'movement_preview.gif', save_all=True, append_images=paired[1:],
                   duration=80, loop=0, disposal=2)
    manifest = {'canvas': [512, 512], 'root': [256, 448], 'baseline': 448,
                'facing': 'right', 'integrated': False, 'tool': 'built-in imagegen',
                'guard_entry_ms': 120, 'guard_effective_at_ms': 120,
                'guarded_loop_ms': 480, 'frames': records,
                'preview_note': 'Entry GIF holds last pose for review; production timing remains 3x40ms.'}
    (ROOT/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print('Exported 15 corrected frames and previews.')


if __name__ == '__main__':
    main()
