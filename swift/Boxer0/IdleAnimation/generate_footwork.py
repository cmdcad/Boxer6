#!/usr/bin/env python3
"""Six-frame in-place advance/retreat shuffles for both palettes.

Clips were missing from the asset catalog. These frames use the same 512x512
canvas, origin (256, 448), and baseline y=448 as the static rig. Footwork is a
closed loop so it can play under continuous SpriteKit root motion without a
net pose snap. Lead foot stays in front of the rear foot.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
FRAMES = ROOT / "frames"
ASSETS = REPO / "Boxer0" / "Assets.xcassets"
PREVIEW = ROOT / "preview"

CANVAS = 512
SUPERSAMPLE = 4
INK = (25, 42, 60, 255)
SKIN = (215, 143, 108, 255)
BOOT = (37, 54, 74, 255)
SOLE = (23, 35, 52, 255)
WHITE = (255, 255, 255, 255)
PALETTES = {
    "a": (40, 118, 210, 255),
    "b": (231, 119, 40, 255),
}

HIP_REAR = (239.0, 310.0)
HIP_LEAD = (282.0, 310.0)
KNEE_REAR = (216.0, 365.0)
KNEE_LEAD = (309.0, 364.0)
ANKLE_REAR = (203.0, 420.0)
ANKLE_LEAD = (304.0, 420.0)

LEN_THIGH_REAR = math.dist(HIP_REAR, KNEE_REAR)
LEN_SHIN_REAR = math.dist(KNEE_REAR, ANKLE_REAR)
LEN_THIGH_LEAD = math.dist(HIP_LEAD, KNEE_LEAD)
LEN_SHIN_LEAD = math.dist(KNEE_LEAD, ANKLE_LEAD)

BOOT_REAR = [(168, 420), (205, 412), (235, 428), (242, 444), (239, 446), (164, 446)]
BOOT_LEAD = [(295, 420), (333, 412), (367, 428), (377, 444), (374, 446), (292, 446)]
TORSO = [(235, 184), (279, 183), (302, 209), (307, 257), (292, 300), (237, 298), (220, 254), (224, 211)]
PELVIS = [(230, 286), (293, 286), (307, 312), (301, 337), (264, 330), (221, 337), (216, 312)]


@dataclass
class Pose:
    lead_dx: float = 0
    lead_lift: float = 0
    rear_dx: float = 0
    rear_lift: float = 0
    hip_dx: float = 0
    hip_dy: float = 0
    chest: float = 0
    head_extra: float = 0
    glove_lead_dx: float = 0
    glove_rear_dx: float = 0
    glove_extra: float = 0


# Closed six-frame shuffles. Frame 0 matches idle rest.
ADVANCE = [
    Pose(),
    Pose(lead_dx=5, lead_lift=11, hip_dx=1.5, hip_dy=-1, chest=-2, glove_lead_dx=2, glove_extra=-2),
    Pose(lead_dx=10, lead_lift=0, hip_dx=3, hip_dy=0, chest=-1, glove_lead_dx=3, glove_extra=-1),
    Pose(lead_dx=7, rear_dx=5, rear_lift=10, hip_dx=3.5, hip_dy=-1, chest=-2, glove_rear_dx=2, glove_extra=-2),
    Pose(lead_dx=3, rear_dx=8, rear_lift=0, hip_dx=2, chest=-1, glove_rear_dx=1, glove_extra=-1),
    Pose(lead_dx=1, rear_dx=3, hip_dx=0.5, chest=-0.5, glove_extra=-0.5),
]

RETREAT = [
    Pose(),
    Pose(rear_dx=-5, rear_lift=11, hip_dx=-1.5, hip_dy=-1, chest=-2, glove_rear_dx=-2, glove_extra=-2),
    Pose(rear_dx=-10, rear_lift=0, hip_dx=-3, hip_dy=0, chest=-1, glove_rear_dx=-3, glove_extra=-1),
    Pose(rear_dx=-7, lead_dx=-5, lead_lift=10, hip_dx=-3.5, hip_dy=-1, chest=-2, glove_lead_dx=-2, glove_extra=-2),
    Pose(rear_dx=-3, lead_dx=-8, lead_lift=0, hip_dx=-2, chest=-1, glove_lead_dx=-1, glove_extra=-1),
    Pose(rear_dx=-1, lead_dx=-3, hip_dx=-0.5, chest=-0.5, glove_extra=-0.5),
]


def ik(hip, ankle, length1, length2, hint):
    hx, hy = hip
    ax, ay = ankle
    dx, dy = ax - hx, ay - hy
    dist = math.hypot(dx, dy)
    dist = max(1.0, min(dist, length1 + length2 - 0.05))
    a = (length1 * length1 - length2 * length2 + dist * dist) / (2 * dist)
    h = math.sqrt(max(0.0, length1 * length1 - a * a))
    mx = hx + a * dx / dist
    my = hy + a * dy / dist
    px, py = -dy / dist, dx / dist
    k1 = (mx + h * px, my + h * py)
    k2 = (mx - h * px, my - h * py)
    d1 = math.dist(k1, hint)
    d2 = math.dist(k2, hint)
    return k1 if d1 <= d2 else k2


def round_pt(x: float, y: float, s: int) -> tuple[int, int]:
    return (int(round(x * s)), int(round(y * s)))


def round_line(draw, p1, p2, width, fill) -> None:
    draw.line([p1, p2], fill=fill, width=width)
    r = max(1, width // 2)
    for p in (p1, p2):
        draw.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=fill)


def draw_ellipse(draw, cx, cy, rx, ry, fill, outline, stroke, s) -> None:
    box = (
        int(round((cx - rx) * s)),
        int(round((cy - ry) * s)),
        int(round((cx + rx) * s)),
        int(round((cy + ry) * s)),
    )
    draw.ellipse(box, fill=fill, outline=outline, width=stroke)


def draw_boxer(accent, pose: Pose) -> Image.Image:
    s = SUPERSAMPLE
    img = Image.new("RGBA", (CANVAS * s, CANVAS * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    stroke = max(1, int(round(4 * s)))
    boot_sole_w = max(1, int(round(7 * s)))

    def P(x, y):
        return round_pt(x, y, s)

    def limb(p1, p2, outline_w, inner_w):
        a, b = P(*p1), P(*p2)
        round_line(d, a, b, max(1, int(round(outline_w * s))), INK)
        round_line(d, a, b, max(1, int(round(inner_w * s))), SKIN)

    def filled_poly(points, fill, dx=0.0, dy=0.0):
        pts = [P(x + dx, y + dy) for x, y in points]
        d.polygon(pts, fill=fill, outline=INK)
        d.line(pts + [pts[0]], fill=INK, width=stroke, joint="curve")

    rear_dx, rear_dy = pose.rear_dx, -pose.rear_lift
    lead_dx, lead_dy = pose.lead_dx, -pose.lead_lift
    hip = (pose.hip_dx, pose.hip_dy)
    upper = (pose.hip_dx, pose.hip_dy + pose.chest)

    hip_r = (HIP_REAR[0] + hip[0], HIP_REAR[1] + hip[1])
    hip_l = (HIP_LEAD[0] + hip[0], HIP_LEAD[1] + hip[1])
    ankle_r = (ANKLE_REAR[0] + rear_dx, ANKLE_REAR[1] + rear_dy)
    ankle_l = (ANKLE_LEAD[0] + lead_dx, ANKLE_LEAD[1] + lead_dy)
    knee_r = ik(hip_r, ankle_r, LEN_THIGH_REAR, LEN_SHIN_REAR, KNEE_REAR)
    knee_l = ik(hip_l, ankle_l, LEN_THIGH_LEAD, LEN_SHIN_LEAD, KNEE_LEAD)

    filled_poly(BOOT_REAR, BOOT, rear_dx, rear_dy)
    d.line([P(168 + rear_dx, 444 + rear_dy), P(240 + rear_dx, 444 + rear_dy)], fill=SOLE, width=boot_sole_w)
    filled_poly(BOOT_LEAD, BOOT, lead_dx, lead_dy)
    d.line([P(294 + lead_dx, 444 + lead_dy), P(375 + lead_dx, 444 + lead_dy)], fill=SOLE, width=boot_sole_w)

    limb(hip_r, knee_r, 37, 31)
    limb(hip_l, knee_l, 37, 31)
    limb(knee_r, ankle_r, 31, 25)
    limb(knee_l, ankle_l, 31, 25)

    uy, ux = upper[1], upper[0]
    limb((247 + ux, 199 + uy), (235 + ux, 222 + uy), 30, 24)
    limb((235 + ux, 222 + uy), (278 + ux, 184 + uy), 27, 21)
    filled_poly(TORSO, SKIN, ux, uy)
    round_line(d, P(258 + ux, 170 + uy), P(258 + ux, 190 + uy), max(1, int(round(24 * s))), INK)
    round_line(d, P(258 + ux, 170 + uy), P(258 + ux, 190 + uy), max(1, int(round(18 * s))), SKIN)
    filled_poly(PELVIS, accent, hip[0], hip[1])
    d.rectangle([P(231 + hip[0], 291 + hip[1]), P(239 + hip[0], 317 + hip[1])], fill=WHITE)
    if accent == PALETTES["b"]:
        d.rectangle([P(245 + hip[0], 291 + hip[1]), P(253 + hip[0], 318 + hip[1])], fill=WHITE)

    limb((283 + ux, 199 + uy), (316 + ux, 213 + uy), 30, 24)
    limb((316 + ux, 213 + uy), (345 + ux, 193 + uy), 27, 21)

    gy = uy + pose.glove_extra
    rx = ux + pose.glove_rear_dx
    lx = ux + pose.glove_lead_dx
    draw_ellipse(d, 296 + rx, 186 + gy, 21, 17, accent, INK, stroke, s)
    d.rounded_rectangle((P(271 + rx, 179 + gy) + P(284 + rx, 196 + gy)), radius=int(round(4 * s)), fill=INK)
    draw_ellipse(d, 287 + rx, 192 + gy, 9, 7, accent, None, 0, s)
    draw_ellipse(d, 364.5 + lx, 192 + gy, 24.5, 21, accent, INK, stroke, s)
    d.rounded_rectangle((P(337 + lx, 187 + gy) + P(351 + lx, 205 + gy)), radius=int(round(4 * s)), fill=INK)
    draw_ellipse(d, 354 + lx, 202 + gy, 10, 8, accent, None, 0, s)
    draw_ellipse(d, 267 + ux, 158.5 + uy + pose.head_extra, 29, 31.5, SKIN, INK, stroke, s)
    return img.resize((CANVAS, CANVAS), Image.Resampling.LANCZOS)


def write_svg(path: Path, accent_hex: str, stripes: str, pose: Pose, clip: str, frame: int, palette: str) -> None:
    rear = f"translate({pose.rear_dx:.2f} {-pose.rear_lift:.2f})"
    lead = f"translate({pose.lead_dx:.2f} {-pose.lead_lift:.2f})"
    hip = f"translate({pose.hip_dx:.2f} {pose.hip_dy:.2f})"
    upper = f"translate({pose.hip_dx:.2f} {pose.hip_dy + pose.chest:.2f})"
    gy = pose.hip_dy + pose.chest + pose.glove_extra
    path.write_text(
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <title>Boxer {palette.upper()} — {clip} frame {frame}</title>
  <desc>Transparent 512 by 512 sprite. Ground baseline y=448. Figure origin (256,448). In-place {clip} shuffle; SpriteKit root provides travel.</desc>
  <defs>
    <style>
      .ink {{ stroke:#192A3C; stroke-width:4; stroke-linecap:round; stroke-linejoin:round }}
      .limb-outline {{ fill:none; stroke:#192A3C; stroke-linecap:round; stroke-linejoin:round }}
      .skin-line {{ fill:none; stroke:#D78F6C; stroke-linecap:round; stroke-linejoin:round }}
      .shorts-fill {{ fill:{accent_hex} }}
      .glove-fill {{ fill:{accent_hex} }}
    </style>
  </defs>
  <g id="boot-rear" transform="{rear}"><path class="ink" fill="#25364A" d="M168 420l37-8 30 16 7 16-3 2h-75z"/><path d="M168 444h72" stroke="#172334" stroke-width="7" stroke-linecap="round"/></g>
  <g id="boot-lead" transform="{lead}"><path class="ink" fill="#25364A" d="M295 420l38-8 34 16 10 16-3 2h-82z"/><path d="M294 444h81" stroke="#172334" stroke-width="7" stroke-linecap="round"/></g>
  <g id="legs-note"><desc>PNG renderer uses IK for thigh/shin endpoints; SVG groups keep rest strokes plus foot/hip translates for editing.</desc></g>
  <g id="thigh-rear" transform="{hip}"><path class="limb-outline" stroke-width="37" d="M239 310L216 365"/><path class="skin-line" stroke-width="31" d="M239 310L216 365"/></g>
  <g id="thigh-lead" transform="{hip}"><path class="limb-outline" stroke-width="37" d="M282 310L309 364"/><path class="skin-line" stroke-width="31" d="M282 310L309 364"/></g>
  <g id="shin-rear" transform="{rear}"><path class="limb-outline" stroke-width="31" d="M216 365L203 420"/><path class="skin-line" stroke-width="25" d="M216 365L203 420"/></g>
  <g id="shin-lead" transform="{lead}"><path class="limb-outline" stroke-width="31" d="M309 364L304 420"/><path class="skin-line" stroke-width="25" d="M309 364L304 420"/></g>
  <g id="upper-arm-rear" transform="{upper}"><path class="limb-outline" stroke-width="30" d="M247 199L235 222"/><path class="skin-line" stroke-width="24" d="M247 199L235 222"/></g>
  <g id="forearm-rear" transform="{upper}"><path class="limb-outline" stroke-width="27" d="M235 222L278 184"/><path class="skin-line" stroke-width="21" d="M235 222L278 184"/></g>
  <g id="torso" transform="{upper}"><path class="ink" fill="#D78F6C" d="M235 184l44-1 23 26 5 48-15 43-55-2-17-44 4-43z"/><path d="M258 170v20" stroke="#192A3C" stroke-width="24" stroke-linecap="round"/><path d="M258 170v20" stroke="#D78F6C" stroke-width="18" stroke-linecap="round"/></g>
  <g id="pelvis" transform="{hip}"><path class="ink shorts-fill" d="M230 286h63l14 26-6 25-37-7-43 7-5-25z"/>{stripes}</g>
  <g id="upper-arm-lead" transform="{upper}"><path class="limb-outline" stroke-width="30" d="M283 199L316 213"/><path class="skin-line" stroke-width="24" d="M283 199L316 213"/></g>
  <g id="forearm-lead" transform="{upper}"><path class="limb-outline" stroke-width="27" d="M316 213L345 193"/><path class="skin-line" stroke-width="21" d="M316 213L345 193"/></g>
  <g id="glove-rear" transform="translate({pose.hip_dx + pose.glove_rear_dx:.2f} {gy:.2f})"><ellipse class="ink glove-fill" cx="296" cy="186" rx="21" ry="17"/><rect x="271" y="179" width="13" height="17" rx="4" fill="#192A3C"/><ellipse class="glove-fill" cx="287" cy="192" rx="9" ry="7"/></g>
  <g id="glove-lead" transform="translate({pose.hip_dx + pose.glove_lead_dx:.2f} {gy:.2f})"><ellipse class="ink glove-fill" cx="364.5" cy="192" rx="24.5" ry="21"/><rect x="337" y="187" width="14" height="18" rx="4" fill="#192A3C"/><ellipse class="glove-fill" cx="354" cy="202" rx="10" ry="8"/></g>
  <g id="head" transform="translate({pose.hip_dx:.2f} {pose.hip_dy + pose.chest + pose.head_extra:.2f})"><ellipse class="ink" fill="#D78F6C" cx="267" cy="158.5" rx="29" ry="31.5"/></g>
</svg>
''',
        encoding="utf-8",
    )


def imageset_json(filename: str) -> str:
    return f'''{{
  "images" : [
    {{
      "filename" : "{filename}",
      "idiom" : "universal",
      "scale" : "1x"
    }}
  ],
  "info" : {{
    "author" : "xcode",
    "version" : 1
  }}
}}
'''


def save_clip(name: str, poses: list[Pose]) -> dict[str, list[Image.Image]]:
    stripe_a = '<path d="M231 291h8v26h-8z" fill="#FFF"/>'
    stripe_b = '<path d="M231 291h8v26h-8zM245 291h8v27h-8z" fill="#FFF"/>'
    out = {"a": [], "b": []}
    for i, pose in enumerate(poses):
        for pal, accent, stripes, hexcol in (
            ("a", PALETTES["a"], stripe_a, "#2876D2"),
            ("b", PALETTES["b"], stripe_b, "#E77728"),
        ):
            stem = f"{name}_{pal}_{i}"
            write_svg(FRAMES / f"{stem}.svg", hexcol, stripes, pose, name, i, pal)
            img = draw_boxer(accent, pose)
            img.save(FRAMES / f"{stem}.png")
            imageset = ASSETS / f"{stem}.imageset"
            imageset.mkdir(parents=True, exist_ok=True)
            img.save(imageset / f"{stem}.png")
            (imageset / "Contents.json").write_text(imageset_json(f"{stem}.png"), encoding="utf-8")
            out[pal].append(img)
    return out


def contact_sheet(rows: list[tuple[str, list[Image.Image]]]) -> Image.Image:
    cols = 6
    sheet = Image.new("RGBA", (CANVAS * cols, CANVAS * len(rows)), (40, 48, 58, 255))
    for r, (_, frames) in enumerate(rows):
        for c, frame in enumerate(frames):
            sheet.alpha_composite(frame, (c * CANVAS, r * CANVAS))
    return sheet


def gif_cycle(frames: list[Image.Image], path: Path) -> None:
    w, h = 420, 420
    ground = int(h * 0.82)
    out = []
    for frame in frames:
        canvas = Image.new("RGBA", (w, h), (232, 238, 244, 255))
        draw = ImageDraw.Draw(canvas)
        draw.line([(20, ground), (w - 20, ground)], fill=(120, 140, 160, 255), width=2)
        scale = 0.7
        size = int(CANVAS * scale)
        sprite = frame.resize((size, size), Image.Resampling.LANCZOS)
        ox = int(round(256 * scale))
        oy = int(round(448 * scale))
        canvas.alpha_composite(sprite, (w // 2 - ox, ground - oy))
        out.append(canvas.convert("P", palette=Image.Palette.ADAPTIVE, colors=64))
    out[0].save(path, save_all=True, append_images=out[1:], duration=80, loop=0, disposal=2)


def main() -> None:
    FRAMES.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    advance = save_clip("advance", ADVANCE)
    retreat = save_clip("retreat", RETREAT)
    contact_sheet(
        [
            ("advance a", advance["a"]),
            ("advance b", advance["b"]),
            ("retreat a", retreat["a"]),
            ("retreat b", retreat["b"]),
        ]
    ).save(PREVIEW / "footwork_contact_sheet.png")
    gif_cycle(advance["a"], PREVIEW / "advance_a.gif")
    gif_cycle(retreat["a"], PREVIEW / "retreat_a.gif")
    print("Wrote 24 footwork frames (6 x 2 clips x 2 palettes)")


if __name__ == "__main__":
    main()
