# Phase 3A — Fighter animation inventory and transition contract

## Decision (2026-10-23)
Proceed with the scheduled animation-system audit instead of rebuilding every
Orange action now. Orange Jab V2 has been committed; retain the current cross.
Heavy *offensive* punch art is not approved or scheduled for replacement.
Existing Orange normal/heavy *hit reactions* are separate defensive clips.

## Current artwork decisions
- Orange jab: V2 installed in `jab_b_0..5` with `jab_recovery_b_0`.
- Orange cross: keep `cross_b_0..7` and its existing recovery.
- Orange bounce: approved `orange_bounce_00..16`.
- Orange normal/heavy reactions: approved `orange_normal_00..17` and
  `orange_heavy_00..13`.
- Guard, locomotion, blocks, knockdown/rise, and remaining Blue/Orange actions:
  audit as provisional/fallback, **not** automatically approved just because
  an image set exists. Blue punch source packages can be reused, not rebuilt.
- No animation retiming, CPU behavior, damage, contact geometry, or combat logic
  changes in this audit.

## Preflight
Run from the repository root on a Mac:

```bash
git pull origin master
python3 tools/audit_fighter_animations.py --markdown
```

The audit checks both fighters' expected image-set counts, 512x512 8-bit RGBA
PNG headers, Contents.json filenames, and the names used by the SpriteKit
loaders. Missing assets and mismatches cause a nonzero exit status.

## Runtime transition contract (future implementation)
1. **Priority**: knockdown/down/rise > hit reaction > active punch > block
   feedback > physical punch recovery > guard/guarded locomotion > locomotion
   > idle/bounce. Match the existing scene's priority; document any deliberate
   exception before changing it.
2. **Punch contact**: Orange jab contact is index 3 of six, cross index 4 of
   eight. Keep once-only contact evaluation and the existing timing clock.
3. **Interruptions**: hit/knockdown/reset cancel or override incompatible
   attack presentation without phantom follow-up hits.
4. **Return to stance**: completed punch goes through physical recovery, then
   guard/locomotion/bounce as appropriate; don't force idle during movement.
5. **Geometry**: maintain the 512x512 canvas, ground/foot alignment, SpriteKit
   root transforms and collision calculations. Orange's approved left-facing
   bounce/reaction assets have an existing loader correction; don't apply that
   blindly to legacy jab/cross sprites.
6. **No false approval**: do not grade transitions from final sprites into
   provisional artwork as finished visual polish.

## Focused verification checkpoint
- The inventory audit passes on the checked-out Mac repository.
- In Xcode, Orange jab and cross can each hit, miss and be blocked.
- Orange jab shows the newly installed six frames and its recovery pose.
- Orange cross still uses the retained eight frames.
- Guard, movement, hit reaction, knockdown and rise interrupt/resolve cleanly.
- Record any pose jump by **from-clip -> to-clip**, frame indices, and
  whether either clip is provisional. Fix code defects immediately; postpone
  artwork-only mismatches until the affected art is approved.

## Next scoped implementation
After the audit, address one high-impact *code* transition defect or missing
asset category at a time, beginning with Orange guard/locomotion compatibility
with the approved bounce and jab. Only then proceed to Phase 4 combat
responsiveness; don't bundle all Orange sprite redesigns into one change.
