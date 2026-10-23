#!/usr/bin/env python3
"""Install Orange Jab V2 without changing cross, CPU, timing, or hit detection.

Usage from the repository root:
  python3 tools/install_orange_jab_v2.py ~/Downloads/Boxer0_Orange_Jab_V2_Game_Ready.zip
  python3 tools/install_orange_jab_v2.py ~/Downloads/Boxer0_Orange_Jab_V2_Game_Ready.zip --apply

The source package contains a 23-frame punch and 13-frame recovery; this
game-ready package samples it into the game's existing six jab frames plus one
dedicated recovery pose. Contact remains on jab_b_3, exactly as before.
"""
import argparse
import json
import shutil
import struct
import zipfile
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / "swift/Boxer0/Boxer0/Assets.xcassets"
NAMES = [f"jab_b_{i}" for i in range(6)] + ["jab_recovery_b_0"]


def validate_png(data, name):
    if len(data) < 26 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{name}: not a PNG")
    w, h = struct.unpack(">II", data[16:24])
    if (w, h) != (512, 512) or data[25] != 6:
        raise ValueError(f"{name}: expected 512x512 RGBA, got {w}x{h}, type {data[25]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--apply", action="store_true", help="Replace validated assets")
    args = parser.parse_args()
    if not CATALOG.is_dir():
        parser.error(f"Asset catalog not found: {CATALOG}")
    with zipfile.ZipFile(args.archive) as z:
        expected = {}
        for name in NAMES:
            prefix = f"Assets.xcassets/{name}.imageset/"
            png, meta = prefix + name + ".png", prefix + "Contents.json"
            if png not in z.namelist() or meta not in z.namelist():
                parser.error(f"Missing {name} image set in ZIP")
            data = z.read(png)
            validate_png(data, name)
            metadata = json.loads(z.read(meta))
            if name + ".png" not in [x.get("filename") for x in metadata.get("images", [])]:
                parser.error(f"Invalid Contents.json for {name}")
            target = CATALOG / f"{name}.imageset"
            if not target.is_dir():
                parser.error(f"Existing image set missing: {target}")
            expected[name] = (data, z.read(meta))
    print("Validated 6 jab frames and 1 recovery pose (512x512 RGBA).")
    print("Cross, bounce, reaction, code, timing and hit detection remain untouched.")
    if not args.apply:
        print("DRY RUN: use --apply to replace the existing jab image sets.")
        return
    for name, (png, metadata) in expected.items():
        folder = CATALOG / f"{name}.imageset"
        (folder / f"{name}.png").write_bytes(png)
        (folder / "Contents.json").write_bytes(metadata)
    print("Installed Orange Jab V2. Inspect in Xcode, then git add/commit/push.")


if __name__ == "__main__":
    main()
