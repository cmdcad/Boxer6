from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
scene=(ROOT/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
model=(ROOT/'Boxer0/HitReactionPlayback.swift').read_text(encoding='utf-8')
view=(ROOT/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
assert 'impactEmphasisEnabled = false' in scene
assert 'reaction.receive(contact.result, from: contact.kind)' in scene
assert 'private(set) var profile: HitFeedbackProfile?' in model
assert 'guard result == .hit else { return false }' in model
assert 'static let duration = 0.24' in model
assert 'static let frameDuration = 0.06' in model
assert 'punch == .jab ? 0.04 : 0.075' in model
assert 'var emphasisDuration: Double { 0.06 }' in model
assert 'elapsed += dt' in model
assert 'profile = nil' in model
helper=scene[scene.index('private func applyImpactEmphasis'):scene.index('private func canvasTransform')]
assert 'colorBlendFactor' in helper and 'reaction.emphasisAmount' in helper
for forbidden in ['.position', '.xScale', '.yScale', '.size', 'SKAction', 'DispatchQueue']:
    assert forbidden not in helper
assert '5C ·' in view and 'playback.orangeProfile' in view
assert scene.count('contactTracker.evaluate(')==1
print('PASS: profiles, 240 ms shared clip, default-off 60 ms emphasis, no transform/geometry mutation, once-only contact and triggering punch HUD')
compiler=shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary=Path(folder)/'feedback-checks'
        subprocess.run([compiler,str(ROOT/'Boxer0/JabPlayback.swift'),str(ROOT/'Boxer0/PunchContact.swift'),
            str(ROOT/'Boxer0/HitReactionPlayback.swift'),str(ROOT/'Tests/HitFeedbackChecks.swift'),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else:
    print('SKIP: Swift feedback tests; swiftc unavailable. On Mac:')
    print('swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Boxer0/HitReactionPlayback.swift Tests/HitFeedbackChecks.swift -o /tmp/feedback-checks && /tmp/feedback-checks')
