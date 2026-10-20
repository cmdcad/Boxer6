"""Source wiring checks. Execute the 40 XCTest methods on Mac for behavior."""
from pathlib import Path
import subprocess
import sys
import re

root = Path(__file__).resolve().parents[1]
scene = (root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
motion = (root/'Boxer0/FootworkMotion.swift').read_text(encoding='utf-8')
tests = (root/'Boxer0Tests/CombatTests.swift').read_text(encoding='utf-8')
assert 'var guardedMovementMultiplier = 0.55' in scene
assert 'speedMultiplier: Double = 1' in motion
assert 'braking || reducingSpeed ? deceleration : acceleration' in motion
for guard in ['blueGuard', 'guardPlayback']:
    assert f'speedMultiplier: {guard}.isEffective ? guardedMovementMultiplier : 1' in scene
assert 'advanceCPUFootwork(dt, guardEntry: !wasEffective)' in scene
assert 'advanceSimulation(by: simulationStepDuration, stepping: true)' in scene
assert 'advanceSimulation(by: marker, stepping: stepping)' in scene
render = scene[scene.index('private func applyFrames'):scene.index('private func applyImpactEmphasis')]
assert render.index('blueGuard.isSelected') < render.index('boxerA.texture = blueTextures')
assert render.index('guardPlayback.isSelected') < render.index('orangeLocomotionClip == .advance')
group = tests[tests.index('final class GuardedMovementTests'):]
assert len(re.findall(r'func test\w+\(',group)) == 16
assert len(re.findall(r'func test\w+\(',tests)) == 40
print('PASS: shared speed modifier/deceleration, both guard movement paths, guard-over-walk texture priority, marker-position splitting, shared movement stepping; 16 new/40 total XCTest methods wired')
for name in ['validate_task9c.py','validate_task9b1.py','validate_task8a.py','validate_task8b.py','validate_recovery_assets.py']:
    subprocess.run([sys.executable,str(root/'Tests'/name)],check=True)
print('SKIP: 40-test XCTest execution and manual iPhone validation; Apple SDK/Xcode unavailable here.')
