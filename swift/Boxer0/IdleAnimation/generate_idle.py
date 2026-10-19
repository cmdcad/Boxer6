#!/usr/bin/env python3
"""Build four idle-breathing frames from the static boxer rig.

Keeps the original StaticBoxers assets untouched. Each frame is a 512x512
transparent PNG with the same canvas, origin (256, 448), and ground baseline
as the static figures. Source SVGs keep the named body-part groups so poses
can be edited.

Breathing uses a smooth 0-0.5-1-0.5 envelope so frame 3 loops into frame 0.
Feet, shins, thighs, and pelvis stay planted. Torso, shoulders, arms, gloves,
and head rise and fall together; gloves get a slightly larger bob.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
STATIC = REPO / "StaticBoxers"
FRAMES = ROOT / "frames"
ASSETS = REPO / "Boxer0" / "Assets.xcassets"
PREVIEW = ROOT / "preview"

CANVAS = 512
ORIGIN = (256, 448)
BASELINE = 448
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

# Idle envelope: rest, inhale, peak, exhale. Peak rise is modest so the
# waist overlap stays connected and limb lengths do not change.
ENVELOPE = [(1 - math.cos(2 * math.pi * i / 4)) / 2 for i in range(4)]
CHEST_PX = 5.0
HEAD_EXTRA_PX = 1.5
GLOVE_EXTRA_PX = 2.5
LEAD_GLOVE_X_PX = 1.2
REAR_GLOVE_X_PX = 0.6


def round_pt(x: float, y: float, s: int) -> tuple[int, int]:
    return (int(round(x * s)), int(round(y * s)))


def poly(path: list[tuple[float, float]], dx: float, dy: float) -> list[tuple[float, float]]:
    return [(x + dx, y + dy) for x, y in path]


def round_line(draw: ImageDraw.ImageDraw, p1, p2, width: int, fill) -> None:
    draw.line([p1, p2], fill=fill, width=width)
    r = max(1, width // 2)
    for p in (p1, p2):
        draw.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=fill)


def draw_ellipse(draw: ImageDraw.ImageDraw, cx, cy, rx, ry, fill, outline, stroke, s: int) -> None:
    box = (
        int(round((cx - rx) * s)),
        int(round((cy - ry) * s)),
        int(round((cx + rx) * s)),
        int(round((cy + ry) * s)),
    )
    draw.ellipse(box, fill=fill, outline=outline, width=stroke)


def draw_boxer(accent, chest: float, head_extra: float, glove_extra: float, lead_x: float, rear_x: float) -> Image.Image:
    s = SUPERSAMPLE
    img = Image.new("RGBA", (CANVAS * s, CANVAS * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    stroke = max(1, int(round(4 * s)))
    boot_sole_w = max(1, int(round(7 * s)))

    def P(x, y, ox=0.0, oy=0.0):
        return round_pt(x + ox, y + oy, s)

    def limb(x1, y1, x2, y2, outline_w, inner_w, ox=0.0, oy=0.0):
        a, b = P(x1, y1, ox, oy), P(x2, y2, ox, oy)
        round_line(d, a, b, max(1, int(round(outline_w * s))), INK)
        round_line(d, a, b, max(1, int(round(inner_w * s))), SKIN)

    def filled_poly(points, fill, ox=0.0, oy=0.0):
        pts = [P(x, y, ox, oy) for x, y in points]
        d.polygon(pts, fill=fill, outline=INK)
        # polygon outline is 1px; stroke the loop at the ink width
        loop = pts + [pts[0]]
        d.line(loop, fill=INK, width=stroke, joint="curve")

    boot_rear = [(168, 420), (205, 412), (235, 428), (242, 444), (239, 446), (164, 446)]
    boot_lead = [(295, 420), (333, 412), (367, 428), (377, 444), (374, 446), (292, 446)]
    filled_poly(boot_rear, BOOT)
    d.line([P(168, 444), P(240, 444)], fill=SOLE, width=boot_sole_w)
    filled_poly(boot_lead, BOOT)
    d.line([P(294, 444), P(375, 444)], fill=SOLE, width=boot_sole_w)

    limb(239, 310, 216, 365, 37, 31)
    limb(282, 310, 309, 364, 37, 31)
    limb(216, 365, 203, 420, 31, 25)
    limb(309, 364, 304, 420, 31, 25)

    uy = chest
    limb(247, 199, 235, 222, 30, 24, 0, uy)
    limb(235, 222, 278, 184, 27, 21, 0, uy)

    torso = [(235, 184), (279, 183), (302, 209), (307, 257), (292, 300), (237, 298), (220, 254), (224, 211)]
    filled_poly(torso, SKIN, 0, uy)
    round_line(d, P(258, 170, 0, uy), P(258, 190, 0, uy), max(1, int(round(24 * s))), INK)
    round_line(d, P(258, 170, 0, uy), P(258, 190, 0, uy), max(1, int(round(18 * s))), SKIN)

    pelvis = [(230, 286), (293, 286), (307, 312), (301, 337), (264, 330), (221, 337), (216, 312)]
    filled_poly(pelvis, accent)
    stripe_h = 26 if accent == PALETTES["a"] else 26
    d.rectangle([P(231, 291), P(239, 291 + stripe_h)], fill=WHITE)
    if accent == PALETTES["b"]:
        d.rectangle([P(245, 291), P(253, 318)], fill=WHITE)

    gy = chest + glove_extra
    limb(283, 199, 316, 213, 30, 24, 0, uy)
    limb(316, 213, 345, 193, 27, 21, 0, uy)

    # Gloves: follow the chest, plus a slightly larger bob.
    draw_ellipse(d, 296 + rear_x, 186 + gy, 21, 17, accent, INK, stroke, s)
    x0, y0 = P(271 + rear_x, 179 + gy)
    x1, y1 = P(284 + rear_x, 196 + gy)
    d.rounded_rectangle((x0, y0, x1, y1), radius=int(round(4 * s)), fill=INK)
    draw_ellipse(d, 287 + rear_x, 192 + gy, 9, 7, accent, None, 0, s)

    draw_ellipse(d, 364.5 + lead_x, 192 + gy, 24.5, 21, accent, INK, stroke, s)
    x0, y0 = P(337 + lead_x, 187 + gy)
    x1, y1 = P(351 + lead_x, 205 + gy)
    d.rounded_rectangle((x0, y0, x1, y1), radius=int(round(4 * s)), fill=INK)
    draw_ellipse(d, 354 + lead_x, 202 + gy, 10, 8, accent, None, 0, s)

    hy = chest + head_extra
    draw_ellipse(d, 267, 158.5 + hy, 29, 31.5, SKIN, INK, stroke, s)

    return img.resize((CANVAS, CANVAS), Image.Resampling.LANCZOS)


def write_svg(path: Path, accent_hex: str, stripes: str, chest: float, head_extra: float, glove_extra: float, lead_x: float, rear_x: float, frame: int, palette: str) -> None:
    gy = chest + glove_extra
    hy = chest + head_extra
    path.write_text(
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <title>Boxer {palette.upper()} — idle frame {frame}</title>
  <desc>Transparent 512 by 512 sprite. Ground baseline y=448. Figure origin is (256,448). Named groups match the static rig. Upper-body idle offsets: chest={chest:.2f} head={hy:.2f} gloves={gy:.2f}.</desc>
  <defs>
    <style>
      .ink {{ stroke:#192A3C; stroke-width:4; stroke-linecap:round; stroke-linejoin:round }}
      .limb-outline {{ fill:none; stroke:#192A3C; stroke-linecap:round; stroke-linejoin:round }}
      .skin-line {{ fill:none; stroke:#D78F6C; stroke-linecap:round; stroke-linejoin:round }}
      .shorts-fill {{ fill:{accent_hex} }}
      .glove-fill {{ fill:{accent_hex} }}
    </style>
  </defs>
  <g id="boot-rear"><path class="ink" fill="#25364A" d="M168 420l37-8 30 16 7 16-3 2h-75z"/><path d="M168 444h72" stroke="#172334" stroke-width="7" stroke-linecap="round"/></g>
  <g id="boot-lead"><path class="ink" fill="#25364A" d="M295 420l38-8 34 16 10 16-3 2h-82z"/><path d="M294 444h81" stroke="#172334" stroke-width="7" stroke-linecap="round"/></g>
  <g id="thigh-rear"><path class="limb-outline" stroke-width="37" d="M239 310L216 365"/><path class="skin-line" stroke-width="31" d="M239 310L216 365"/></g>
  <g id="thigh-lead"><path class="limb-outline" stroke-width="37" d="M282 310L309 364"/><path class="skin-line" stroke-width="31" d="M282 310L309 364"/></g>
  <g id="shin-rear"><path class="limb-outline" stroke-width="31" d="M216 365L203 420"/><path class="skin-line" stroke-width="25" d="M216 365L203 420"/></g>
  <g id="shin-lead"><path class="limb-outline" stroke-width="31" d="M309 364L304 420"/><path class="skin-line" stroke-width="25" d="M309 364L304 420"/></g>
  <g id="upper-arm-rear" transform="translate(0 {chest:.2f})"><path class="limb-outline" stroke-width="30" d="M247 199L235 222"/><path class="skin-line" stroke-width="24" d="M247 199L235 222"/></g>
  <g id="forearm-rear" transform="translate(0 {chest:.2f})"><path class="limb-outline" stroke-width="27" d="M235 222L278 184"/><path class="skin-line" stroke-width="21" d="M235 222L278 184"/></g>
  <g id="torso" transform="translate(0 {chest:.2f})"><path class="ink" fill="#D78F6C" d="M235 184l44-1 23 26 5 48-15 43-55-2-17-44 4-43z"/><path d="M258 170v20" stroke="#192A3C" stroke-width="24" stroke-linecap="round"/><path d="M258 170v20" stroke="#D78F6C" stroke-width="18" stroke-linecap="round"/></g>
  <g id="pelvis"><path class="ink shorts-fill" d="M230 286h63l14 26-6 25-37-7-43 7-5-25z"/>{stripes}</g>
  <g id="upper-arm-lead" transform="translate(0 {chest:.2f})"><path class="limb-outline" stroke-width="30" d="M283 199L316 213"/><path class="skin-line" stroke-width="24" d="M283 199L316 213"/></g>
  <g id="forearm-lead" transform="translate(0 {chest:.2f})"><path class="limb-outline" stroke-width="27" d="M316 213L345 193"/><path class="skin-line" stroke-width="21" d="M316 213L345 193"/></g>
  <g id="glove-rear" transform="translate({rear_x:.2f} {gy:.2f})"><ellipse class="ink glove-fill" cx="296" cy="186" rx="21" ry="17"/><rect x="271" y="179" width="13" height="17" rx="4" fill="#192A3C"/><ellipse class="glove-fill" cx="287" cy="192" rx="9" ry="7"/></g>
  <g id="glove-lead" transform="translate({lead_x:.2f} {gy:.2f})"><ellipse class="ink glove-fill" cx="364.5" cy="192" rx="24.5" ry="21"/><rect x="337" y="187" width="14" height="18" rx="4" fill="#192A3C"/><ellipse class="glove-fill" cx="354" cy="202" rx="10" ry="8"/></g>
  <g id="head" transform="translate(0 {hy:.2f})"><ellipse class="ink" fill="#D78F6C" cx="267" cy="158.5" rx="29" ry="31.5"/></g>
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


def composite_preview(frames_a: list[Image.Image], frames_b: list[Image.Image]) -> list[Image.Image]:
    w, h = 844, 390
    ground_y = int(h * 0.78)
    out = []
    for fa, fb in zip(frames_a, frames_b):
        canvas = Image.new("RGBA", (w, h), (232, 238, 244, 255))
        draw = ImageDraw.Draw(canvas)
        draw.line([(24, ground_y), (w - 24, ground_y)], fill=(120, 140, 160, 255), width=2)
        scale = 0.62
        size = int(CANVAS * scale)
        a = fa.resize((size, size), Image.Resampling.LANCZOS)
        b = fb.transpose(Image.Transpose.FLIP_LEFT_RIGHT).resize((size, size), Image.Resampling.LANCZOS)
        # Anchor at figure origin: x=256, y=448 in the 512 canvas.
        def paste(sprite, cx):
            ox = int(round(256 * scale))
            oy = int(round(448 * scale))
            canvas.alpha_composite(sprite, (cx - ox, ground_y - oy))
            r = 4
            draw.ellipse((cx - r, ground_y - r, cx + r, ground_y + r), outline=(40, 118, 210, 255), width=2)

        paste(a, int(w * 0.32))
        paste(b, int(w * 0.68))
        out.append(canvas.convert("P", palette=Image.Palette.ADAPTIVE, colors=64))
    return out


def main() -> None:
    FRAMES.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)

    stripe_a = '<path d="M231 291h8v26h-8z" fill="#FFF"/>'
    stripe_b = '<path d="M231 291h8v26h-8zM245 291h8v27h-8z" fill="#FFF"/>'
    frames = {"a": [], "b": []}

    for i, u in enumerate(ENVELOPE):
        chest = -CHEST_PX * u
        head_extra = -HEAD_EXTRA_PX * u
        glove_extra = -GLOVE_EXTRA_PX * u
        lead_x = LEAD_GLOVE_X_PX * u
        rear_x = REAR_GLOVE_X_PX * u
        for pal, accent, stripes, hexcol in (
            ("a", PALETTES["a"], stripe_a, "#2876D2"),
            ("b", PALETTES["b"], stripe_b, "#E77728"),
        ):
            svg_path = FRAMES / f"idle_{pal}_{i}.svg"
            png_path = FRAMES / f"idle_{pal}_{i}.png"
            write_svg(svg_path, hexcol, stripes, chest, head_extra, glove_extra, lead_x, rear_x, i, pal)
            img = draw_boxer(accent, chest, head_extra, glove_extra, lead_x, rear_x)
            img.save(png_path)
            frames[pal].append(img)

            imageset = ASSETS / f"idle_{pal}_{i}.imageset"
            imageset.mkdir(parents=True, exist_ok=True)
            img.save(imageset / f"idle_{pal}_{i}.png")
            (imageset / "Contents.json").write_text(imageset_json(f"idle_{pal}_{i}.png"), encoding="utf-8")

    gif_frames = composite_preview(frames["a"], frames["b"])
    gif_path = PREVIEW / "idle_playback.gif"
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=200,
        loop=0,
        disposal=2,
    )

    sheet = Image.new("RGBA", (CANVAS * 4, CANVAS * 2), (40, 48, 58, 255))
    for i, (fa, fb) in enumerate(zip(frames["a"], frames["b"])):
        sheet.alpha_composite(fa, (i * CANVAS, 0))
        sheet.alpha_composite(fb, (i * CANVAS, CANVAS))
    sheet.save(PREVIEW / "idle_contact_sheet.png")
    print(f"Wrote 8 frames to {FRAMES}")
    print(f"Preview GIF: {gif_path}")
    print(f"Envelope: {['%.3f' % u for u in ENVELOPE]}")


if __name__ == "__main__":
    main()
