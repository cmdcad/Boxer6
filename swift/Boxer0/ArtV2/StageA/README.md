# Boxer0 V2 — Stage A blue idle review

Four newly generated individual idle frames in the approved smooth hand-drawn arcade style. No source was sliced out of the concept sheet. This is an isolated review package, not a live asset replacement.

## Deliverables

- frames/idle_a_0.png through idle_a_3.png: individual 512 x 512 transparent RGBA PNGs.
- idle_preview.gif: four frames, 200 ms each, 800 ms looping. A 256px sprite canvas produces approximately160px visible character height, representative of a compact landscape gameplay view. Exact iPhone size depends on scene layout.
- idle_preview.png: transparent 512px APNG preview, same four 200ms frames.
- alignment_sheet.png: review-only baseline/root guides and labels. These markings are not present in individual frames.
- manifest.json: timing, source/export bounds, alignment offsets and checksums.
- export_idle.py and validate_idle.py: deterministic export/validation recipe.
- source/: original generated images retained separately from normalized exports.
- prompts.json: built-in imagegen prompt set and source references.

## Alignment and transparency results

Canvas 512 x 512; right-facing; ground/root (256,448); baseline y448; 4 frames; 800ms loop. SpriteKit anchor for future review is (0.5,0.125), as in the existing project.

One uniform export scale, 0.3180914513, was calculated from neutral height and used for all frames. There is no individual frame fitting or body deformation. All four selected images used the same final placement offset (54,70). Baseline measurements use alpha>=32 so antialias fringe pixels do not redefine the sole. Tiny antialias fringe may extend one pixel below that ink baseline.

| Frame | Visible ink bounds [left,top,right,bottom) | Sole-span midpoint X | Sole Y |
|---|---|---|---|
| 1 | [154, 128, 360, 449] | 256.5 | 448 |
| 2 | [153, 127, 360, 449] | 256.0 | 448 |
| 3 | [154, 127, 360, 449] | 256.5 | 448 |
| 4 | [154, 129, 359, 449] | 256.0 | 448 |

More than 88% of each export is fully transparent; alpha spans0...255. Outer borders are transparent, silhouettes are uncropped, frames are distinct and GIF/APNG timing totals800ms. The reference sprites.png is RGB with a baked checkerboard and was used only for visual reference. No background color-keying or checkerboard removal was used on exports: generated transparency was preserved.

## Visual review and remaining limitations

Inspected all selected source frames and the normalized alignment sheet. A first peak-inhale generation stretched the character by about19 logical pixels and was rejected; the selected retry keeps the head within the small breathing range. Selected head-top ink bounds range y127...129 (two logical pixels). Sole-span midpoint varies by at most0.5px around the intended root; ink silhouette widths vary by2px. All feet retain the same baseline.

Generated frames are not perfectly pixel-locked: boot/lace/shorts shading and edge details vary slightly, and frame3 settles a little lower than neutral. Compared with frame0, thresholded boot-region alpha (y390...511) changes215/111/73 pixels in frames1/2/3 respectively. This is small localized contour variation rather than root translation, but can still cause subtle shimmer. No claim of zero jitter or final production approval is made. Judge the 800ms gameplay-size loop for distracting glove/outline changes before approving Stage B. If distracting, refine those regions before creating walking assets.

Only the supplied sprite sheet was available as character/style reference; no separate original character design image was provided. The reference's labels/frame counts were not adopted. Current engine idle remains four frames over800ms. Existing contact geometry, gameplay logic, live Assets.xcassets and build label10A are unchanged.

## Validation and next stage

Executed: python ArtV2/StageA/export_idle.py and python ArtV2/StageA/validate_idle.py. Dimension, RGBA/alpha, margins, root/baseline, uniqueness, checksum and GIF/APNG frame/timing checks pass. SpriteKit/iPhone playback is NOT RUN here (Windows, no Xcode). No live integration occurred, so no XCTest regression execution is claimed or required by this isolated artwork export. Review this package first; SpriteKit playback remains a separate validation step before asset replacement.

Stage B Advance/Retreat and orange variants have NOT been started. The user's task explicitly requires idle approval before proceeding to Stage B. No active placeholders were replaced.

Generation used the built-in imagegen tool with transparent_background=true. Full prompt set is in prompts.json. Pillow was used only for the requested uniform-scale/canvas export, alpha inspection and preview packaging, not for redrawing or warping the character.


## Review progression

User approved proceeding on 2026-10-19 ("ok lets"). Stage B now starts using this selected blue character as the reference. This authorizes Advance/Retreat artwork production; live catalog replacement remains deferred.
