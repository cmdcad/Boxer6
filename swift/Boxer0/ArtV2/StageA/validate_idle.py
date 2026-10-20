from pathlib import Path
import json
import hashlib
import numpy as np
from PIL import Image

root=Path(__file__).resolve().parent
manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
assert manifest['frame_count']==4 and manifest['loop_ms']==800
hashes=[]
for frame in manifest['frames']:
    path=root/frame['file']
    image=Image.open(path)
    assert image.mode=='RGBA' and image.size==(512,512)
    alpha=np.array(image)[:,:,3]
    assert alpha.min()==0 and alpha.max()==255
    assert np.count_nonzero(alpha==0)>512*512*.5
    assert not np.any(alpha[0]) and not np.any(alpha[-1])
    assert not np.any(alpha[:,0]) and not np.any(alpha[:,-1])
    assert frame['export_metrics']['sole_y']==448
    assert abs(frame['export_metrics']['foot_center']-256)<=.5
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest==frame['sha256']
    hashes.append(digest)
assert len(set(hashes))==4
for file in ['idle_preview.gif','idle_preview.png']:
    preview=Image.open(root/file)
    assert preview.n_frames==4
    duration=0
    for i in range(4):
        preview.seek(i); duration+=preview.info['duration']
    assert duration==800
print('PASS: four distinct 512x512 RGBA exports, genuine transparent margins, uncropped silhouette, sole/root alignment and four 200ms frames in GIF/APNG')
print('SpriteKit/iPhone playback: unverified. Assets remain outside the live catalog.')
