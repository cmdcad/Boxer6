"""Approved nine poses, articulated from named SVG rig groups; fixed canvas/root.
No runtime transforms or scaling changes. Rigid limbs preserve rig proportions.
"""
from pathlib import Path
import copy
import io
import json
import math
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent
FRAMES = ROOT/'frames'
ASSETS = ROOT.parent/'Boxer0/Assets.xcassets'
PREVIEW = ROOT/'preview'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
HIP = (264,310)
# Knee flexion and rearward torso fall. Last two poses gently settle on floor.
POSES = [(0,264,310),(-8,263,315),(-23,266,332),(-43,274,356),
         (-64,281,381),(-83,285,395),(-96,285,400),(-98,285,400)]

def dist(a,b): return math.hypot(a[0]-b[0], a[1]-b[1])
def rotated(p, angle, pivot, target):
    a=math.radians(angle); x=p[0]-pivot[0]; y=p[1]-pivot[1]
    return (target[0]+x*math.cos(a)-y*math.sin(a),target[1]+x*math.sin(a)+y*math.cos(a))
def rigid(a,b,c,d):
    angle=math.degrees(math.atan2(d[1]-c[1],d[0]-c[0])-math.atan2(b[1]-a[1],b[0]-a[0]))
    return f'translate({c[0]} {c[1]}) rotate({angle}) translate({-a[0]} {-a[1]})'
def knee(hip, ankle, upper, lower):
    d=dist(hip,ankle); assert d <= upper+lower+1e-5 and d>abs(upper-lower)
    along=(upper*upper-lower*lower+d*d)/(2*d)
    lift=math.sqrt(max(0,upper*upper-along*along)); ux=(ankle[0]-hip[0])/d; uy=(ankle[1]-hip[1])/d
    return (hip[0]+ux*along+uy*lift, hip[1]+uy*along-ux*lift)
def render(root):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=ET.tostring(root),output_width=2048,output_height=2048))).convert('RGBA').resize((512,512),Image.Resampling.LANCZOS)
def create(index):
    if index == 0:
        return ET.parse(FRAMES/'idle_b_0.svg').getroot(), Image.open(FRAMES/'idle_b_0.png').convert('RGBA')
    root=ET.parse(FRAMES/'idle_b_0.svg').getroot()
    angle,hx,hy=POSES[index]; target=(hx,hy)
    t=index/7
    upper=f'translate({hx} {hy}) rotate({angle}) translate(-264 -310)'
    for group in list(root):
        name=group.get('id','')
        if not name: continue
        if name.startswith(('thigh-','shin-','boot-')): continue
        group.set('transform',upper+' '+group.get('transform',''))
    for side,hip0,knee0,ankle0,ankle_end in [
        ('rear',(239,310),(216,365),(203,420),(385,420)),
        ('lead',(282,310),(309,364),(304,420),(375,420))]:
        h=rotated(hip0,angle,HIP,target)
        ankle=(ankle0[0]+(ankle_end[0]-ankle0[0])*t,420)
        if index==0: k=knee0
        else: k=knee(h,ankle,dist(hip0,knee0),dist(knee0,ankle0))
        for part,a,b,c,d in [('thigh',hip0,knee0,h,k),('shin',knee0,ankle0,k,ankle)]:
            root.find(f"{{{NS}}}g[@id='{part}-{side}']").set('transform',rigid(a,b,c,d))
        root.find(f"{{{NS}}}g[@id='boot-{side}']").set('transform',f'translate({ankle[0]-ankle0[0]} 0)')
    # Floor alignment belongs to authored poses, never a runtime root offset.
    # All poses keep their lowest opaque support at the existing y=448 baseline.
    image=render(root); bbox=image.getchannel('A').point(lambda a: 255 if a >= 128 else 0).getbbox(); correction=448-bbox[3]
    wrapper=ET.Element(f'{{{NS}}}g',{'id':'pose','transform':f'translate(0 {correction})'})
    for group in list(root):
        if group.tag==f'{{{NS}}}g': root.remove(group); wrapper.append(group)
    root.append(wrapper)
    root.find(f'{{{NS}}}title').text=f'Orange knockdown {index+1}/8'
    root.find(f'{{{NS}}}desc').text='512x512 transparent; fixed root (256,448); baseline448; orange palette; runtime mirror only. Articulated rigid rig, no scale deformation.'
    image=render(root)
    assert image.getbbox()[0]>0 and image.getbbox()[2]<512
    return root,image

def main():
    images=[]
    for i in range(8):
        root,image=create(i); images.append(image)
        save(f'knockdown_b_{i}',root,image)
    root=copy.deepcopy(root); root.find(f'{{{NS}}}title').text='Orange down: static hold'
    save('down_b_0',root,images[-1])
    sheet=Image.new('RGB',(512*4,540*2),(232,238,244)); d=ImageDraw.Draw(sheet)
    previews=[]
    for i,image in enumerate(images):
        mirrored=ImageOps.mirror(image)
        tile=Image.new('RGBA',(512,512),(232,238,244,255));tile.alpha_composite(mirrored)
        sheet.paste(tile.convert('RGB'),((i%4)*512,(i//4)*540))
        d.text(((i%4)*512+12,(i//4)*540+515),f'{i+1}/8 - {i*80} ms',fill=(25,42,60))
        previews.append(tile.convert('RGB'))
    sheet.save(PREVIEW/'knockdown_contact_sheet.png')
    previews[0].save(PREVIEW/'knockdown_b.gif',save_all=True,append_images=previews[1:],duration=80,loop=0)
    manifest={'canvas':[512,512],'root':[256,448],'baseline':448,'palette':'orange','runtimeMirrored':True,
        'knockdown':{'frames':[f'knockdown_b_{i}' for i in range(8)],'frameDurationMs':80,'durationMs':640,'loops':False},
        'down':{'frames':['down_b_0'],'holdUntilReset':True}}
    (ROOT/'knockdown_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Generated eight knockdown frames, static down, editable SVGs, asset sets and review previews.')
def save(name,root,image):
    ET.ElementTree(root).write(FRAMES/f'{name}.svg',encoding='utf-8',xml_declaration=True)
    image.save(FRAMES/f'{name}.png')
    folder=ASSETS/f'{name}.imageset';folder.mkdir(exist_ok=True);image.save(folder/f'{name}.png')
    (folder/'Contents.json').write_text(json.dumps({'images':[{'filename':f'{name}.png','idiom':'universal','scale':'1x'}],'info':{'author':'xcode','version':1}},indent=2)+'\n')
if __name__=='__main__': main()
