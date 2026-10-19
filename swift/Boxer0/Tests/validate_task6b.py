from pathlib import Path
import shutil
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
scene = (root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
model = (root/'Boxer0/PunchContact.swift').read_text(encoding='utf-8')
view = (root/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
assert 'guard state == .standing, health.current == 0' in model
assert 'defeatRecorded = true' in model and 'defeatRecorded = false' in model
assert 'guard canExchangePunches else { return false }' in model
assert 'health.canExchangePunches && jabAssetsAvailable' in scene
assert 'health.canExchangePunches && crossAssetsAvailable' in scene
handler = scene[scene.index('private func handlePunchEvent'):scene.index('private func advanceOrange')]
assert handler.index('if event.contact && health.canExchangePunches') < handler.index('contactTracker.evaluate(')
# 7B.1 now allows the accepted final HIT recoil before the fall.
assert 'if reactionAssetsAvailable && reaction.receive' in handler
orange = scene[scene.index('private func advanceOrange'):scene.index('private var movementDirection')]
assert orange.count('else if orangeCombatState == .standing') == 2
assert orange.count('if reaction.isActive') == 2
reset = scene[scene.index('func resetHealth()'):scene.index('var contactGeometry')]
for expected in ['health.reset()', 'punch.cancel()', 'contactTracker.finish()', 'reaction.cancel()', 'orangeFrame = 0', 'applyFrames()']:
    assert expected in reset
for forbidden in ['rootA.', 'rootB.', 'contactTracker =', 'isPlaying =']:
    assert forbidden not in reset
assert 'DEFEATED' in view and 'state == .defeated' in view
assert '7B.1 ' in view
print('PASS: eligibility before contact counters, one-shot defeat model, blocked post-defeat contacts, standing-only idle/step, clean reset, HUD source checks')
compiler = shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary = Path(folder)/'defeat-checks'
        sources = ['Boxer0/JabPlayback.swift','Boxer0/PunchContact.swift','Boxer0/HitReactionPlayback.swift','Tests/DefeatStateChecks.swift']
        subprocess.run([compiler] + [str(root/p) for p in sources] + ['-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else:
    print('SKIP: Swift behavioral tests; swiftc unavailable. Xcode/device verification pending.')
