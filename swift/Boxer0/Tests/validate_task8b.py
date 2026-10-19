from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from PIL import Image
root=Path(__file__).resolve().parents[1]
scene=(root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
model=(root/'Boxer0/FootworkMotion.swift').read_text(encoding='utf-8')
view=(root/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
for clip in ['advance','retreat']:
    for i in range(6):
        name=f'{clip}_b_{i}'
        image=Image.open(root/f'Boxer0/Assets.xcassets/{name}.imageset/{name}.png')
        assert image.size==(512,512) and image.mode=='RGBA'
assert 'var speed = 65.0' in model and 'decisionInterval = 0.20' in model
assert 'private var orangeMotion = FootworkMotion()' in scene
assert 'orangeMotion.advance(duration: dt' in scene
assert 'cpuDistance.advance(dt' in scene
assert 'setOrangeLocomotion(travel < 0 ? .advance : .retreat)' in scene
assert 'let gap = max(aBody.width,bBody.width)' in scene
assert 'min(limits.upperBound, max(limits.lowerBound' in scene
assert 'size.width * orangeXFraction' in scene
assert 'if selected {' in scene
assert 'CPU:' in view and 'playback.cpuMovement' in view and '8C ' in view
for file in (root/'Boxer0').glob('*.swift'):
    code=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"','',file.read_text(encoding='utf-8'))
    depth=0
    for c in code:
        depth+=(c=='{')-(c=='}');assert depth>=0,file
    assert depth==0,file
print('PASS:12 existing orange footwork assets, shared movement engine, distance decisions, symmetric torso/edge bounds, priority, layout preservation, diagnostics and brace nesting')
compiler=shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary=Path(folder)/'cpu-movement-checks'
        subprocess.run([compiler,str(root/'Boxer0/FootworkMotion.swift'),str(root/'Tests/CPUMovementChecks.swift'),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else: print('SKIP: executable Swift checks; swiftc/Xcode unavailable. iPhone movement validation pending.')
