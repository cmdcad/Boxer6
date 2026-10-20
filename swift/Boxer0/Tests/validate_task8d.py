from pathlib import Path
import json
import re
import shutil
import subprocess
import tempfile
from PIL import Image
root=Path(__file__).resolve().parents[1]
scene=(root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
view=(root/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
manifest=json.loads((root/'IdleAnimation/player_guard_manifest.json').read_text())
assert len(manifest['variants'])==9
for item in manifest['variants']:
    src=Image.open(root/f"IdleAnimation/frames/{item['source']}.png").convert('RGBA')
    dst=Image.open(root/f"IdleAnimation/frames/{item['target']}.png").convert('RGBA')
    assert src.getchannel('A').tobytes()==dst.getchannel('A').tobytes() and dst.size==(512,512)
    assert dst.tobytes()==Image.open(root/f"Boxer0/Assets.xcassets/{item['target']}.imageset/{item['target']}.png").tobytes()
assert 'private var blueGuard = GuardPlayback()' in scene
assert 'private var blueBlockFeedback = BlockFeedbackPlayback()' in scene
sync=scene[scene.index('private func syncBlueGuard'):scene.index('private func advanceBlueDefense')]
assert 'guardHeld && canHoldGuard && !punch.isActive && !blueVisualBusy' in sync
assert 'let eligible = guardHeld && canHoldGuard && !punch.isActive && !blueVisualBusy && !blueGuard.isSelected' not in sync
assert ': (blueGuardEffectiveAtContact ?? blueGuard.isEffective)' in scene
assert 'event.defenderID == .blue && playerGuardAssetsAvailable' in scene
assert 'B\\(cpuContactTracker.blocks)' in scene
# Task 10A supersedes guard-entry braking and slower raised-guard movement; entry still brakes.
assert 'enteringGuard ? 0.0 : Double(movementDirection ?? 0)' in scene
assert 'speedMultiplier: blueGuard.isEffective ? guardedMovementMultiplier : 1' in scene
assert 'if event.defenderID == .blue { motion.stop() } else { stopCPUFootwork() }' in scene
assert 'guardInputGeneration += 1' in scene
assert 'clearHeldInput(); clearBlueGuardInput(); motion.stop()' in scene
assert 'blueBlockFeedback.kind == .cross ? blockCrossA : blockJabA' in scene
control=view[view.index('private var playerGuardControl'):view.index('func punchButton')]
assert 'HoldTouchSurface(title: "Guard"' in control
assert 'inputGeneration: playback.guardInputGeneration' in control
assert 'playback.setGuardHeld(held)' in control and 'Button(' not in control
assert 'Blue Guard:' in view and '10A ' in view
for file in (root/'Boxer0').glob('*.swift'):
    code=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"','',file.read_text(encoding='utf-8'))
    depth=0
    for c in code:
        depth+=(c=='{')-(c=='}');assert depth>=0,file
    assert depth==0,file
print('PASS:9 alpha-identical variants, shared guard/recoil, held-touch generation, attack eligibility, defender-specific BLOCK, guard-entry braking and slower raised-guard movement, lifecycle cleanup, diagnostics and brace nesting')
compiler=shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary=Path(folder)/'player-guard-checks'
        files=['Boxer0/JabPlayback.swift','Boxer0/PunchContact.swift','Boxer0/HitReactionPlayback.swift','Boxer0/FootworkMotion.swift','Tests/PlayerGuardChecks.swift']
        subprocess.run([compiler]+[str(root/p) for p in files]+['-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else: print('SKIP: executable Swift checks; swiftc/Xcode unavailable. iPhone touch/guard validation pending.')
