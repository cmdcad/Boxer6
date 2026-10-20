"""Conservative edge decontamination for these nine binary-alpha exports.

Authorized scripted cleanup. No resizing, pose changes or image generation.
Matte reconstruction is an estimate; originals remain authoritative.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent


def components(mask):
    todo = set(map(tuple, np.argwhere(mask)))
    result = []
    while todo:
        q = [todo.pop()]
        points = []
        while q:
            y, x = q.pop()
            points.append((y, x))
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    p = (y+dy, x+dx)
                    if p in todo:
                        todo.remove(p)
                        q.append(p)
        result.append(points)
    return result


def clean(im):
    src = np.array(im.convert('RGBA'))
    dst = src.copy()
    mask = src[:, :, 3] > 0
    h, w = mask.shape
    pad = np.pad(mask, 1)
    interior = np.ones_like(mask)
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            interior &= pad[1+dy:1+dy+h, 1+dx:1+dx+w]
    rgb = src[:, :, :3].astype(float)
    neutral = (np.ptp(rgb, axis=2)<25) & (rgb.min(2)>130)
    candidates = np.argwhere(mask & ~interior & neutral)
    edited = 0
    for y, x in candidates:
        # All decisions use immutable src, never pixels changed in this pass.
        foreground = []
        background = []
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                yy, xx = y+dy, x+dx
                if not (0<=yy<h and 0<=xx<w):
                    continue
                c = rgb[yy, xx]
                if mask[yy, xx] and c.min()<90 and np.ptp(c)<60:
                    foreground.append((dy*dy+dx*dx, c))
                if not mask[yy, xx] and c.min()>140 and np.ptp(c)<25:
                    background.append(c)
        if not foreground:
            continue
        foreground.sort(key=lambda z: z[0])
        f = foreground[0][1]
        b = np.median(background, axis=0) if background else np.array([255.,255.,255.])
        v = f-b
        if np.dot(v,v)<100:
            continue
        coverage = float(np.clip(np.dot(rgb[y,x]-b,v)/np.dot(v,v),0,1))
        dst[y,x,:3] = np.clip(np.round(f),0,255).astype(np.uint8)
        dst[y,x,3] = round(src[y,x,3]*coverage)
        edited += 1
    removed = 0
    # Remove only very small disconnected islands, not thin connected detail.
    for points in components(dst[:, :, 3]>0):
        if len(points)<=12:
            for y, x in points:
                dst[y,x] = 0
                removed += 1
    dst[dst[:, :, 3]==0] = 0
    assert np.array_equal(dst[interior], src[interior]), 'Interior unexpectedly modified'
    return Image.fromarray(dst), {'fringe_pixels_reconstructed': edited,
                                  'detached_speck_pixels_removed': removed,
                                  'partial_alpha_pixels': int(((dst[:,:,3]>0)&(dst[:,:,3]<255)).sum()),
                                  'interior_pixels_unchanged': True}


def main():
    out = ROOT/'Cleaned'
    out.mkdir(exist_ok=True)
    records = []
    files = sorted(ROOT.glob('sprite_frame_*.png'))
    # Each row has original/cleaned on dark, then original/cleaned on light.
    sheet = Image.new('RGB', (341*4, 251*len(files)), '#e8eef4')
    for row, p in enumerate(files):
        original = Image.open(p).convert('RGBA')
        result, info = clean(original)
        assert result.size == original.size
        result.save(out/p.name)
        records.append({'file': p.name, **info})
        for col, (im, color) in enumerate([(original,'#243449'),(result,'#243449'),
                                           (original,'#ffffff'),(result,'#ffffff')]):
            panel = Image.new('RGB', (341,251), color)
            panel.paste(im,(0,0),im)
            ImageDraw.Draw(panel).text((8,232), f'{p.stem}: {"original" if col%2==0 else "cleaned"}',
                                       fill='white' if col<2 else '#183249')
            sheet.paste(panel,(col*341,row*251))
    sheet.save(out/'edge_comparison.jpg', quality=95)
    (out/'cleanup_report.json').write_text(json.dumps({'method':'estimated outer-edge matte reconstruction',
        'limitations':'Binary alpha and baked checkerboard cannot be perfectly inverted. Inspect before production.',
        'frames':records},indent=2)+'\n')
    print(json.dumps(records,indent=2))


if __name__ == '__main__':
    main()
