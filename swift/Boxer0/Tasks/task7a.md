# Boxer0 — Task 7A: Basic Defensive Guard

## 1. Objective

Introduce a basic defensive guard system into the existing Swift/SpriteKit boxing prototype.

The orange boxer should be able to enter and hold a defensive guard using a debug control.

When a Jab or Cross makes contact while the guard is active, the punch should register as BLOCK rather than HIT.

For this milestone, blocked punches cause zero damage.

Preserve all completed functionality through Task 6D.

Inspect the latest Swift source files, sprite assets, animation metadata, and existing contact/damage architecture before implementing changes.

Do not rebuild completed systems or introduce opponent AI.

## 2. Guard animation

Use the existing `guard` animation defined in the Boxing Placeholder Sprite Specification.

| Property | Value |
|---|---|
| Animation | `guard` |
| Frames | 3 |
| Total entry duration | 120 ms |
| Frame duration | 40 ms |
| Playback | Once, then hold final frame |

The guard sequence should show the orange boxer raising its gloves into a defensive position.

After reaching frame 3, hold that frame until guard is released.

Do not continuously loop the guard animation.

Verify that the required orange-boxer guard assets exist. Report missing assets rather than substituting unrelated frames.

## 3. Guard debug control

Add a debug control labeled `Guard` near the existing Rise and Reset Health controls.

Use a toggle for this initial implementation:

- Tap Guard while standing to activate.
- Tap Guard again to deactivate.
- Show the active state clearly.
- Keep the control accessible in landscape orientation.

Guard must be unavailable while the orange boxer is:

- Defeated.
- Playing a hit reaction.
- Playing knockdown.
- Down.
- Rising.

When guard is deactivated, return to the existing idle animation.

Do not modify the blue boxer's movement or attack controls.

## 4. Guard state

Keep defensive state separate from combat eligibility and animation playback.

Recommended state structure:

**Combat state**
- `standing`
- `defeated`

**Defense state**
- `unguarded`
- `guarding`

**Animation state**
- `idle`
- `guard`
- `hit_react`
- `knockdown`
- `down`
- `rise`

Guarding is only valid while the boxer is standing.

Do not create a new combat state solely for guard.

## 5. Guard activation timing

The guard animation takes 120 ms to reach its final defensive pose.

For Task 7A, use a simple rule:

**Guard becomes effective only after the third guard frame is reached.**

During guard entry:

- The boxer is visually raising its gloves.
- The guard is not yet effective.
- An incoming punch can still register HIT and cause normal damage.

After the guard reaches its final frame:

- The guard becomes effective.
- Contacting punches register BLOCK.
- No damage is applied.

When Guard is toggled off, defensive protection ends immediately and the boxer returns to idle.

Use scene time, not wall-clock timers, so pause and frame stepping behave consistently.

## 6. Punch contact classification

Extend the existing contact-resolution system to support three outcomes:

`HIT`, `BLOCK`, and `MISS`.

Resolve each punch once at its existing contact frame.

Recommended order:

1. Verify both fighters are combat-eligible.
2. Evaluate existing glove-to-target spatial contact.
3. If there is no contact, return MISS.
4. If contact exists and defender guard is effective, return BLOCK.
5. Otherwise, return HIT.

Do not classify a punch as BLOCK merely because the defender is guarding.

**A punch outside contact range must still register MISS.**

Preserve the existing Jab and Cross contact-frame timing and geometry.

## 7. Damage and reaction behavior

| Outcome | Damage | Orange response |
|---|---:|---|
| Jab HIT | 5 | Existing hit reaction |
| Cross HIT | 10 | Existing hit reaction |
| Jab BLOCK | 0 | Hold guard |
| Cross BLOCK | 0 | Hold guard |
| MISS | 0 | No new reaction |

Blocked punches must not trigger the existing `hit_react` animation.

The orange boxer should remain in the guard pose after a successful block.

Do not introduce block recoil, guard-breaking, chip damage, stamina consumption, or knockback.

These can be considered in later milestones.

## 8. Guard interruption rules

If an unblocked punch lands during the guard-entry animation:

- Register HIT.
- Apply normal damage.
- Cancel guard entry.
- Clear the guarding state.
- Play the existing hit reaction.
- Return to idle afterward.

The player must activate Guard again to resume guarding.

If the punch reduces health to zero, preserve the established sequence:

`Hit Reaction → Knockdown → Down`

Any active guard state must be cleared when defeat occurs.

Do not allow a pending guard animation completion event to reactivate protection after defeat or reset.

## 9. Debug counters

Preserve existing Jab, Cross, HIT, and MISS counters.

Add a BLOCK counter, displayed as `B`.

Suggested HUD:

`J: 2   C: 2   H: 1   B: 2   M: 1`

Each resolved punch increments exactly one outcome counter.

The new invariant is:

`J + C = H + B + M`

This applies to punches that reach contact resolution while combat is active. Punches rejected after defeat must not change these counters.

For example:

- Two Jabs.
- Two Crosses.
- One HIT.
- Two BLOCKS.
- One MISS.

Result:

`2 + 2 = 1 + 2 + 1`

Do not count a blocked punch as both HIT and BLOCK.

## 10. Guard diagnostics

Preserve existing debug overlays and animation readouts.

Add a guard-status indicator:

- `Guard: OFF`
- `Guard: RAISING`
- `Guard: ACTIVE`

The orange-boxer animation diagnostic should show:

- `Orange: guard 1/3`
- `Orange: guard 2/3`
- `Orange: guard 3/3`

When the guard is fully raised, hold frame 3 and show `Guard: ACTIVE`.

Do not confuse the selected Guard toggle with effective blocking status.

## 11. Pause and frame stepping

Guard animation must use the existing scene animation clock.

Requirements:

- Pause freezes guard-entry animation.
- Guard must not become effective while scene time is frozen.
- Resume continues the animation.
- Frame stepping advances guard-entry frames according to existing timing rules.
- Punch contact resolution remains exactly once per punch.
- No duplicate BLOCK events occur.

Do not introduce independent timers.

## 12. Reset and recovery interactions

**Reset Health**

When Reset Health is pressed:

- Restore both fighters to 100 health.
- Restore standing combat states.
- Clear guard state.
- Cancel guard animation.
- Return orange boxer to idle.
- Preserve fighter positions and existing counters.
- Re-enable Jab and Cross.

**Rise**

After the orange boxer completes Rise:

- Restore health and standing state according to Task 6D.
- Return to idle.
- Leave guard OFF.
- Require a new Guard activation.

Guard must never automatically reactivate following knockdown recovery.

## 13. Validation

Test the following scenarios:

| Scenario | Expected result |
|---|---|
| Guard OFF, Jab connects | HIT, 5 damage |
| Guard OFF, Cross connects | HIT, 10 damage |
| Guard ACTIVE, Jab connects | BLOCK, 0 damage |
| Guard ACTIVE, Cross connects | BLOCK, 0 damage |
| Guard ACTIVE, punch out of range | MISS |
| Punch during guard entry | HIT, normal damage |
| Guard toggled OFF | Returns to idle |
| Guard held through multiple blocks | Remains active |
| Reset while guarding | Guard clears |
| Defeat | Guard unavailable |
| Rise completes | Guard OFF |
| Pause during guard entry | Entry freezes |

Additional acceptance checks:

- [ ] Guard animation plays three frames once.
- [ ] Final guard frame remains held.
- [ ] Guard becomes effective only after entry completes.
- [ ] Guard deactivates immediately when toggled off.
- [ ] Blocked punches cause zero damage.
- [ ] Blocked punches do not trigger hit reactions.
- [ ] Misses remain misses while guarding.
- [ ] Counters satisfy `J + C = H + B + M`.
- [ ] Each punch generates only one contact outcome.
- [ ] Guard state clears on defeat and reset.
- [ ] Existing punch, movement, knockdown, and Rise behavior remains functional.
- [ ] No AI, stamina, guard-break, chip damage, or scoring is introduced.

## 14. Deliverables

Provide:

1. Updated Swift source files.
2. Integrated orange guard animation.
3. Guard toggle control.
4. Defensive-state implementation.
5. HIT/BLOCK/MISS classification.
6. Updated debug counters and guard diagnostics.
7. Device or simulator validation results.
8. Any remaining limitations.

## Completion criterion

The orange boxer can manually enter and hold guard.

Jab and Cross punches that connect against an active guard register BLOCK and cause no damage.

Punches outside range register MISS, while punches against an unguarded opponent register HIT and apply normal damage.

The guard animation, counters, reset behavior, and existing combat systems remain consistent.

## Task 7A implementation report

User approved creation of three missing guard frames. Integrated guard_b_0...2 image sets, matching source PNG/SVGs, generate_guard.py, guard_manifest.json and mirrored review previews. Existing named boxer rig groups retain original limb lengths, orange palette, 512x512 canvas/root(256,448), fixed lower-body pixels and baseline448. The contact sheet was visually inspected: gloves lift beside the head. No runtime root/scale/facing offsets or changes to target geometry were introduced.

Updated existing Swift files only: HitReactionPlayback.swift, PunchContact.swift, IdleTestScene.swift, ContentView.swift. No new Swift target membership is needed. Build label7A. Copy all three image sets when updating the Mac project.

### Guard and contact behavior

FighterDefenseState stores unguarded/guarding separately from FighterCombatState. GuardPlayback uses the existing scene clock, with three40ms entry intervals and indefinite final-frame hold. Timing interpretation: frames1/2/3 start at0/40/80ms; effective protection begins at120ms, after the full entry duration completes. Until120ms the status remains RAISING even while frame3 is visible. This honors the specified120ms entry and the acceptance criterion that protection follows entry completion.

The top debug strip adds Guard beside Rise and Reset Health. Selected state is highlighted, while Guides separately show OFF/RAISING/ACTIVE. The toggle is available only with loaded guard assets, app focus, standing orange, no active reaction and no fall/down/rise playback. Toggle-off immediately cancels protection and resets idle phase. Paused activation presents frame1 and freezes until Resume or explicit Step.

PunchContactTracker retains one evaluation per accepted punch. It first evaluates the unchanged spatial circle/target intersection. No overlap yields MISS regardless of guard; overlap yields BLOCK only if protection is effective, otherwise HIT. The new B counter increments only for BLOCK. J+C=H+B+M. Blue contact circles/distance overlays use blue for BLOCK, green for HIT and red for MISS. Block does not also increment HIT.

The health handler and reaction model already accept HIT only, so BLOCK causes zero damage and no new recoil; held guard remains selected. An entry HIT cancels guard before the existing reaction begins, preventing stale protection from activating afterward. Final HIT/defeat still follows recoil/fall/down. Reset, scene removal and Rise completion clear guard explicitly; another activation is required. Defeated contacts remain rejected before counters. No timers or completion callbacks were introduced.

Health, positions, scales, facing, movement/input safeguards, punch timings, knockdown and Rise remain unchanged. The added toggle and B counter make the existing debug layout denser; iPhone SE landscape readability must still be checked on device.

### Validation

PASS: python Tests/validate_task7a.py checks all three integrated RGBA assets, baseline, fixed lower body, rigid arm lengths, defense-state/clock wiring, spatial-first classification, outcome counter branches, guard interruption/reset/recovery, a single orange diagnostic block and balanced runtime Swift brace counts.
PASS: validate_task6d.py, validate_task6c.py, validate_task6b.py, validate_task6a.py, validate_task5c.py, validate_task5b.py and validate_task5a1.py source/asset/numerical regressions. Historical build-label assertions now accept7A.

Added Tests/GuardChecks.swift for120ms entry, final hold, toggle-off, stepping, cancellation without stale activation, Jab/Cross BLOCK with zero damage/recoil, out-of-range MISS despite active guard, repeated-marker suppression, 2J+2C=1H+2B+1M, and an entry HIT clearing defense. These Swift behavioral tests have NOT run on Windows: swiftc/Xcode/SpriteKit are unavailable. Brace/source checks do not replace compiler or device validation.

On Mac:

```sh
swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Boxer0/HitReactionPlayback.swift Tests/GuardChecks.swift -o /tmp/guard-checks
/tmp/guard-checks
```

Pending iPhone SE checks: confirm7A; Guard OFF close Jab/Cross HIT for5/10 damage; Guard ACTIVE close Jab/Cross BLOCK with unchanged health and guard pose; retreat and punch for MISS; pause and step Guard to verify three entry intervals and no spontaneous protection; time a punch during entry for HIT/cancel/recoil; toggle off, Reset while raising/active, defeat and Rise to verify OFF afterward. Check counters/invariant, repeated taps/contacts and landscape top-strip/bottom-control readability.

No opponent AI, chip damage, block recoil, guard break, stamina or scoring were added.
