"""Approved orange reaction poses: visible recoil on first contact render.

All changes are baked into complete frames. Runtime root/facing/scale never move.
In the source right-facing rig negative X is recoil away from an incoming glove;
runtime mirroring turns that into positive scene X for the orange defender.
"""
from pathlib import Path
import json
import math
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
import generate_idle as idle
from generate_cross import TORSO

ROOT=Path(__file__).resolve().parent
FRAMES=ROOT/'frames'
ASSETS=ROOT.parent/'Boxer0/Assets.xcassets'
PREVIEW=ROOT/'preview'
# name, head+neck X, top-torso recoil X. First frame is not idle/rest.
POSES=[('initial recoil',-6,-4),('peak recoil',-14,-9),('recover',-7,-4),('near guard',-1,-0.5)]
REAR=((247,199),(235,222),(278,184))
LEAD=((283,199),(316,213),(345,193))


def geometry(index):
    _,head_dx,upper_dx=POSES[index]
    # Keep the hips and complete lower body fixed; torso leans from its base.
    torso=[(x+upper_dx*max(0,min(1,(300-y)/117)),y) for x,y in TORSO]
    rear=tuple((x+upper_dx,y) for x,y in REAR)
    lead=tuple((x+upper_dx,y) for x,y in LEAD)
    return torso,rear,lead,head_dx


def write_svg(index,torso,rear,lead,head_dx):
    ns='http://www.w3.org/2000/svg'
    ET.register_namespace('',ns)
    tree=ET.parse(FRAMES/'idle_b_0.svg')
    root=tree.getroot()
    root.find(f'{{{ns}}}title').text=f'Boxer B — hit_react {index+1}: {POSES[index][0]}'
    root.find(f'{{{ns}}}desc').text='Orange hit reaction: 512×512 transparent, root (256,448), baseline448. Four frames ×60ms. Negative image-X recoil becomes positive scene-X when mirrored. Feet and pelvis fixed.'
    for hand,pose,rest in [('rear',rear,REAR),('lead',lead,LEAD)]:
        for part,a,b in [('upper-arm',pose[0],pose[1]),('forearm',pose[1],pose[2])]:
            group=root.find(f"{{{ns}}}g[@id='{part}-{hand}']")
            group.attrib.pop('transform',None)
            for child in group:
                child.set('d',f'M{a[0]:.4f} {a[1]:.4f}L{b[0]:.4f} {b[1]:.4f}')
        root.find(f"{{{ns}}}g[@id='glove-{hand}']").set('transform',f'translate({pose[2][0]-rest[2][0]:.4f} 0)')
    group=root.find(f"{{{ns}}}g[@id='torso']")
    paths=list(group)
    paths[0].set('d','M'+'L'.join(f'{x:.4f} {y:.4f}' for x,y in torso)+'Z')
    for child in paths[1:]:
        child.set('d',f'M{258+head_dx:.4f} 170v20')
    root.find(f"{{{ns}}}g[@id='head']").set('transform',f'translate({head_dx:.4f} 0)')
    tree.write(FRAMES/f'hit_react_b_{index}.svg',encoding='utf-8',xml_declaration=True)


def main():
    images=[]
    rest=Image.open(FRAMES/'idle_b_0.png').convert('RGBA')
    for index in range(4):
        torso,rear,lead,head_dx=geometry(index)
        for pose,original in [(rear,REAR),(lead,LEAD)]:
            assert abs(math.dist(pose[0],pose[1])-math.dist(original[0],original[1]))<1e-8
            assert abs(math.dist(pose[1],pose[2])-math.dist(original[1],original[2]))<1e-8
        image=idle.draw_boxer(idle.PALETTES['b'],0,0,0,lead[2][0]-345,rear[2][0]-278,
            lead_pose=lead,rear_pose=rear,torso_points=torso,head_dx=head_dx,rear_in_front=False)
        assert image.tobytes()!=rest.tobytes()
        assert image.crop((0,305,512,512)).tobytes()==rest.crop((0,305,512,512)).tobytes()
        name=f'hit_react_b_{index}'
        image.save(FRAMES/f'{name}.png')
        write_svg(index,torso,rear,lead,head_dx)
        folder=ASSETS/f'{name}.imageset'
        folder.mkdir(exist_ok=True)
        image.save(folder/f'{name}.png')
        (folder/'Contents.json').write_text(json.dumps({'images':[{'filename':f'{name}.png','idiom':'universal','scale':'1x'}],
            'info':{'author':'xcode','version':1}},indent=2)+'\n')
        images.append(image)
    sheet=Image.new('RGBA',(512*4,540),(232,238,244,255))
    draw=ImageDraw.Draw(sheet)
    gif=[]
    for index,image in enumerate(images):
        sheet.alpha_composite(image,(index*512,0))
        draw.text((index*512+12,515),f'{index+1}: {POSES[index][0]} ({index*60} ms)',fill=(25,42,60))
        frame=Image.new('RGBA',(512,512),(232,238,244,255))
        # Runtime orientation: show orange facing left in this preview.
        frame.alpha_composite(image.transpose(Image.Transpose.FLIP_LEFT_RIGHT))
        gif.append(frame.convert('RGB'))
    sheet.convert('RGB').save(PREVIEW/'hit_react_contact_sheet.png')
    gif[0].save(PREVIEW/'hit_react_b.gif',save_all=True,append_images=gif[1:],duration=60,loop=0)
    print('Wrote four orange hit_react PNG/SVG poses, image sets and review previews.')


if __name__=='__main__':
    main()
