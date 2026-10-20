from pathlib import Path
from fractions import Fraction
import hashlib
import json
import runpy
import struct
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent


def apng_delays(path):
    data=path.read_bytes();offset=8;delays=[]
    while offset<len(data):
        length=struct.unpack('>I',data[offset:offset+4])[0]
        if data[offset+4:offset+8]==b'fcTL':
            payload=data[offset+8:offset+8+length]
            n,d=struct.unpack('>HH',payload[20:24]);delays.append(Fraction(n,d or 100))
        offset+=length+12
    return delays


def head_x(a):
    yy,xx=np.where(a[125:170,:,3]>=128)
    return float(xx.mean())


def glove(a):
    rgb=a[:220,:,:3].astype(int)
    return (rgb[:,:,2]>90)&(rgb[:,:,0]<120)&(rgb[:,:,2]>rgb[:,:,0]*1.4)&(rgb[:,:,2]>rgb[:,:,1]*1.1)&(a[:220,:,3]>=128)


def main():
    manifest=json.loads((ROOT/'manifest.json').read_text())
    base=np.array(Image.open(ROOT/'source/held_guard.png'))
    component_fn=runpy.run_path(str(ROOT.parents[3]/'ArtV2/Sprites/clean_edges.py'))['components']
    errors=[];rows=[];motion={}
    if len(manifest['frames'])!=6:errors.append('Expected six production PNGs')
    for rec in manifest['frames']:
        p=ROOT/rec['file'];im=Image.open(p);a=np.array(im);alpha=a[:,:,3]
        y,x=np.where(alpha>=32)
        blobs=component_fn(alpha>=32)
        shift=head_x(base)-head_x(a)
        glove_ratio=float(glove(a).sum()/glove(base).sum())
        checks={'rgba512':im.size==(512,512) and im.mode=='RGBA',
                'exact_fixed_lower_body':bool(np.array_equal(a[258:],base[258:])),
                'alpha':bool(alpha.min()==0 and alpha.max()==255),
                'single_silhouette':len([b for b in blobs if len(b)>=12])==1,
                'baseline448':int(y.max())==448,
                'clear_margins':bool(not (alpha[:8]>=32).any() and not (alpha[-8:]>=32).any() and not (alpha[:,:8]>=32).any() and not (alpha[:,-8:]>=32).any()),
                'visible_upper_body_shift':shift>0.5,
                'guard_gloves_retained':.95<=glove_ratio<=1.05,
                'checksum':hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256']}
        for key,ok in checks.items():
            if not ok:errors.append(p.name+': '+key)
        rows.append({'file':p.name,'checks':checks,'head_region_backward_shift_px':shift,
                     'guard_glove_area_ratio':glove_ratio})
        motion.setdefault(rec['kind'],[]).append(shift)
    for kind,ms in [('jab',120),('cross',160)]:
        frames=[r for r in manifest['frames'] if r['kind']==kind]
        if len(frames)!=3 or len({r['sha256'] for r in frames})!=3:
            errors.append(kind+': wrong count or duplicate poses')
        if not (motion[kind][1]>motion[kind][0]>motion[kind][2]):
            errors.append(kind+': expected onset, peak, return')
        for suffix,expected in [('',[Fraction(ms,3000)]*3),
                                 ('_to_guard',[Fraction(ms,3000)]*3+[Fraction(2,5)])]:
            p=ROOT/f'block_{kind}{suffix}.png'
            if apng_delays(p)!=expected:errors.append(p.name+': wrong rational timing')
            if suffix:
                im=Image.open(p);im.seek(im.n_frames-1)
                if not np.array_equal(np.array(im.convert('RGBA')),base):
                    errors.append(kind+': not exact held guard at completion')
    if motion['cross'][1]<=motion['jab'][1]+3:
        errors.append('Cross peak must be visibly stronger than Jab')
    result={'passed':not errors,'errors':errors,'frames':rows,'head_region_shifts_px':motion,
            'exact_apng_durations_ms':{'jab':120,'cross':160},
            'image_generation_used':False,'limits':manifest['limits']}
    (ROOT/'validation_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':not errors,'errors':errors,'head_region_shifts_px':motion},indent=2))
    assert not errors


if __name__=='__main__':main()
