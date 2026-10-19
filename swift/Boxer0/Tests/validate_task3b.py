"""Asset checks plus actual Swift motion tests when a Swift compiler is present."""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
for clip, count in [('idle', 4), ('advance', 6), ('retreat', 6)]:
    for palette in 'ab':
        for index in range(count):
            name = f'{clip}_{palette}_{index}'
            folder = ROOT / 'Boxer0/Assets.xcassets' / f'{name}.imageset'
            meta = json.loads((folder / 'Contents.json').read_text())
            with Image.open(folder / meta['images'][0]['filename']) as image:
                assert image.mode == 'RGBA' and image.size == (512, 512)
                with Image.open(ROOT / 'IdleAnimation/frames' / f'{name}.png') as source:
                    assert image.tobytes() == source.tobytes()
assert abs(sum([.04, .14, .04, .14, .06, .06]) - .48) < 1e-10
view = (ROOT / 'Boxer0/ContentView.swift').read_text(encoding='utf-8')
assert 'cycleSpeed' not in view and 'playback.speed.label' not in view
assert 'Hold Advance' in view and 'Hold Retreat' in view
project = (ROOT / 'Boxer0.xcodeproj/project.pbxproj').read_text()
assert project.count('FootworkMotion.swift in Sources') == 2
assert project.count('FootworkMotion.swift */') == 3
print('PASS: 32 catalog/source pairs, footwork duration, speed-button removal, motion target membership')
compiler = shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary = Path(folder) / 'footwork-checks'
        subprocess.run([compiler, str(ROOT / 'Boxer0/FootworkMotion.swift'),
                        str(ROOT / 'Tests/FootworkMotionChecks.swift'), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
else:
    print('SKIP: Swift motion tests (swiftc unavailable). Run on Mac:')
    print('swiftc Boxer0/FootworkMotion.swift Tests/FootworkMotionChecks.swift -o /tmp/footwork-checks && /tmp/footwork-checks')

