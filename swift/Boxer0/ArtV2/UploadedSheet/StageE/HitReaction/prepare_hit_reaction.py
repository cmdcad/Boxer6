"""Curate supplied hit-reaction art; no generated poses or gameplay edits."""
from pathlib import Path
import hashlib
import json
import runpy
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[3]
SOURCE = PROJECT/'ArtV2/latest'
IDLE = ROOT.parent.parent/'StageA/frames/idle_a_0.png'
CLEANUP = runpy.run_path(str(PROJECT/'ArtV2/Sprites/clean_edges.py'))
SCALE = 1.48
# Reviewed source belt centers, used for translation only. One common scale.
PLAN = [(2, (51, 95), 'initial recoil'), (4, (61.5, 89), 'peak backward recoil'),
        (3, (65, 86), 'recover torso'), (1, (54, 94.5), 'settle toward stance')]
WAIST_LINES = {2:((32,99),(70,91)),4:((41,98),(82,80)),
               3:((47,94),(83,78)),1:((32,97),(76,92))}
ARM_PRESERVE = {2:(70,50,109,95),3:(75,40,119,85),4:(75,40,108,90)}


def main():
    for folder in ['frames', 'source', 'source/cleaned']:
        (ROOT/folder).mkdir(exist_ok=True)
    idle = Image.open(IDLE).convert('RGBA')
    lower = idle.copy()
    lower.paste((0,0,0,0), (290,254,512,260))  # Exclude original Idle forearm.
    fixed_base = Image.new('RGBA',(512,512))
    fixed_base.paste(lower.crop((0,254,512,512)),(0,254))
    # Small original abdomen connector behind the tilted source waist.
    fixed_base.paste(idle.crop((225,240,285,254)),(225,240))
    frames, records = [], []
    for index, (number, belt, phase) in enumerate(PLAN):
        src = SOURCE/f'sprite_frame_{number:02}.png'
        raw = Image.open(src).convert('RGBA')
        raw.save(ROOT/f'source/{src.name}')
        clean, cleanup = CLEANUP['clean'](raw)
        a = np.array(clean)
        blobs = CLEANUP['components'](a[:,:,3]>0)
        body = max(blobs, key=len)
        keep = np.zeros(a.shape[:2], bool)
        for y,x in body:
            keep[y,x] = True
        removed = int(((a[:,:,3]>0)&~keep).sum())
        a[~keep] = 0
        clean = Image.fromarray(a)
        clean.save(ROOT/f'source/cleaned/{src.name}')
        (x0,y0),(x1,y1) = WAIST_LINES[number]
        yy,xx=np.indices(a.shape[:2])
        waist=y0+(xx-x0)*(y1-y0)/(x1-x0)
        cut=yy>=waist
        if number in ARM_PRESERVE:
            l,t,r,b=ARM_PRESERVE[number]
            cut &= ~((xx>=l)&(xx<r)&(yy>=t)&(yy<b))
        a[cut]=0
        upper=Image.fromarray(a)
        # Pad first: prevents full-canvas edge sampling from smearing tight crops.
        padded = Image.new('RGBA', (raw.width+16,raw.height+16))
        padded.alpha_composite(upper,(8,8))
        scaled = padded.resize(tuple(round(v*SCALE) for v in padded.size), Image.Resampling.LANCZOS)
        offset = (round(256-(belt[0]+8)*SCALE), round(262-(belt[1]+8)*SCALE))
        placed = Image.new('RGBA',(512,512))
        placed.alpha_composite(scaled,offset)
        final = fixed_base.copy()
        final.alpha_composite(placed)
        dest = ROOT/f'frames/hit_react_a_{index}.png'
        final.save(dest)
        frames.append(final)
        records.append({'index':index,'phase':phase,'source':str(src.relative_to(PROJECT)),
                        'source_size':list(raw.size),'source_belt_center':list(belt),
                        'common_scale':SCALE,'offset':list(offset),'duration_ms':60,
                        'source_waist_mask_line':WAIST_LINES[number],
                        'source_arm_preserve_rect':ARM_PRESERVE.get(number),
                        'cleanup':cleanup,'additional_detached_mark_pixels_removed':removed,
                        'file':dest.relative_to(ROOT).as_posix(),
                        'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    frames[0].save(ROOT/'hit_reaction.png',save_all=True,append_images=frames[1:],
                   duration=60,loop=0,disposal=0,blend=0)
    sequence=frames+[idle]
    sequence[0].save(ROOT/'hit_reaction_to_idle.png',save_all=True,append_images=sequence[1:],
                     duration=[60]*4+[400],loop=0,disposal=0,blend=0)
    previews=[]
    for im in sequence:
        bg=Image.new('RGB',(320,280),'#e8eef4')
        small=im.resize((256,256),Image.Resampling.LANCZOS)
        bg.paste(small,(32,0),small)
        ImageDraw.Draw(bg).line((8,224,312,224),fill='#9faebb')
        previews.append(bg)
    previews[0].save(ROOT/'hit_reaction_gameplay.gif',save_all=True,append_images=previews[1:],
                     duration=[60]*4+[400],loop=0,disposal=2)
    sheet=Image.new('RGB',(512*5,550),'#e8eef4')
    draw=ImageDraw.Draw(sheet)
    for i,im in enumerate(sequence):
        x=i*512;sheet.paste(im,(x,0),im)
        draw.line((x,448,x+511,448),fill='#ca7767')
        draw.line((x+256,430,x+256,465),fill='#639ac1')
        label=f'{i+1}: {PLAN[i][2]} ({i*60}ms)' if i<4 else 'Return to approved Idle (240ms)'
        draw.text((x+12,518),label,fill='#183249')
    sheet.save(ROOT/'alignment_sheet.png')
    manifest={'canvas':[512,512],'root':[256,448],'baseline':448,'facing':'right',
              'frame_count':4,'duration_ms':240,'frame_duration_ms':60,
              'source_order':[2,4,3,1],'common_scale':SCALE,'integrated':False,
              'generated_artwork':False,'frames':records,
              'fixed_lower_body':'Approved Idle lower body, with a small abdomen connector behind source-specific waist masks. Recoiling elbows can overlap the upper hip; all pixels y>=300 (shorts, legs and feet) remain exact Idle.',
              'limitations':['Supplied low-resolution cutouts have hard/cropped source edges; no missing contour is invented.',
                             'Fixed lower body intentionally omits the source leg poses to avoid cropped boots/sliding.',
                             'Source shading/style and waist joins need review against approved Idle.',
                             'No SpriteKit, XCTest or iPhone execution.']}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Prepared four frames: source order 02,04,03,01; 240ms; no generation.')


if __name__=='__main__':
    main()
