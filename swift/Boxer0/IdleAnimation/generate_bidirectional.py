"""Approved palette-only variants; alpha and pose geometry remain exact."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
INK=np.array([25,42,60],dtype=float)
def variant(source,target,old,new):
    image=Image.open(ROOT/f'frames/{source}.png').convert('RGBA')
    pixels=np.array(image);rgb=pixels[:,:,:3].astype(float)
    v=np.array(old,dtype=float)-INK
    t=np.sum((rgb-INK)*v,axis=2)/np.sum(v*v)
    residual=np.linalg.norm(rgb-(INK+t[:,:,None]*v),axis=2)
    mask=(residual<7)&(t>0.05)&(t<1.04)&(pixels[:,:,3]>0)
    adjusted=np.clip(INK+t[:,:,None]*(np.array(new)-INK),0,255)
    pixels[:,:,:3][mask]=adjusted[mask].round().astype('uint8')
    result=Image.fromarray(pixels)
    assert np.array_equal(pixels[:,:,3],np.array(image)[:,:,3])
    result.save(ROOT/f'frames/{target}.png')
    svg=(ROOT/f'frames/{source}.svg').read_text(encoding='utf-8')
    oldhex='#'+''.join(f'{c:02X}' for c in old)
    newhex='#'+''.join(f'{c:02X}' for c in new)
    svg=svg.replace(oldhex,newhex).replace(oldhex.lower(),newhex)
    (ROOT/f'frames/{target}.svg').write_text(svg,encoding='utf-8')
    folder=ROOT.parent/f'Boxer0/Assets.xcassets/{target}.imageset';folder.mkdir(exist_ok=True)
    result.save(folder/f'{target}.png')
    (folder/'Contents.json').write_text(json.dumps({'images':[{'filename':f'{target}.png','idiom':'universal','scale':'1x'}],'info':{'author':'xcode','version':1}},indent=2)+'\n')
def main():
    variants=[]
    for clip,count in [('jab',6),('cross',8),('hit_react',4),('knockdown',8),('down',1),('rise',8)]:
        source,dest=('a','b') if clip in ['jab','cross'] else ('b','a')
        old,new=((40,118,210),(231,119,40)) if source=='a' else ((231,119,40),(40,118,210))
        for i in range(count):
            src=f'{clip}_{source}_{i}';dst=f'{clip}_{dest}_{i}'
            variant(src,dst,old,new);variants.append({'source':src,'target':dst})
    (ROOT/'bidirectional_manifest.json').write_text(json.dumps({'canvas':[512,512],'root':[256,448],'variants':variants},indent=2)+'\n')
    print(f'Generated{len(variants)} palette variants with identical alpha geometry.')
if __name__=='__main__':main()
