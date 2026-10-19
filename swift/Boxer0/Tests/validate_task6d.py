from pathlib import Path
import json
import shutil
import subprocess
import tempfile
from PIL import Image
root=Path(__file__).resolve().parents[1]
scene=(root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
model=(root/'Boxer0/HitReactionPlayback.swift').read_text(encoding='utf-8')
health=(root/'Boxer0/PunchContact.swift').read_text(encoding='utf-8')
view=(root/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
manifest=json.loads((root/'IdleAnimation/rise_manifest.json').read_text())
assert manifest['root']==[256,448] and manifest['rise']['durationMs']==800
for name in manifest['rise']['frames']:
    image=Image.open(root/f'IdleAnimation/frames/{name}.png')
    assert image.mode=='RGBA' and image.size==(512,512)
    bbox=image.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()
    assert bbox[3]==448 and 0<bbox[0]<bbox[2]<512,(name,bbox)
    folder=root/f'Boxer0/Assets.xcassets/{name}.imageset'
    assert image.tobytes()==Image.open(folder/f'{name}.png').tobytes()
    assert json.loads((folder/'Contents.json').read_text())['images'][0]['filename']==f'{name}.png'
    assert (root/f'IdleAnimation/frames/{name}.svg').exists()
for rise,other in [('rise_b_0','down_b_0'),('rise_b_7','idle_b_0')]:
    assert Image.open(root/f'IdleAnimation/frames/{rise}.png').tobytes()==Image.open(root/f'IdleAnimation/frames/{other}.png').tobytes()
assert 'guard clip == .down else { return false }' in model
assert 'static let riseDuration = 0.80' in model and 'static let riseFrameDuration = 0.10' in model
assert 'return recovered' in model
can=scene[scene.index('var canRise'):scene.index('var orangeClip')]
assert 'orangeCombatState == .defeated && knockdown.clip == .down' in can
assert 'guard canRise, knockdown.startRise()' in can
assert 'health.' not in can and '.position' not in can
assert scene.count('health.recoverOrange()')==1
assert 'if knockdown.advance(dt) { completeOrangeRecovery() }' in scene
assert 'if knockdown.step() { completeOrangeRecovery() }' in scene
recover=health[health.index('mutating func recoverOrange'):health.index('mutating func reset()',health.index('mutating func recoverOrange'))]
assert 'orange.reset()' in recover and 'orangeCombat.reset()' in recover
assert 'blue.reset()' not in recover and 'lastContactSequence =' not in recover
reset=scene[scene.index('func resetHealth()'):scene.index('var contactGeometry')]
assert 'knockdown.cancel()' in reset
assert 'Button("Rise", action: playback.rise)' in view and '.disabled(!playback.canRise)' in view
assert 'playback.orangeCombatState.rawValue' in view and '8A ' in view
print('PASS: eight integrated transparent poses, baseline/root contract, exact down/idle endpoints, down-only Rise, shared clock, orange-only completion health policy, reset and HUD source checks')
compiler=shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary=Path(folder)/'rise-checks'
        sources=['Boxer0/JabPlayback.swift','Boxer0/PunchContact.swift','Boxer0/HitReactionPlayback.swift','Tests/RiseChecks.swift']
        subprocess.run([compiler]+[str(root/p) for p in sources]+['-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else:
    print('SKIP: Swift behavioral checks; swiftc/Xcode unavailable. iPhone playback validation pending.')
