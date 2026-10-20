# Stage C — repaired blue guard artwork

This package repairs the earlier Stage C exports. Those exports either shrank the character, copied normal walking frames without a guard, or sliced adjoining source figures and retained clipped boots and neighboring fragments. The earlier export_guard*.py files are retained as history; they are superseded by export_repaired.py and must not regenerate the deliverables.

## Production source

The approved actual-upload Stage A Idle and Stage B Advance/Retreat frames provide the character identity and complete leg poses. Built-in imagegen edits each complete individual reference to raise the gloves, keeping the established pose, costume and framing. Guard entry starts with the approved Idle, proceeds through an intermediate glove-raising pose and finishes in a high guard. These are edited/refined sprites, not untouched extractions from the uploaded illustration.

Generated sources are retained in source/repaired/. generation_prompts.json records the exact requests and reference files. No raw overlapping audit strips are sliced into final sprites. Pillow/numpy only resample complete canvases uniformly, register the baseline, measure, and create previews; they do not paint, mask or warp body parts.

## Contract

- Fifteen right-facing 512 x 512 RGBA PNGs: three guard-entry frames, six guarded Advance and six guarded Retreat frames.
- Logical root (256,448), support baseline 448. Full generated canvases are uniformly resampled to 512; no individual bounding-box fitting is used. Small vertical registration is recorded per frame.
- Guard entry: 3 x 40 ms = 120 ms, then hold the final pose. Protection must still wait the complete 120 ms in the existing simulation.
- Guarded walking previews: 6 x 80 ms = 480 ms per loop. Frame order follows approved Stage B leg phases.
- Production APNGs retain exact timing. The separate guard-entry gameplay GIF holds its final pose longer so it can be inspected; this is not a change to the game timing.

## Validation and limits

Run python ArtV2/UploadedSheet/StageC/export_repaired.py, then python ArtV2/UploadedSheet/StageC/validate_repaired.py from the project root. The validation report checks actual exported pixel data, dimensions, transparency, significant connected components, canvas margins, checksums, unique frames, differences from normal footwork and APNG timing. Foot measurements fail if a foot cannot be found; missing geometry is never reported as a perfect baseline.

Review alignment_sheet.png plus the gameplay GIFs for anatomy, guard progression and motion continuity. AI edits can introduce minor line, shading, glove and lace variation. Component checks cannot certify anatomy or foot locking.

This remains an isolated artwork package. No Swift source, live texture catalog, guard effectiveness, movement speed, damage or contact geometry is changed. Device playback, SpriteKit root/target alignment and XCTest are unverified on this Windows host. Guarded movement uses slower existing speeds (blue 55 and orange 35.75 scene points/sec); Stage B's stride calibration must not be mistaken for proof of foot locking at those speeds. Integration must inspect movement phase against actual root travel and preserve the established mechanics. Orange variants are a later stage.

Status: repaired package awaiting visual review; not integrated or automatically approved.

Executed on 2026-10-20: export_repaired.py and validate_repaired.py completed successfully; validation_results.json reports passed=true with no errors across all 15 exports. Final alignment-sheet review confirms complete boots, removal of neighboring fragments and a visible neutral/intermediate/high-guard sequence. Minor generated ink/shading differences remain. The live app and its tests were not modified or run.
