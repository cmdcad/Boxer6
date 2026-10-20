# Stage E — blue block recoil

Six prepared complete-frame sprites: block_jab_a_0..2 and block_cross_a_0..2. They reuse Stage C's held guard. No new artwork generation or generation credits were used. This work follows the user's latest instruction to let the agent handle image changes with scripted compositing.

## Motion

A small2D upper-body lean pivots at the belt(y258); the lower body is copied exactly. This is a restrained affine artwork effect, not independently redrawn anatomical poses or a new body-part rig. There is no root/node translation, vertical scaling, flash or facing change. Gloves stay in the raised guard posture.

Jab uses head-level lean parameters4,8,2 canvas pixels, over120ms. Cross uses7,14,3 over160ms. Both show immediate recoil, peak and return toward held guard. Exact held guard follows completion; the guard-entry animation is not replayed. At half-size gameplay preview scale, the measured head-region peak movement is about3.3px for Jab and5.8px for Cross. Ordinary-speed perception still requires review.

## Files and timing

- frames/: six right-facing512x512 RGBA PNGs, root(256,448), baseline448.
- source/held_guard.png: unchanged reference copy.
- block_jab.png and block_cross.png: three-frame production APNG previews.
- *_to_guard.png: recoil followed by exact held guard with a400ms review hold.
- *_gameplay.gif and block_comparison.gif: gameplay-size previews.
- alignment_sheet.png: guide-marked review sheet only.
- manifest.json and validation_results.json: parameters, hashes, timings and executed checks.
- prepare_block_recoil.py and validate_block_recoil.py: reproducible preparation/checks.

The three Cross frames last160/3ms each. APNG fractional delay fields preserve that exact rational timing. GIF cannot express thirds of a millisecond; individual Cross GIF timing is50/60/50ms, totaling160ms, and the comparison GIF samples at10ms. This does not change engine playback.

## Validation and scope

Executed both scripts successfully on2026-10-20. Six distinct poses pass dimensions, transparency, margins, significant connected silhouette, baseline, checksum, exact fixed-lower-body equality, glove-area retention, onset/peak/return ordering, stronger Cross displacement, exact APNG timing and exact held guard at completion. The final alignment sheet was visually inspected.

Minor interpolation softening and waist contour variation remain artistic-review points. The effect is deliberately modest; asset checks cannot certify ordinary-speed visibility on every device. Live Swift, texture catalog, damage, health, counters, guard eligibility, pause and reset logic are unchanged. No XCTest, SpriteKit or iPhone playback was performed; integration remains pending review.

Stage E is still incomplete. Hit reaction and block-recoil preview packages are prepared; matching Knockdown, Down and Rise artwork preparation remains.
