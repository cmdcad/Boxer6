"""Assemble extracted/reused/reconstructed fall poses at the existing timing."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
DOWNRISE=ROOT.parent/'DownRise'
HIT=ROOT.parent/'HitReaction'
IDLE=ROOT.parent.parent/'StageA/frames/idle_a_0.png'
PHASES=['Standing collapse','Drop to hands and knees','Knees give way',
        'Collapse onto forearms','Fall onto side','Torso lands','Settle lower','Exact Down']


def bounds(im):
    y,x=np.where(np.array(im.getchannel('A'))>=32)
    assert len(x)
    return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]


def main():
    (ROOT/'frames').mkdir(exist_ok=True)
    records=[];frames=[]
    down=Image.open(DOWNRISE/'frames/down_a_0.png').convert('RGBA')
    idle=Image.open(IDLE).convert('RGBA')
    down.save(ROOT/'source/reference_down.png');idle.save(ROOT/'source/reference_idle.png')
    for i in range(8):
        dy=0;scale=1
        if i==0:
            source=ROOT/'source/fall_start_extracted.png'
            raw=Image.open(source).convert('RGBA')
            scale=320/145 # Original illustrated standing-height contract.
            resized=raw.resize(tuple(round(v*scale) for v in raw.size),Image.Resampling.LANCZOS)
            b=bounds(resized);dy=448-(b[3]-1)
            im=Image.new('RGBA',(512,512));im.alpha_composite(resized,(round(256-50*scale),dy))
            method='Extracted authored standing-collapse pose; neighbor separated by reviewed mask.'
        elif i in [1,2]:
            n=2 if i==1 else 1
            source=DOWNRISE/f'frames/rise_a_{n}.png'
            im=Image.open(source).convert('RGBA')
            im.save(ROOT/f'source/kneeling_reference_{i}.png')
            method='Reused intact kneeling configuration from supplied artwork.'
        elif i<=6:
            source=ROOT/f'source/knockdown_a_{i}_reconstructed.png'
            raw=Image.open(source).convert('RGBA')
            assert raw.width==raw.height,(source,raw.size)
            resized=raw.resize((512,512),Image.Resampling.LANCZOS)
            dy=448-(bounds(resized)[3]-1)
            assert abs(dy)<=24,(source,'Excessive floor correction',dy)
            im=Image.new('RGBA',(512,512));im.alpha_composite(resized,(0,dy))
            method='Built-in imagegen reconstruction of obscured/missing collapse transition.'
        else:
            source=DOWNRISE/'frames/down_a_0.png';im=down.copy()
            method='Exact existing prepared Down pose.'
        p=ROOT/f'frames/knockdown_a_{i}.png';im.save(p);frames.append(im)
        records.append({'index':i,'phase':PHASES[i],'file':p.relative_to(ROOT).as_posix(),
                        'duration_ms':80,'source':str(source),'method':method,
                        'source_scale':scale,'vertical_registration':dy,'bounds':bounds(im),
                        'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    frames[0].save(ROOT/'knockdown.png',save_all=True,append_images=frames[1:],
                   duration=80,loop=0,disposal=0,blend=0)
    sheet=Image.new('RGB',(512*4,550*2),'#e8eef4');d=ImageDraw.Draw(sheet)
    for i,im in enumerate(frames):
        x,y=(i%4)*512,(i//4)*550;sheet.paste(im,(x,y),im)
        d.line((x,y+448,x+511,y+448),fill='#ca7767')
        d.line((x+256,y+430,x+256,y+465),fill='#639ac1')
        d.text((x+12,y+518),f'{i+1}: {PHASES[i]} ({i*80}ms)',fill='#183249')
    sheet.save(ROOT/'alignment_sheet.png')
    hit=[Image.open(HIT/f'frames/hit_react_a_{i}.png').convert('RGBA') for i in range(4)]
    seq=[(idle,'Standing',400)]+[(im,f'Final hit reaction {i+1}/4',60) for i,im in enumerate(hit)]+[(im,f'Knockdown {i+1}/8',80) for i,im in enumerate(frames)]+[(down,'Down held',600)]
    preview=[]
    for im,label,ms in seq:
        bg=Image.new('RGB',(320,280),'#e8eef4');small=im.resize((256,256),Image.Resampling.LANCZOS)
        bg.paste(small,(32,0),small);d=ImageDraw.Draw(bg)
        d.line((8,224,312,224),fill='#9faebb');d.text((12,255),label,fill='#183249');preview.append(bg)
    preview[0].save(ROOT/'defeat_sequence_gameplay.gif',save_all=True,append_images=preview[1:],
                     duration=[ms for im,label,ms in seq],loop=0,disposal=2)
    fall_preview=preview[5:]
    fall_preview[0].save(ROOT/'knockdown_gameplay.gif',save_all=True,append_images=fall_preview[1:],
                         duration=[80]*8+[600],loop=0,disposal=2)
    manifest={'canvas':[512,512],'root':[256,448],'baseline':448,'facing':'right',
              'frame_count':8,'duration_ms':640,'frame_duration_ms':80,'integrated':False,
              'reconstructed_frames':[3,4,5,6],'frames':records,
              'limits':['Mixed source resolutions/shading require review for motion/visual consistency.',
                        'Generated collapse anatomy and transitions require visual inspection.',
                        'Floor registration is a pixel-space diagnostic, not a skeletal contact model.',
                        'No Swift, catalog, XCTest, SpriteKit or iPhone validation/integration performed.']}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Assembled8 fall frames,640ms, ending at exact prepared Down.')


if __name__=='__main__':main()
