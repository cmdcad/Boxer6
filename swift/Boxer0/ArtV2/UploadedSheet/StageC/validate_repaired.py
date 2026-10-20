"""Independent checks of the final files, not placeholder foot measurements."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent


def component_sizes(mask):
    remaining = set(map(tuple, np.argwhere(mask)))
    sizes = []
    while remaining:
        queue = [remaining.pop()]
        size = 0
        while queue:
            y, x = queue.pop()
            size += 1
            for p in [(y-1, x), (y+1, x), (y, x-1), (y, x+1)]:
                if p in remaining:
                    remaining.remove(p)
                    queue.append(p)
        sizes.append(size)
    return sizes


def main():
    manifest = json.loads((ROOT/'manifest.json').read_text())
    results, errors = [], []
    for r in manifest['frames']:
        p = ROOT/r['file']
        im = Image.open(p)
        a = np.array(im.getchannel('A'))
        yy, xx = np.where(a >= 32)
        sizes = component_sizes(a >= 32)
        significant = [int(v) for v in sizes if v >= 12]
        checks = {'rgba_512': im.mode == 'RGBA' and im.size == (512, 512),
                  'true_alpha': bool(a.min() == 0 and a.max() == 255),
                  'clear_canvas_edges': not ((a[:8]>=32).any() or (a[-8:]>=32).any() or (a[:, :8]>=32).any() or (a[:, -8:]>=32).any()),
                  'one_connected_character': len(significant) == 1,
                  'baseline_448': int(yy.max()) == 448,
                  'character_height_consistent': 280 <= int(yy.max()-yy.min()+1) <= 345,
                  'both_feet_present': bool((a[340:, :256]>=32).any() and (a[340:, 256:]>=32).any()),
                  'hash_matches': hashlib.sha256(p.read_bytes()).hexdigest() == r['sha256']}
        for name, ok in checks.items():
            if not ok:
                errors.append(f'{p.name}: {name}')
        if r['clip'] != 'guard_entry':
            old = ROOT.parent/'StageB/frames'/f"{r['clip'].replace('guarded_', '')}_a_{r['index']}.png"
            if im.tobytes() == Image.open(old).tobytes():
                errors.append(f'{p.name}: unchanged normal footwork')
        results.append({'file': p.name, 'checks': checks,
                        'significant_component_sizes': significant,
                        'detached_ink_pixels': int(sum(sizes)-max(sizes)),
                        'bounds': r['measurements']['bounds']})
    for clip, n, ms in [('guard_entry', 3, 40), ('guarded_advance', 6, 80), ('guarded_retreat', 6, 80)]:
        if len([r for r in manifest['frames'] if r['clip'] == clip]) != n:
            errors.append(f'{clip}: wrong exported frame count')
        im = Image.open(ROOT/f'{clip}_preview.png')
        durations = []
        for i in range(im.n_frames):
            im.seek(i)
            durations.append(im.info.get('duration'))
        if im.n_frames != n or durations != [ms]*n:
            errors.append(f'{clip}: wrong production APNG timing {durations}')
        hashes = [r['sha256'] for r in manifest['frames'] if r['clip'] == clip]
        if len(set(hashes)) != n:
            errors.append(f'{clip}: duplicate frames')
    result = {'passed': not errors, 'errors': errors, 'frames': results,
              'limits': ['Asset checks only; visual review also required.',
                         'No SpriteKit integration, XCTest or iPhone playback performed.',
                         'Guarded movement stride must be checked at actual 55/35.75 scene points per second; no zero-sliding claim.']}
    (ROOT/'validation_results.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'passed': not errors, 'errors': errors}, indent=2))
    assert not errors


if __name__ == '__main__':
    main()
