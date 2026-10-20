# V2 actual-upload production plan — corrected scope

Integration update (2026-10-20): 148 production frames are now installed in the live catalogs, including both fighters' guarded walking. See INTEGRATION.md and integration_results.json. Original affected catalogs are saved in pre_v2_live_assets.zip. Source/asset checks pass; Xcode compilation, XCTest execution and iPhone visual validation remain pending. Earlier per-stage "not integrated" notes describe their preparation history and are superseded by this update.

Stage F update (2026-10-20): all 74 orange palette variants are prepared under StageF, using deterministic costume-only recoloring with no generation credits. Exact alpha, dimensions and pixels outside the palette mask passed checks for every frame. See StageF/README.md, manifest.json, validation_results.json and palette_comparison.jpg. Blue and orange packages remain isolated from the live app; visual review and SpriteKit/device integration are outstanding.

Latest workflow (2026-10-20): the user wants the agent to handle pose changes and preparation; the user may optionally crop/clean source images. This supersedes the earlier user-art delegation. Prefer supplied artwork and authorized scripted compositing to reduce generation credits. See ../MANUAL_ART_HANDOFF.md. Stage E block recoil is now prepared by script and awaits review.

Source: the user's sprites.png, not the separately generated alternatives under ArtV2/StageA or StageB. Existing game assets remain active until the current stage is reviewed and validated. The previous alternative Stage B is not the approved replacement source.

Current status (2026-10-20): actual-upload Stage A (Idle) and Stage B are approved; Stage C has a repaired package. Stage D's initial export failed review; its repaired sixteen-frame package now passes asset validation and awaits visual review. Reconcile every illustrated category to the existing engine contract rather than adopting illustration labels. SpriteKit/device integration remains unverified.

| Animation | Final frames | Duration | Status |
|---|---:|---|---|
| Idle |4|800ms loop|Approved in chat; actual source pose, faithful cleanup and four-frame breathing loop|
| Advance |6|480ms loop|Stage B approved in chat on 2026-10-20|
| Retreat |6|480ms loop|Stage B approved in chat on 2026-10-20|
| Guard entry |3|120ms|Stage C repaired package; awaiting review, not integrated|
| Guarded advance |6|480ms nominal loop; integration must coordinate phase with movement|Stage C repaired package; awaiting review, device stride unverified|
| Guarded retreat |6|480ms nominal loop; integration must coordinate phase with movement|Stage C repaired package; awaiting review, device stride unverified|
| Jab |6|300ms|Stage D repaired; awaiting review; contact index3 at150ms|
| Cross |8|480ms|Stage D repaired with genuine transitions; awaiting review; contact index4 at240ms|
| Jab recovery |1 held pose|120ms|Stage D repaired; awaiting review|
| Cross recovery |1 held pose|220ms|Stage D repaired; awaiting review|
| Hit reaction |4|240ms|Stage E/HitReaction prepared from supplied02,04,03,01; checks pass; awaiting visual review|
| Block Jab/Cross |3 each|120/160ms|Stage E/BlockRecoil prepared by scripted guard lean; checks pass; awaiting visual review|
| Knockdown |8|640ms|Stage E/Knockdown prepared by agent: extracted start, two reused kneels, four reconstructed collapse poses, exact Down. Checks pass; awaiting visual review.|
| Down |1|held|Stage E/DownRise prepared from intact cleaned source01; checks pass; awaiting visual review|
| Rise |8|800ms|Stage E/DownRise prepared:01,02,03,05,04,07,09,approved Idle; checks pass; awaiting visual review|

## Cross correction — user-approved future work

Use the six illustrated poses as references rather than treating them as six consecutive final frames. Create two anatomically consistent transition poses, not arbitrary duplicate frames. Preparation, hip/shoulder rotation, extension, contact, retraction and return toward guard must read continuously. Preserve character scale, right-facing design, glove style, root(256,448), baseline448,512px true-alpha export,480ms animation,240ms contact and separate220ms recovery. Preview all eight before SpriteKit integration. This is future Cross-stage authorization, not a request to produce Cross now.

## Source constraints

The upload is a1536x1024 RGB illustration with baked checkerboard and adjoining/overlapping poses. Individual characters are roughly70x145 source pixels, so faithful edge restoration may be needed before512px export. Preserve the uploaded character and actual artwork identity during cleanup; do not substitute the separately designed, bulkier character from the earlier mistaken workflow.

No Swift gameplay, source geometry, probabilities or existing texture catalogs are modified during isolated artwork production. Run the full XCTest suite after any future integration, and report Mac/iPhone results separately from asset checks.


## Next-agent handoff

Stage A approval received in chat: user replied "approved" after reviewing the actual-upload Idle preview. Stage B approval received on 2026-10-20: user stated "b is approved. can u update the task". Both Advance and Retreat previews are approved; do not request their approval again.

Stage C was subsequently reviewed and repaired at the user's request. The original exports had scaling, clipping, neighboring-fragment and missing-guard problems. Use StageC/export_repaired.py, source/repaired/, README.md and validation_results.json; older export_guard*.py iterations are superseded. The corrected package awaits visual review and is not integrated. Preserve the complete 120ms guard-entry delay and existing mechanics. Inspect current Swift movement/animation playback before future integration; nominal art loops do not establish device foot locking.

Stage D's first package failed review: baked checkerboard, clipped source poses, neighboring limbs, blended Cross transitions and incorrect recovery GIF timing. Its earlier report did not establish visual correctness. Use StageD/export_repaired.py and validate_repaired.py; older extract/export/report scripts are superseded. Repaired poses are drawn separately using the approved Idle as identity reference. The user explicitly authorized scripted compositing to keep approved lower-body pixels fixed. Preserve current contact geometry and validate artwork against the existing circles; do not change gameplay to conceal bad exports. Consult the repaired README, reports and previews for final results and limits.

After Stage D review, continue with hit/block reactions, knockdown/Down/Rise, and orange variants after the blue artwork is approved.

Use ArtV2/UploadedSheet as the production source; ArtV2/StageA and ArtV2/StageB are superseded alternatives. Keep live assets active until integration is ready. Preserve canvas, root, scale, facing, timing and contact contracts; do not change mechanics to compensate for artwork. After integration, run the full XCTest suite and report actual simulator/iPhone results separately from asset checks.
