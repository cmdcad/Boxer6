# Stage F — orange palette variants

Prepared 2026-10-20. All 74 prepared blue production frames have orange costume variants. No image generation was used. Live assets and Swift code remain unchanged.

Run `python ArtV2/UploadedSheet/StageF/prepare_orange.py` from the project root to rebuild frames, previews, reports and the ZIP. The manifest maps each output to its exact blue source and records both file hashes.

The script changes blue costume hue to orange while retaining saturation and value. It does not resample, translate, mirror, change opacity, or alter pixels outside the palette mask. All 74 frames passed exact alpha and non-costume-pixel comparisons. Canvases remain 512 × 512 with the existing root (256,448). Frames face right; SpriteKit must mirror orange at runtime as before.

Review `palette_comparison.jpg` and the Jab, Cross, Knockdown and Rise GIFs. GIFs loop for review; gameplay one-shot behavior and recovery timing remain governed by the existing engine. Canonical output filenames include `guard_b_*` and future `guarded_advance_b_*` / `guarded_retreat_b_*` sets.

Limitations: this pass preserves all blue-source visual limitations, including softer supplied hit/Down/Rise art and differences in reconstructed collapse frames. Dark boot shades become brown-orange; neutral ink and white trim are protected by the hue/saturation mask. This is palette preparation, not a new anatomical or animation validation. No simulator, iPhone or SpriteKit integration tests have run for these assets.

Next: review the prepared blue/orange set, then integrate the replacement catalogs and verify scale, contact overlays, movement phase, frame timing and gameplay on Apple hardware.
