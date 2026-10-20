from active_art import frame
"""Dedicated recovery artwork checks; runtime rendering remains device-tested."""
from pathlib import Path
from PIL import Image
import numpy as np
import json

root = Path(__file__).resolve().parents[1]
for kind, reused in [('jab',4), ('cross',5)]:
    alpha = []
    for color in 'ab':
        name = f'{kind}_recovery_{color}_0'
        image = Image.open(frame(name))
        assert image.mode == 'RGBA' and image.size == (512,512)
        assert image.getpixel((0,0))[3] == 0
        ready = Image.open(frame(f'{kind}_{color}_0')).convert('RGBA')
        old = Image.open(frame(f'{kind}_{color}_{reused}')).convert('RGBA')
        assert image.tobytes() != ready.tobytes() and image.tobytes() != old.tobytes()
        assert image.crop((0,340,512,512)).tobytes() == ready.crop((0,340,512,512)).tobytes()
        # Silhouette and baseline of the complete lower body are preserved.
        assert image.getchannel('A').crop((0,300,512,512)).tobytes() == ready.getchannel('A').crop((0,300,512,512)).tobytes()
        alpha.append(np.array(image)[:,:,3])
        folder = root/f'Boxer0/Assets.xcassets/{name}.imageset'
        manifest = json.loads((folder/'Contents.json').read_text())
        assert Image.open(folder/manifest['images'][0]['filename']).tobytes() == image.tobytes()
    assert np.array_equal(*alpha)
scene = (root/'Boxer0/IdleTestScene.swift').read_text(encoding='utf-8')
assert 'var usesDedicatedRecoveryPoses = true' in scene
assert scene.count('? dedicated[0] : textures[') == 2
assert 'orangeHasDedicatedRecoveryPose ?' in scene
print('PASS: four distinct integrated RGBA poses, palette-identical alpha, planted feet/lower silhouette, reversible texture selection')
