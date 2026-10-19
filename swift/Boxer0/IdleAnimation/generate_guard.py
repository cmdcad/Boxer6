"""Approved three glove-raising poses; original rig proportions and fixed feet."""
import json
import math
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageOps
import generate_idle as idle
import generate_knockdown as rig

REAR=((247,199),(235,222),(278,184))
LEAD=((283,199),(316,213),(345,193))
def pose(original,target,t):
    a,e,w=original
    wrist=(w[0]+(target[0]-w[0])*t,w[1]+(target[1]-w[1])*t)
    # Fixed segment lengths, elbow on the outside of the glove-raising arc.
    elbow=rig.knee(a,wrist,math.dist(a,e),math.dist(e,w))
    return a,elbow,wrist

def main():
    images=[]
    for index,t in enumerate([0,0.5,1]):
        rear=pose(REAR,(235,148),t) if t else REAR
        lead=pose(LEAD,(284,153),t) if t else LEAD
        image=idle.draw_boxer(idle.PALETTES['b'],0,0,0,lead[2][0]-345,rear[2][0]-278,
            lead_pose=lead,rear_pose=rear,rear_in_front=True)
        tree=ET.parse(rig.FRAMES/'idle_b_0.svg');root=tree.getroot()
        for hand,points,original in [('rear',rear,REAR),('lead',lead,LEAD)]:
            for part,a,b in [('upper-arm',points[0],points[1]),('forearm',points[1],points[2])]:
                group=root.find(f"{{{rig.NS}}}g[@id='{part}-{hand}']")
                group.attrib.pop('transform',None)
                for child in group: child.set('d',f'M{a[0]} {a[1]}L{b[0]} {b[1]}')
            root.find(f"{{{rig.NS}}}g[@id='glove-{hand}']").set('transform',f'translate({points[2][0]-original[2][0]} {points[2][1]-original[2][1]})')
        # Same front-arm layering as the raster rig.
        insert=list(root).index(root.find(f"{{{rig.NS}}}g[@id='glove-rear']"))
        for part in ['upper-arm-rear','forearm-rear']:
            group=root.find(f"{{{rig.NS}}}g[@id='{part}']");root.remove(group);root.insert(insert,group);insert+=1
        root.find(f'{{{rig.NS}}}title').text=f'Orange guard {index+1}/3'
        root.find(f'{{{rig.NS}}}desc').text='Transparent512x512; root(256,448); baseline448; orange guard; three40ms entry poses then hold.'
        rig.save(f'guard_b_{index}',root,image);images.append(image)
    sheet=Image.new('RGB',(1536,540),(232,238,244));draw=ImageDraw.Draw(sheet);gif=[]
    for i,image in enumerate(images):
        tile=Image.new('RGBA',(512,512),(232,238,244,255));tile.alpha_composite(ImageOps.mirror(image))
        sheet.paste(tile.convert('RGB'),(512*i,0));draw.text((512*i+12,515),f'{i+1}/3 - {40*i} ms',fill=(25,42,60));gif.append(tile.convert('RGB'))
    sheet.save(rig.PREVIEW/'guard_contact_sheet.png')
    gif[0].save(rig.PREVIEW/'guard_b.gif',save_all=True,append_images=gif[1:],duration=[40,40,600],loop=0)
    (rig.ROOT/'guard_manifest.json').write_text(json.dumps({'canvas':[512,512],'root':[256,448],'baseline':448,'guard':{'frames':[f'guard_b_{i}' for i in range(3)],'frameDurationMs':40,'entryDurationMs':120,'effectiveAtMs':120,'holdFinal':True}},indent=2)+'\n')
    print('Generated three approved guard poses and asset sets.')
if __name__=='__main__': main()

