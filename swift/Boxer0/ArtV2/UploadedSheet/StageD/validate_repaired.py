"""Independent pixel/preview checks; visual anatomy review remains required."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent


def components(mask):
    remaining = set(map(tuple, np.argwhere(mask)))
    result = []
    while remaining:
        queue = [remaining.pop()]
        points = []
        while queue:
            y, x = queue.pop()
            points.append((y, x))
            for p in [(y-1, x), (y+1, x), (y, x-1), (y, x+1)]:
                if p in remaining:
                    remaining.remove(p)
                    queue.append(p)
        result.append(np.array(points))
    return result


def main():
    m = json.loads((ROOT/'manifest.json').read_text())
    errors, rows, contacts = [], [], []
    idle = np.array(Image.open(ROOT.parent/'StageA/frames/idle_a_0.png'))
    for rec in m['frames']:
        p = ROOT/rec['file']
        im = Image.open(p)
        a = np.array(im)
        alpha = a[:, :, 3]
        ys, xs = np.where(alpha >= 32)
        blobs = components(alpha >= 32)
        significant = [len(b) for b in blobs if len(b) >= 12]
        rgb = a[:, :, :3].astype(int)
        gray = ((rgb.max(2)-rgb.min(2)<6) & (rgb.mean(2)>100) & (rgb.mean(2)<230) & (alpha>=240))
        checks = {'rgba_512': im.size == (512, 512) and im.mode == 'RGBA',
                  'true_transparency': bool(alpha.min() == 0 and alpha.max() == 255),
                  'one_character': len(significant) == 1,
                  'clear_edges': bool(not (alpha[:8]>=32).any() and not (alpha[-8:]>=32).any() and not (alpha[:, :8]>=32).any() and not (alpha[:, -8:]>=32).any()),
                  'consistent_height': 280 <= int(ys.max()-ys.min()+1) <= 345,
                  'baseline': int(ys.max()) == 448,
                  'fixed_lower_body_exact': bool(np.array_equal(a[260:], idle[260:])),
                  'no_large_gray_checkerboard': int(gray.sum()) < 800,
                  'hash': hashlib.sha256(p.read_bytes()).hexdigest() == rec['sha256']}
        for name, ok in checks.items():
            if not ok:
                errors.append(f'{p.name}: {name}')
        rows.append({'file': p.name, 'checks': checks, 'gray_midtone_pixels': int(gray.sum()),
                     'significant_component_sizes': significant,
                     'bounds': [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)]})
        if rec['is_contact_frame']:
            kind = rec['clip']
            cfg = m[f'{kind}_contact']
            x, y = cfg['center']
            radius = cfg['radius']
            yy, xx = np.indices(alpha.shape)
            blue = ((rgb[:, :, 2]>90) & (rgb[:, :, 0]<120) & (rgb[:, :, 2]>rgb[:, :, 0]*1.4) & (rgb[:, :, 2]>rgb[:, :, 1]*1.1) & (alpha>=128))
            glove_blobs = [b for b in components(blue & (yy<250) & (xx>300)) if len(b)>=50]
            assert glove_blobs, f'No attacking blue glove detected in {kind}'
            glove = min(glove_blobs, key=lambda b: np.hypot(b[:, 1].mean()-x, b[:, 0].mean()-y))
            center = [(int(glove[:, 1].min())+int(glove[:, 1].max()))/2,
                      (int(glove[:, 0].min())+int(glove[:, 0].max()))/2]
            distance = float(np.hypot(center[0]-x, center[1]-y))
            disk = (xx-x)**2+(yy-y)**2 <= radius**2
            fill = float((disk & blue).sum()/disk.sum())
            contacts.append({'kind': kind, 'configured_center': [x, y],
                             'detected_blue_glove_bbox_center': center, 'center_distance_px': distance,
                             'circle_blue_coverage': fill,
                             'note': 'Color segmentation is a diagnostic, not artist-authored geometry.'})
            if distance > 16 or fill < .45:
                errors.append(f'{kind}: contact needs visual alignment review (distance {distance:.1f}px, coverage {fill:.2f})')
    for clip, n, ms, recovery_ms in [('jab', 6, 50, 120), ('cross', 8, 60, 220)]:
        records = [r for r in m['frames'] if r['clip'] == clip]
        if len(records) != n or len({r['sha256'] for r in records}) != n:
            errors.append(f'{clip}: wrong count or duplicate frames')
        for name, expected in [(f'{clip}_preview.png', [ms]*n),
                               (f'{clip}_with_recovery.png', [ms]*n+[recovery_ms, 400]),
                               (f'{clip}_with_recovery.gif', [ms]*n+[recovery_ms, 400])]:
            im = Image.open(ROOT/name)
            durations = []
            for i in range(im.n_frames):
                im.seek(i)
                durations.append(im.info.get('duration'))
            if durations != expected:
                errors.append(f'{name}: timing {durations} != {expected}')
    result = {'passed': not errors, 'errors': errors, 'frames': rows, 'contacts': contacts,
              'limitations': ['Visual review required for anatomy, no ghosting and motion continuity.',
                              'No live integration, Swift/XCTest or iPhone execution on Windows.',
                              'Color segmentation cannot independently establish anatomical glove centers.']}
    (ROOT/'validation_report.json').write_text(json.dumps(result, indent=2)+'\n')
    (ROOT/'contact_validation.json').write_text(json.dumps({'contacts': contacts, 'errors': [e for e in errors if 'contact' in e]}, indent=2)+'\n')
    print(json.dumps({'passed': not errors, 'errors': errors, 'contacts': contacts}, indent=2))
    assert not errors


if __name__ == '__main__':
    main()
