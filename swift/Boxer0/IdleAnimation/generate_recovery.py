"""Four approved dedicated recovery textures, using the established editable rig.

No existing punch frames are rewritten. No runtime timing or geometry changes.
"""
import json
import math
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
import generate_idle as idle
import generate_jab as jab
import generate_cross as cross
from generate_footwork import ik
from generate_bidirectional import variant

FRAMES, ASSETS, PREVIEW = jab.FRAMES, jab.ASSETS, jab.PREVIEW
NS = 'http://www.w3.org/2000/svg'


def poses(kind):
    if kind == 'jab':
        shoulder, wrist = (291.0, 199.0), (350.0, 205.0)
        lead = (shoulder, ik(shoulder, wrist, jab.UPPER, jab.LOWER, jab.ELBOW), wrist)
        rear = (cross.REAR_SHOULDER, cross.REAR_ELBOW, cross.REAR_WRIST)
        return lead, rear, cross.TORSO, 0
    # Reduced turn and bent rear elbow communicate withdrawal, not contact.
    turn = .65
    shoulder, wrist = (247+35*turn, 199-4*turn), (322.0, 193.0)
    rear = (shoulder, ik(shoulder, wrist, cross.REAR_UPPER, cross.REAR_LOWER, (300, 215)), wrist)
    shoulder, wrist = (283+3*turn, 199), (303.0, 174.0)
    lead = (shoulder, ik(shoulder, wrist, jab.UPPER, jab.LOWER, (320, 207)), wrist)
    torso = [(x+(tx-x)*turn, y+(ty-y)*turn) for (x,y),(tx,ty) in zip(cross.TORSO,cross.TURNED_TORSO)]
    return lead, rear, torso, 8*turn


def write_svg(name, kind, lead, rear, torso, head_dx):
    ET.register_namespace('', NS)
    tree = ET.parse(FRAMES/'idle_a_0.svg')
    root = tree.getroot()
    root.find(f'{{{NS}}}title').text = f'Boxer A dedicated {kind} recovery'
    root.find(f'{{{NS}}}desc').text = '512x512 transparent; root (256,448); fixed feet/baseline. Static recovery pose, faces right.'
    for hand, pose, rest in [('lead', lead, jab.WRIST), ('rear', rear, cross.REAR_WRIST)]:
        shoulder, elbow, wrist = pose
        for part, a, b in [('upper-arm', shoulder, elbow), ('forearm', elbow, wrist)]:
            group = root.find(f"{{{NS}}}g[@id='{part}-{hand}']")
            group.attrib.pop('transform', None)
            for path in group:
                path.set('d', f'M{a[0]:.4f} {a[1]:.4f}L{b[0]:.4f} {b[1]:.4f}')
        root.find(f"{{{NS}}}g[@id='glove-{hand}']").set('transform', f'translate({wrist[0]-rest[0]:.4f} {wrist[1]-rest[1]:.4f})')
    if kind == 'cross':
        paths = list(root.find(f"{{{NS}}}g[@id='torso']"))
        paths[0].set('d', 'M'+'L'.join(f'{x:.4f} {y:.4f}' for x,y in torso)+'Z')
        for path in paths[1:]:
            path.set('d', f'M{258+head_dx:.4f} 170v20')
        root.find(f"{{{NS}}}g[@id='head']").set('transform', f'translate({head_dx:.4f} 0)')
        anchor = root.find(f"{{{NS}}}g[@id='forearm-lead']")
        for identifier in ['upper-arm-rear', 'forearm-rear']:
            node = root.find(f"{{{NS}}}g[@id='{identifier}']")
            root.remove(node)
            root.insert(list(root).index(anchor)+1, node)
            anchor = node
    tree.write(FRAMES/f'{name}.svg', encoding='utf-8', xml_declaration=True)


def main():
    for kind in ['jab', 'cross']:
        lead, rear, torso, head_dx = poses(kind)
        for pose, upper, lower in [(lead, jab.UPPER, jab.LOWER), (rear, cross.REAR_UPPER, cross.REAR_LOWER)]:
            assert abs(math.dist(pose[0],pose[1])-upper) < 1e-6
            assert abs(math.dist(pose[1],pose[2])-lower) < 1e-6
        image = idle.draw_boxer(idle.PALETTES['a'], 0,0,0, lead[2][0]-345, rear[2][0]-278,
                                lead_pose=lead, rear_pose=rear if kind == 'cross' else None, torso_points=torso, head_dx=head_dx)
        name = f'{kind}_recovery_a_0'
        image.save(FRAMES/f'{name}.png')
        write_svg(name, kind, lead, rear, torso, head_dx)
        folder = ASSETS/f'{name}.imageset'
        folder.mkdir(exist_ok=True)
        image.save(folder/f'{name}.png')
        (folder/'Contents.json').write_text(json.dumps({'images':[{'filename':f'{name}.png','idiom':'universal','scale':'1x'}],
            'info':{'author':'xcode','version':1}}, indent=2)+'\n', encoding='utf-8')
        variant(name, f'{kind}_recovery_b_0', (40,118,210), (231,119,40))
    sheet = Image.new('RGBA', (512*3, 540*2), (232,238,244,255))
    draw = ImageDraw.Draw(sheet)
    for row, color in enumerate('ab'):
        for col, (name, label) in enumerate([(f'jab_{color}_0', 'Ready'), (f'jab_recovery_{color}_0', 'Dedicated Jab recovery (120 ms)'), (f'cross_recovery_{color}_0', 'Dedicated Cross recovery (220 ms)')]):
            sheet.alpha_composite(Image.open(FRAMES/f'{name}.png').convert('RGBA'), (col*512,row*540))
            draw.text((col*512+12,row*540+514), label, fill=(25,42,60))
    sheet.convert('RGB').save(PREVIEW/'recovery_contact_sheet.png')
    print('Generated four dedicated recovery sprites and comparison sheet; existing punch artwork untouched.')


if __name__ == '__main__':
    main()
