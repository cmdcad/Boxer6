# Stage D — repaired blue punches and recovery

This package replaces the rejected Stage D exports. The old grid slices retained checkerboard backgrounds, clipped poses and neighboring limbs. Their added Cross frames were 50/50 blends, and their recovery GIF timing was incorrect. The earlier validation conclusion did not establish visual correctness.

## Assets and timing

- Jab: six frames, 50 ms each, 300 ms total; contact index3 at150 ms.
- Cross: eight frames, 60 ms each, 480 ms total; contact index4 at240 ms.
- Jab recovery: one separate pose held120 ms.
- Cross recovery: one separate pose held220 ms.
- All sixteen exports: right-facing512x512 RGBA, root(256,448), support baseline448.

The approved actual-upload Idle provides character identity. Built-in imagegen creates isolated anatomical punch poses, including genuine Cross transition drawings. No frame is created by crossfading adjacent poses. The user explicitly authorized Python compositing to retain the approved lower-body pixels at y>=260, keeping legs and boots exactly stationary. Upper-body waist joins require visual inspection. Raw generated sources are retained in source/repaired/; the final exports include this fixed lower-body composite.

## Reproduce and inspect

Use export_repaired.py, then validate_repaired.py. Older extract/export/report scripts are superseded and must not regenerate the final package. Previous frames and manifest are archived under source/previous_frames/ and source/previous_manifest.json.

Inspect full_alignment_sheet.png, jab_with_recovery.gif and cross_with_recovery.gif. Exact-timing APNG versions are also supplied. Each recovery sequence returns to approved Idle, with a400ms preview-only Idle hold.

Contact overlays show the unchanged configured glove circles in red. Green shows the existing body target in the same image coordinates for comparison, not a second opponent. validate_repaired.py uses localized blue-color segmentation to measure glove/circle alignment; this is diagnostic and cannot replace anatomical review. No hitbox, reach, scene/root geometry or timing is changed to accommodate artwork.

The independent validation checks pixel data, transparency, connected components, margins, gray background contamination, frame counts, checksums, unique frames, exact fixed lower-body equality and actual preview durations. It does not certify every aspect of anatomy or animation quality. Minor generated ink/shading and glove-detail differences remain possible.

## Scope and status

Artwork package only; no live integration or gameplay edits. Swift/XCTest and SpriteKit/iPhone playback are unverified because this host is Windows. Check the final validation_report.json and contact_validation.json for executed results. Full device contact/body alignment still needs verification during integration.

Stage D awaits visual review. Complete Stage E blue reactions/knockdown/Down/Rise before producing orange palette variants from the approved blue set. Tool provenance and full prompts are saved in generation_prompts.json.

## Executed results — 2026-10-20

export_repaired.py and validate_repaired.py completed successfully. All sixteen frames pass the current checks, including exact fixed lower-body equality and correct punch/recovery/Idle preview durations. No significant detached fragments or large baked gray checkerboard regions were detected. Final alignment-sheet review confirms single complete figures, distinct torso rotation for Cross, straight contact arms, separate recovery poses and individually drawn transition poses without blended silhouettes.

Color segmentation estimates glove-center offsets of6.36px for Jab and8.28px for Cross relative to unchanged configured centers. Blue-glove coverage of the configured circles is73.8% and62.1%, respectively. Visual contact overlays confirm overlap; these measurements are not proof of exact anatomical hitbox fit or device behavior.

The composite includes the original complete belt starting at y254, excluding Idle's forearm fragment at x>=290,y254..259. All pixels from y260 downward remain exact approved Idle. This prevents foot sliding in the exported stationary punch sequence while leaving generated upper-body rotation. Minor waist contour, ink/shading and glove-detail variation remains for visual review. Later contact-arm and withdrawal correction prompts are saved in correction_prompts.json.
