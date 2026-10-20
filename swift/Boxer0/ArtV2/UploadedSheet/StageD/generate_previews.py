"""Generate comprehensive animated previews for Stage D.

Creates:
- Jab animation (6 frames, 300ms)
- Cross animation (8 frames, 480ms)
- Jab animation followed by recovery
- Cross animation followed by recovery
- Full alignment sheet with all 16 frames
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent

def create_gif(frame_paths, output_path, duration_ms, loop=0):
    """Create animated GIF from frame list."""
    images = [Image.open(p) for p in frame_paths]
    if images:
        images[0].save(output_path, save_all=True,
                      append_images=images[1:], duration=duration_ms, loop=loop, disposal=2)

def main():
    # Generate animated GIFs
    jab_frames = [ROOT / f'frames/jab_{i}.png' for i in range(6)]
    cross_frames = [ROOT / f'frames/cross_{i}.png' for i in range(8)]
    jab_recovery = ROOT / 'frames/jab_recovery.png'
    cross_recovery = ROOT / 'frames/cross_recovery.png'

    # Individual punch GIFs
    create_gif(jab_frames, ROOT / 'jab_animation.gif', 50)
    create_gif(cross_frames, ROOT / 'cross_animation.gif', 60)

    # Punch + recovery sequences
    jab_with_recovery = jab_frames + [jab_recovery]
    create_gif(jab_with_recovery, ROOT / 'jab_with_recovery.gif', 50)

    cross_with_recovery = cross_frames + [cross_recovery]
    create_gif(cross_with_recovery, ROOT / 'cross_with_recovery.gif', 60)

    # Full alignment sheet: 16 frames in 2 rows
    # Row 1: Jab (6) + empty (2)
    # Row 2: Cross (8)
    sheet = Image.new('RGBA', (512 * 8, 550 * 2), (232, 238, 244, 255))
    draw = ImageDraw.Draw(sheet)

    # Jab row
    for i in range(6):
        x = i * 512
        y = 0
        img = Image.open(ROOT / f'frames/jab_{i}.png')
        sheet.alpha_composite(img, (x, y))
        draw.line((x, y + 448, x + 511, y + 448), fill=(210, 90, 70))
        draw.line((x + 256, y + 430, x + 256, y + 465), fill=(70, 130, 200))
        time_str = f"{i * 50} ms"
        if i == 3:
            time_str += " CONTACT"
        draw.text((x + 12, y + 520), f'Jab {i + 1}: {time_str}', fill=(25, 42, 60))

    # Recovery in jab row slots 6-7
    for i in range(2):
        x = (6 + i) * 512
        y = 0
        if i == 0:
            img = Image.open(jab_recovery)
            sheet.alpha_composite(img, (x, y))
            draw.line((x, y + 448, x + 511, y + 448), fill=(210, 90, 70))
            draw.line((x + 256, y + 430, x + 256, y + 465), fill=(70, 130, 200))
            draw.text((x + 12, y + 520), 'Jab Recovery: 120ms', fill=(25, 42, 60))
        if i == 1:
            img = Image.open(cross_recovery)
            sheet.alpha_composite(img, (x, y))
            draw.line((x, y + 448, x + 511, y + 448), fill=(210, 90, 70))
            draw.line((x + 256, y + 430, x + 256, y + 465), fill=(70, 130, 200))
            draw.text((x + 12, y + 520), 'Cross Recovery: 220ms', fill=(25, 42, 60))

    # Cross row
    for i in range(8):
        x = i * 512
        y = 550
        img = Image.open(ROOT / f'frames/cross_{i}.png')
        sheet.alpha_composite(img, (x, y))
        draw.line((x, y + 448, x + 511, y + 448), fill=(210, 90, 70))
        draw.line((x + 256, y + 430, x + 256, y + 465), fill=(70, 130, 200))
        time_str = f"{i * 60} ms"
        if i == 4:
            time_str += " CONTACT"
        if i in [3, 6]:
            time_str += " TRANSITION"
        draw.text((x + 12, y + 520), f'Cross {i + 1}: {time_str}', fill=(25, 42, 60))

    sheet.convert('RGB').save(ROOT / 'full_alignment_sheet.png')

    print(f'Generated animated previews:')
    print(f'  jab_animation.gif - 6 frames, 300ms total')
    print(f'  cross_animation.gif - 8 frames, 480ms total')
    print(f'  jab_with_recovery.gif - 6 punch + 1 recovery')
    print(f'  cross_with_recovery.gif - 8 punch + 1 recovery')
    print(f'  full_alignment_sheet.png - All 16 frames in 2 rows')

if __name__ == '__main__':
    main()
