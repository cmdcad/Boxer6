"""Deterministic costume-only palette variants; never move or resample pixels."""
from pathlib import Path
import hashlib
import json
import zipfile
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
BASE = HERE.parent

def mappings():
    rows = []
    def add(stage, source, target):
        rows.append((BASE / stage / 'frames' / (source + '.png'), target + '.png'))
    for clip, count, stage in [('idle',4,'StageA'),('advance',6,'StageB'),('retreat',6,'StageB')]:
        for i in range(count): add(stage,f'{clip}_a_{i}',f'{clip}_b_{i}')
    for clip, count, target in [('guard_entry',3,'guard'),('guarded_advance',6,'guarded_advance'),('guarded_retreat',6,'guarded_retreat')]:
        for i in range(count): add('StageC',f'{clip}_{i}',f'{target}_b_{i}')
    for clip,count in [('jab',6),('cross',8)]:
        for i in range(count): add('StageD',f'{clip}_{i}',f'{clip}_b_{i}')
        add('StageD',f'{clip}_recovery',f'{clip}_recovery_b_0')
    for clip,count,stage in [('hit_react',4,'HitReaction'),('block_jab',3,'BlockRecoil'),('block_cross',3,'BlockRecoil'),('down',1,'DownRise'),('rise',8,'DownRise'),('knockdown',8,'Knockdown')]:
        for i in range(count): add('StageE/'+stage,f'{clip}_a_{i}',f'{clip}_b_{i}')
    return rows

def recolor(a):
    # HSV conversion retains shading and saturation. Protect neutral ink, skin,
    # white trim, and hidden RGB. Blue costume hue alone becomes orange (26deg).
    rgb = a[:,:,:3].astype(np.float64)/255
    maximum, minimum = rgb.max(2), rgb.min(2)
    delta = maximum-minimum
    hue = np.zeros_like(maximum)
    nz = delta > 0
    r,g,b = rgb.transpose(2,0,1)
    for channel, formula in [(0,(g-b)/np.where(nz,delta,1)%6),(1,(b-r)/np.where(nz,delta,1)+2),(2,(r-g)/np.where(nz,delta,1)+4)]:
        mask = nz & (rgb.argmax(2)==channel)
        hue[mask] = formula[mask]*60
    saturation = delta/np.where(maximum>0,maximum,1)
    mask = (hue>=190)&(hue<=260)&(saturation>=.24)&(maximum>=.16)&(a[:,:,3]>0)
    # Orange hue 26 degrees, preserving each source pixel's value and saturation.
    c = maximum*saturation
    x = c*(26/60)
    m = maximum-c
    orange = np.stack([c+m,x+m,m],axis=2)
    out = a.copy()
    out[:,:,:3][mask] = np.rint(orange[mask]*255).astype(np.uint8)
    return out,mask

def main():
    (HERE/'frames').mkdir(parents=True,exist_ok=True)
    records=[]
    rows=mappings()
    assert len(rows)==74
    for source,name in rows:
        im=Image.open(source).convert('RGBA'); a=np.array(im)
        assert im.size==(512,512)
        out,mask=recolor(a)
        assert np.array_equal(a[:,:,3],out[:,:,3])
        assert np.array_equal(a[~mask],out[~mask])
        assert mask.sum()>100
        target=HERE/'frames'/name
        Image.fromarray(out).save(target)
        records.append({'source':str(source.relative_to(BASE)).replace('\\','/'),'output':'frames/'+name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'recolored_pixels':int(mask.sum()),'alpha_identical':True,'outside_palette_mask_identical':True})
    samples=['idle_b_0.png','guard_b_2.png','jab_b_3.png','cross_b_4.png','hit_react_b_1.png','block_cross_b_1.png','knockdown_b_5.png','down_b_0.png']
    sheet=Image.new('RGB',(1024,4*310),(231,235,239)); draw=ImageDraw.Draw(sheet)
    for n,name in enumerate(samples):
        record=next(r for r in records if r['output']=='frames/'+name)
        x=(n%2)*512; y=(n//2)*310
        for k,path in enumerate([BASE/record['source'],HERE/record['output']]):
            im=Image.open(path).convert('RGBA').resize((256,256),Image.Resampling.LANCZOS)
            sheet.paste(im,(x+k*256,y+25),im)
        draw.text((x+12,y+8),name+'   Blue / Orange',fill=(20,25,35))
    sheet.save(HERE/'palette_comparison.jpg',quality=93)
    for clip,count,ms in [('jab',6,50),('cross',8,60),('knockdown',8,80),('rise',8,100)]:
        frames=[]
        for i in range(count):
            im=Image.open(HERE/'frames'/f'{clip}_b_{i}.png').convert('RGBA')
            bg=Image.new('RGB',(512,512),(231,235,239)); bg.paste(im,(0,0),im)
            ImageDraw.Draw(bg).text((15,15),f'Orange {clip} {i+1}/{count}',fill=(20,25,35))
            frames.append(bg)
        frames[0].save(HERE/f'{clip}_preview.gif',save_all=True,append_images=frames[1:],duration=ms,loop=0)
    report={'passed':True,'frame_count':74,'canvas':[512,512],'root':[256,448],'facing':'right; mirror at runtime','integrated':False,'image_generation_used':False,'method':'HSV costume hues 190–260 degrees, saturation >= .24, value >= .16; replace hue with 26 degrees, preserve saturation/value. No geometric edits.','frames':records}
    (HERE/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (HERE/'validation_results.json').write_text(json.dumps({'passed':True,'frames_checked':74,'alpha_identical':True,'pixels_outside_palette_mask_identical':True,'dimensions_identical':True,'geometry_resampled':False,'device_validation':'not run'},indent=2),encoding='utf-8')
    with zipfile.ZipFile(BASE/'orange_variants_stage_f.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(HERE.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts: z.write(p,p.relative_to(HERE))
    print('PASS: 74 orange frames; exact alpha and all non-costume pixels preserved.')

if __name__=='__main__': main()
