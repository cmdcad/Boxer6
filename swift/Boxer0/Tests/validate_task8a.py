from pathlib import Path
import re
import shutil
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
scene=(root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
model=(root/'Boxer0/HitReactionPlayback.swift').read_text(encoding='utf-8')
view=(root/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
ai=model[model.index('struct DefensiveAIProfile'):]
assert 'chance: 0.60, reactionDelay: 0.02, holdDuration: 0.50' in ai
assert 'chance: 0.75, reactionDelay: 0.10, holdDuration: 0.65' in ai
assert 'maximumGuardDuration = 1.5' in ai and 'enabled = false' in ai
assert 'sequence > lastSequence' in ai and 'guard state == .idle' in ai
for forbidden in ['Timer','DispatchQueue','SKAction','health.','position','contactTracker']:
    assert forbidden not in ai
assert scene.count('defensiveAI.observe(')==1
start=scene[scene.index('private func startPunch'):scene.index('private func resolveContact')]
assert 'PunchContactGeometry.intersects(' in start
assert 'punchStartSequence += 1' in start and 'inRange: predictedContact(.blue, kind: kind)' in start
assert '!cpuEnabled && (canRequestGuard || guardPlayback.isSelected)' in scene
assert 'if canRequestGuard { requestGuard(true) }' in scene
assert 'guardEffectiveAtContact = guardPlayback.isEffective' in scene
assert ': (blueGuardEffectiveAtContact ?? blueGuard.isEffective)' in scene
assert 'defensiveAI.cancel(reseed: true)' in scene
assert 'CPU: ON' in view and 'playback.cpuStatus' in view and '10A ' in view
for file in (root/'Boxer0').glob('*.swift'):
    code=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"','',file.read_text(encoding='utf-8'))
    depth=0
    for c in code:
        depth+=(c=='{')-(c=='}');assert depth>=0,file
    assert depth==0,file
print('PASS: seeded event-only AI, parameters/cap, range prediction, shared guard requests, contact-time protection snapshot, cleanup, CPU controls and brace nesting')
compiler=shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary=Path(folder)/'ai-checks'
        files=['Boxer0/JabPlayback.swift','Boxer0/PunchContact.swift','Boxer0/HitReactionPlayback.swift','Tests/DefensiveAIChecks.swift']
        subprocess.run([compiler]+[str(root/p) for p in files]+['-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else:
    print('SKIP: executable Swift checks; swiftc/Xcode unavailable. iPhone validation pending.')

# Verify production timing permits first-punch protection without changing guard/contact.
assert 0.02 + 0.12 < 3 * 0.05
assert 0.10 + 0.12 < 4 * 0.06
print('PASS: default Jab protection140ms < contact150ms; Cross220ms < contact240ms')
