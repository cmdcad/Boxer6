from pathlib import Path
import hashlib
import json
import runpy
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent


def main():
    m=json.loads((ROOT/'manifest.json').read_text())
    components=runpy.run_path(str(ROOT.parents[3]/'ArtV2/Sprites/clean_edges.py'))['components']
    errors=[];rows=[]
    if len(m['frames'])!=8 or len({r['sha256'] for r in m['frames']})!=8:
        errors.append('Expected eight distinct fall frames')
    for rec in m['frames']:
        p=ROOT/rec['file'];im=Image.open(p);a=np.array(im);alpha=a[:,:,3]
        yy,xx=np.where(alpha>=32);blobs=components(alpha>=32)
        rgb=a[:,:,:3].astype(int)
        gray=(np.ptp(rgb,axis=2)<6)&(rgb.mean(2)>100)&(rgb.mean(2)<230)&(alpha>=240)
        checks={'rgba512':im.size==(512,512) and im.mode=='RGBA',
                'alpha':bool(alpha.min()==0 and alpha.max()==255),
                'one_significant_silhouette':len([b for b in blobs if len(b)>=12])==1,
                'baseline448':int(yy.max())==448,
                'clear_margins':bool(not (alpha[:8]>=32).any() and not (alpha[-8:]>=32).any() and not (alpha[:,:8]>=32).any() and not (alpha[:,-8:]>=32).any()),
                'no_large_checkerboard_region':int(gray.sum())<1000,
                'checksum':hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256']}
        for name,ok in checks.items():
            if not ok:errors.append(p.name+': '+name)
        rows.append({'file':p.name,'checks':checks,'bounds':rec['bounds'],
                     'significant_component_sizes':[len(b) for b in blobs if len(b)>=12]})
    final=Image.open(ROOT/m['frames'][-1]['file']).convert('RGBA')
    down=Image.open(ROOT.parent/'DownRise/frames/down_a_0.png').convert('RGBA')
    if final.tobytes()!=down.tobytes():errors.append('Fall final frame does not match exact held Down')
    times={}
    for filename,expected in [('knockdown.png',[80]*8),
                              ('knockdown_gameplay.gif',[80]*8+[600]),
                              ('defeat_sequence_gameplay.gif',[400]+[60]*4+[80]*8+[600])]:
        im=Image.open(ROOT/filename);duration=[]
        for i in range(im.n_frames):im.seek(i);duration.append(im.info.get('duration'))
        times[filename]=duration
        if duration!=expected:errors.append(filename+': wrong duration/count')
    top=[r['bounds'][1] for r in m['frames']]
    motion_warnings=[]
    for i in range(1,len(top)):
        if top[i]<top[i-1]-12:
            motion_warnings.append(f'Frame{i+1} rises by{top[i-1]-top[i]}px; inspect continuity')
    result={'passed':not errors,'errors':errors,'motion_review_warnings':motion_warnings,
            'frames':rows,'timings_ms':times,'reconstructed_frames':m['reconstructed_frames'],
            'limits':m['limits']}
    (ROOT/'validation_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':not errors,'errors':errors,'motion_review_warnings':motion_warnings,'top_y':top},indent=2))
    assert not errors


if __name__=='__main__':main()
