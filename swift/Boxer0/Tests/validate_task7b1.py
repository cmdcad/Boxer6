from pathlib import Path
import json
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[1]
scene=(root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
model=(root/'Boxer0/HitReactionPlayback.swift').read_text(encoding='utf-8')
view=(root/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
manifest=json.loads((root/'IdleAnimation/block_recoil_manifest.json').read_text())
held=Image.open(root/'IdleAnimation/frames/guard_b_2.png').convert('RGBA')
ns={'s':'http://www.w3.org/2000/svg'}
for kind,amount,duration in [('jab',10,120),('cross',18,160)]:
    assert manifest['clips'][kind]['durationMs']==duration
    for i,name in enumerate(manifest['clips'][kind]['frames']):
        image=Image.open(root/f'IdleAnimation/frames/{name}.png')
        assert image.mode=='RGBA' and image.size==(512,512)
        assert image.crop((0,305,512,512)).tobytes()==held.crop((0,305,512,512)).tobytes()
        assert image.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()[3]==448
        assert image.tobytes()==Image.open(root/f'Boxer0/Assets.xcassets/{name}.imageset/{name}.png').tobytes()
        if i<2: assert image.tobytes()!=held.tobytes()
        else: assert image.tobytes()==held.tobytes()
        if i==0:
            svg=ET.parse(root/f'IdleAnimation/frames/{name}.svg').getroot()
            head=svg.find("s:g[@id='head']",ns)
            assert f'translate({-amount}' in head.get('transform')
assert 'duration: 0.12' in model and 'duration: 0.16' in model
assert 'event.result == .block, event.sequence > lastSequence' in model
render=scene[scene.index('private func applyFrames'):scene.index('private func applyImpactEmphasis')]
assert render.index('blockFeedback.isActive && blockRecoilAssetsAvailable')<render.index('boxerB.texture = guardB[')
assert 'boxerB.texture = textures[blockFeedback.frameIndex]' in render
for forbidden in ['boxerB.position','rootB.position','boxerB.xScale','boxerB.yScale','blockFeedbackNode']:
    assert forbidden not in render
assert 'blockFeedbackNode' not in scene and 'applyBlockFeedback()' not in scene
assert 'if event.defenderID == .orange && blockRecoilAssetsAvailable' in scene
assert 'Block recoil assets missing' in view and '8D ' in view
for file in (root/'Boxer0').glob('*.swift'):
    code=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"','',file.read_text(encoding='utf-8'))
    depth=0
    for c in code:
        depth+=(c=='{')-(c=='}');assert depth>=0,file
    assert depth==0,file
print('PASS: six recoil assets, actual upper-body displacement, fixed lower-body pixels/baseline, exact held-guard recovery, texture priority, no root translation/ring fallback and brace nesting')
compiler=shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary=Path(folder)/'block-feedback-checks'
        files=['Boxer0/JabPlayback.swift','Boxer0/PunchContact.swift','Boxer0/HitReactionPlayback.swift','Tests/BlockFeedbackChecks.swift']
        subprocess.run([compiler]+[str(root/p) for p in files]+['-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else:
    print('SKIP: Swift behavioral checks; swiftc/Xcode unavailable. Ordinary-speed iPhone visual validation remains pending.')
