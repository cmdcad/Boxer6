from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import sys
import json
import math
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
scene = (ROOT/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
view = (ROOT/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
assert 'private var punch = PunchPlayback()' in scene
assert 'private var jab = ' not in scene
assert 'punchButton("Jab"' in view and 'punchButton("Cross"' in view
assert 'Cross assets missing' in view
for folder in ['Boxer0','Tests']:
    for path in (ROOT/folder).glob('*.swift'):
        text = path.read_text(encoding='utf-8')
        assert not re.search(r'\b(?:if|guard|while)\s+let\s+\w+\s*\{', text), path
        assert text.count('{') == text.count('}'), path
print('PASS: shared playback integration, consistent punch controls, explicit optional bindings and source structure')
compiler = shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary = Path(folder)/'punch-checks'
        subprocess.run([compiler,str(ROOT/'Boxer0/JabPlayback.swift'),str(ROOT/'Tests/PunchPlaybackChecks.swift'),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else:
    print('SKIP: Swift punch tests; swiftc unavailable. Run on Mac:')
    print('swiftc Boxer0/JabPlayback.swift Tests/PunchPlaybackChecks.swift -o /tmp/punch-checks && /tmp/punch-checks')
sys.path.insert(0, str(ROOT/'IdleAnimation'))
import generate_cross as rig
import generate_jab as jab
import generate_idle as idle
rest = Image.open(ROOT/'IdleAnimation/frames/idle_a_0.png').convert('RGBA')
for index in range(8):
    folder = ROOT/f'Boxer0/Assets.xcassets/cross_a_{index}.imageset'
    metadata = json.loads((folder/'Contents.json').read_text())
    image = Image.open(folder/metadata['images'][0]['filename'])
    assert image.mode == 'RGBA' and image.size == (512,512)
    assert image.getextrema()[3][0] == 0
    bounds = image.getbbox()
    assert 0 < bounds[0] < bounds[2] < 512 and 0 < bounds[1] < bounds[3] < 512
    assert image.tobytes() == Image.open(ROOT/f'IdleAnimation/frames/cross_a_{index}.png').tobytes()
    assert image.crop((0,340,512,512)).tobytes() == rest.crop((0,340,512,512)).tobytes()
    rear,lead,torso,head_dx = rig.geometry(index)
    for pose,upper,lower in [(rear,rig.REAR_UPPER,rig.REAR_LOWER),(lead,jab.UPPER,jab.LOWER)]:
        assert abs(math.dist(pose[0],pose[1])-upper) < 1e-6
        assert abs(math.dist(pose[1],pose[2])-lower) < 1e-6
    if index in (0,7):
        assert image.tobytes() == rest.tobytes()
    if 1 <= index <= 5:
        # Protective lead glove stays adjacent to the face during the punch.
        glove = (lead[2][0]+19.5,lead[2][1]-1)
        head = (267+head_dx,158.5)
        assert math.dist(glove,head) < 55
# New renderer options must not change previously validated jab poses.
for index,(_,shoulder,wrist) in enumerate(jab.POSES):
    elbow = jab.elbow_for(shoulder,wrist)
    image = idle.draw_boxer(idle.PALETTES['a'],0,0,0,wrist[0]-345,0,lead_pose=(shoulder,elbow,wrist))
    assert image.tobytes() == Image.open(ROOT/f'IdleAnimation/frames/jab_a_{index}.png').tobytes()
preview = Image.open(ROOT/'IdleAnimation/preview/cross_a.gif')
assert preview.n_frames == 8
for index in range(8):
    preview.seek(index)
    assert preview.info['duration'] == 60
assert sum(60 for _ in range(8)) == 480
print('PASS: eight transparent cross frames, catalog/source pairs, unchanged feet, guard endpoints, arm lengths, protective glove, 480 ms GIF, jab renderer regression')

