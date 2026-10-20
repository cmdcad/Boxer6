# Stage E — blue Knockdown, review package

Eight frames over640ms (80ms each), ending in the exact prepared Down pose. Right-facing512x512 RGBA, logical root(256,448), baseline448. The existing live animation remains unchanged; these are isolated replacement assets awaiting review.

## Source and reconstruction

- Frame0: original illustrated standing-collapse pose, manually separated from a touching neighboring boot, edge-cleaned and registered at the existing source scale.
- Frames1/2: intact high/low kneeling configurations from supplied artwork already prepared in DownRise. These configurations are shared with recovery, while the complete sequence includes dedicated downward-collapse transitions.
- Frames3/4/5/6: four individually reconstructed collapse/landing poses using built-in imagegen, with the original overlap references, approved Idle identity and prepared Down destination. These restore hidden limbs/contours and supply the missing transition detail.
- Frame7: exact prepared Down pixels, continuing as the held Down state afterward.

Only four reconstructed images were generated, rather than regenerating the complete clip. Full prompts are in generation_prompts.json and source outputs are retained. No frames were padded with arbitrary duplicates or crossfaded. The final Down frame's match to the separate held Down asset is intentional.

## Deliverables

frames/knockdown_a_0.png through7.png, knockdown.png(exact640ms APNG preview), knockdown_gameplay.gif(fall then Down hold), defeat_sequence_gameplay.gif(Standing, final hit reaction, fall, Down), alignment_sheet.png, source/, manifest.json, validation_results.json and the three preparation/validation scripts.

Run extract_references.py, prepare_knockdown.py and validate_knockdown.py from the project root. Reconstructed source outputs must already exist; export does not call image generation. Export uniformly resamples generated full canvases to512 and registers their floor contact; it does not independently fit body bounds. The two kneeling images and final Down retain their existing512 canvases.

## Executed checks and limitations

Executed successfully2026-10-20. All eight distinct frames pass dimensions, transparency, canvas margins, a single significant silhouette, baseline448, checksums, large-gray-background detection, exact Down destination and actual APNG/GIF timing. The alignment sheet and reconstructed poses were visually inspected. A small foreign boot fragment in the first extraction was corrected before packaging.

The extracted/supplied frames are lower-resolution and softer than the reconstructed frames; ink, shading and costume-detail differences are visible. The near-final silhouette top is8px lower than the final source Down contour, so inspect that last transition in motion. Bounding-box checks cannot certify anatomical proportions, perceived speed or perfect continuity. This is a review package, not final device acceptance.

Previews loop for inspection, with temporary400ms Standing and600ms Down holds. Game behavior remains one-shot Knockdown, followed by indefinitely held Down until existing Rise/reset behavior is invoked. No health, damage, defeat, reaction, root motion, controls or timing code was changed. No live catalog integration, XCTest, SpriteKit or iPhone validation was performed on this Windows host.

All blue Stage E categories now have prepared preview packages: HitReaction, BlockRecoil, DownRise and Knockdown. Visual approval and later integration/regression testing remain outstanding. Orange palette variants follow approval of the blue set.
