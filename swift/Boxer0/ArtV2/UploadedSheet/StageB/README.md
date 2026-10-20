# Boxer0 V2 — Stage B actual-upload blue footwork

Stage A actual-upload Idle was approved in chat. This package continues that selected compact boxer, not the earlier superseded alternative character. The approved cleaned Idle provides identity; cropped Advance/Retreat strips from the uploaded sheet provide pose reference. Frames were reconstructed/refined with built-in imagegen because neighboring source poses touch/overlap and cannot be cleanly grid-sliced. They are not claimed to be untouched pixel cutouts.

## Deliverables

- frames/advance_a_0.png ... advance_a_5.png: six individual right-facing512x512 transparent RGBA PNGs.
- frames/retreat_a_0.png ... retreat_a_5.png: six individual right-facing512x512 transparent RGBA PNGs.
- advance_preview.png and retreat_preview.png: transparent APNGs, six80ms frames each,480ms looping.
- advance_gameplay.gif and retreat_gameplay.gif: approximately160px visible character height with a review-only scrolling ground grid.
- movement_preview.gif: both gameplay-size loops side by side. Advance is left; Retreat is right.
- alignment_sheet.png: root/baseline review guides. Labels and ground graphics are absent from the exported individual frames.
- manifest.json: exact selected sources, timing, checksums, planned phases, measured sole points and registration offsets.
- prompts.json and correction_prompts.json: built-in generation/edit prompt records; source/ retains generated/refined candidates.
- export_footwork.py, validate_footwork.py and validation_results.json: repeatable export, executed technical checks and motion review flags.

## Frame and motion contract

Both clips retain6 frames over480ms. Canvas512x512; right-facing; origin/ground root(256,448); support baseline448. No source art is individually fitted or warped. Every frame uses the same scale as the approved Idle and the same starting canvas transform.

Advance steps with the front/right foot first, then the rear foot follows. Retreat steps with the rear/left foot first, then the front follows. Each includes swing, landing and follow-through; no foot crossing. Gloves remain in the ordinary boxing stance. These are normal footwork clips, not guarded-walking artwork.

The clips legitimately share their wide double-plant and narrow closing stance because both directions pass through those same static configurations. Each clip still has six unique rendered poses. This is not arbitrary padding or a change to the future eight-frame Cross requirement. The Cross correction remains: create two genuine transitions when that production stage is reached.

## Root and planted-foot registration

Raw AI pose outputs do not numerically lock feet. Several candidates were rejected/corrected for wrong foot support, excessive height/scale, or an over-high swing. Export uses bounded vertical placement to put the named support sole on the baseline, and horizontal stance registration to coordinate the drawn planted sole with the existing root travel. Registration changes placement, never body proportions or image scale. The sprite canvas origin stays(256,448); there is no independent net image travel added across a loop.

Calibration:100 scene points/sec,0.5 sprite scale,80ms per frame ->8 scene points (16 canvas pixels) root travel per frame. The registration aligns sole-midpoint samples to that travel, including double-plant phases and the loop wrap. This makes the preview's ground grid a useful diagnostic rather than a decorative background.

| Frame | Ink bounds [left,top,right,bottom) | Horizontal registration | Vertical registration | Rear / lead ground gap |
|---|---|---:|---:|---|
| advance 1 | [180, 129, 376, 449] | 10 | -1 | 0 / 12 |
| advance 2 | [163, 134, 384, 449] | -2 | 5 | 0 / 12 |
| advance 3 | [136, 136, 377, 449] | 0 | 7 | 0 / 0 |
| advance 4 | [171, 130, 358, 449] | 11 | 0 | 7 / 0 |
| advance 5 | [172, 130, 341, 449] | -2 | 0 | 9 / 0 |
| advance 6 | [198, 128, 323, 449] | -1 | 0 | 0 / 2 |
| retreat 1 | [175, 137, 341, 449] | 4 | 5 | 10 / 0 |
| retreat 2 | [121, 139, 359, 449] | -22 | 10 | 4 / 0 |
| retreat 3 | [136, 136, 377, 449] | 0 | 7 | 0 / 0 |
| retreat 4 | [157, 130, 368, 449] | 1 | 1 | 0 / 17 |
| retreat 5 | [172, 130, 327, 449] | -4 | 1 | 0 / 8 |
| retreat 6 | [199, 128, 324, 449] | 0 | 0 | 0 / 2 |

Negative ground-gap values would indicate ink below baseline. Slight gap on the second sole of a double-plant stance can reflect a tilted boot/antialias edge. Measurements use alpha>=32; fringe pixels are not anatomical landmarks.

Measured support-sole midpoint ranges under the preview calibration (frame-1 denotes the preceding cycle's final pose):

- advance, rear support, frames [-1, 0, 1, 2]: 0.75 preview pixels.
- advance, lead support, frames [2, 3, 4, 5]: 0.00 preview pixels.
- retreat, lead support, frames [-1, 0, 1, 2]: 0.50 preview pixels.
- retreat, rear support, frames [2, 3, 4, 5]: 0.25 preview pixels.

These are sampled image-space diagnostics, not proof of zero sliding on every frame or device. Foot rolling, toe shape and ankle placement are not a skeletal contact rig. Registration creates visible weight shifts and head/hip bob; assess their smoothness in the actual loop. Generated ink, laces, clothing folds and muscle shading can vary slightly between poses.

## Validation results and limitations

Executed export_footwork.py and validate_footwork.py. Technical checks pass: twelve512px true-alpha PNGs, six unique poses per clip, transparent margins, uncropped silhouettes, front/rear ordering, checksums and six80ms frames (480ms) in each GIF/APNG. Motion-review warnings, if any, are listed in validation_results.json.

Visual review inspected generated lift/follow-through poses, corrected landings, and the final alignment sheet. The original uploaded sheet's baked checkerboard is not exported. All art remains outside live Assets.xcassets. Swift gameplay, movement speed, contacts, guard rules, damage, existing animation timings and build label10A are unchanged. No XCTest execution is claimed: no integration occurred, and Xcode/Apple SDKs are unavailable on this Windows host.

SpriteKit/iPhone playback remains unverified. Actual fighter scale varies with viewport; CPU base speed is65 rather than the blue preview's100. This preview calibration does not establish correct foot locking for every scene scale or the later orange variants. Future integration must evaluate the visual stride against actual root travel for both fighters, without altering gameplay movement to disguise poor alignment. Body bob, lateral weight shift, minor ink/shading changes and foot rolling remain artistic-review points. The low-swing Advance correction is selected; the earlier high-step candidate is retained only as rejected source history. Pose registration can move the torso relative to the existing fixed target rectangle, so body/target alignment must also be checked before integration. No full production/device acceptance is claimed from asset checks alone.

## Review progression

Approved by the user in chat on 2026-10-20: "b is approved. can u update the task". This approves both Advance and Retreat artwork previews. They are not installed in the app yet; SpriteKit/iPhone validation remains outstanding. Stage C (Guard and guarded movement) is next, followed by the remaining production stages in ../PRODUCTION_PLAN.md. Keep the working sprites active until integration is ready for regression testing.

Tool provenance: built-in imagegen with transparent_background=true. Pillow/numpy are used only for requested uniform canvas export, bounded pose registration, measurement, previews and packaging; no painted body-part warping or synthetic leg drawing is performed by the exporter. Full prompts and selected source paths are retained.
