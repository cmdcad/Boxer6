# Phase 3E — Shared Blue jab and Orange footwork handoffs

## Implemented on master
- Blue's six jab textures are generated from the approved Orange Jab V2 frames at load time, mirrored horizontally and hue-shifted by 180 degrees. Original Blue jab assets remain fallback.
- Blue's dedicated jab recovery pose is generated from the approved Orange jab recovery image by the same process, with original Blue recovery fallback.
- Orange advance/retreat reversals preserve the current travel-driven footwork frame and accumulator, avoiding a hard reset to frame zero.
- Existing guarded/unguarded footwork uses the same frame clock; bounce restarts on return to idle.

## Intentionally unchanged
- Orange Jab V2 frames, attack timing, contact geometry, CPU combat logic, block feedback, cross animation.
- No source PNG replacement or ZIP installation.

## Verification in Xcode (not yet performed)
1. Play Blue jab and compare pose order/contact timing to Orange's approved jab; verify Blue faces right and hue-shifted colors are acceptable.
2. Trigger Blue jab recovery; check there is no silhouette or orientation jump.
3. Force Orange advance -> retreat and retreat -> advance; look for footwork phase discontinuities.
4. Toggle Orange guard while moving; confirm footwork phase remains continuous and return-to-idle bounce begins at stance.
5. Verify both fighters' punches still resolve exactly one contact event and preserve previous damage/timing.
6. Check missing shared Orange jab assets correctly fall back to Blue jab assets.

Note: CIHueAdjust shifts all chromatic colors, not just orange regions; visual approval of Blue's palette is required before treating the result as final artwork.
