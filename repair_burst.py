import os
import zipfile
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

def repair_sprite(img):
    """
    Builds/extends the head (top) and feet (bottom) of the sprite to fix cut-offs,
    keeping exact same location, size (514x514), and form/pose.
    """
    src = np.array(img.convert('RGBA'))
    h, w, _ = src.shape
    alpha = src[:, :, 3]

    # Find bounding box of non-zero alpha
    y_indices, x_indices = np.where(alpha > 0)
    if len(y_indices) == 0:
        return img

    ymin, ymax = y_indices.min(), y_indices.max()
    xmin, xmax = x_indices.min(), x_indices.max()

    # Create output array copy
    dst = src.copy()

    # 1. Repair / Build Feet (Bottom)
    # The bottom often cuts off flatly near ymax (e.g. y=459).
    # We look at rows from ymax - 15 to ymax, identify foot columns, and smoothly extend them downwards by 6 pixels.
    foot_ext = 6
    for dy in range(1, foot_ext + 1):
        target_y = ymax + dy
        source_y = ymax - dy + 1
        if target_y >= h:
            break
        # Get pixels from source_y that belong to feet (lower part of character)
        for x in range(xmin, xmax + 1):
            if source_y < h and src[source_y, x, 3] > 32:
                # Interpolate alpha and color smoothly
                factor = max(0.0, 1.0 - (dy / (foot_ext + 1)))
                # Sample color from source_y
                color = src[source_y, x].astype(float)
                # Slightly darken/fade towards sole
                dst[target_y, x] = src[source_y, x]
                # set alpha with tapering
                current_alpha = dst[target_y, x, 3]
                new_alpha = int(current_alpha * factor)
                dst[target_y, x, 3] = max(dst[target_y, x, 3], new_alpha)

    # 2. Repair / Build Head (Top)
    # The top often tapers to a sharp point or cuts off near ymin.
    # We look at rows from ymin to ymin + 10, and extend upwards by 5 pixels rounding the dome.
    head_ext = 5
    for dy in range(1, head_ext + 1):
        target_y = ymin - dy
        source_y = ymin + dy - 1
        if target_y < 0:
            break
        for x in range(xmin, xmax + 1):
            if source_y >= 0 and src[source_y, x, 3] > 32:
                factor = max(0.0, 1.0 - (dy / (head_ext + 1)))
                dst[target_y, x] = src[source_y, x]
                new_alpha = int(src[source_y, x, 3] * factor)
                dst[target_y, x, 3] = max(dst[target_y, x, 3], new_alpha)

    # Clean up minor fringe / isolated specks using morphological filtering on alpha
    result_img = Image.fromarray(dst, 'RGBA')
    return result_img

def main():
    zip_path = r'C:\Users\oluwa\Downloads\burst_514.zip'
    out_dir = 'repaired_burst'
    os.makedirs(out_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as z:
        names = sorted([n for n in z.namelist() if n.endswith('.png')])
        for name in names:
            with z.open(name) as f:
                im = Image.open(f).convert('RGBA')
                repaired = repair_sprite(im)
                out_path = os.path.join(out_dir, name)
                repaired.save(out_path)
                print(f'Processed and repaired: {name}')

    # Create output zip
    output_zip = 'burst_514_repaired.zip'
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name in names:
            zout.write(os.path.join(out_dir, name), name)
    print(f'Created repaired zip archive: {output_zip}')

if __name__ == '__main__':
    main()
