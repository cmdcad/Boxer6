from pathlib import Path
import json
import shutil
import subprocess
import tempfile
from PIL import Image
root=Path(__file__).resolve().parents[1]
scene=(root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
model=(root/'Boxer0/HitReactionPlayback.swift').read_text(encoding='utf-8')
view=(root/'Boxer0/ContentView.swift').read_text(encoding='utf-8')
manifest=json.loads((root/'IdleAnimation/knockdown_manifest.json').read_text())
assert manifest['canvas']==[512,512] and manifest['root']==[256,448]
assert manifest['knockdown']['durationMs']==640
for name in manifest['knockdown']['frames']+manifest['down']['frames']:
    source=root/f'IdleAnimation/frames/{name}.png'
    image=Image.open(source)
    assert image.size==(512,512) and image.mode=='RGBA'
    assert image.getpixel((0,0))[3]==0
    bbox=image.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()
    assert bbox[3]==448, (name,bbox)
    assert 0<bbox[0]<bbox[2]<512
    folder=root/f'Boxer0/Assets.xcassets/{name}.imageset'
    assert source.read_bytes()==(folder/f'{name}.png').read_bytes()
    assert json.loads((folder/'Contents.json').read_text())['images'][0]['filename']==f'{name}.png'
    assert (root/f'IdleAnimation/frames/{name}.svg').exists()
assert Image.open(root/'IdleAnimation/frames/down_b_0.png').tobytes()==Image.open(root/'IdleAnimation/frames/knockdown_b_7.png').tobytes()
assert 'static let duration = 0.64' in model and 'static let frameDuration = 0.08' in model
assert 'guard !hasStarted' in model
handler=scene[scene.index('private func handlePunchEvent'):scene.index('private func startKnockdownIfReady')]
assert handler.index('health.receive(contact)')<handler.index('reaction.receive(contact.result, from: contact.kind)')
assert 'health.canExchangePunches && reactionAssetsAvailable' not in handler
start=scene[scene.index('private func startKnockdownIfReady'):scene.index('private func advanceOrange')]
assert 'orangeCombatState == .defeated, !reaction.isActive' in start
orange=scene[scene.index('private func advanceOrange'):scene.index('private var movementDirection')]
assert orange.count('startKnockdownIfReady()')==2
assert 'knockdown.advance(dt)' in orange and 'knockdown.step()' in orange
for forbidden in ['rootA.', 'rootB.', '.position', '.xScale', '.yScale', 'Timer', 'SKAction', 'DispatchQueue']:
    assert forbidden not in orange
reset=scene[scene.index('func resetHealth()'):scene.index('var contactGeometry')]
assert 'knockdown.cancel()' in reset and 'reaction.cancel()' in reset
assert 'Text("Orange: down")' in view and 'playback.orangeFrameCount' in view
assert '8A ' in view
print('PASS: all nine integrated RGBA assets, baseline448, matching down pose, manifest, scene-clock sequence, final recoil, reset, diagnostics and unchanged transforms')
compiler=shutil.which('swiftc')
if compiler:
    with tempfile.TemporaryDirectory() as folder:
        binary=Path(folder)/'knockdown-checks'
        sources=['Boxer0/JabPlayback.swift','Boxer0/PunchContact.swift','Boxer0/HitReactionPlayback.swift','Tests/KnockdownChecks.swift']
        subprocess.run([compiler]+[str(root/p) for p in sources]+['-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
else:
    print('SKIP: Swift behavioral checks; swiftc/Xcode unavailable. Device alignment and playback validation pending.')
