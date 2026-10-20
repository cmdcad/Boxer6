"""Full-canvas export of individually drawn punch poses; no crossfades."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
IDLE = ROOT.parent/'StageA/frames/idle_a_0.png'


def bounds(im):
    y, x = np.where(np.array(im.getchannel('A')) >= 32)
    assert len(x)
    return [int(x.min()), int(y.min()), int(x.max()+1), int(y.max()+1)]


def main():
    clips, records = {}, []
    idle = Image.open(IDLE).convert('RGBA')
    # Idle's right forearm extends beside the belt down to y259. It is not
    # part of the stationary lower body and must not be copied into punches.
    lower_body = idle.copy()
    lower_body.paste((0, 0, 0, 0), (290, 254, 512, 260))
    # Explicit user approval: scripted compositing keeps the approved feet fixed.
    fixed_lower_y = 254
    specs = [('jab', 6, 50), ('cross', 8, 60), ('jab_recovery', 1, 120), ('cross_recovery', 1, 220)]
    for clip, count, ms in specs:
        images = []
        for i in range(count):
            name = clip if 'recovery' in clip else f'{clip}_{i}'
            src = IDLE if i == 0 and clip in ['jab', 'cross'] else ROOT/f'source/repaired/{name}.png'
            raw = Image.open(src).convert('RGBA')
            assert raw.width == raw.height
            im = raw.resize((512, 512), Image.Resampling.LANCZOS)
            b = bounds(im)
            dy = 448-(b[3]-1)
            assert abs(dy) <= 16, (name, b, dy)
            final = Image.new('RGBA', (512, 512))
            final.alpha_composite(im, (0, dy))
            final.paste(lower_body.crop((0, fixed_lower_y, 512, 512)), (0, fixed_lower_y))
            dest = ROOT/f'frames/{name}.png'
            final.save(dest)
            records.append({'clip': clip, 'index': i, 'file': dest.relative_to(ROOT).as_posix(),
                            'selected_source': str(src.relative_to(ROOT.parent)),
                            'source_canvas': list(raw.size), 'vertical_registration': dy,
                            'duration_ms': ms, 'bounds': bounds(final),
                            'fixed_lower_body_from_y': fixed_lower_y,
                            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
                            'is_contact_frame': (clip == 'jab' and i == 3) or (clip == 'cross' and i == 4),
                            'genuine_transition_pose': clip == 'cross' and i in [3, 6]})
            images.append(final)
        clips[clip] = images
        if count > 1:
            images[0].save(ROOT/f'{clip}_preview.png', save_all=True, append_images=images[1:],
                           duration=ms, loop=0, disposal=0, blend=0)
    # Export exact-speed punch -> recovery -> Idle previews.
    for clip, ms, recovery_ms in [('jab', 50, 120), ('cross', 60, 220)]:
        seq = clips[clip]+clips[f'{clip}_recovery']+[Image.open(IDLE).convert('RGBA')]
        durations = [ms]*len(clips[clip])+[recovery_ms, 400]
        seq[0].save(ROOT/f'{clip}_with_recovery.png', save_all=True, append_images=seq[1:],
                    duration=durations, loop=0, disposal=0, blend=0)
        smalls = []
        for im in seq:
            bg = Image.new('RGB', (320, 280), '#e8eef4')
            small = im.resize((256, 256), Image.Resampling.LANCZOS)
            bg.paste(small, (32, 0), small)
            ImageDraw.Draw(bg).line((8, 224, 312, 224), fill='#9faebb')
            smalls.append(bg)
        smalls[0].save(ROOT/f'{clip}_with_recovery.gif', save_all=True, append_images=smalls[1:],
                       duration=durations, loop=0, disposal=2)
        clips[clip][0].save(ROOT/f'{clip}_animation.gif', save_all=True,
                            append_images=clips[clip][1:], duration=ms, loop=0, disposal=2)
    sheet = Image.new('RGB', (4096, 1100), '#e8eef4')
    d = ImageDraw.Draw(sheet)
    rows = [clips['jab']+clips['jab_recovery']+clips['cross_recovery'], clips['cross']]
    for row, ims in enumerate(rows):
        for col, im in enumerate(ims):
            x, y = col*512, row*550
            sheet.paste(im, (x, y), im)
            d.line((x, y+448, x+511, y+448), fill='#ca7767')
            d.line((x+256, y+430, x+256, y+465), fill='#639ac1')
            label = f'{"Jab" if row == 0 else "Cross"} {col+1}'
            if row == 0 and col >= 6:
                label = 'Jab recovery 120ms' if col == 6 else 'Cross recovery 220ms'
            d.text((x+12, y+518), label, fill='#183249')
    sheet.save(ROOT/'full_alignment_sheet.png')
    sheet.save(ROOT/'alignment_sheet.png')
    diagnostics = []
    for clip, idx, center, radius in [('jab', 3, (384.5, 189), 20), ('cross', 4, (378, 186), 18)]:
        bg = Image.new('RGB', (512, 512), '#e8eef4')
        im = clips[clip][idx]
        bg.paste(im, (0, 0), im)
        d = ImageDraw.Draw(bg)
        x, y = center
        d.ellipse((x-radius, y-radius, x+radius, y+radius), outline='#d83d59', width=2)
        d.line((x-7, y, x+7, y), fill='#d83d59', width=2)
        d.line((x, y-7, x, y+7), fill='#d83d59', width=2)
        d.rectangle((220, 127, 308, 300), outline='#479a6d', width=1)
        d.text((12, 475), 'Red: existing glove geometry. Green: existing body target.', fill='#183249')
        bg.save(ROOT/f'contact_overlay_{clip}_frame{idx}.png')
        diagnostics.append(bg)
    contact_sheet = Image.new('RGB', (1024, 512), '#e8eef4')
    for i, im in enumerate(diagnostics):
        contact_sheet.paste(im, (i*512, 0))
    contact_sheet.save(ROOT/'contact_diagnostic_sheet.png')
    manifest = {'canvas': [512, 512], 'root': [256, 448], 'baseline': 448, 'facing': 'right',
                'integrated': False, 'tool': 'built-in imagegen', 'frames': records,
                'jab_contact': {'index': 3, 'time_ms': 150, 'center': [384.5, 189], 'radius': 20},
                'cross_contact': {'index': 4, 'time_ms': 240, 'center': [378, 186], 'radius': 18},
                'note': 'User-approved fixed lower-body composite starts at y254. The Idle forearm at x>=290,y254..259 is excluded; all pixels y>=260 remain exact Idle. Simulation and live geometry unchanged.'}
    (ROOT/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print('Exported all 16 frames, timed recovery previews and contact overlays.')


if __name__ == '__main__':
    main()
