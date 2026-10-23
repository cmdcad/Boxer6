#!/usr/bin/env python3
"""Audit Boxer0 Orange animation image sets (no third-party dependencies).

Run at repository root:
  python3 tools/audit_orange_animations.py

This is an asset/catalog preflight, not a substitute for an Xcode runtime test.
It never edits the repository. Every PNG must be 512x512 RGBA and its imageset
Contents.json must point to that exact PNG. Checks the Orange jab, retained
cross, bounce, normal/heavy reactions, and both offensive recovery poses.
"""
import json
import struct
import sys
import zlib
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / "swift/Boxer0/Boxer0/Assets.xcassets"
CLIPS = (
    ("Orange jab", "jab_b", 6),
    ("Orange jab recovery", "jab_recovery_b", 1),
    ("Orange cross (retained)", "cross_b", 8),
    ("Orange cross recovery", "cross_recovery_b", 1),
    ("Orange bounce", "orange_bounce", 17),
    ("Orange normal reaction", "orange_normal", 18),
    ("Orange heavy reaction", "orange_heavy", 14),
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def inspect_png(path):
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("bad PNG signature")
    offset = len(PNG_SIGNATURE)
    ihdr = None
    ended = False
    while offset + 12 <= len(data):
        length = struct.unpack_from(">I", data, offset)[0]
        if length > len(data) - offset - 12:
            raise ValueError("truncated PNG chunk")
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        expected_crc = struct.unpack_from(">I", data, offset + 8 + length)[0]
        if zlib.crc32(kind + payload) & 0xFFFFFFFF != expected_crc:
            raise ValueError(f"CRC mismatch in {kind!r}")
        if kind == b"IHDR":
            if ihdr is not None or length != 13:
                raise ValueError("invalid IHDR")
            width, height, depth, color = struct.unpack_from(">IIBB", payload)
            ihdr = (width, height, depth, color)
        if kind == b"IEND":
            ended = True
            if length != 0:
                raise ValueError("invalid IEND")
            offset += 12
            break
        offset += 12 + length
    if not ended or offset != len(data):
        raise ValueError("missing IEND or trailing data")
    if ihdr != (512, 512, 8, 6):
        raise ValueError(f"expected 512x512 8-bit RGBA, got {ihdr}")


def inspect_imageset(name):
    folder = CATALOG / f"{name}.imageset"
    png = folder / f"{name}.png"
    meta = folder / "Contents.json"
    if not png.is_file() or not meta.is_file():
        raise ValueError("missing PNG or Contents.json")
    config = json.loads(meta.read_text(encoding="utf-8"))
    images = config.get("images", [])
    if not any(item.get("filename") == f"{name}.png" for item in images):
        raise ValueError("Contents.json does not reference matching PNG")
    inspect_png(png)


def main():
    if not CATALOG.is_dir():
        print(f"FAIL: asset catalog not found at {CATALOG}", file=sys.stderr)
        return 1
    errors = []
    for label, prefix, count in CLIPS:
        for index in range(count):
            name = f"{prefix}_{index}"
            if prefix.startswith("orange_"):
                name = f"{prefix}_{index:02d}"
            try:
                inspect_imageset(name)
            except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
                errors.append(f"{name}: {exc}")
        print(f"{label}: {count} expected frames")
    if errors:
        print(f"\nFAIL: {len(errors)} image set issue(s):", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("\nPASS: all 65 Orange image sets and PNG metadata validated.")
    print("Next: verify jab faces Blue, contact pose jab_b_3, recovery-to-bounce,")
    print("cross unchanged, and hit/block/miss behavior in Xcode.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
