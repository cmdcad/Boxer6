# Stage E — Down and Rise, supplied artwork

Prepared one held Down pose and eight Rise frames over800ms (100ms each). Canvas512x512 RGBA, right-facing, logical root(256,448), baseline448. Live game assets and Swift behavior are unchanged.

## Source selection

The original ArtV2/Sprites folder now mixes hit-reaction files01..06 with older recovery07..09. The intact earlier Down/Rise copies were found in ArtV2/Sprites/Cleaned. These are the sources used here. Their selected pixel data is archived under source/ with hashes in manifest.json, and subsequent preparation runs prefer those archived copies. Never run generic sprite_frame exports into a folder holding a different animation set.

Rise order:01(prone),02(hands/knees),03(torso lifted),05(one knee),04(crouch),07(low standing),09(settling upright), then exact approved Stage A Idle. The original filenames are not a valid chronological order:04/05 are reordered. Upright alternatives06/08 are not needed. Down is exact Rise frame0; that intentional match provides a continuous start, not arbitrary frame padding. All eight Rise frames are distinct.

The sources were already edge-cleaned, so the edge pass was not repeated. Remaining detached islands were removed by keeping the connected body. One common scale, derived from source09 standing height versus approved Idle, is used for every supplied pose. Reviewed horizontal ground-root anchors provide translation; visible ground contacts register to448. No per-pose silhouette fitting, anatomical warping, paint repair or image generation was used. Leg/foot repositioning belongs to the source rise poses, unlike stationary punches/blocks.

## Deliverables

- frames/down_a_0.png: static Down.
- frames/rise_a_0.png through7.png: eight Rise frames.
- rise.png: exact800ms APNG preview.
- down_rise_gameplay.gif: Down hold400ms, Rise800ms, standing hold400ms. Holds are for review only.
- alignment_sheet.png: all Rise poses with review-only guides.
- source/, manifest.json, validation_results.json and the two Python scripts.

Run prepare_down_rise.py then validate_down_rise.py from the project root. Executed2026-10-20; all checks pass: nine exports, dimensions/alpha/margins, single significant silhouettes, baseline, checksums, consistent scale, archived source identity, eight unique Rise frames, exact Down start, exact approved Idle ending and actual preview timings. Final alignment sheet inspected visually.

## Limits and next work

Original low-resolution art remains softer and has different ink/shading from approved Idle. Pose transitions, contacts and horizontal anchors need review in motion; this is not a skeletal rig or a promise of perfect continuity. No missing anatomy was invented. No live integration, XCTest, SpriteKit or iPhone validation was performed.

This is not a falling animation. Do not reverse Rise and label it an authored Knockdown. A matching eight-frame Knockdown remains the outstanding blue Stage E artwork item; existing live falling assets remain available until replacement is ready. The prepared Down pose is the future fall's destination and should remain consistent with it.

Status: prepared for visual review, not automatically approved or integrated.
