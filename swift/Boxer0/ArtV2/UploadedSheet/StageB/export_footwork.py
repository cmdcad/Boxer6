"""Export approved-source footwork candidates without touching live assets.

Every frame uses Stage A's common scale. Bounded pose registration aligns
planted soles to the existing root travel; no frame is fitted or deformed.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent

def measures(image):
    alpha = np.array(image)[:,:,3]
    ys,xs = np.where(alpha >= 32)
    result = {'bounds':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]}
    for name,left,right in [('rear',0,256),('lead',256,512)]:
        fy,fx = np.where(alpha[340:,left:right] >= 32)
        bottom = int(fy.max()+340)
        by,bx = np.where(alpha[bottom-2:bottom+1,left:right] >= 32)
        result[name] = {'sole_y':bottom,'sole_x':float((bx.min()+bx.max())/2+left),
                        'ground_gap':448-bottom}
    return result

def source_for(clip,index):
    path = ROOT/f'source/{clip}_a_{index}_generated.png'
    retry = ROOT/f'source/{clip}_a_{index}_retry.png'
    if retry.exists(): path = retry
    if clip == "advance" and index == 1 and (ROOT/"source/advance_a_1_low_swing.png").exists():
        path = ROOT/"source/advance_a_1_low_swing.png"
    # Both directions naturally share the wide double-plant and closing stance.
    if index == 2 and (ROOT/'source/retreat_a_2_retry.png').exists():
        path = ROOT/'source/retreat_a_2_retry.png'
    if index == 5 and (ROOT/'source/advance_a_5_retry.png').exists():
        path = ROOT/'source/advance_a_5_retry.png'
    return path

def main():
    (ROOT/'frames').mkdir(exist_ok=True)
    stagea = json.loads((ROOT.parent/'StageA/manifest.json').read_text(encoding='utf-8'))
    plan = json.loads((ROOT/'prompts.json').read_text(encoding='utf-8'))
    scale = stagea['common_scale']
    offset = tuple(stagea['frames'][0]['offset'])
    records, images = [], []
    gameplay = {}
    for clip in ['advance','retreat']:
        clip_images = []
        sign = 1 if clip == 'advance' else -1
        wide_raw = Image.open(source_for(clip,2)).convert('RGBA')
        wide_resized = wide_raw.resize(tuple(round(v*scale) for v in wide_raw.size),Image.Resampling.LANCZOS)
        wide_canvas = Image.new('RGBA',(512,512)); wide_canvas.alpha_composite(wide_resized,offset)
        wide = measures(wide_canvas)
        anchors = {foot:wide[foot]['sole_x']+sign*32 for foot in ['rear','lead']}
        for index in range(6):
            name = f'{clip}_a_{index}'
            path = source_for(clip,index)
            raw = Image.open(path)
            assert raw.mode == 'RGBA' and raw.size == (1254,1254), (path,raw.mode,raw.size)
            assert raw.getchannel('A').getextrema() == (0,255)
            resized = raw.resize(tuple(round(v*scale) for v in raw.size),Image.Resampling.LANCZOS)
            image = Image.new('RGBA',(512,512)); image.alpha_composite(resized,offset)
            before = measures(image)
            if index in [2,5]:
                support_y = max(before['rear']['sole_y'],before['lead']['sole_y'])
            else:
                support = ('rear' if index < 3 else 'lead') if clip == 'advance' else ('lead' if index < 3 else 'rear')
                support_y = before[support]['sole_y']
            dy = 448-support_y
            assert abs(dy) <= 12, (path,'excessive source baseline/scale drift',dy)
            support = ('rear' if index < 3 else 'lead') if clip == 'advance' else ('lead' if index < 3 else 'rear')
            # 80ms at100 scene points/s and0.5 sprite scale =16 canvas pixels.
            # Register the pose to that planted contact; retain actual joint motion.
            dx = round(anchors[support]-sign*16*index-before[support]['sole_x'])
            assert abs(dx) <= 24, (path,'excessive root-motion pose registration',dx)
            image = Image.new('RGBA',(512,512))
            image.alpha_composite(resized,(offset[0]+dx,offset[1]+dy))
            dest = ROOT/f'frames/{name}.png'; image.save(dest)
            job = next(j for j in plan['jobs'] if j['clip'] == clip and j['index'] == index)
            records.append({'clip':clip,'index':index,'file':dest.relative_to(ROOT).as_posix(),
                'duration_ms':80,'selected_source':path.relative_to(ROOT).as_posix(),'vertical_registration':dy,'horizontal_registration':dx,'support':support,'planned_pose':{k:job[k] for k in ['lead_dx','rear_dx','lead_lift','rear_lift','phase']},
                'measurements':measures(image),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
            clip_images.append(image); images.append(image)
        clip_images[0].save(ROOT/f'{clip}_preview.png',save_all=True,append_images=clip_images[1:],
                            duration=80,loop=0,disposal=0,blend=0)
        preview = []
        for index,image in enumerate(clip_images):
            frame = Image.new('RGBA',(360,280),(232,238,244,255)); draw=ImageDraw.Draw(frame)
            draw.line((0,244,359,244),fill=(140,155,168))
            sign = 1 if clip == 'advance' else -1
            shift = (-sign*8*index)%24
            for x in range(-24,385,24): draw.line((x+shift,244,x+shift,258),fill=(140,155,168))
            frame.alpha_composite(image.resize((256,256),Image.Resampling.LANCZOS),(52,20))
            draw.text((8,7),clip.upper()+' / 480 ms',fill=(25,42,60))
            preview.append(frame.convert('RGB'))
        gameplay[clip] = preview
        preview[0].save(ROOT/f'{clip}_gameplay.gif',save_all=True,append_images=preview[1:],duration=80,loop=0)
    combined = []
    for i in range(6):
        frame = Image.new('RGB',(720,280))
        frame.paste(gameplay['advance'][i],(0,0)); frame.paste(gameplay['retreat'][i],(360,0))
        combined.append(frame)
    combined[0].save(ROOT/'movement_preview.gif',save_all=True,append_images=combined[1:],duration=80,loop=0)
    sheet = Image.new('RGBA',(512*6,550*2),(232,238,244,255)); draw=ImageDraw.Draw(sheet)
    for n,image in enumerate(images):
        x=(n%6)*512; y=(n//6)*550
        sheet.alpha_composite(image,(x,y))
        draw.line((x,y+448,x+511,y+448),fill=(210,90,70))
        draw.line((x+256,y+430,x+256,y+465),fill=(70,130,200))
        draw.text((x+12,y+520),f'{records[n]["clip"]} {n%6+1}: {n%6*80} ms',fill=(25,42,60))
    sheet.convert('RGB').save(ROOT/'alignment_sheet.png')
    slip = {}
    for clip,sign in [('advance',1),('retreat',-1)]:
        poses = [r for r in records if r['clip'] == clip]
        support = [('rear',[-1,0,1,2]),('lead',[2,3,4,5])] if clip == 'advance' else [('lead',[-1,0,1,2]),('rear',[2,3,4,5])]
        slip[clip] = []
        for foot,indices in support:
            world = [sign*8*i+poses[i%6]['measurements'][foot]['sole_x']*.5 for i in indices]
            slip[clip].append({'support':foot,'frames':indices,'world_sole_positions':world,
                              'range_px':max(world)-min(world)})
    manifest = {'canvas':[512,512],'root':[256,448],'baseline':448,'facing':'right',
        'frame_count_per_clip':6,'loop_ms':480,'common_scale':scale,'common_offset':list(offset),
        'integrated':False,'preview_root_speed':100,'preview_sprite_scale':.5,
        'plant_slip_diagnostic':slip,'frames':records}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('Exported12 footwork frames,480ms APNG/GIF loops and common-transform alignment sheet.')

if __name__ == '__main__': main()
