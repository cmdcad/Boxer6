from pathlib import Path
import hashlib
import json
import runpy
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent


def main():
    m=json.loads((ROOT/'manifest.json').read_text())
    comp=runpy.run_path(str(ROOT.parents[3]/'ArtV2/Sprites/clean_edges.py'))['components']
    idle=np.array(Image.open(ROOT.parent.parent/'StageA/frames/idle_a_0.png'))
    rows=[];errors=[]
    items=[m['down']]+m['frames']
    for r in items:
        p=ROOT/r['file'];im=Image.open(p);a=np.array(im);alpha=a[:,:,3]
        y,x=np.where(alpha>=32);blobs=comp(alpha>=32)
        checks={'rgba512':im.mode=='RGBA' and im.size==(512,512),
                'alpha':bool(alpha.min()==0 and alpha.max()==255),
                'one_significant_silhouette':len([v for v in blobs if len(v)>=12])==1,
                'baseline448':int(y.max())==448,
                'clear_margins':bool(not (alpha[:8]>=32).any() and not (alpha[-8:]>=32).any() and not (alpha[:,:8]>=32).any() and not (alpha[:,-8:]>=32).any()),
                'checksum':hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']}
        for key,ok in checks.items():
            if not ok:errors.append(p.name+': '+key)
        rows.append({'file':p.name,'checks':checks,
                     'bounds':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]})
    if len(m['frames'])!=8 or len({r['sha256'] for r in m['frames']})!=8:
        errors.append('Expected eight distinct Rise frames')
    down=Image.open(ROOT/m['down']['file']).convert('RGBA')
    first=Image.open(ROOT/m['frames'][0]['file']).convert('RGBA')
    final=np.array(Image.open(ROOT/m['frames'][-1]['file']).convert('RGBA'))
    if down.tobytes()!=first.tobytes():errors.append('Rise does not start in exact Down pose')
    if not np.array_equal(final,idle):errors.append('Rise does not end in exact approved Idle')
    for rec in m['source_registration']:
        p=ROOT/f"source/sprite_frame_{rec['source_number']:02}.png"
        im=Image.open(p).convert('RGBA')
        if im.size!=(341,227) or hashlib.sha256(im.tobytes()).hexdigest()!=rec['archived_source_pixel_sha256']:
            errors.append(p.name+': source set mismatch')
        if rec['common_scale']!=m['common_scale']:errors.append('Per-pose scale mismatch')
    times={}
    for filename,expected in [('rise.png',[100]*8),('down_rise_gameplay.gif',[400]+[100]*8+[400])]:
        im=Image.open(ROOT/filename);durations=[]
        for i in range(im.n_frames):im.seek(i);durations.append(im.info.get('duration'))
        times[filename]=durations
        if durations!=expected:errors.append(filename+': wrong duration/count')
    result={'passed':not errors,'errors':errors,'frames':rows,'timings_ms':times,
            'source_order':m['source_order'],'image_generation_used':False,'limits':m['limits']}
    (ROOT/'validation_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':not errors,'errors':errors,'timings_ms':times},indent=2))
    assert not errors


if __name__=='__main__':main()
