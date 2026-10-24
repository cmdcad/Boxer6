#!/usr/bin/env python3
"""Preflight draft Phase 6 PNG sequences; this never creates or alters artwork.

Usage: python3 tools/check_sprite_frames.py generated_video2
Requires Pillow. Exits nonzero on missing frames, dimensions or alpha failures.
Footline variance is reported for manual inspection, not silently corrected.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from PIL import Image

EXPECTED = ("jab_blue", "body_hook_blue", "uppercut_blue")
FRAME = re.compile(r"_(\d+)\.png$", re.IGNORECASE)


def inspect(root):
    problems = []
    sequences = {}
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        files = sorted(folder.glob("*.png"))
        if not files:
            problems.append(f"{folder.name}: no PNG frames")
            continue
        indexes = []
        feet = []
        transparent = 0
        for path in files:
            match = FRAME.search(path.name)
            if not match:
                problems.append(f"{path.name}: expected numbered _00.png suffix")
            else:
                indexes.append(int(match.group(1)))
            with Image.open(path) as image:
                if image.size != (512, 512):
                    problems.append(f"{path}: expected 512x512, got {image.size}")
                if image.mode != "RGBA":
                    problems.append(f"{path}: expected RGBA, got {image.mode}")
                    continue
                alpha = image.getchannel("A")
                lo, hi = alpha.getextrema()
                if lo != 0:
                    problems.append(f"{path}: background is not transparent")
                if hi == 0:
                    problems.append(f"{path}: empty silhouette")
                if lo == 0:
                    transparent += 1
                bounds = alpha.getbbox()
                if bounds:
                    feet.append(bounds[3])
        if indexes != list(range(len(files))):
            problems.append(f"{folder.name}: frames must be consecutively numbered from 00")
        sequences[folder.name] = {
            "frames": len(files),
            "transparent_frames": transparent,
            "footline_range_px": (max(feet) - min(feet)) if feet else None,
            "review_required": True,
        }
    for name in EXPECTED:
        if name not in sequences:
            problems.append(f"missing expected reference sequence: {name}")
    return {"sequences": sequences, "problems": problems,
            "note": "Passing preflight does not certify cleaned limbs, reaction timing, or production-ready art."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not args.directory.is_dir():
        parser.error("directory does not exist")
    report = inspect(args.directory)
    output = json.dumps(report, indent=2) + "\n"
    print(output, end="")
    if args.report:
        args.report.write_text(output, encoding="utf-8")
    return 1 if report["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
