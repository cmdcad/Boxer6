from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
scene=(root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
model=(root/'Boxer0/HitReactionPlayback.swift').read_text(encoding='utf-8')
view=(root/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
assert 'duration: 0.08, radius: 18, opacity: 0.65' in model
assert 'duration: 0.11, radius: 23, opacity: 0.85' in model
fx=model[model.index('struct BlockFeedbackPlayback'):]
assert 'event.result == .block, event.sequence > lastSequence' in fx
assert 'event.defender.scenePoint(fromImage:' in fx
assert 'kind = event.kind' in fx and 'elapsed = 0' in fx
# Verify documented anchors against actual authored guard-glove geometry.
svg=ET.parse(root/'IdleAnimation/frames/guard_b_2.svg').getroot()
ns={'s':'http://www.w3.org/2000/svg'}
for hand,expected in [('rear',(253,150)),('lead',(303.5,152))]:
    group=svg.find(f"s:g[@id='glove-{hand}']",ns)
    dx,dy=map(float,re.search(r'translate\(([^)]+)\)',group.get('transform')).group(1).split())
    ellipse=group.find('s:ellipse',ns)
    assert (float(ellipse.get('cx'))+dx,float(ellipse.get('cy'))+dy)==expected
update=scene[scene.index('override func update'):scene.index('private var lastPublishedFrame')]
assert update.index('guard isPlaying, hasFocus')<update.index('advanceBlockFeedback(dt)')<update.index('handlePunchEvent(event)')
step=scene[scene.index('func stepFrame()'):scene.index('func setSpeed(')]
assert step.index('advanceBlockFeedback(effectStep)')<step.index('handlePunchEvent(event)')
assert scene.count('blockFeedback.receive(contact)')==1
for start,end in [('func resetHealth()','var contactGeometry'),('func startRise()','private(set) var guardAssetsAvailable'),('private func completeOrangeRecovery','private func startKnockdownIfReady')]:
    assert 'blockFeedback.cancel()' in scene[scene.index(start):scene.index(end)]
assert 'if !guardPlayback.isSelected { blockFeedback.cancel() }' in scene
render=scene[scene.index('private func applyBlockFeedback'):scene.index('private func applyImpactEmphasis')]
assert 'transform.scenePoint(fromImage: blockFeedback.imageAnchor)' in render
assert 'transform.sceneRadius' in render and 'node.path = nil' in render
for forbidden in ['boxerB.position','boxerB.color','rootA.','rootB.','showsGuides','SKAction','Timer','DispatchQueue']:
    assert forbidden not in render
assert 'Block FX:' in view and '7B ' in view
for file in (root/'Boxer0').glob('*.swift'):
    raw=file.read_text(encoding='utf-8')
    code=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"','',raw)
    depth=0
    for c in code:
        depth+=(c=='{')-(c=='}');assert depth>=0,file
    assert depth==0,file
print('PASS: profiles, authored glove anchors, contact-only event, scene-clock order, cleanup, isolated localized node, real FX diagnostics and Swift brace nesting')
compiler=shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary=Path(folder)/'block-feedback-checks'
        files=['Boxer0/JabPlayback.swift','Boxer0/PunchContact.swift','Boxer0/HitReactionPlayback.swift','Tests/BlockFeedbackChecks.swift']
        subprocess.run([compiler]+[str(root/p) for p in files]+['-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else:
    print('SKIP: Swift behavioral checks; swiftc/Xcode unavailable. iPhone visual validation pending.')
