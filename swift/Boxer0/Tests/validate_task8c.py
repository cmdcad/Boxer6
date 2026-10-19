from pathlib import Path
import json
import re
import shutil
import subprocess
import tempfile
from PIL import Image
root=Path(__file__).resolve().parents[1]
scene=(root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
punch=(root/'Boxer0/JabPlayback.swift').read_text(encoding='utf-8')
contact=(root/'Boxer0/PunchContact.swift').read_text(encoding='utf-8')
view=(root/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
manifest=json.loads((root/'IdleAnimation/bidirectional_manifest.json').read_text())
assert len(manifest['variants'])==35
for item in manifest['variants']:
    src=Image.open(root/f"IdleAnimation/frames/{item['source']}.png").convert('RGBA')
    dst=Image.open(root/f"IdleAnimation/frames/{item['target']}.png").convert('RGBA')
    assert dst.size==(512,512) and dst.getchannel('A').tobytes()==src.getchannel('A').tobytes()
    assert dst.tobytes()!=src.tobytes()
    asset=Image.open(root/f"Boxer0/Assets.xcassets/{item['target']}.imageset/{item['target']}.png")
    assert dst.tobytes()==asset.tobytes()
assert scene.count('tracker.evaluate(')==1
assert 'resolveContact(.blue' in scene and 'resolveContact(.orange' in scene
assert scene.count('health.receive(event)')==1
assert 'guardEffective: attacker == .blue &&' in scene
assert 'private var blueReaction = HitReactionPlayback()' in scene
assert 'private var blueKnockdown = KnockdownPlayback()' in scene
assert 'health.recoverBlue()' in scene and 'health.recoverOrange()' in scene
assert 'CPUOffense' in punch and 'struct AttackContext' in punch
assert 'contactEvaluated' in punch and 'context?.completed = true' in contact
assert 'blue.applyDamage(PunchDamage.amount(for: event.kind))' in contact
assert 'orange.applyDamage(PunchDamage.amount(for: event.kind))' in contact
assert 'cpuStartedThisTick' in scene and 'cpuOffense.disable()' in scene
assert 'Blue Rise' in view and 'CPU Attack:' in view and '8C ' in view
for file in (root/'Boxer0').glob('*.swift'):
    code=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"','',file.read_text(encoding='utf-8'))
    depth=0
    for c in code:
        depth+=(c=='{')-(c=='}');assert depth>=0,file
    assert depth==0,file
print('PASS:35 alpha-identical pose variants, one bidirectional resolver/damage path, identities/context, blue shared recovery, offense clock/disable, diagnostics and brace nesting')
compiler=shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary=Path(folder)/'bidirectional-checks'
        files=['Boxer0/JabPlayback.swift','Boxer0/PunchContact.swift','Boxer0/HitReactionPlayback.swift','Tests/BidirectionalChecks.swift']
        subprocess.run([compiler]+[str(root/p) for p in files]+['-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else: print('SKIP: executable Swift checks; swiftc/Xcode unavailable. Bidirectional device validation pending.')
