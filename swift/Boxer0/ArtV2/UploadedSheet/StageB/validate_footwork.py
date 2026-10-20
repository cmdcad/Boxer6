"""Asset checks and measured motion warnings; not a SpriteKit/device test."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image
from export_footwork import measures

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
assert manifest['frame_count_per_clip'] == 6 and manifest['loop_ms'] == 480
assert manifest['root'] == [256,448]
warnings = []
for clip in ['advance','retreat']:
    frames = [r for r in manifest['frames'] if r['clip'] == clip]
    assert len(frames) == 6
    hashes = []
    for record in frames:
        path = ROOT/record['file']; image = Image.open(path)
        assert image.mode == 'RGBA' and image.size == (512,512)
        alpha = np.array(image)[:,:,3]
        assert alpha.min() == 0 and alpha.max() == 255
        assert np.mean(alpha == 0) > .5
        assert not np.any(alpha[0]) and not np.any(alpha[-1])
        assert not np.any(alpha[:,0]) and not np.any(alpha[:,-1])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == record['sha256']; hashes.append(digest)
        m = measures(image)
        assert m == record['measurements']
        assert m['lead']['sole_x'] > m['rear']['sole_x'], 'Foot ordering crossed'
        support_error = min(abs(m['lead']['ground_gap']),abs(m['rear']['ground_gap']))
        if support_error > 2:
            warnings.append(f'{clip} frame{record["index"]+1}: support sole is{support_error}px from baseline')
        swing = 'lead' if (clip == 'advance' and record['index'] < 3) or (clip == 'retreat' and record['index'] >= 3) else 'rear'
        if record['index'] in [1,4] and m[swing]['ground_gap'] < 4:
            warnings.append(f'{clip} frame{record["index"]+1}: swing clearance below4px')
    assert len(set(hashes)) == 6, 'Repeated neutral poses'
    for filename in [f'{clip}_preview.png',f'{clip}_gameplay.gif']:
        preview = Image.open(ROOT/filename)
        assert preview.n_frames == 6
        total = 0
        for index in range(6): preview.seek(index); total += preview.info['duration']
        assert total == 480
    for phase in manifest['plant_slip_diagnostic'][clip]:
        if phase['range_px'] > 3:
            warnings.append(f'{clip} {phase["support"]} support phase: estimated sole drift{phase["range_px"]:.2f}px at preview scale')
print('PASS:12 uncropped512px RGBA exports with six unique poses per clip, transparent margins, front/rear order and two6-frame480ms GIF/APNG loops')
for warning in warnings: print('MOTION REVIEW:', warning)
print('SpriteKit/iPhone integration and zero-slip acceptance: unverified. Live catalog unchanged.')
(ROOT/'validation_results.json').write_text(json.dumps({'technical_checks':'passed',
    'motion_review_warnings':warnings,'device_verified':False,'integrated':False},indent=2)+'\n',encoding='utf-8')
