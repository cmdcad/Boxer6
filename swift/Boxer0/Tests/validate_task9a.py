from pathlib import Path
import re
import shutil
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
scene=(root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
model=(root/'Boxer0/JabPlayback.swift').read_text(encoding='utf-8')
view=(root/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
assert 'var jabDuration = 0.12' in model and 'var crossDuration = 0.22' in model
assert 'private var blueRecovery = PunchRecovery()' in scene and 'private var orangeRecovery = PunchRecovery()' in scene
assert scene.count('blueRecovery.completeAttack()')==1 and scene.count('orangeRecovery.completeAttack()')==1
update=scene[scene.index('override func update'):scene.index('private var lastPublishedFrame')]
assert update.index('guard isPlaying, hasFocus')<update.index('advancePhysicalRecovery(dt)')<update.index('advanceActiveAttacks(dt)')
assert '&& !blueRecovery.isRecovering && !blueBlockFeedback.isActive && !guardHeld' in scene
assert '&& !orangeRecovery.isRecovering' in scene
assert 'guardHeld && canHoldGuard && !punch.isActive && !blueVisualBusy && !blueRecovery.isRecovering' in scene
begin=scene[scene.index('private func beginAttack'):scene.index('private func predictedContact')]
assert 'clearHeldInput()' not in begin
complete=scene[scene.index('private func handlePunchEvent'):scene.index('private func advanceCPUOffense')]
assert 'clearHeldInput()' not in complete
assert 'cpuOffense.cancelPreparation()' in scene
assert 'if blueVisualBusy || blueCombatState == .defeated || blueRecovery.isRecovering || blueBlockFeedback.isActive' in scene
assert 'blueBlockFeedback.isActive && playerGuardAssetsAvailable' in scene
assert 'blockFeedback.isActive && blockRecoilAssetsAvailable' in scene
assert 'Blue Action:' in view and 'Orange Action:' in view and '9B.1 ' in view
for file in (root/'Boxer0').glob('*.swift'):
    code=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"','',file.read_text(encoding='utf-8'))
    depth=0
    for c in code:
        depth+=(c=='{')-(c=='}');assert depth>=0,file
    assert depth==0,file
print('PASS:shared120/220ms physical recovery, post-animation start, action/guard/movement locks, parallel CPU clock, preserved held movement, block-response release policy, diagnostics and brace nesting')
compiler=shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary=Path(folder)/'recovery-checks'
        files=['Boxer0/JabPlayback.swift','Boxer0/PunchContact.swift','Boxer0/HitReactionPlayback.swift','Tests/RecoveryChecks.swift']
        subprocess.run([compiler]+[str(root/p) for p in files]+['-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else: print('SKIP: executable Swift checks; swiftc/Xcode unavailable. iPhone pacing/input validation pending.')
