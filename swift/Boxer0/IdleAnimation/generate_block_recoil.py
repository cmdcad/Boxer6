"""Approved six guard-recoil poses. Upper body moves, lower body remains pixel-fixed."""
import json
import copy
import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageOps
import generate_idle as idle
import generate_guard as guard
import generate_knockdown as rig
from generate_cross import TORSO

def main():
    sheet=Image.new('RGB',(1536,1080),(232,238,244));draw=ImageDraw.Draw(sheet)
    held=Image.open(rig.FRAMES/'guard_b_2.png').convert('RGBA')
    manifest={'canvas':[512,512],'root':[256,448],'baseline':448,'clips':{}}
    for row,(kind,amount,duration) in enumerate([('jab',10,120),('cross',18,160)]):
        images=[]
        for i,factor in enumerate([1,.4,0]):
            dx=-amount*factor
            root=ET.parse(rig.FRAMES/'guard_b_2.svg').getroot()
            torso=[(x+dx*.8*max(0,min(1,(300-y)/117)),y) for x,y in TORSO]
            rear=tuple((x+dx*.8,y) for x,y in guard.pose(guard.REAR,(235,148),1))
            lead=tuple((x+dx*.8,y) for x,y in guard.pose(guard.LEAD,(284,153),1))
            if factor:
                image=idle.draw_boxer(idle.PALETTES['b'],0,0,0,lead[2][0]-345,rear[2][0]-278,
                    lead_pose=lead,rear_pose=rear,torso_points=torso,head_dx=dx,rear_in_front=True)
                for hand,points,original in [('rear',rear,guard.REAR),('lead',lead,guard.LEAD)]:
                    for part,a,b in [('upper-arm',points[0],points[1]),('forearm',points[1],points[2])]:
                        group=root.find(f"{{{rig.NS}}}g[@id='{part}-{hand}']")
                        for child in group: child.set('d',f'M{a[0]} {a[1]}L{b[0]} {b[1]}')
                    root.find(f"{{{rig.NS}}}g[@id='glove-{hand}']").set('transform',f'translate({points[2][0]-original[2][0]} {points[2][1]-original[2][1]})')
                group=root.find(f"{{{rig.NS}}}g[@id='torso']")
                list(group)[0].set('d','M'+'L'.join(f'{x} {y}' for x,y in torso)+'Z')
                for child in list(group)[1:]: child.set('d',f'M{258+dx} 170v20')
                root.find(f"{{{rig.NS}}}g[@id='head']").set('transform',f'translate({dx} 0)')
            else: image=held.copy()
            assert image.crop((0,305,512,512)).tobytes()==held.crop((0,305,512,512)).tobytes()
            name=f'block_{kind}_b_{i}'
            root.find(f'{{{rig.NS}}}title').text=f'Orange {kind} block recoil {i+1}/3'
            root.find(f'{{{rig.NS}}}desc').text=f'Transparent512x512, root(256,448), baseline448, fixed feet, raised guard. {duration}ms clip. Head source-X recoil{dx}px, mirrored away from punch.'
            rig.save(name,root,image);images.append(image)
            tile=Image.new('RGBA',(512,512),(232,238,244,255));tile.alpha_composite(ImageOps.mirror(image));sheet.paste(tile.convert('RGB'),(512*i,540*row))
            draw.text((512*i+12,540*row+515),f'{kind} recoil {i+1}/3',fill=(25,42,60))
        gif=[]
        for image in images:
            tile=Image.new('RGBA',(512,512),(232,238,244,255));tile.alpha_composite(ImageOps.mirror(image));gif.append(tile.convert('RGB'))
        gif[0].save(rig.PREVIEW/f'block_{kind}_b.gif',save_all=True,append_images=gif[1:],duration=duration//3,loop=0)
        manifest['clips'][kind]={'frames':[f'block_{kind}_b_{i}' for i in range(3)],'durationMs':duration,'frameDurationMs':duration/3,'headRecoilPixels':amount}
    sheet.save(rig.PREVIEW/'block_recoil_contact_sheet.png')
    (rig.ROOT/'block_recoil_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Generated six approved block-recoil PNG/SVG poses, assets and previews.')
if __name__=='__main__': main()
