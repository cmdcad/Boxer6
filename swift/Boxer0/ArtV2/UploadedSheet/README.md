# Uploaded sprite sheet — direct-source extraction audit

User clarified that the actual uploaded sprites.png artwork must replace the old sprites throughout the game; separately generated StageA/StageB images are not the intended replacement source. The original upload is copied here as uploaded_sprites_original.png. Working gameplay assets have not yet been replaced.

## What was executed

Inspected the live animation loader, the512px canvas/root contract, contact markers and uploaded RGB image. Ran extract_sheet.py to remove border-connected light checkerboard regions while preserving enclosed whites and inspect foreground connectivity. extraction_review.png and extraction_manifest.json are diagnostic candidates only, not production assets.

Many poses touch or overlap: the six Jab drawings form one connected foreground region; Cross also forms one. Guarded Advance's six drawings are one connected region. Several walking boots touch neighboring boots. Knockdown and early Rise poses overlap. A simple grid crop or connected-component slice cannot recover every complete individual pose without trimming or retaining part of a neighbor.

Flood-fill candidates can also retain checkerboard in enclosed gaps between limbs; this is visible in the review sheet. Some Rise crop bounds exclude hair at the top. Therefore these cutouts are explicitly NOT validated production-ready PNGs and must not be integrated as-is. Clean individual exports or additional repair/matting work are required. The review image is evidence of the source problems, not an animation deliverable.

## Contract mismatch

The engine requires4 Idle,6 Advance,6 Retreat,3 guard-entry,6 Jab,8 Cross,4 hit-reaction,8 knockdown,1 Down and8 Rise frames, plus existing recovery/block profiles and optional guarded footwork. The sheet labels6 Cross poses rather than8. It also labels other sequences with different counts, and some knockdown/rise labels do not uniquely identify isolated poses. No animation/contact timing was changed, no missing poses were silently fabricated and no old clips were silently substituted.

An asynchronous question asks whether selected uploaded Cross poses may be reused to populate the eight timed slots while preserving480ms total and240ms contact. That dependent mapping is pending the user's answer. Any eventual source remapping and repaired overlap must be documented and validated before full integration. Original individual transparent frames would avoid the source-overlap/matting issue.

Status: direct-source preparation/audit performed; full replacement remains incomplete. Existing Assets.xcassets, gameplay Swift files, contact geometry and test behavior are unchanged in this clarification step. No XCTest or device validation is claimed.


## User correction to frame reconciliation

The Cross question is resolved: do NOT fill eight slots with arbitrary duplicates. When the Cross production stage is reached, create two anatomically consistent transition poses using the six illustrated poses as references, while preserving480ms duration,240ms contact and separate220ms recovery. Preview before integration. Continue Stage A Idle first. Idle/Guard/Hit frame counts must also follow the engine contract rather than illustration labels. See PRODUCTION_PLAN.md. The previous extraction audit is retained as source evidence; its candidates are not the final Stage A assets.
