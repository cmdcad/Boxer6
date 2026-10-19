"""Check config against source SVGs and execute actual Swift contact tests if available."""
from pathlib import Path
import math
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT/'Boxer0/PunchContact.swift').read_text(encoding='utf-8')
scene = (ROOT/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
ns = {'s':'http://www.w3.org/2000/svg'}
centers = {}
for kind,index,hand in [('jab',3,'lead'),('cross',4,'rear')]:
    group = ET.parse(ROOT/f'IdleAnimation/frames/{kind}_a_{index}.svg').getroot().find(f"s:g[@id='glove-{hand}']",ns)
    ellipse = group.find('s:ellipse',ns)
    dx,dy = map(float,re.search(r'translate\(([-\d.]+) ([-\d.]+)\)',group.attrib['transform']).groups())
    center = (float(ellipse.attrib['cx'])+dx,float(ellipse.attrib['cy'])+dy)
    configured = tuple(map(float,re.search(rf'var {kind}Center = CGPoint\(x: ([\d.]+), y: ([\d.]+)\)',source).groups()))
    assert center == configured
    centers[kind] = center
    print(f'PASS: {kind} center {center} matches the actual attacking SVG ellipse + transform')
# Independent reach analysis in canvas units (uniform scene scale cancels).
body_min = float(re.search(r'bodyMinX: CGFloat = ([\d.]+)',scene).group(1))
body_max = float(re.search(r'bodyMaxX: CGFloat = ([\d.]+)',scene).group(1))
gap_factor = float(re.search(r'minimumBodyGapFactor: CGFloat = ([\d.]+)',scene).group(1))
minimum_roots = 2*(body_max-256)+(body_max-body_min)*gap_factor
x,y,w,h = map(float,re.search(r'defenderTarget = CGRect\(x: ([\d.]+), y: ([\d.]+), width: ([\d.]+), height: ([\d.]+)\)',source).groups())
for kind,center in centers.items():
    radius = float(re.search(rf'var {kind}Radius: CGFloat = ([\d.]+)',source).group(1))
    max_reach = (center[0]-256)+(x+w-256)+radius
    assert y <= center[1] <= y+h
    assert minimum_roots <= max_reach
    assert 338.78 > max_reach # Original full-silhouette spacing could never hit.
    print(f'PASS: {kind} reach {max_reach:g} exceeds approved min root distance {minimum_roots:g}')
    for width,height in [(568,186),(667,241),(844,235),(932,275),(1024,634)]:
        scale = min(height*.88,width*.46,420)/512
        initial_separation = width*.4/scale
        assert initial_separation > max_reach
        min_root = 20+(256-149)*scale
        max_root = .7*width-minimum_roots*scale
        assert min_root < max_root
        assert max_root+(398-256)*scale < width-20
        assert .7*width-(256-149)*scale > 20
for folder in ['Boxer0','Tests']:
    for file in (ROOT/folder).glob('*.swift'):
        text = file.read_text(encoding='utf-8')
        assert not re.search(r'\b(?:if|guard|while)\s+let\s+\w+\s*\{',text)
        assert text.count('{') == text.count('}'),file
assert scene.count('contactTracker.evaluate(') == 1
assert 'if event.contact && health.canExchangePunches {' in scene
assert 'contactTracker.begin(kind)' in scene and 'contactTracker.finish()' in scene
assert 'SKPhysicsBody' not in source+scene
project = (ROOT/'Boxer0.xcodeproj/project.pbxproj').read_text()
assert project.count('PunchContact.swift in Sources') == 2
assert project.count('PunchContact.swift */') == 3
print('PASS: five viewport reach/boundary checks, explicit bindings, contact-only evaluation, no physics, source membership')
compiler = shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary = Path(folder)/'contact-checks'
        subprocess.run([compiler,str(ROOT/'Boxer0/JabPlayback.swift'),str(ROOT/'Boxer0/PunchContact.swift'),
                        str(ROOT/'Tests/PunchContactChecks.swift'),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else:
    print('SKIP: Swift geometry/contact tests; swiftc unavailable. Run on Mac:')
    print('swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Tests/PunchContactChecks.swift -o /tmp/contact-checks && /tmp/contact-checks')
