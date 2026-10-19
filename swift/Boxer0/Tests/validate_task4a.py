"""Validate approved jab assets and execute actual Swift tests when available."""
from pathlib import Path
import json
import math
import shutil
import subprocess
import sys
import tempfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'IdleAnimation'))
import generate_jab as rig

rest = Image.open(ROOT/'IdleAnimation/frames/idle_a_0.png').convert('RGBA')
for i, (label, shoulder, wrist) in enumerate(rig.POSES):
    folder = ROOT/f'Boxer0/Assets.xcassets/jab_a_{i}.imageset'
    meta = json.loads((folder/'Contents.json').read_text())
    image = Image.open(folder/meta['images'][0]['filename'])
    assert image.mode == 'RGBA'
    assert image.size == (512,512)
    assert image.getextrema()[3][0] == 0 and image.getextrema()[3][1] == 255
    bounds = image.getbbox()
    assert 0 < bounds[0] < bounds[2] < 512 and 0 < bounds[1] < bounds[3] < 512
    source = Image.open(ROOT/f'IdleAnimation/frames/jab_a_{i}.png').convert('RGBA')
    assert source.tobytes() == image.tobytes()
    assert image.crop((0,280,512,512)).tobytes() == rest.crop((0,280,512,512)).tobytes()
    # Rear guard has no motion or changed rasterization.
    assert image.crop((284,174,307,192)).tobytes() == rest.crop((284,174,307,192)).tobytes()
    if i in (0,5):
        assert image.tobytes() == rest.tobytes()
    elbow = rig.elbow_for(shoulder,wrist)
    assert abs(math.dist(shoulder,elbow)-rig.UPPER) < 1e-6
    assert abs(math.dist(elbow,wrist)-rig.LOWER) < 1e-6
project = (ROOT/'Boxer0.xcodeproj/project.pbxproj').read_text()
assert project.count('JabPlayback.swift in Sources') == 2
assert project.count('JabPlayback.swift */') == 3
preview = Image.open(ROOT/'IdleAnimation/preview/jab_a.gif')
assert preview.n_frames == 6
for index in range(6):
    preview.seek(index)
    assert preview.info['duration'] == 50
print('PASS: six 512x512 transparent jab frames, catalog/source matches, planted feet, fixed rear glove, exact guard endpoints and arm lengths')
compiler = shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary = Path(folder)/'jab-checks'
        subprocess.run([compiler,str(ROOT/'Boxer0/JabPlayback.swift'),str(ROOT/'Tests/JabPlaybackChecks.swift'),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else:
    print('SKIP: Swift jab tests; swiftc unavailable. Run on Mac:')
    print('swiftc Boxer0/JabPlayback.swift Tests/JabPlaybackChecks.swift -o /tmp/jab-checks && /tmp/jab-checks')

