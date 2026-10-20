# V2 Stage A — Uploaded boxer Idle

This package supersedes the earlier separately designed character. It uses actual Idle pose1 from the user's uploaded sprites.png (source box6,48,73,193). The low-resolution67x145 cutout was exported to the existing canvas, then faithfully cleaned with built-in imagegen to remove fringe/checker specks while keeping the compact character, pose, face, shorts, gloves and boots. Three minimal upper-body breathing edits were derived from that cleaned uploaded pose. This is artwork cleanup/refinement, not a claim that all four final images are untouched pixel slices.

## Deliverables

- frames/idle_a_0.png through idle_a_3.png: four unique512x512 right-facing transparent RGBA frames.
- idle_preview.gif: four200ms frames,800ms loop, approximately160px visible character height representative of a compact landscape gameplay viewport.
- idle_preview.png: same animation as transparent512px APNG.
- alignment_sheet.png: four-frame review sheet with root/baseline guides (guides are absent from individual PNGs).
- reference_sheet.png and source/isolated_uploaded_pose.png: actual user-supplied source evidence.
- source_contract.json, manifest.json, prompts.json: source crop, coordinates, checksums, mapping and full built-in cleanup/edit prompts.
- export_idle.py and validate_idle.py: repeatable canvas export and asset validation.

## Alignment report

Shared canvas512x512, ground/root(256,448), visible soles y448. One common scale established from the cleaned neutral pose is applied to all frames; no per-frame fitting or body deformation. Minor integer placement is based on sole midpoint/baseline. The source editing sequence is reordered as[0,1,3,2] to give measured neutral -> inhale -> peak -> settle, rather than blindly using generation order. Each final pose lasts200ms.

| Final frame | Ink bounds [left,top,right,bottom) | Sole-span midpoint X | Sole Y |
|---|---|---|---|
| 1 | [184, 129, 329, 449] | 256.0 | 448 |
| 2 | [184, 127, 329, 449] | 256.0 | 448 |
| 3 | [183, 126, 330, 449] | 256.0 | 448 |
| 4 | [184, 129, 330, 449] | 256.5 | 448 |

Metrics use alpha>=32; antialias fringe can extend about one pixel beyond the ink baseline. Sole-span midpoints remain within0.5px of root256; head tops vary by3 logical pixels and widths by2px. More than89% of each canvas is fully transparent. All outer borders are transparent; no cropped limbs, text, labels or decorative background. Final PNGs have true alpha, not checkerboard-colored backgrounds.

## Review limitations

Inspected the uploaded cutout, cleaned neutral, generated breathing pose and final alignment sheet. Character identity and the uploaded compact silhouette are retained. The original illustration is low resolution; linework remains softer/coarser than newly drawn high-resolution art. Small white trim, shading and boot-edge changes remain between AI-refined frames. Boots keep the baseline, but are not pixel-identical: thresholded boot-region differences versus neutral are166/250/183 pixels in final frames2/3/4. Review the actual800ms gameplay-size loop for distracting shimmer. No claim of zero visual jumps or final production approval is made.

## Validation and integration status

Executed export_idle.py and validate_idle.py: dimensions, RGBA/alpha, margins, root/baseline, checksums, four unique frames and800ms GIF/APNG timing all PASS. SpriteKit/iPhone playback is NOT RUN (Windows host, no Xcode). Existing live Assets.xcassets, Swift gameplay, contact geometry, build label10A and controls are unchanged. No XCTest execution is claimed for this isolated asset package. Future integration requires the established full regression suite and device review.

Stage B and later production are not resumed until this actual-upload Stage A is reviewed. The Cross correction is recorded in ../PRODUCTION_PLAN.md: create two genuine transitions when that stage is reached; preserve8 frames/480ms, contact at240ms, and separate220ms recovery. Do not fill Cross with arbitrary duplicate poses. Other illustration count discrepancies must likewise follow the existing engine contract (Idle4, Guard3, Hit reaction4, etc.).

Generation/editing mode: built-in imagegen, transparent_background=true. Pillow was used for requested canvas export, alpha/coordinate checks and preview packaging, not to invent poses. Earlier alternative-art folders are marked superseded and are not the approved replacement source.
