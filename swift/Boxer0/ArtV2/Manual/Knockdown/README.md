# Next extraction — blue Knockdown

Latest update2026-10-20: the user asked the agent to handle extraction because neighboring limbs overlap. The agent has now prepared UploadedSheet/StageE/Knockdown using one extracted collapse pose, two intact kneeling configurations, four built-in imagegen reconstructions and the exact prepared Down pose. No user extraction is required for the current review package. The extraction instructions below are retained as source-reference history.

User authorization2026-10-20: user can crop/clean/extract poses; agent should generate genuinely missing or unusable frames when necessary. Evaluate supplied poses before generation to minimize credits.

## User extraction needed now

From the original sheet's fourth row, right-hand KNOCKDOWN(8 frames) group, extract the FIRST SEVEN numbered poses left-to-right. Deliver knockdown_source_01.png through knockdown_source_07.png in this directory. We already have an approved-source prepared Down destination to use for final frame8; reference_down_a_0.png is a copy for comparison, not another drawing request. The eight-frame Knockdown package will preserve640ms total (80ms/frame), ending in that exact Down pose.

reference_knockdown_strip.png is an unmodified RGB crop showing the source poses without most surrounding labels. It is a visual extraction reference, NOT a transparent production asset. The illustration has touching/overlapping characters, so a uniform grid is unsafe.

Crop each complete boxer, keep extra transparent margin, remove checkerboard/labels, preserve original scale and anti-aliased transparency, and avoid resizing each pose independently. Native-size crops are acceptable: agent will export512x512 and align root(256,448)/baseline448. Do not cut limbs to get rid of an overlapping neighbor. If full isolation is impossible, include the unclean crop and label its problem; the agent is authorized to create missing contours/transition poses after inspection. No need for the user to draw new poses.

## Agent follow-up after delivery

Inspect individual silhouettes/alpha, identify actual missing frames or contours, generate only those needed, clean/align copies, make all8 frames over640ms, and preview last hit reaction -> fall -> exact held Down. Do not reverse Rise as a fall or change combat mechanics. Keep existing live assets until replacement review and later integration/regression tests.

Current status: extraction folder/reference prepared; no missing-frame generation yet. The original audit cutouts are joined groups, not valid individual frames. No live Swift or assets have changed.
