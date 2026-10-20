"""Prepare supplied Down/Rise poses without generation or gameplay edits."""
from pathlib import Path
import hashlib
import json
import runpy
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[3]
INPUT=PROJECT/'ArtV2/Sprites/Cleaned'
IDLE=ROOT.parent.parent/'StageA/frames/idle_a_0.png'
CLEANUP=runpy.run_path(str(INPUT.parent/'clean_edges.py'))
# Ground-root horizontal landmarks, manually reviewed in native source pixels.
ANCHORS={1:162,2:172,3:176,5:172,4:169,7:171,9:174}
ORDER=[1,2,3,5,4,7,9,'idle']
PHASES=['Down','Push onto hands and knees','Lift torso','One knee, guard returning',
        'Crouch on feet','Low standing stance','Settle upright','Approved Idle']


def cleaned_source(number):
    src=INPUT/f'sprite_frame_{number:02}.png'
    archived=ROOT/'source'/src.name
    if archived.exists():src=archived
    raw=Image.open(src).convert('RGBA')
    assert raw.size==(341,227), 'Unexpected source set: do not mix hit-reaction files with Down/Rise.'
    result=raw.copy()
    report={'already_edge_cleaned':True,'edge_cleanup_repeated':False}
    a=np.array(result);blobs=CLEANUP['components'](a[:,:,3]>0)
    body=max(blobs,key=len);keep=np.zeros(a.shape[:2],bool)
    for y,x in body:keep[y,x]=True
    removed=int(((a[:,:,3]>0)&~keep).sum());a[~keep]=0
    return raw,Image.fromarray(a),{**report,'additional_detached_pixels_removed':removed}


def bbox(im):
    y,x=np.where(np.array(im.getchannel('A'))>=32)
    return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]


def main():
    for d in ['frames','source','source/cleaned']:(ROOT/d).mkdir(exist_ok=True)
    idle=Image.open(IDLE).convert('RGBA')
    samples={n:cleaned_source(n) for n in ANCHORS}
    reference_bounds=bbox(samples[9][1]);idle_bounds=bbox(idle)
    scale=(idle_bounds[3]-idle_bounds[1])/(reference_bounds[3]-reference_bounds[1])
    records=[];poses={}
    for n,(raw,clean,report) in samples.items():
        name=f'sprite_frame_{n:02}.png'
        raw.save(ROOT/'source'/name);clean.save(ROOT/'source/cleaned'/name)
        padded=Image.new('RGBA',(raw.width+16,raw.height+16));padded.alpha_composite(clean,(8,8))
        resized=padded.resize(tuple(round(v*scale) for v in padded.size),Image.Resampling.LANCZOS)
        b=bbox(resized)
        offset=(round(256-(ANCHORS[n]+8)*scale),448-(b[3]-1))
        canvas=Image.new('RGBA',(512,512));canvas.alpha_composite(resized,offset)
        poses[n]=canvas
        records.append({'source_number':n,'source':str((INPUT/name).relative_to(PROJECT)),
                        'source_anchor_x':ANCHORS[n],'offset':list(offset),'common_scale':scale,
                        'archived_source_pixel_sha256':hashlib.sha256(raw.tobytes()).hexdigest(),
                        'bounds':bbox(canvas),'cleanup':report})
    down=poses[1];down.save(ROOT/'frames/down_a_0.png')
    frames=[];frame_records=[]
    for i,n in enumerate(ORDER):
        im=idle.copy() if n=='idle' else poses[n]
        path=ROOT/f'frames/rise_a_{i}.png';im.save(path);frames.append(im)
        frame_records.append({'index':i,'source_number':n,'phase':PHASES[i],
                              'file':path.relative_to(ROOT).as_posix(),'duration_ms':100,
                              'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bounds':bbox(im)})
    frames[0].save(ROOT/'rise.png',save_all=True,append_images=frames[1:],duration=100,loop=0,disposal=0,blend=0)
    sheet=Image.new('RGB',(512*4,550*2),'#e8eef4');d=ImageDraw.Draw(sheet)
    for i,im in enumerate(frames):
        x,y=(i%4)*512,(i//4)*550;sheet.paste(im,(x,y),im)
        d.line((x,y+448,x+511,y+448),fill='#ca7767')
        d.line((x+256,y+430,x+256,y+465),fill='#639ac1')
        d.text((x+12,y+518),f'{i+1}: {PHASES[i]} ({i*100}ms)',fill='#183249')
    sheet.save(ROOT/'alignment_sheet.png')
    preview=[]
    sequence=[(down,'Down (held)',400)]+[(im,f'Rise {i+1}/8',100) for i,im in enumerate(frames)]+[(idle,'Standing',400)]
    for im,label,ms in sequence:
        bg=Image.new('RGB',(320,280),'#e8eef4');small=im.resize((256,256),Image.Resampling.LANCZOS)
        bg.paste(small,(32,0),small);d=ImageDraw.Draw(bg)
        d.line((8,224,312,224),fill='#9faebb');d.text((12,255),label,fill='#183249')
        preview.append(bg)
    preview[0].save(ROOT/'down_rise_gameplay.gif',save_all=True,append_images=preview[1:],
                     duration=[ms for im,label,ms in sequence],loop=0,disposal=2)
    manifest={'canvas':[512,512],'root':[256,448],'baseline':448,'facing':'right',
              'integrated':False,'image_generation_used':False,'rise_frame_count':8,'rise_duration_ms':800,
              'common_scale':scale,'source_order':ORDER,'source_registration':records,'frames':frame_records,
              'down':{'file':'frames/down_a_0.png','held':True,'sha256':hashlib.sha256((ROOT/'frames/down_a_0.png').read_bytes()).hexdigest()},
              'excluded_sources':{'06':'Upright alternative; omits the low-stance transition if used too early.',
                                  '08':'Standing alternative;09 is selected before exact approved Idle.'},
              'limits':['Source artwork is low resolution and softer than approved Idle; no missing detail was generated.',
                        'Manual ground-root landmarks and source pose changes require visual review; no skeletal contact rig is claimed.',
                        'Feet may reposition naturally while rising; root remains logically fixed. This is not stationary punch/block artwork.',
                        'Not a falling/Knockdown clip; reversing Rise is not an authored fall.',
                        'No Swift, texture-catalog, XCTest, SpriteKit or iPhone execution changes.']}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Prepared Down +8 Rise frames,800ms; common scale{scale:.6f}; no generation.')


if __name__=='__main__':main()
