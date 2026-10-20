from active_art import frame
"""Source/asset checks only; scene rendering requires Xcode/device validation."""
from pathlib import Path
from PIL import Image
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
scene = (root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
punch = (root/'Boxer0/JabPlayback.swift').read_text(encoding='utf-8')
render = scene[scene.index('private func applyFrames()'):scene.index('private func applyImpactEmphasis()')]
assert 'var recoveryPoseFrame: Int { self == .jab ? 4 : 5 }' in punch
for color in 'ab':
    for kind, index, contact in [('jab', 4, 3), ('cross', 5, 4)]:
        images = [Image.open(frame(f'{kind}_{color}_{i}')).convert('RGBA') for i in [index, 0, contact]]
        pose, ready, hit = images
        assert pose.size == (512, 512)
        assert pose.tobytes() != ready.tobytes() and pose.tobytes() != hit.tobytes()
        assert pose.crop((0, 300, 512, 512)).tobytes() == ready.crop((0, 300, 512, 512)).tobytes()
        asset = root/f'Boxer0/Assets.xcassets/{kind}_{color}_{index}.imageset/{kind}_{color}_{index}.png'
        assert Image.open(asset).convert('RGBA').tobytes() == pose.tobytes()
for physical, sprite, guard, reaction in [('blueRecovery','boxerA','blueGuard','blueReaction'), ('orangeRecovery','boxerB','guardPlayback','reaction')]:
    branch = render.index(f'else if {physical}.isRecovering')
    assert render.index(f'{reaction}.isActive') < branch < render.index(f'else if {guard}.isSelected')
    assert f'? dedicated[0] : textures[{physical}.kind.recoveryPoseFrame]' in render
    assert f'return {physical}.diagnosticLabel' in scene
assert 'ceil(remaining * 1000' in punch
assert 'blueActionLabel + orangeActionLabel != lastPublishedActions' in scene
assert 'cpuEnabled && cpuOffense.state != .ready' in scene
assert '.position =' not in render and '.xScale =' not in render
print('PASS: withdrawal poses, integrated textures, fixed lower body, shared recovery-driven rendering, priority and countdown publication')
for name in ['validate_task9a.py', 'validate_task9b.py', 'validate_task8c.py', 'validate_task8d.py']:
    subprocess.run([sys.executable, str(root/'Tests'/name)], check=True)
