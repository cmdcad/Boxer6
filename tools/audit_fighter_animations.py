#!/usr/bin/env python3
"""Phase 3: inventory both fighters' animation assets and runtime references.

Run from any directory:
    python3 tools/audit_fighter_animations.py
    python3 tools/audit_fighter_animations.py --markdown

No image generation or modifications. 'Present' means catalog completeness,
not visual approval. Provisional art remains playable until explicitly replaced.
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "swift/Boxer0/Boxer0/Assets.xcassets"
SCENE = ROOT / "swift/Boxer0/Boxer0/IdleTestScene.swift"

# (fighter, action, asset prefix, frames, status, loader)
# The approved label records explicit project decisions, not an image-quality test.
CLIPS = [
    ("Blue", "Idle", "idle_a", 4, "provisional", "makeTexture"),
    ("Blue", "Advance", "advance_a", 6, "provisional", "makeTexture"),
    ("Blue", "Retreat", "retreat_a", 6, "provisional", "makeTexture"),
    ("Blue", "Jab", "jab_a", 6, "provisional", "loadPunchTextures"),
    ("Blue", "Cross", "cross_a", 8, "provisional", "loadPunchTextures"),
    ("Blue", "Jab recovery", "jab_recovery_a", 1, "provisional", "loadPunchTextures"),
    ("Blue", "Cross recovery", "cross_recovery_a", 1, "provisional", "loadPunchTextures"),
    ("Blue", "Guard", "guard_a", 3, "provisional", "loadPunchTextures"),
    ("Blue", "Guard advance", "guarded_advance_a", 6, "provisional", "loadPunchTextures"),
    ("Blue", "Guard retreat", "guarded_retreat_a", 6, "provisional", "loadPunchTextures"),
    ("Blue", "Block jab", "block_jab_a", 3, "provisional", "loadPunchTextures"),
    ("Blue", "Block cross", "block_cross_a", 3, "provisional", "loadPunchTextures"),
    ("Blue", "Hit reaction", "hit_react_a", 4, "provisional", "loadPunchTextures"),
    ("Blue", "Knockdown", "knockdown_a", 8, "provisional", "loadPunchTextures"),
    ("Blue", "Down", "down_a", 1, "provisional", "loadPunchTextures"),
    ("Blue", "Rise", "rise_a", 8, "provisional", "loadPunchTextures"),
    ("Orange", "Legacy idle", "idle_b", 4, "fallback", "makeTexture"),
    ("Orange", "Bounce", "orange_bounce", 17, "approved", "loadNumberedTextures"),
    ("Orange", "Advance", "advance_b", 6, "provisional", "loadPunchTextures"),
    ("Orange", "Retreat", "retreat_b", 6, "provisional", "loadPunchTextures"),
    ("Orange", "Jab V2", "jab_b", 6, "approved", "loadPunchTextures"),
    ("Orange", "Cross", "cross_b", 8, "retained", "loadPunchTextures"),
    ("Orange", "Jab recovery V2", "jab_recovery_b", 1, "approved", "loadPunchTextures"),
    ("Orange", "Cross recovery", "cross_recovery_b", 1, "retained", "loadPunchTextures"),
    ("Orange", "Guard", "guard_b", 3, "provisional", "loadPunchTextures"),
    ("Orange", "Guard advance", "guarded_advance_b", 6, "provisional", "loadPunchTextures"),
    ("Orange", "Guard retreat", "guarded_retreat_b", 6, "provisional", "loadPunchTextures"),
    ("Orange", "Block jab", "block_jab_b", 3, "provisional", "loadPunchTextures"),
    ("Orange", "Block cross", "block_cross_b", 3, "provisional", "loadPunchTextures"),
    ("Orange", "Legacy hit reaction", "hit_react_b", 4, "fallback", "loadPunchTextures"),
    ("Orange", "Normal reaction V2", "orange_normal", 18, "approved", "loadNumberedTextures"),
    ("Orange", "Heavy reaction V2", "orange_heavy", 14, "approved", "loadNumberedTextures"),
    ("Orange", "Knockdown", "knockdown_b", 8, "provisional", "loadPunchTextures"),
    ("Orange", "Down", "down_b", 1, "provisional", "loadPunchTextures"),
    ("Orange", "Rise", "rise_b", 8, "provisional", "loadPunchTextures"),
]
PNG_SIG = b"\x89PNG\r\n\x1a\n"


def frame_name(prefix, index):
    return f"{prefix}_{index:02d}" if prefix.startswith("orange_") else f"{prefix}_{index}"


def check_frame(name):
    folder = ASSETS / f"{name}.imageset"
    png = folder / f"{name}.png"
    meta = folder / "Contents.json"
    if not png.is_file() or not meta.is_file():
        return "missing image or metadata"
    try:
        metadata = json.loads(meta.read_text(encoding="utf-8"))
        if not any(item.get("filename") == png.name for item in metadata.get("images", [])):
            return "metadata filename mismatch"
        with png.open("rb") as file:
            header = file.read(26)
        if len(header) < 26 or not header.startswith(PNG_SIG):
            return "invalid PNG header"
        w, h, depth, color = struct.unpack_from(">IIBB", header, 16)
        if (w, h, depth, color) != (512, 512, 8, 6):
            return f"unexpected PNG format {w}x{h}, depth {depth}, color {color}"
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return str(exc)
    return None


def is_referenced(scene, prefix, loader):
    if loader == "loadNumberedTextures":
        return bool(re.search(r'loadNumberedTextures\(prefix:\s*"' + re.escape(prefix) + r'"', scene))
    if loader == "loadPunchTextures":
        return bool(re.search(r'loadPunchTextures\(prefix:\s*"' + re.escape(prefix) + r'"', scene))
    # Idle/advance/retreat A and legacy idle B use interpolated names.
    return f'"{prefix}_\\($0)"' in scene


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--markdown", action="store_true", help="Output a Markdown table")
    args = parser.parse_args()
    if not ASSETS.is_dir() or not SCENE.is_file():
        parser.error("Run in a checked-out Boxer6 repository containing IdleTestScene.swift")
    scene = SCENE.read_text(encoding="utf-8")
    issues = []
    rows = []
    for fighter, action, prefix, count, status, loader in CLIPS:
        missing = []
        for index in range(count):
            name = frame_name(prefix, index)
            error = check_frame(name)
            if error:
                missing.append(f"{name}: {error}")
        referenced = is_referenced(scene, prefix, loader)
        if missing or not referenced:
            issues.extend(missing)
            if not referenced:
                issues.append(f"{prefix}: missing runtime loader reference")
        rows.append((fighter, action, prefix, count, status, "OK" if not missing and referenced else "CHECK"))
    if args.markdown:
        print("| Fighter | Action | Prefix | Frames | Artwork status | Preflight |")
        print("|---|---|---|---:|---|---|")
        for fighter, action, prefix, count, status, result in rows:
            print(f"| {fighter} | {action} | `{prefix}` | {count} | {status} | {result} |")
    else:
        for fighter, action, prefix, count, status, result in rows:
            print(f"{result:5} {fighter:6} {action:21} {prefix:22} {count:2} {status}")
    if issues:
        print("\nPreflight issues:", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print(f"\nPASS: {len(CLIPS)} clips, {sum(c[3] for c in CLIPS)} frame references complete.")
    print("NOTE: preflight does not prove correct facing, anchors, smooth transitions, or Xcode build.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
