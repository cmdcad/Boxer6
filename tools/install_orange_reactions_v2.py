#!/usr/bin/env python3
"""Install approved Boxer0 Orange Reaction V2 assets from their ZIP.

Run from repository root:
  python3 tools/install_orange_reactions_v2.py ~/Downloads/Boxer0_Orange_Reactions_V2_Install.zip
  python3 tools/install_orange_reactions_v2.py ~/Downloads/Boxer0_Orange_Reactions_V2_Install.zip --apply

Without --apply, this validates and previews the replacement. Only the 32
normal/heavy Orange reaction image sets are touched; bounce is left unchanged.
"""
import argparse
import json
import shutil
import struct
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CATALOG = REPO / "swift/Boxer0/Boxer0/Assets.xcassets"
GROUPS = (("orange_normal", 18), ("orange_heavy", 14))


def expected_paths():
    for prefix, count in GROUPS:
        for index in range(count):
            name = f"{prefix}_{index:02d}"
            folder = f"Assets.xcassets/{name}.imageset"
            yield name, f"{folder}/{name}.png", f"{folder}/Contents.json"


def validate_png(data, name):
    if data[:8] != b"\x89PNG\r\n\x1a\n" or len(data) < 26:
        raise ValueError(f"{name}: invalid PNG")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (512, 512) or data[25] != 6:
        raise ValueError(f"{name}: expected 512x512 RGBA PNG, got {width}x{height}, color type {data[25]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip", type=Path, help="Approved Orange V2 ZIP")
    parser.add_argument("--apply", action="store_true", help="Replace image sets after validation")
    args = parser.parse_args()
    if not CATALOG.is_dir():
        parser.error(f"Asset catalog missing: {CATALOG}")
    expected = list(expected_paths())
    with zipfile.ZipFile(args.zip) as archive:
        names = set(archive.namelist())
        required = {p for _, png, meta in expected for p in (png, meta)}
        missing = sorted(required - names)
        if missing:
            parser.error(f"ZIP missing {len(missing)} required files: {missing[:3]}")
        for name, png, meta in expected:
            validate_png(archive.read(png), name)
            config = json.loads(archive.read(meta))
            filenames = [item.get("filename") for item in config.get("images", [])]
            if f"{name}.png" not in filenames:
                parser.error(f"{meta}: does not reference {name}.png")
            if not (CATALOG / f"{name}.imageset").is_dir():
                parser.error(f"Expected existing image set missing: {name}.imageset")
        print(f"Validated {len(expected)} image sets (18 normal + 14 heavy).")
        print("Orange bounce assets will not be changed.")
        if not args.apply:
            print("DRY RUN: rerun with --apply to install.")
            return
        # Stage and validate all files before modifying any existing imageset.
        with tempfile.TemporaryDirectory(prefix="boxer0-orange-v2-") as temp:
            staging = Path(temp)
            for name, png, meta in expected:
                folder = staging / f"{name}.imageset"
                folder.mkdir()
                (folder / f"{name}.png").write_bytes(archive.read(png))
                (folder / "Contents.json").write_bytes(archive.read(meta))
            for name, _, _ in expected:
                source = staging / f"{name}.imageset"
                target = CATALOG / f"{name}.imageset"
                shutil.copy2(source / f"{name}.png", target / f"{name}.png")
                shutil.copy2(source / "Contents.json", target / "Contents.json")
    print("Installed Orange V2 reactions. Review 'git diff' before committing.")


if __name__ == "__main__":
    main()
