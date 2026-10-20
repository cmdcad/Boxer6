from pathlib import Path
import hashlib
import json
import runpy
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent


def main():
    manifest=json.loads((ROOT/'manifest.json').read_text())
    idle=np.array(Image.open(ROOT.parent.parent/'StageA/frames/idle_a_0.png'))
    components=runpy.run_path(str(ROOT.parents[3]/'ArtV2/Sprites/clean_edges.py'))['components']
    errors=[]
    rows=[]
    for rec in manifest['frames']:
        p=ROOT/rec['file'];im=Image.open(p);a=np.array(im);alpha=a[:,:,3]
        yy,xx=np.where(alpha>=32)
        blobs=components(alpha>=32)
        significant=[len(b) for b in blobs if len(b)>=12]
        checks={'rgba512':im.mode=='RGBA' and im.size==(512,512),
                'alpha_range':bool(alpha.min()==0 and alpha.max()==255),
                'single_silhouette':len(significant)==1,
                'baseline448':int(yy.max())==448,
                'fixed_legs_and_feet':bool(np.array_equal(a[300:],idle[300:])),
                'clear_margins':bool(not (alpha[:8]>=32).any() and not (alpha[-8:]>=32).any() and not (alpha[:,:8]>=32).any() and not (alpha[:,-8:]>=32).any()),
                'hash':hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256']}
        for name,ok in checks.items():
            if not ok: errors.append(p.name+': '+name)
        rows.append({'file':p.name,'checks':checks,'significant_component_sizes':significant,
                     'bounds':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]})
    if len(manifest['frames'])!=4 or len({r['sha256'] for r in manifest['frames']})!=4:
        errors.append('Expected four distinct frames')
    timings={}
    for filename,expected in [('hit_reaction.png',[60]*4),('hit_reaction_to_idle.png',[60]*4+[400]),
                              ('hit_reaction_gameplay.gif',[60]*4+[400])]:
        im=Image.open(ROOT/filename);duration=[]
        for i in range(im.n_frames):
            im.seek(i);duration.append(im.info.get('duration'))
        timings[filename]=duration
        if duration!=expected: errors.append(filename+': incorrect timing')
        if filename=='hit_reaction_to_idle.png' and not np.array_equal(np.array(im.convert('RGBA')),idle):
            errors.append('Final preview pose is not exact approved Idle')
    result={'passed':not errors,'errors':errors,'frames':rows,'timings_ms':timings,
            'source_order':manifest['source_order'],'image_generation_used':False,
            'limits':manifest['limitations']}
    (ROOT/'validation_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':not errors,'errors':errors,'timings':timings},indent=2))
    assert not errors


if __name__=='__main__':main()
