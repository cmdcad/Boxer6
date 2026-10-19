from pathlib import Path
import json
import math
import shutil
import subprocess
import tempfile
import sys
from PIL import Image
root=Path(__file__).resolve().parents[1]
scene=(root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
model=(root/'Boxer0/HitReactionPlayback.swift').read_text(encoding='utf-8')
contact=(root/'Boxer0/PunchContact.swift').read_text(encoding='utf-8')
view=(root/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
sys.path.insert(0,str(root/'IdleAnimation'))
import generate_guard as art
manifest=json.loads((root/'IdleAnimation/guard_manifest.json').read_text())
assert manifest['root']==[256,448] and manifest['guard']['entryDurationMs']==120
rest=Image.open(root/'IdleAnimation/frames/idle_b_0.png').convert('RGBA')
for i,name in enumerate(manifest['guard']['frames']):
    image=Image.open(root/f'IdleAnimation/frames/{name}.png')
    assert image.size==(512,512) and image.mode=='RGBA'
    assert image.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()[3]==448
    assert image.crop((0,305,512,512)).tobytes()==rest.crop((0,305,512,512)).tobytes()
    assert image.tobytes()==Image.open(root/f'Boxer0/Assets.xcassets/{name}.imageset/{name}.png').tobytes()
    assert (root/f'IdleAnimation/frames/{name}.svg').exists()
    for original,target in [(art.REAR,(235,148)),(art.LEAD,(284,153))]:
        pose=art.pose(original,target,i/2) if i else original
        for a,b in [(0,1),(1,2)]: assert abs(math.dist(pose[a],pose[b])-math.dist(original[a],original[b]))<1e-6
assert 'enum FighterDefenseState' in model and 'entryDuration = 0.12' in model
assert 'case block = "BLOCK"' in contact
assert '!overlaps ? .miss : (guardEffective ? .block : .hit)' in contact
assert 'case .block: blocks += 1' in contact
assert 'guardEffective: attacker == .blue && (guardEffectiveAtContact ?? guardPlayback.isEffective)' in scene
assert 'if event.result == .hit {' in scene and 'guardPlayback.cancel()' in scene
assert scene.count('tracker.evaluate(')==1
assert 'guardPlayback.advance(dt)' in scene and 'guardPlayback.step()' in scene
for start,end in [('func resetHealth()','var contactGeometry'),('private func completeOrangeRecovery','private func startKnockdownIfReady')]:
    assert 'guardPlayback.cancel()' in scene[scene.index(start):scene.index(end)]
assert '.disabled(!playback.canToggleGuard)' in view and 'playback.guardStatus' in view
assert 'B\\(playback.blockCount)' in view
assert view.count('if playback.reactionAssetsAvailable {')==1
assert view.count('Text("Orange: down")')==1
for file in (root/'Boxer0').glob('*.swift'):
    text=file.read_text(encoding='utf-8');assert text.count('{')==text.count('}'),file
print('PASS: guard assets/proportions/fixed feet, defense-state/clock, spatial-first BLOCK, counters, interruption/reset/recovery, single diagnostic block and balanced braces')
compiler=shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary=Path(folder)/'guard-checks'
        files=['Boxer0/JabPlayback.swift','Boxer0/PunchContact.swift','Boxer0/HitReactionPlayback.swift','Tests/GuardChecks.swift']
        subprocess.run([compiler]+[str(root/p) for p in files]+['-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else:
    print('SKIP: Swift behavioral checks; swiftc/Xcode unavailable. Device validation pending.')
