"""Extract actual uploaded artwork, preserving enclosed whites and dark outlines.

Outputs are candidates, not an assertion that the concept sheet is production-ready.
"""
from pathlib import Path
from collections import deque
from PIL import Image,ImageDraw
import numpy as np
import json,shutil
ROOT=Path(__file__).resolve().parent
SOURCE=Path(r'C:\Users\oluwa\Downloads\sprites.png')
GROUPS=[('idle',(0,42,505,195)),('advance',(507,42,1024,195)),('retreat',(1025,42,1536,195)),
 ('guard',(0,264,505,417)),('guard_advance',(508,264,1024,417)),('guard_retreat',(1026,264,1536,417)),
 ('jab',(0,489,506,645)),('cross',(510,489,1025,645)),('hit_react',(1027,489,1536,645)),
 ('block',(0,710,369,855)),('recovery',(379,709,738,855)),('knockdown',(744,710,1536,855)),('rise',(0,897,804,1001))]

def components(mask):
 h,w=mask.shape;seen=np.zeros_like(mask);result=[]
 for y,x in zip(*np.where(mask)):
  if seen[y,x]:continue
  q=deque([(int(y),int(x))]);seen[y,x]=True;points=[]
  while q:
   cy,cx=q.popleft();points.append((cy,cx))
   for yy,xx in [(cy-1,cx),(cy+1,cx),(cy,cx-1),(cy,cx+1)]:
    if 0<=yy<h and 0<=xx<w and mask[yy,xx] and not seen[yy,xx]:seen[yy,xx]=True;q.append((yy,xx))
  if len(points)>180:result.append(points)
 return sorted(result,key=lambda pts:min(x for y,x in pts))

def extract(crop):
 rgb=np.array(crop.convert('RGB'));h,w=rgb.shape[:2]
 grey=(rgb.max(2).astype(int)-rgb.min(2).astype(int)<=16)&(rgb.min(2)>=155)
 outside=np.zeros((h,w),dtype=bool);q=deque()
 for y in range(h):
  for x in [0,w-1]:
   if grey[y,x]:outside[y,x]=True;q.append((y,x))
 for x in range(w):
  for y in [0,h-1]:
   if grey[y,x] and not outside[y,x]:outside[y,x]=True;q.append((y,x))
 while q:
  y,x=q.popleft()
  for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
   if 0<=yy<h and 0<=xx<w and grey[yy,xx] and not outside[yy,xx]:outside[yy,xx]=True;q.append((yy,xx))
 results=[]
 for points in components(~outside):
  yy,xx=np.array(points).T
  left,top,right,bottom=int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)
  if bottom-top<30:continue
  alpha=np.zeros((h,w),dtype=np.uint8);alpha[yy,xx]=255
  rgba=np.dstack([rgb,alpha]);rgba[alpha==0,:3]=0
  results.append((Image.fromarray(rgba).crop((left,top,right,bottom)),[left,top,right,bottom]))
 return results

def main():
 source=Image.open(SOURCE)
 folder=ROOT/'cutouts';folder.mkdir(exist_ok=True)
 records=[];thumbs=[]
 for clip,box in GROUPS:
  found=extract(source.crop(box))
  for i,(im,bounds) in enumerate(found):
   file=f'{clip}_{i}.png';im.save(folder/file)
   sourcebox=[bounds[0]+box[0],bounds[1]+box[1],bounds[2]+box[0],bounds[3]+box[1]]
   records.append({'clip':clip,'candidate':i,'file':'cutouts/'+file,'source_box':sourcebox,'size':list(im.size),'needs_visual_review':True})
   frame=Image.new('RGBA',(160,190),(232,238,244,255));draw=ImageDraw.Draw(frame)
   preview=im.copy();preview.thumbnail((148,160),Image.Resampling.LANCZOS)
   frame.alpha_composite(preview,((160-preview.width)//2,165-preview.height));draw.text((6,172),f'{clip} {i}',fill=(25,42,60));thumbs.append(frame)
  print(clip,len(found),[list(im.size) for im,b in found])
 sheet=Image.new('RGBA',(160*8,190*((len(thumbs)+7)//8)),(232,238,244,255))
 for i,im in enumerate(thumbs):sheet.alpha_composite(im,((i%8)*160,(i//8)*190))
 sheet.convert('RGB').save(ROOT/'extraction_review.png')
 (ROOT/'extraction_manifest.json').write_text(json.dumps({'source':str(SOURCE),'integrated':False,'candidates':records},indent=2)+'\n',encoding='utf-8')
 shutil.copy2(SOURCE,ROOT/'uploaded_sprites_original.png')
if __name__=='__main__':main()
