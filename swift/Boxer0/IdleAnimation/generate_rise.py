"""Eight approved recovery poses from the existing articulated SVG rig.
Dedicated recovery staging; exact down/idle endpoint pixels. No runtime offsets.
"""
import json
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageOps
import generate_knockdown as rig

POSES=[(-98,285,400),(-82,281,392),(-64,275,374),(-48,269,353),
       (-34,265,334),(-20,263,321),(-8,263,314),(0,264,310)]
FOOT=[1,.91,.77,.60,.42,.24,.10,0]

def main():
    images=[]
    for index,pose in enumerate(POSES):
        if index in (0,7):
            name='down_b_0' if index==0 else 'idle_b_0'
            root=ET.parse(rig.FRAMES/f'{name}.svg').getroot()
            image=Image.open(rig.FRAMES/f'{name}.png').convert('RGBA')
        else:
            root,image=rig.create(index,pose=pose,foot_progress=FOOT[index])
        root.find(f'{{{rig.NS}}}title').text=f'Orange rise {index+1}/8'
        root.find(f'{{{rig.NS}}}desc').text='Orange recovery; 512x512 transparent; fixed root (256,448), baseline448, 100ms per pose. Runtime mirroring; original rigid limb lengths.'
        rig.save(f'rise_b_{index}',root,image)
        images.append(image)
    sheet=Image.new('RGB',(2048,1080),(232,238,244));draw=ImageDraw.Draw(sheet);gif=[]
    for i,image in enumerate(images):
        tile=Image.new('RGBA',(512,512),(232,238,244,255));tile.alpha_composite(ImageOps.mirror(image))
        sheet.paste(tile.convert('RGB'),((i%4)*512,(i//4)*540))
        draw.text(((i%4)*512+12,(i//4)*540+515),f'{i+1}/8 - {i*100} ms',fill=(25,42,60))
        gif.append(tile.convert('RGB'))
    sheet.save(rig.PREVIEW/'rise_contact_sheet.png')
    gif[0].save(rig.PREVIEW/'rise_b.gif',save_all=True,append_images=gif[1:],duration=100,loop=0)
    manifest={'canvas':[512,512],'root':[256,448],'baseline':448,'palette':'orange','runtimeMirrored':True,
        'rise':{'frames':[f'rise_b_{i}' for i in range(8)],'frameDurationMs':100,'durationMs':800,'loops':False,
                'firstMatches':'down_b_0','lastMatches':'idle_b_0'}}
    (rig.ROOT/'rise_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Wrote eight rise PNG/SVG poses, image sets, manifest and previews.')
if __name__=='__main__': main()
