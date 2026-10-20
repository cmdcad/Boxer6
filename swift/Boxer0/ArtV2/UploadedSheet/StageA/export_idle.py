"""Normalize approved generated frames for review; does not touch live assets.

This export applies one common scale and translates using the sole baseline.
No color key, background removal, body warp or per-frame proportion scaling.
"""
from pathlib import Path
import json
import hashlib
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent

def metrics(image):
    alpha = np.asarray(image)[:,:,3]
    ys, xs = np.where(alpha >= 32)
    bottom = int(ys.max())
    feet_y, feet_x = np.where((alpha >= 32) & (np.indices(alpha.shape)[0] >= bottom-16))
    return dict(bounds=[int(xs.min()),int(ys.min()),int(xs.max())+1,bottom+1],
                sole_y=bottom, foot_center=float((feet_x.min()+feet_x.max())/2))

def main():
    folder = ROOT/'frames'; folder.mkdir(exist_ok=True)
    # Order measured poses into neutral -> inhale -> peak -> settle.
    order = [0, 1, 3, 2]
    images = [Image.open(ROOT/f'source/idle_a_{i}_generated.png').convert('RGBA') for i in order]
    base = metrics(images[0])
    # Common scale, established once, never fit each breathing pose independently.
    scale = 320/(base['sole_y']-base['bounds'][1])
    exported, records = [], []
    for i,image in enumerate(images):
        assert image.getchannel('A').getextrema() == (0,255)
        assert image.size == images[0].size, 'Unexpected generator canvas drift; review first'
        source = metrics(image)
        size = tuple(round(v*scale) for v in image.size)
        resized = image.resize(size,Image.Resampling.LANCZOS)
        # Integer placement preserves PNG alpha; sole pixels define contact baseline.
        resized_metrics = metrics(resized)
        offset = (round(256-resized_metrics['foot_center']),448-resized_metrics['sole_y'])
        canvas = Image.new('RGBA',(512,512))
        canvas.alpha_composite(resized,offset)
        path = folder/f'idle_a_{i}.png'
        canvas.save(path)
        visible = metrics(canvas)
        assert visible['sole_y'] == 448
        assert all(v > 0 for v in visible['bounds'][:2])
        assert visible['bounds'][2] < 512 and visible['bounds'][3] < 512
        records.append(dict(file=path.relative_to(ROOT).as_posix(),duration_ms=200,
                            source_file=f'source/idle_a_{order[i]}_generated.png',
                            source_metrics=source,export_metrics=visible,offset=list(offset),
                            sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        exported.append(canvas)
    # A loop at a 256px sprite canvas: approx160px visible character height.
    preview=[]
    for image in exported:
        frame=Image.new('RGBA',(320,280),(232,238,244,255))
        frame.alpha_composite(image.resize((256,256),Image.Resampling.LANCZOS),(32,20))
        preview.append(frame.convert('RGB'))
    preview[0].save(ROOT/'idle_preview.gif',save_all=True,append_images=preview[1:],duration=200,loop=0)
    # APNG preserves alpha and the exact 512px exported canvases.
    exported[0].save(ROOT/'idle_preview.png',save_all=True,append_images=exported[1:],duration=200,loop=0,disposal=0,blend=0)
    sheet=Image.new('RGBA',(512*4,550),(232,238,244,255))
    draw=ImageDraw.Draw(sheet)
    for i,image in enumerate(exported):
        sheet.alpha_composite(image,(512*i,0))
        draw.line((512*i,448,512*(i+1)-1,448),fill=(210,90,70),width=1)
        draw.line((512*i+256,430,512*i+256,465),fill=(70,130,200),width=1)
        draw.text((512*i+12,520),f'Frame {i+1}: {i*200} ms',fill=(25,42,60))
    sheet.convert('RGB').save(ROOT/'alignment_sheet.png')
    (ROOT/'manifest.json').write_text(json.dumps(dict(canvas=[512,512],root=[256,448],baseline=448,
        facing='right',frame_count=4,loop_ms=800,common_scale=scale,frames=records,
        integrated=False),indent=2)+'\n',encoding='utf-8')
    print('Exported four transparent frames and 800ms GIF/APNG previews; live catalog unchanged.')

if __name__ == '__main__': main()
