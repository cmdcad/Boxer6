"""Structural checks, not a substitute for compiling/running XCTest in Xcode."""
from pathlib import Path
import json
import re
import shutil
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
project = (root/'Boxer0.xcodeproj/project.pbxproj').read_text(encoding='utf-8')
clean = re.sub(r'/\*[\s\S]*?\*/|//[^\n]*', '', project)
tokens = re.findall(r'"(?:\\.|[^"\\])*"|[{}()=;,]|[^\s{}()=;,]+', clean)
index = 0
def take(expected=None):
    global index
    value = tokens[index]; index += 1
    assert expected is None or value == expected, (expected, value)
    return value
def parse():
    if tokens[index] == '{':
        take('{'); result = {}
        while tokens[index] != '}':
            key = take(); take('='); value = parse(); take(';')
            assert key not in result, key
            result[key] = value
        take('}'); return result
    if tokens[index] == '(':
        take('('); result = []
        while tokens[index] != ')':
            result.append(parse())
            if tokens[index] == ',': take(',')
        take(')'); return result
    value = take()
    return json.loads(value) if value.startswith('"') else value
pbx = parse()
assert index == len(tokens)
objects = pbx['objects']
for token in tokens:
    if re.fullmatch('[A-F0-9]{24}', token): assert token in objects, token
targets = [obj for obj in objects.values() if obj.get('isa') == 'PBXNativeTarget']
assert len(targets) == 2
test_target = next(obj for obj in targets if obj['name'] == 'Boxer0Tests')
assert test_target['productType'] == 'com.apple.product-type.bundle.unit-test'
scheme = ET.parse(root/'Boxer0.xcodeproj/xcshareddata/xcschemes/Boxer0.xcscheme')
assert scheme.find('.//TestableReference/BuildableReference').attrib['BlueprintName'] == 'Boxer0Tests'
assert scheme.find('.//TestAction').attrib['buildConfiguration'] == 'Debug'
scene = (root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
tests = (root/'Boxer0Tests/CombatTests.swift').read_text(encoding='utf-8')
model = (root/'Boxer0/JabPlayback.swift').read_text(encoding='utf-8')
assert 'advanceSimulation(by: dt)' in scene
assert 'scene.advanceSimulation(by: step)' in tests
assert 'var randomDraw: (() -> Double)?' in model
assert 'let capacity = 160' in model and 'var enabled = false' in model
assert 'combatInvariantViolations' in scene and 'INVARIANT_FAILURE' in scene
assert 'Thread.sleep' not in tests and 'Timer' not in tests
for file in list((root/'Boxer0').glob('*.swift')) + list((root/'Boxer0Tests').glob('*.swift')):
    code = re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"', '', file.read_text(encoding='utf-8'))
    depth = 0
    for char in code:
        depth += (char == '{') - (char == '}')
        assert depth >= 0, file
    assert depth == 0, file
methods = re.findall(r'func (test\w+)\(', tests)
assert len(methods) == len(set(methods))
print(f'PASS: parsed project objects/references, shared Debug test scheme, production scheduler driver, RNG injection, bounded log, invariant hooks, Swift brace structure; {len(methods)} XCTest methods discovered')
print('SKIP: XCTest build/execution and device rendering; Xcode/Apple SDK unavailable on this host.')
print('Compilation checks: NOT RUN. XCTest passed/failed: NOT RUN (not inferred from structural checks).')
