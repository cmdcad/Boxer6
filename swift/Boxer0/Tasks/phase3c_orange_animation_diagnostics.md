# Phase 3C — Orange animation diagnostics (implemented)

## Problem
The Xcode overlay previously displayed a high-level Orange state such as
`idle` or `guardPose` even while SpriteKit displayed `orange_bounce`,
`guarded_advance_b`, or a block recoil image. The displayed frame could
also be wrong during guarded locomotion. This made it difficult to identify
which provisional art was causing an apparent transition jump.

## Implementation
`IdleTestScene.swift` now derives `orangeAnimationName`,
`orangeFrameIndex`, and `orangeFrameCount` from one read-only
`orangePresentedAnimation` tuple. Its priority and texture-family selection
match the existing Orange branch order in `applyFrames()`:

1. Knockdown / rise / down
2. Hit reaction (approved normal/heavy when available, legacy otherwise)
3. Active jab or cross
4. Block recoil
5. Physical jab/cross recovery (dedicated pose when enabled)
6. Guard, including guarded advance/retreat
7. Unguarded advance/retreat
8. Approved bounce, otherwise legacy idle

The existing `ContentView.swift` debug text already reads these properties,
so no UI changes are required. Reported texture names now identify the
actual image-set prefixes (`jab_b`, `cross_b`, `orange_bounce`, etc.).
All frame indices remain zero-based in the scene and are displayed as
one-based counts by the existing SwiftUI overlay.

No art, root transforms, damage, timing, CPU logic, animation state,
or texture assignment was changed.

## Mac verification
```bash
git pull origin master
python3 tools/audit_fighter_animations.py --markdown
```

Build and run in Xcode, then observe the existing Orange animation label.
It should show:
- `orange_bounce` while standing idle
- `jab_b` during Orange's six-frame jab
- `jab_recovery_b` during dedicated jab recovery
- `cross_b` during the retained eight-frame cross
- `guard_b` when guarding in place
- `guarded_advance_b` / `guarded_retreat_b` when guarded and walking
- `advance_b` / `retreat_b` when walking without guard
- `block_jab_b` / `block_cross_b` during a block response
- `orange_normal` / `orange_heavy` during approved hit reactions

If a visual jump is observed, record the last and first displayed names and
frame numbers (for example `cross_b 8/8 -> cross_recovery_b 1/1`).
That provides an actionable asset-pair bug report without forcing a
premature rebuild of every Orange action.

## Next
Use the diagnostic output to prioritize the Orange cross redesign and
other provisional-to-approved handoffs. Only modify the artwork that causes
an observed discontinuity. Xcode visual validation is pending.
