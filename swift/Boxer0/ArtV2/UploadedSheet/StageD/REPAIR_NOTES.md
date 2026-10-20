# Stage D repair — 2026-10-20

The original Stage D exports failed review. They retained baked checkerboard, clipped source poses and neighboring limbs. The two extra Cross slots were image blends rather than genuine transition drawings. Recovery GIF durations were also incorrect. The old report's count of valid frames did not establish visual correctness.

Use export_repaired.py and validate_repaired.py for the repaired package; older extract/export/report scripts are historical and must not regenerate final assets. Existing frames and manifest were archived under source/previous_frames and source/previous_manifest.json before repair.

The repair uses built-in imagegen to draw isolated individual poses from the approved actual-upload Idle. No Cross transition is constructed by interpolation or crossfade. Source outputs and prompts are retained. The user explicitly approved scripted compositing to keep the legs and boots fixed. Export resamples full canvases, performs small vertical registration and retains the exact approved Idle pixels at y>=260 (waist through boots). This is a fixed lower-body composite, not pose interpolation. It does not modify gameplay. Waist joins require visual inspection.

Contact overlays use the unchanged existing Jab (384.5,189), radius20 and Cross (378,186), radius18. Red is configured contact geometry; green is the existing defender upper-body target shown on the same image coordinate system for alignment reference, not a second opponent. Automated glove color segmentation is diagnostic only and cannot replace visual inspection.

Punch/recovery previews must show Jab 6x50ms + recovery120ms or Cross 8x60ms + recovery220ms, followed by Idle. The 400ms Idle hold is for preview readability. Gameplay recovery/timing is unchanged.

Orange production follows completion and approval of the full blue set, including Stage E reactions/knockdown/Down/Rise. No orange variants or live integration are included in this repair.

SpriteKit, XCTest and iPhone playback cannot be run on this Windows host. Final asset checks and remaining artistic limitations are recorded separately in validation_report.json and README.md.
