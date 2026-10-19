"""Source/SVG regression and independent scale-mismatch reproduction.

This does not execute the Swift runtime; PunchContactChecks.swift does that on Mac.
"""
from pathlib import Path
import math
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(ROOT/'Tests/validate_task5a.py')],check=True)
scene=(ROOT/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
contact=(ROOT/'Boxer0/PunchContact.swift').read_text(encoding='utf-8')
view=(ROOT/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
assert 'spacing.horizontalLimits(attacker: canvasTransform(for: boxerA)' in scene
assert 'node.convert(.zero, to: self)' in scene
assert 'node.size = CGSize(width: Self.spriteCanvas, height: Self.spriteCanvas)' in scene
assert 'rootA.addChild(boxerA)' in scene and 'rootB.addChild(boxerB)' in scene
assert 'if boxerA.size != canvasSize' not in scene
assert 'CGPoint(x: 1, y: 0)' in scene and 'CGPoint(x: 0, y: 1)' in scene
assert 'rootB.xScale = -fighterScale' in scene
assert 'boxerA.xScale = fighterScale' not in scene
assert 'node.size.width / Self.spriteCanvas' not in scene
assert 'contactDistanceGuide' in scene and 'latestDistanceText' in view
assert '5A.2' in view
assert 'FighterSpacing' in contact and 'signedGap' in contact
# Unchanged geometry. A hit cannot be created by inflating the target/radius.
assert 'jabCenter = CGPoint(x: 384.5, y: 189)' in contact
assert 'crossCenter = CGPoint(x: 378, y: 186)' in contact
assert 'jabRadius: CGFloat = 20' in contact and 'crossRadius: CGFloat = 18' in contact
assert 'defenderTarget = CGRect(x: 220, y: 127, width: 88, height: 173)' in contact
print('PASS: rendered transform shared by spacing/contact, normalized canvas, distance diagnostics, unchanged contact geometry')
# Independent 1D proof with both glove Ys inside the target vertical interval.
# Same root baseline means Y conversion cancels; signed edge gap = roots - reach.
for name,reach in [('Jab',200.5),('Cross',192.0)]:
    for factor in [.5,1,2]:
        scale=.32*factor
        legal_roots=174.4*scale
        assert legal_roots < reach*scale
        for roots,expected in [(400,'MISS'),(reach+.1,'MISS'),(reach,'HIT'),(reach-.1,'HIT'),(174.4,'HIT')]:
            gap=(roots-reach)*scale
            result='HIT' if gap<=1e-9 else 'MISS'
            assert result==expected
    old_roots=174.4*.32
    half_scale_reach=reach*.16
    assert old_roots>half_scale_reach
    corrected_roots=174.4*.16
    assert corrected_roots<half_scale_reach
    print(f'{name}: far MISS; threshold+0.1 MISS; tangent HIT; threshold-0.1 HIT; minimum spacing HIT')
    print(f'  mixed-scale reproduction: roots {old_roots:.3f} pt > reach {half_scale_reach:.3f} pt (MISS); shared-scale roots {corrected_roots:.3f} pt (HIT)')
print('Video confirms transform asymmetry (Ax .320 vs Bx -.102) and a blue sizing regression; 5A.2 root/child correction still needs device verification.')
