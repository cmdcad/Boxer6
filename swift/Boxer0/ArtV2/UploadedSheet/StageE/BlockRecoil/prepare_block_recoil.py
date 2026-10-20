"""User-authorized scripted guard compositing. No generated artwork.

Small row-preserving upper-body leans pivot at the belt; the lower body is
copied exactly. This is a 2D artwork effect, not a new rig or gameplay change.
"""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import struct
import zlib
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
REFERENCE = ROOT.parent.parent/'StageC/frames/guard_entry_2.png'
PIVOT_Y = 258
HEAD_Y = 129
PROFILES = {'jab': {'duration_ms':120, 'head_recoil_px':[4,8,2]},
            'cross': {'duration_ms':160, 'head_recoil_px':[7,14,3]}}


def save_apng(path, frames, delays):
    """Keep exact 160/3 ms Cross frame delays in APNG rational fields."""
    frames[0].save(path,save_all=True,append_images=frames[1:],
                   duration=[float(d*1000) for d in delays],loop=0,disposal=0,blend=0)
    data=path.read_bytes();output=bytearray(data[:8]);offset=8;frame=0
    while offset<len(data):
        length=struct.unpack('>I',data[offset:offset+4])[0]
        kind=data[offset+4:offset+8]
        payload=data[offset+8:offset+8+length]
        if kind==b'fcTL':
            delay=delays[frame]
            payload=payload[:20]+struct.pack('>HH',delay.numerator,delay.denominator)+payload[24:]
            frame+=1
        output+=struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
        offset+=length+12
    assert frame==len(frames)
    path.write_bytes(output)


def make_frame(guard,recoil):
    k=recoil/(PIVOT_Y-HEAD_Y)
    upper=Image.new('RGBA',(512,512))
    upper.paste(guard.crop((0,0,512,PIVOT_Y)),(0,0))
    # Inverse mapping for x_out=x_in-k*(pivot_y-y). No vertical scaling.
    leaned=upper.transform((512,512),Image.Transform.AFFINE,
                           (1,-k,k*PIVOT_Y,0,1,0),resample=Image.Resampling.BICUBIC)
    result=guard.copy()
    result.paste(leaned.crop((0,0,512,PIVOT_Y)),(0,0))
    return result


def gameplay_frame(im,label):
    bg=Image.new('RGB',(320,280),'#e8eef4')
    small=im.resize((256,256),Image.Resampling.LANCZOS)
    bg.paste(small,(32,0),small)
    d=ImageDraw.Draw(bg)
    d.line((8,224,312,224),fill='#9faebb')
    d.text((12,255),label,fill='#183249')
    return bg


def main():
    (ROOT/'frames').mkdir(exist_ok=True)
    (ROOT/'source').mkdir(exist_ok=True)
    guard=Image.open(REFERENCE).convert('RGBA')
    guard.save(ROOT/'source/held_guard.png')
    records=[];clips={}
    for kind,profile in PROFILES.items():
        frames=[]
        for i,recoil in enumerate(profile['head_recoil_px']):
            im=make_frame(guard,recoil)
            dest=ROOT/f'frames/block_{kind}_a_{i}.png';im.save(dest)
            frames.append(im)
            records.append({'kind':kind,'index':i,'file':dest.relative_to(ROOT).as_posix(),
                            'head_recoil_px':recoil,'duration_ms':profile['duration_ms']/3,
                            'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
        clips[kind]=frames
        delay=Fraction(profile['duration_ms'],3000)
        save_apng(ROOT/f'block_{kind}.png',frames,[delay]*3)
        save_apng(ROOT/f'block_{kind}_to_guard.png',frames+[guard],[delay]*3+[Fraction(2,5)])
        previews=[gameplay_frame(im,kind.title()+' block') for im in frames+[guard]]
        # GIF has10ms precision; Cross is quantized but totals160ms.
        times=[40,40,40,400] if kind=='jab' else [50,60,50,400]
        previews[0].save(ROOT/f'block_{kind}_gameplay.gif',save_all=True,
                         append_images=previews[1:],duration=times,loop=0,disposal=2)
    sheet=Image.new('RGB',(512*4,550*2),'#e8eef4');d=ImageDraw.Draw(sheet)
    for row,kind in enumerate(['jab','cross']):
        for i,im in enumerate(clips[kind]+[guard]):
            x,y=i*512,row*550;sheet.paste(im,(x,y),im)
            d.line((x,y+448,x+511,y+448),fill='#ca7767')
            d.line((x+256,y+430,x+256,y+465),fill='#639ac1')
            label=f'{kind.title()} block {i+1}' if i<3 else 'Held guard resumes'
            d.text((x+12,y+518),label,fill='#183249')
    sheet.save(ROOT/'alignment_sheet.png')
    comparison=[]
    for t in range(0,560,10):
        bg=Image.new('RGB',(640,280),'#e8eef4')
        for col,kind in enumerate(['jab','cross']):
            total=PROFILES[kind]['duration_ms']
            im=clips[kind][min(2,int(t*3/total))] if t<total else guard
            bg.paste(gameplay_frame(im,kind.title()+' block'),(col*320,0))
        comparison.append(bg)
    comparison[0].save(ROOT/'block_comparison.gif',save_all=True,append_images=comparison[1:],
                        duration=10,loop=0,disposal=2)
    manifest={'canvas':[512,512],'root':[256,448],'baseline':448,'facing':'right',
              'integrated':False,'image_generation_used':False,'profiles':PROFILES,
              'source_reference':str(REFERENCE.relative_to(ROOT.parent.parent)),
              'source_sha256':hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
              'upper_body_pivot_y':PIVOT_Y,'fixed_lower_body_from_y':PIVOT_Y,
              'method':'Scripted 2D upper-body lean; no redraw, root translation or vertical scaling.',
              'frames':records,'preview_note':'APNG uses exact rational timing; GIF Cross frame times are quantized to10ms.',
              'limits':['Guard posture is preserved from the reference; this is an affine lean, not new anatomical drawings.',
                        'Minor interpolation softening and waist contour changes need visual review.',
                        'No live integration, Swift/XCTest, SpriteKit or iPhone validation performed.']}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Prepared6 block-recoil frames; Jab120ms, Cross160ms; no image generation.')


if __name__=='__main__':main()
