"""Approved eight-frame blue cross, built from the existing editable rig.

Offline pose solving only. Runtime remains complete-frame texture playback.
"""
from pathlib import Path
import json
import math
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
import generate_idle as idle
from generate_footwork import ik
import generate_jab as jab

ROOT = Path(__file__).resolve().parent
FRAMES = ROOT/'frames'
ASSETS = ROOT.parent/'Boxer0/Assets.xcassets'
PREVIEW = ROOT/'preview'
TORSO = [(235,184),(279,183),(302,209),(307,257),(292,300),(237,298),(220,254),(224,211)]
TURNED_TORSO = [(270,186),(298,186),(298,214),(301,257),(292,300),(237,298),(228,254),(250,214)]
REAR_SHOULDER = (247.0,199.0)
REAR_ELBOW = (235.0,222.0)
REAR_WRIST = (278.0,184.0)
REAR_UPPER = math.dist(REAR_SHOULDER,REAR_ELBOW)
REAR_LOWER = math.dist(REAR_ELBOW,REAR_WRIST)
# (name, projected torso turn/weight transfer, rear wrist, lead defensive wrist)
POSES = [
 ('ready',0,REAR_WRIST,jab.WRIST),
 ('begin rotation',.25,(290,184),(302,174)),
 ('weight transfer',.6,(302,181),(296,171)),
 ('extend rear arm',.9,(335,180),(296,169)),
 ('contact',1,(360,184),(296,169)),
 ('withdraw',.85,(338,183),(297,171)),
 ('recover',.35,(295,184),(316,180)),
 ('guard',0,REAR_WRIST,jab.WRIST),
]


def geometry(index):
    _,turn,rear_wrist,lead_wrist = POSES[index]
    if index in (0,7):
        return (REAR_SHOULDER,REAR_ELBOW,REAR_WRIST), (jab.SHOULDER,jab.ELBOW,jab.WRIST), TORSO, 0
    rear_shoulder=(247+35*turn,199-4*turn)
    lead_shoulder=(283+3*turn,199)
    rear_elbow=ik(rear_shoulder,rear_wrist,REAR_UPPER,REAR_LOWER,(300,215))
    lead_elbow=ik(lead_shoulder,lead_wrist,jab.UPPER,jab.LOWER,(320,207))
    torso=[(x+(tx-x)*turn,y+(ty-y)*turn) for (x,y),(tx,ty) in zip(TORSO,TURNED_TORSO)]
    return (rear_shoulder,rear_elbow,rear_wrist),(lead_shoulder,lead_elbow,lead_wrist),torso,8*turn


def write_svg(index,rear,lead,torso,head_dx):
    ns='http://www.w3.org/2000/svg'
    ET.register_namespace('',ns)
    tree=ET.parse(FRAMES/'idle_a_0.svg')
    root=tree.getroot()
    root.find(f'{{{ns}}}title').text=f'Boxer A — cross {index+1}: {POSES[index][0]}'
    root.find(f'{{{ns}}}desc').text='Cross: 512×512 transparent; root (256,448), baseline 448. Eight frames ×60 ms; contact frame 5 at 240 ms.'
    if index not in (0,7):
        for hand,pose in [('rear',rear),('lead',lead)]:
            shoulder,elbow,wrist=pose
            for part,a,b in [('upper-arm',shoulder,elbow),('forearm',elbow,wrist)]:
                group=root.find(f"{{{ns}}}g[@id='{part}-{hand}']")
                group.attrib.pop('transform',None)
                for path in group:
                    path.set('d',f'M{a[0]:.4f} {a[1]:.4f}L{b[0]:.4f} {b[1]:.4f}')
            rest=REAR_WRIST if hand=='rear' else jab.WRIST
            root.find(f"{{{ns}}}g[@id='glove-{hand}']").set('transform',f'translate({wrist[0]-rest[0]:.4f} {wrist[1]-rest[1]:.4f})')
        group=root.find(f"{{{ns}}}g[@id='torso']")
        paths=list(group)
        paths[0].set('d','M'+'L'.join(f'{x:.4f} {y:.4f}' for x,y in torso)+'Z')
        for path in paths[1:]:
            path.set('d',f'M{258+head_dx:.4f} 170v20')
        root.find(f"{{{ns}}}g[@id='head']").set('transform',f'translate({head_dx:.4f} 0)')
        # During the turn the rear arm crosses in front of the torso.
        lead_forearm=root.find(f"{{{ns}}}g[@id='forearm-lead']")
        insert_at=list(root).index(lead_forearm)+1
        for name in ['upper-arm-rear','forearm-rear']:
            node=root.find(f"{{{ns}}}g[@id='{name}']")
            root.remove(node)
            insert_at=list(root).index(lead_forearm)+1
            if name=='forearm-rear':
                insert_at=list(root).index(root.find(f"{{{ns}}}g[@id='upper-arm-rear']"))+1
            root.insert(insert_at,node)
    tree.write(FRAMES/f'cross_a_{index}.svg',encoding='utf-8',xml_declaration=True)


def main():
    images=[]
    rest=Image.open(FRAMES/'idle_a_0.png').convert('RGBA')
    for index in range(8):
        rear,lead,torso,head_dx=geometry(index)
        for pose,upper,lower in [(rear,REAR_UPPER,REAR_LOWER),(lead,jab.UPPER,jab.LOWER)]:
            assert abs(math.dist(pose[0],pose[1])-upper)<1e-6
            assert abs(math.dist(pose[1],pose[2])-lower)<1e-6
        if index in (0,7):
            image=idle.draw_boxer(idle.PALETTES['a'],0,0,0,0,0)
            assert image.tobytes()==rest.tobytes()
        else:
            image=idle.draw_boxer(idle.PALETTES['a'],0,0,0,lead[2][0]-345,rear[2][0]-278,
                                  lead_pose=lead,rear_pose=rear,torso_points=torso,head_dx=head_dx)
        name=f'cross_a_{index}'
        image.save(FRAMES/f'{name}.png')
        write_svg(index,rear,lead,torso,head_dx)
        folder=ASSETS/f'{name}.imageset'
        folder.mkdir(exist_ok=True)
        image.save(folder/f'{name}.png')
        (folder/'Contents.json').write_text(json.dumps({'images':[{'filename':f'{name}.png','idiom':'universal','scale':'1x'}],
            'info':{'author':'xcode','version':1}},indent=2)+'\n')
        images.append(image)
    sheet=Image.new('RGBA',(512*4,540*2),(232,238,244,255))
    draw=ImageDraw.Draw(sheet)
    gif=[]
    for index,image in enumerate(images):
        x=(index%4)*512; y=(index//4)*540
        sheet.alpha_composite(image,(x,y))
        draw.text((x+12,y+514),f'{index+1}: {POSES[index][0]} ({index*60} ms)',fill=(25,42,60))
        frame=Image.new('RGBA',(512,512),(232,238,244,255))
        frame.alpha_composite(image)
        gif.append(frame.convert('RGB'))
    sheet.convert('RGB').save(PREVIEW/'cross_contact_sheet.png')
    gif[0].save(PREVIEW/'cross_a.gif',save_all=True,append_images=gif[1:],duration=60,loop=0)
    print('Wrote eight cross_a PNG/SVG poses, image sets, contact sheet and timing preview.')


if __name__=='__main__':
    main()
