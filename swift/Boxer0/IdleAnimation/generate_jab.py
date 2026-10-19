"""Approved Task 4A assets: six blue jab poses from the existing editable rig.

No root translation or mirroring. Shoulder protraction is limited to 12 canvas
pixels; both arm segment lengths remain those of the original short-armed rig.
Rear guard, head, torso, legs and feet remain unchanged.
"""
from pathlib import Path
import json
import math
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
import generate_idle as idle
from generate_footwork import ik

ROOT = Path(__file__).resolve().parent
FRAMES = ROOT / 'frames'
ASSETS = ROOT.parent / 'Boxer0/Assets.xcassets'
PREVIEW = ROOT / 'preview'
SHOULDER = (283.0, 199.0)
ELBOW = (316.0, 213.0)
WRIST = (345.0, 193.0)
UPPER = math.dist(SHOULDER, ELBOW)
LOWER = math.dist(ELBOW, WRIST)
# Zero-based frame 3 is the contact marker at 150 ms.
POSES = [
    ('ready', SHOULDER, WRIST),
    ('preparation', SHOULDER, (327.0, 202.0)),
    ('extension', (290.0, 198.0), (354.0, 185.0)),
    ('contact', (295.0, 197.0), (365.0, 190.0)),
    ('withdrawal', (287.0, 199.0), (338.0, 198.0)),
    ('guard', SHOULDER, WRIST),
]


def elbow_for(shoulder, wrist):
    if shoulder == SHOULDER and wrist == WRIST:
        return ELBOW
    return ik(shoulder, wrist, UPPER, LOWER, ELBOW)


def write_svg(path, label, shoulder, elbow, wrist):
    ns = 'http://www.w3.org/2000/svg'
    ET.register_namespace('', ns)
    tree = ET.parse(FRAMES / 'idle_a_0.svg')
    root = tree.getroot()
    root.find(f'{{{ns}}}title').text = f'Boxer A — jab {label}'
    root.find(f'{{{ns}}}desc').text = 'Task 4A jab. 512×512; root (256,448); baseline y=448. Six frames, 50 ms each. Rear guard and feet fixed.'
    for identifier, first, last in [('upper-arm-lead', shoulder, elbow), ('forearm-lead', elbow, wrist)]:
        group = root.find(f"{{{ns}}}g[@id='{identifier}']")
        for child in group:
            child.set('d', f'M{first[0]:.4f} {first[1]:.4f}L{last[0]:.4f} {last[1]:.4f}')
    glove = root.find(f"{{{ns}}}g[@id='glove-lead']")
    glove.set('transform', f'translate({wrist[0]-345:.4f} {wrist[1]-193:.4f})')
    tree.write(path, encoding='utf-8', xml_declaration=True)


def main():
    images = []
    for index, (label, shoulder, wrist) in enumerate(POSES):
        elbow = elbow_for(shoulder, wrist)
        assert abs(math.dist(shoulder, elbow)-UPPER) < 1e-6
        assert abs(math.dist(elbow, wrist)-LOWER) < 1e-6
        image = idle.draw_boxer(idle.PALETTES['a'], 0, 0, 0, wrist[0]-345, 0,
                                lead_pose=(shoulder, elbow, wrist))
        name = f'jab_a_{index}'
        image.save(FRAMES / f'{name}.png')
        write_svg(FRAMES / f'{name}.svg', label, shoulder, elbow, wrist)
        folder = ASSETS / f'{name}.imageset'
        folder.mkdir(exist_ok=True)
        image.save(folder / f'{name}.png')
        (folder / 'Contents.json').write_text(json.dumps({
            'images': [{'filename': f'{name}.png', 'idiom': 'universal', 'scale': '1x'}],
            'info': {'author': 'xcode', 'version': 1}}, indent=2)+'\n')
        images.append(image)
    # Exact guard endpoints preserve the existing idle raster appearance.
    rest = Image.open(FRAMES / 'idle_a_0.png').convert('RGBA')
    assert images[0].tobytes() == images[5].tobytes() == rest.tobytes()
    sheet = Image.new('RGBA', (512*6, 540), (232, 238, 244, 255))
    draw = ImageDraw.Draw(sheet)
    for index, image in enumerate(images):
        sheet.alpha_composite(image, (index*512, 0))
        draw.text((index*512+16, 512), f'{index+1}: {POSES[index][0]} ({index*50} ms)', fill=(25,42,60))
    sheet.convert('RGB').save(PREVIEW / 'jab_contact_sheet.png')
    gif = []
    for image in images:
        frame = Image.new('RGBA', (512,512), (232,238,244,255))
        frame.alpha_composite(image)
        gif.append(frame.convert('RGB'))
    gif[0].save(PREVIEW/'jab_a.gif', save_all=True, append_images=gif[1:], duration=50, loop=0)
    print('Wrote six jab_a PNG/SVG poses, catalog entries, contact sheet and timing preview.')


if __name__ == '__main__':
    main()
