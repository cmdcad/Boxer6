from pathlib import Path
from collections import deque
import runpy
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[3]


def main():
    (ROOT/'source').mkdir(exist_ok=True)
    strip=Image.open(PROJECT/'ArtV2/Manual/Knockdown/reference_knockdown_strip.png')
    strip.crop((260,55,390,153)).save(ROOT/'source/elbows_collapse_reference.png')
    strip.crop((337,70,505,153)).save(ROOT/'source/side_collapse_reference.png')
    strip.crop((475,75,618,153)).save(ROOT/'source/near_down_reference.png')
    raw=strip.crop((0,15,100,153)).convert('RGBA')
    a=np.array(raw);rgb=a[:,:,:3].astype(int)
    # Border-connected checkerboard only; preserve interior costume whites.
    candidate=(rgb.min(2)>140)&(np.ptp(rgb,axis=2)<25)
    seen=np.zeros(candidate.shape,bool);q=deque()
    h,w=candidate.shape
    for y,x in [(0,x) for x in range(w)]+[(h-1,x) for x in range(w)]+[(y,0) for y in range(h)]+[(y,w-1) for y in range(h)]:
        if candidate[y,x] and not seen[y,x]:seen[y,x]=True;q.append((y,x))
    while q:
        y,x=q.popleft()
        for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
            if 0<=yy<h and 0<=xx<w and not seen[yy,xx] and candidate[yy,xx]:
                seen[yy,xx]=True;q.append((yy,xx))
    a[seen,3]=0
    # Reviewed boundary separates the next figure's rear boot from this pose.
    mask=Image.new('L',raw.size)
    ImageDraw.Draw(mask).polygon([(0,0),(100,0),(100,75),(84,98),(77,115),
                                 (74,125),(86,130),(86,138),(0,138)],fill=255)
    a[np.array(mask)==0,3]=0
    cleanup=runpy.run_path(str(PROJECT/'ArtV2/Sprites/clean_edges.py'))
    clean,report=cleanup['clean'](Image.fromarray(a))
    arr=np.array(clean);blobs=cleanup['components'](arr[:,:,3]>0);body=max(blobs,key=len)
    keep=np.zeros(arr.shape[:2],bool)
    for y,x in body:keep[y,x]=True
    arr[~keep]=0
    Image.fromarray(arr).save(ROOT/'source/fall_start_extracted.png')
    print('Saved first-pose extraction and three overlap references; no generation.')


if __name__=='__main__':main()
