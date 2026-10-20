"""Asset and synchronization-order checks; actual Swift tests run when available."""
from pathlib import Path
import importlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'IdleAnimation'))
import generate_hit_react as rig
import generate_cross as cross
import generate_idle as idle
scene=(ROOT/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
clock=(ROOT/'Boxer0/JabPlayback.swift').read_text(encoding='utf-8')
view=(ROOT/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
ns={'s':'http://www.w3.org/2000/svg'}
rest=Image.open(ROOT/'IdleAnimation/frames/idle_b_0.png').convert('RGBA')
for index in range(4):
    folder=ROOT/f'Boxer0/Assets.xcassets/hit_react_b_{index}.imageset'
    meta=json.loads((folder/'Contents.json').read_text())
    image=Image.open(folder/meta['images'][0]['filename'])
    assert image.mode=='RGBA' and image.size==(512,512)
    assert image.getextrema()[3][0]==0
    assert image.tobytes()==Image.open(ROOT/f'IdleAnimation/frames/hit_react_b_{index}.png').tobytes()
    assert image.crop((0,305,512,512)).tobytes()==rest.crop((0,305,512,512)).tobytes()
    assert image.tobytes()!=rest.tobytes(), 'No substituted idle pose, especially at first impact'
    torso,rear,lead,head_dx=rig.geometry(index)
    assert head_dx<0, 'Mirrored orange must recoil away from the attacking blue fighter'
    for pose,original in [(rear,rig.REAR),(lead,rig.LEAD)]:
        for a,b in [(0,1),(1,2)]:
            assert abs(math.dist(pose[a],pose[b])-math.dist(original[a],original[b]))<1e-8
    svg=ET.parse(ROOT/f'IdleAnimation/frames/hit_react_b_{index}.svg').getroot()
    base=ET.parse(ROOT/'IdleAnimation/frames/idle_b_0.svg').getroot()
    for group in ['boot-rear','boot-lead','thigh-rear','thigh-lead','shin-rear','shin-lead','pelvis']:
        assert ET.tostring(svg.find(f"s:g[@id='{group}']",ns))==ET.tostring(base.find(f"s:g[@id='{group}']",ns))
preview=Image.open(ROOT/'IdleAnimation/preview/hit_react_b.gif')
assert preview.n_frames==4
for i in range(4):
    preview.seek(i)
    assert preview.info['duration']==60
# Ensure optional renderer extension still reproduces every validated cross pixel.
for i in range(8):
    rear,lead,torso,head_dx=cross.geometry(i)
    if i in (0,7):
        image=idle.draw_boxer(idle.PALETTES['a'],0,0,0,0,0)
    else:
        image=idle.draw_boxer(idle.PALETTES['a'],0,0,0,lead[2][0]-345,rear[2][0]-278,
            lead_pose=lead,rear_pose=rear,torso_points=torso,head_dx=head_dx)
    assert image.tobytes()==Image.open(ROOT/f'IdleAnimation/frames/cross_a_{i}.png').tobytes()
print('PASS: four non-idle reaction poses, 240 ms preview, fixed lower body/SVG groups, recoil direction, original limb lengths and cross-render regression')
update=scene[scene.index('override func update'):scene.index('private var lastPublishedFrame')]
assert update.index('guard isPlaying, hasFocus')<update.index('advanceOrange(dt)')<update.index('advanceActiveAttacks(dt)')<update.index('applyFrames()')
assert update.count('advanceOrange(dt)')==1
step=scene[scene.index('func stepFrame()'):scene.index('func setSpeed(')]
assert step.index('advanceOrange(effectStep)')<step.index('advanceActiveAttacks(effectStep)')<step.index('applyFrames()')
handler=scene[scene.index('private func resolveContact'):scene.index('private func advanceOrange')]
assert handler.index('tracker.evaluate(')<handler.index('reaction.receive(.hit, from: event.kind)')<handler.index('onPunchContact?(event)')
assert 'DispatchQueue' not in handler and 'async' not in handler and 'SKAction' not in handler
assert 'preserveContactPose &&' in clock
assert 'Orange:' in view
assert 'rootB.position = right' in scene
assert scene.count('rootB.position =')==1
project=(ROOT/'Boxer0.xcodeproj/project.pbxproj').read_text()
assert project.count('HitReactionPlayback.swift in Sources')==2
assert project.count('HitReactionPlayback.swift */')==3
for folder in ['Boxer0','Tests']:
    for file in (ROOT/folder).glob('*.swift'):
        text=file.read_text(encoding='utf-8')
        assert not re.search(r'\b(?:if|guard|while)\s+let\s+\w+\s*\{',text)
        assert text.count('{')==text.count('}'),file
print('PASS: same-update contact/reaction wiring, step order, pause guard, stationary root, explicit bindings, HUD and target membership')
compiler=shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary=Path(folder)/'reaction-checks'
        subprocess.run([compiler,str(ROOT/'Boxer0/JabPlayback.swift'),str(ROOT/'Boxer0/PunchContact.swift'),
            str(ROOT/'Boxer0/HitReactionPlayback.swift'),str(ROOT/'Tests/HitReactionChecks.swift'),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else:
    print('SKIP: Swift reaction/playback tests; swiftc unavailable. On Mac:')
    print('swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Boxer0/HitReactionPlayback.swift Tests/HitReactionChecks.swift -o /tmp/reaction-checks && /tmp/reaction-checks')
