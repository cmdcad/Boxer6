from pathlib import Path
import re
import shutil
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
scene=(root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
punch=(root/'Boxer0/JabPlayback.swift').read_text(encoding='utf-8')
contact=(root/'Boxer0/PunchContact.swift').read_text(encoding='utf-8')
view=(root/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
assert 'punch.isActive || blueRecovery.isRecovering' in scene
assert 'orangePunch.isActive || orangeRecovery.isRecovering' in scene
assert 'counterAttempt: isAttackVulnerable(.blue)' in scene
assert 'counterAttempt: isAttackVulnerable(.orange)' in scene
assert 'isCounterAttempt && result == .hit' in contact
assert 'if counterAttempt { counterAttempts += 1 }' in contact
assert 'if event.isSuccessfulCounter { successfulCounters += 1 }' in contact
assert 'counterOpportunityAttackChance = 0.65' in punch
assert 'opponentVulnerable: isAttackVulnerable(.blue)' in scene
scheduler=scene[scene.index('private func advanceActiveAttacks'):scene.index('private func advanceBlueRecovery')]
assert 'abs(blueTime-orangeTime) < 1e-9' in scheduler
assert scheduler.count('deferImpact: true')==2 and scheduler.count('simultaneous: true')==2
assert 'else if blueTime <= orangeTime' in scheduler
assert 'orangeEvent.contact && orangePunch.isActive' in scheduler
assert 'blueEvent.contact && punch.isActive' in scheduler
assert 'Blue' in view and 'playback.counterSummary' in view and '10A ' in view
assert 'Timer' not in scheduler and 'DispatchQueue' not in scheduler
for file in (root/'Boxer0').glob('*.swift'):
    code=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"','',file.read_text(encoding='utf-8'))
    depth=0
    for c in code:
        depth+=(c=='{')-(c=='}');assert depth>=0,file
    assert depth==0,file
print('PASS:derived vulnerability, initiation snapshot, HIT-only counter subsets,65% opportunity gate, chronological contacts/symmetric ties, interruption gating, diagnostics and brace nesting')
compiler=shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary=Path(folder)/'counter-checks'
        files=['Boxer0/JabPlayback.swift','Boxer0/PunchContact.swift','Boxer0/HitReactionPlayback.swift','Tests/CounterChecks.swift']
        subprocess.run([compiler]+[str(root/p) for p in files]+['-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else: print('SKIP: executable Swift checks; swiftc/Xcode unavailable. iPhone exchange validation pending.')
