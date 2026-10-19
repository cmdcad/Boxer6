from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
model = (root/'Boxer0/PunchContact.swift').read_text()
scene = (root/'Boxer0/IdleTestScene.swift').read_text()
view = (root/'Boxer0/ContentView.swift').read_text()
assert 'static let jab = 5' in model and 'static let cross = 10' in model
assert 'current -= min(current, max(0, amount))' in model
assert 'guard event.sequence > lastContactSequence' in model
assert 'guard event.result == .hit' in model
assert scene.count('health.receive(contact)') == 1
handler = scene[scene.index('private func handlePunchEvent'):scene.index('private func advanceOrange')]
assert handler.index('contactTracker.evaluate(') < handler.index('health.receive(contact)') < handler.index('reaction.receive(')
reset = scene[scene.index('func resetHealth()'):scene.index('var contactGeometry')]
assert 'health.reset()' in reset
# Task 7B extends reset to cancel animations while preserving counters/positions.
for forbidden in ['position =', 'contactTracker =', 'health =']:
    assert forbidden not in reset
assert 'ProgressView(value: Double(value), total: Double(maximum))' in view
assert 'Text("\\(value)/\\(maximum)")' in view
assert 'Button("Reset Health", action: playback.resetHealth)' in view
assert '7B ' in view
assert view.index('healthHUD\n            SpriteView') > 0
print('PASS: damage/contact wiring, deduplication guard, bounded health, isolated reset, numeric/proportional HUD source checks')
compiler = shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary = Path(folder)/'health-checks'
        subprocess.run([compiler, str(root/'Boxer0/JabPlayback.swift'), str(root/'Boxer0/PunchContact.swift'), str(root/'Tests/HealthDamageChecks.swift'), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
else:
    print('SKIP: behavioral Swift checks; swiftc unavailable. Run HealthDamageChecks.swift on Mac.')
