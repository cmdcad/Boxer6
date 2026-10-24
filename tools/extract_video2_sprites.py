#!/usr/bin/env python3
"""Create draft 512x512 transparent SpriteKit frames from Video2_Frame_Groups.zip.

Usage: python3 tools/extract_video2_sprites.py Video2_Frame_Groups.zip --output generated_video2
Dependencies: pip install opencv-python pillow numpy

WARNING: Video screenshots contain overlapping fighters and targeting marks.
This is a DRAFT segmentation utility, not production-quality sprite artwork.
Review every frame and manually redraw/clean occluded arms, legs and gloves.
"""
import argparse
import io
import json
import zipfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

GROUPS = {
    "1_Blue_Punch_1": "jab_blue",
    "2_Blue_Punch_2": "jab_blue_variant2",
    "3_Blue_Punch_3": "jab_blue_variant3",
    "4_Blue_Low_Hit_1": "body_hook_blue",
    "5_Blue_Low_Hit_2": "body_hook_blue_variant2",
    "6_Blue_Uppercut": "uppercut_blue",
}

def extract(image):
    rgb = np.asarray(image.convert("RGB"))
    # Source screenshots: 976x718, Blue on left. Excludes health HUD and text.
    x0, x1, y0, y1 = 110, 685, 65, 592
    crop = rgb[y0:y1, x0:x1]
    hsv = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)
    yy, xx = np.indices(h.shape)
    cyan = (h >= 83) & (h <= 107) & (s < 130) & (v > 105)
    skin = (crop[:,:,0].astype(int) > crop[:,:,1].astype(int) + 15) & (crop[:,:,1].astype(int) > crop[:,:,2].astype(int) + 8) & (v > 70)
    warm_kit = (h < 20) & (s > 140) & (v > 80)
    blue_kit = (h > 105) & (h < 135) & (s > 125) & (v > 75)
    active = (yy < 465) | ((xx > 25) & (xx < crop.shape[1] - 25) & (yy < 510))
    mask = np.full(h.shape, cv2.GC_PR_BGD, np.uint8)
    mask[cyan] = cv2.GC_BGD
    mask[(skin | warm_kit | blue_kit) & active] = cv2.GC_FGD
    mask[(v < 85) & (yy < 425) & (xx > 25) & (xx < crop.shape[1]-25)] = cv2.GC_PR_FGD
    # Eliminate the blue aiming reticle below the fighters.
    reticle = (xx + x0 - 365)**2 + (yy + y0 - 565)**2 < 53**2
    mask[reticle] = cv2.GC_BGD
    mask[cyan] = cv2.GC_BGD
    mask[:4,:] = mask[-4:,:] = mask[:,:3] = mask[:,-4:] = cv2.GC_BGD
    bg = np.zeros((1,65), np.float64)
    fg = np.zeros((1,65), np.float64)
    cv2.grabCut(cv2.cvtColor(crop, cv2.COLOR_RGB2BGR), mask, None, bg, fg, 4, cv2.GC_INIT_WITH_MASK)
    alpha = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(alpha, 8)
    if n > 1:
        largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        alpha[labels != largest] = 0
    alpha = cv2.GaussianBlur(alpha, (3,3), 0.5)
    rgba = Image.fromarray(np.dstack((crop, alpha)), "RGBA")
    scale = 0.72
    resized = rgba.resize((int(rgba.width*scale), int(rgba.height*scale)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (512,512))
    # Same origin/footline as the current SpriteKit fighter sprites.
    canvas.paste(resized, (int(256-(390-x0)*scale), int(448-(565-y0)*scale)), resized)
    return canvas

def main():
    p = argparse.ArgumentParser()
    p.add_argument("archive", type=Path)
    p.add_argument("--output", type=Path, default=Path("generated_video2"))
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = {}
    with zipfile.ZipFile(args.archive) as archive:
        for source, name in GROUPS.items():
            frames = sorted(x for x in archive.namelist() if x.endswith(".png") and "/"+source+"/" in x)
            if not frames: continue
            dest = args.output / name
            dest.mkdir(exist_ok=True)
            for index, filename in enumerate(frames):
                with Image.open(io.BytesIO(archive.read(filename))) as image:
                    extract(image).save(dest / f"{name}_{index:02d}.png", optimize=True)
            manifest[name] = {"frames":len(frames), "fps":24, "status":"draft, manual cleanup required"}
    (args.output/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))

if __name__ == "__main__":
    main()
