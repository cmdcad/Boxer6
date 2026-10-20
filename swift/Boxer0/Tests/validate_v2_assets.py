"""Installed catalog integrity and guarded-walk wiring; not an Apple build."""
from pathlib import Path
import hashlib
import json
from PIL import Image

root=Path(__file__).resolve().parents[1]
base=root/'ArtV2/UploadedSheet'
report=json.loads((base/'integration_results.json').read_text())
assert len(report['assets'])==148
for row in report['assets']:
    name=row['catalog']
    folder=root/'Boxer0/Assets.xcassets'/f'{name}.imageset'
    contents=json.loads((folder/'Contents.json').read_text())
    image=folder/contents['images'][0]['filename']
    assert hashlib.sha256(image.read_bytes()).hexdigest()==row['sha256'],name
    assert image.read_bytes()==(base/row['source']).read_bytes(),name
    im=Image.open(image)
    assert im.mode=='RGBA' and im.size==(512,512)
    assert im.getextrema()[3][0]==0 and im.getextrema()[3][1]==255
scene=(root/'Boxer0/IdleTestScene.swift').read_text()
for color in 'AB':
    for direction in ['Advance','Retreat']:
        field=f'guarded{direction}{color}'
        assert f'private var {field}: [SKTexture]' in scene
        assert f'{field} = loadPunchTextures(prefix: "guarded_{direction.lower()}_{color.lower()}", count: 6)' in scene
        assert f'boxer{color}.texture = {field}[' in scene
assert 'static let originAnchor = CGPoint(x: 0.5, y: 1.0 - 448.0 / 512.0)' in scene
assert (base/'pre_v2_live_assets.zip').exists()
print('PASS:148 exact catalog/source hashes, transparent RGBA512 canvases, both guarded-walk render paths, preserved root, rollback archive.')
