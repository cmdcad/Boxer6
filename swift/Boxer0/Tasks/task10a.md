# Boxer0 — Task 10A: Boxing Footwork and Defensive Movement

**Milestone:** 10A  
**Platform:** iPhone landscape  
**Frameworks:** Swift, SpriteKit, SwiftUI  
**Scope:** Guarded movement, defensive positioning, movement-state integration, and regression testing  
**Status:** Ready for implementation

## 1. Objective

Allow both fighters to advance and retreat while maintaining an effective guard.

The blue boxer should be able to hold Guard while using the existing Advance and Retreat controls.

The orange CPU boxer should be able to reposition defensively while its autonomous guard is raised.

The implementation must:

- Preserve the existing guard protection rules.
- Introduce slower movement while guarding.
- Maintain correct defensive animations.
- Preserve fighter boundaries and separation.
- Avoid animation conflicts.
- Preserve punch recovery and vulnerability behavior.
- Integrate with existing CPU distance management.
- Extend the automated tests introduced in Task 9C.

Do not introduce sidestepping, circling, dodging, stamina, new punches, or new damage rules.

## 2. Inspect the existing architecture

Before implementation, inspect the latest project source and identify:

1. Player Advance and Retreat input handling.
2. Existing acceleration and deceleration.
3. CPU movement decisions from Task 8B.
4. Player hold-to-guard implementation.
5. CPU autonomous guard behavior.
6. Guard-entry animation and protection timing.
7. Existing movement and idle animation selection.
8. Action arbitration from Task 9A.
9. Recovery and vulnerability classification.
10. Existing XCTest infrastructure.

Reuse the established movement system.

Do not create an independent guarded-movement engine.

## 3. Guarded movement behavior

Both fighters may move while their guard is fully raised.

Supported actions:

- Guarded advance.
- Guarded retreat.
- Guarded hold.

The boxer must retain its effective guard throughout these movements unless an existing higher-priority event interrupts it.

**Guarded movement is a movement modifier, not a new combat state.**

Continue deriving protection from the established guard state.

Movement alone must not grant or remove protection.

## 4. Movement speed

Introduce a configurable defensive movement multiplier.

Recommended initial value:

`guardedMovementMultiplier = 0.55`

This means guarded movement uses approximately 55% of the fighter's normal movement speed.

Example:

| Movement | Illustrative speed |
|---|---:|
| Normal advance | 65 points/sec |
| Guarded advance | 35.75 points/sec |
| Normal retreat | 65 points/sec |
| Guarded retreat | 35.75 points/sec |

Use actual movement speeds from the current implementation rather than assuming 65 points/sec.

The multiplier must apply consistently to both fighters unless the existing design already defines different base movement speeds.

Do not change normal movement speed.

## 5. Acceleration and deceleration

Preserve the existing smooth movement behavior.

When Guard becomes effective:

- Transition toward guarded movement speed.
- Do not instantly snap velocity to the new limit.
- Preserve movement direction where appropriate.

When Guard is released:

- Return toward normal movement speed smoothly.
- Do not teleport or produce a sudden velocity jump.

Reuse the existing acceleration and deceleration mechanisms.

The boxer must not exceed the appropriate movement-speed limit after the transition settles.

## 6. Guard-entry movement

Preserve the established 120 ms guard-entry animation.

Initial policy:

- Guard entry begins when the fighter is eligible.
- Existing movement decelerates toward a stop during guard entry.
- Guard remains ineffective until the full 120 ms completes.
- Once guard is effective, guarded movement becomes available.

Do not allow full-speed movement during guard entry.

Do not allow movement to accelerate guard activation.

If Guard is released before entry completes, cancel the pending activation according to existing rules.

## 7. Blue player controls

Preserve hold-to-guard behavior.

Expected combinations:

| Input | Expected behavior |
|---|---|
| Advance only | Normal advance |
| Retreat only | Normal retreat |
| Guard only | Stationary guard |
| Guard + Advance | Guarded advance |
| Guard + Retreat | Guarded retreat |
| Release Advance while guarding | Stationary guard |
| Release Retreat while guarding | Stationary guard |
| Release Guard while moving | Normal movement resumes |

Support simultaneous touch input on the existing controls.

A player should not have to release and press Advance again after activating or releasing Guard.

Preserve the existing behavior when both movement directions are held simultaneously.

Do not change Jab or Cross button behavior.

## 8. Guarded movement animations

The current sprite assets contain:

- Idle.
- Advance.
- Retreat.
- Guard.

They may not contain dedicated guarded-walking animations.

Therefore, use a staged implementation.

### Stage A — Existing assets

Use the established guard pose while translating the fighter root through the normal movement system.

The fighter should visibly maintain its gloves in the defensive position.

Do not switch to ordinary advance or retreat sprites if doing so visually lowers the gloves while the game still considers guard effective.

Maintain the correct root, baseline, scale, and facing direction.

### Stage B — Optional dedicated sprites

If the stationary guard pose sliding across the ring looks unnatural, report the visual limitation.

Do not automatically create replacement artwork.

A later sprite task may introduce:

- `guard_advance`
- `guard_retreat`

These should use the established Boxer0 sprite specification.

Do not modify the current sprite contract without approval.

## 9. Orange CPU defensive footwork

Extend Task 8B's distance-management behavior.

When the CPU guard is fully raised, it may:

- Advance cautiously if too far.
- Retreat cautiously if too close.
- Hold position within its preferred distance band.

Use the existing movement intentions:

- `advance`
- `retreat`
- `hold`

Do not introduce a second movement-decision controller.

Guarded movement should use the same distance thresholds as normal CPU movement.

The CPU must not begin an attack while guard remains raised.

Do not modify CPU guard probabilities or reaction delays.

## 10. CPU guard and movement arbitration

Update the existing arbitration policy to allow movement under effective guard.

Conceptual priority:

1. Defeat, knockdown, down, Rise.
2. Hit reaction.
3. Active punch.
4. Punch recovery.
5. Block reaction.
6. Guard entry.
7. Raised guard with optional guarded movement.
8. Normal movement.
9. Idle.

The raised-guard state must no longer imply complete immobility.

However, guard entry and block reaction should retain their existing restrictions.

If a block occurs during guarded movement:

- Stop or decelerate movement for the block reaction.
- Display the existing block response.
- Preserve guard protection as established.
- Resume guarded movement afterward if still eligible.

Do not allow movement animation to overwrite the block reaction.

## 11. Contact and damage

Preserve the existing spatial contact system.

Guarded movement changes the defender's actual position before the contact marker.

At contact time:

- Outside range → MISS.
- Inside range with effective guard → BLOCK.
- Inside range without effective guard → HIT.

Guarded movement must not:

- Enlarge the defensive hitbox.
- Increase punch reach.
- Automatically block out-of-range punches.
- Reduce damage from an actual HIT.
- Create additional contact evaluations.

The established Jab and Cross damage values remain unchanged.

## 12. Recovery and counterpunching

Preserve Tasks 9A and 9B.

A boxer cannot use guarded movement to bypass physical recovery.

While attacking or recovering:

- Guard entry remains restricted.
- Effective guard cannot activate early.
- Movement follows the established action restrictions.

A fighter remains attack-vulnerable during its normal punch and recovery periods.

Guarded movement does not introduce new counterpunch vulnerability rules.

Counterpunch detection must continue using the existing attack and recovery states.

## 13. Fighter boundaries and separation

Reuse the existing ring boundaries.

Guarded movement must not allow a fighter to:

- Leave the ring.
- Cross through the opponent.
- Overlap fighter roots.
- Ignore minimum separation.
- Teleport when switching movement modes.

If the CPU reaches a boundary while retreating under guard, it should hold position.

Do not introduce new collision geometry.

## 14. CPU ON/OFF behavior

**CPU ON**

- Autonomous movement remains active.
- Autonomous guarding remains active.
- Guarded movement is permitted.
- CPU offense remains subject to existing attack eligibility.

**CPU OFF**

- Autonomous movement stops.
- Autonomous guard decisions stop.
- Pending CPU movement intentions are cleared.
- Existing manual controls remain available.

Do not leave stale guarded movement active after switching CPU OFF.

## 15. Reset, defeat, and Rise

**Reset Health**

- Clear pending guarded-movement transitions.
- Clear stale held-input state according to existing reset behavior.
- Restore normal movement eligibility.
- Preserve established fighter positions and health reset rules.

**Defeat**

- Stop guarded movement.
- Remove guard effectiveness.
- Play the existing hit reaction and knockdown.
- Hold the down pose.

**Rise**

- No guarded movement during Rise.
- Do not restore stale held Guard input.
- Resume ordinary movement eligibility after Rise completes.

Preserve CPU mode behavior.

## 16. Pause and frame stepping

Use the existing scene simulation clock.

Verify:

- Guarded movement freezes during pause.
- Guard-entry timing freezes during pause.
- Movement resumes smoothly.
- Frame stepping advances movement consistently.
- No accumulated movement jump occurs after resume.
- No stale movement callback changes state after Reset.

Do not use wall-clock movement timers.

## 17. Debug diagnostics

Extend the existing debug overlay.

Suggested values:

- `Blue Move: GUARDED ADVANCE`
- `Blue Move: GUARDED RETREAT`
- `Blue Move: GUARDED HOLD`
- `Orange Move: GUARDED ADVANCE`
- `Orange Move: GUARDED RETREAT`

Optionally display:

- Current movement speed.
- Guarded movement multiplier.
- Effective guard state.

Keep the diagnostics compact.

## 18. Automated validation

Extend the existing `Boxer0Tests` XCTest suite.

Suggested new group:

`GuardedMovementTests`

Required tests:

1. Guarded movement uses the configured speed multiplier.
2. Normal movement speed remains unchanged.
3. Guard entry does not provide early protection.
4. Guarded movement becomes available after guard entry.
5. Guard release restores normal movement eligibility.
6. Held movement input survives guard transitions.
7. Both fighters obey ring boundaries.
8. Fighter separation constraints remain valid.
9. Guarded movement can change contact outcome.
10. A successful block during movement causes zero damage.
11. Block reaction temporarily overrides movement.
12. Movement resumes appropriately after block reaction.
13. Recovery prevents premature guard activation.
14. Defeat and Rise clear incompatible movement.
15. CPU OFF stops autonomous guarded movement.
16. Pause and frame stepping preserve correct movement.

Tests must use production movement and combat logic.

Do not create separate test-only movement calculations.

## 19. Regression requirements

Run the complete existing XCTest suite after implementation.

The previous baseline is:

**24 tests passed, 0 failures.**

All existing tests must continue passing.

Report the new total test count.

If a previous test needs updating because the intended guard-movement policy has changed, explain the modification.

Do not delete tests merely to achieve a passing result.

## 20. Manual iPhone validation

Test the following:

| Scenario | Expected behavior |
|---|---|
| Hold Guard + Advance | Blue moves forward slowly while guarded |
| Hold Guard + Retreat | Blue moves backward slowly while guarded |
| Release movement | Blue remains guarded and stationary |
| Release Guard while advancing | Blue returns to normal movement |
| CPU raises guard while moving | Smooth transition to guarded movement |
| CPU retreats under guard | Slower defensive retreat |
| CPU blocks while moving | Visible block reaction |
| Blue blocks while moving | Zero damage |
| Blue throws punch after guard release | Existing attack rules apply |
| Blue is hit during guard entry | Normal HIT |
| Blue is knocked down | Movement stops |
| Pause during guarded movement | Position freezes |
| CPU OFF | Autonomous movement stops |

## 21. Acceptance criteria

- [ ] Blue can advance while holding Guard.
- [ ] Blue can retreat while holding Guard.
- [ ] Orange can reposition while guarding.
- [ ] Guarded movement is slower than normal movement.
- [ ] Acceleration and deceleration remain smooth.
- [ ] Guard entry remains 120 ms.
- [ ] Guard effectiveness remains unchanged.
- [ ] Guarded movement does not interrupt guard animation incorrectly.
- [ ] Block reaction remains visible.
- [ ] Movement does not bypass punch recovery.
- [ ] Spatial contact remains authoritative.
- [ ] Ring boundaries and fighter separation remain correct.
- [ ] CPU offense and defense remain functional.
- [ ] Pause, Reset, defeat, and Rise remain correct.
- [ ] Existing automated tests still pass.
- [ ] New guarded-movement tests pass.
- [ ] No new gameplay mechanics outside this milestone.

## 22. Deliverables

Provide:

1. Swift files modified.
2. Guarded-movement integration details.
3. Movement-speed configuration.
4. Animation selection changes.
5. CPU defensive footwork changes.
6. New XCTest files and test results.
7. Full regression-suite results.
8. iPhone validation observations.
9. Any remaining visual limitations.

## Completion criterion

Both fighters can advance and retreat while maintaining an effective guard.

Guarded movement is slower than ordinary movement, respects the established combat restrictions, and interacts correctly with contact detection and block reactions.

The CPU can reposition defensively without losing its existing offensive or defensive intelligence.

All previously accepted mechanics remain functional, and automated regression tests pass.

---

## Implementation report — 10A

### Swift changes

- Boxer0/FootworkMotion.swift: existing analytic movement integrator accepts an optional speedMultiplier (default 1). Reducing an active speed limit uses the existing deceleration rate toward the new target rather than clamping velocity. Releasing Guard returns toward the normal target through existing acceleration. No separate movement integrator exists.
- Boxer0/IdleTestScene.swift: guardedMovementMultiplier = 0.55, applied only when the corresponding established guard is effective. Blue base 100 points/sec -> guarded 55; orange base 65 -> guarded 35.75. Normal base speeds, acceleration/deceleration, collision geometry, distance thresholds, guard timing and AI probabilities are unchanged. Multiplier is constrained to 0...1 by the integrator.
- Blue retains held directions through guard entry/release; entry brakes toward zero while protection remains ineffective. Raised guard permits ordinary direction arbitration at reduced speed. Holding both directions preserves the existing zero-direction/braking policy.
- Orange reuses CPUDistanceController and FootworkMotion under raised guard. Guard entry now brakes the existing velocity rather than abruptly clearing it. Existing guard animation stays visually above locomotion. CPU attack eligibility continues to reject selected guard. CPU OFF still clears movement intentions and velocity.
- Confirmed BLOCK stops the defender's movement immediately. Existing recoil takes priority and temporarily prevents translation. Still-held blue movement or current CPU intentions resume after recoil if eligible. Guard protection and zero BLOCK damage remain unchanged.
- Frame stepping now calls the same production advanceSimulation path as normal rendering, with an explicit paused-step flag. Pause freezes simulation and retains physically held directions and velocity; release/cancellation, inactive lifecycle, Reset and defeat retain their existing input-clearing behavior. Resume resets the render timestamp to prevent accumulated movement jumps.
- Simulation intervals crossing an existing punch contact marker are subdivided at that marker. Thus moving targets are evaluated at the contact position rather than after the remainder of the render tick. No reach, hitbox, damage, contact count, counter rule or animation duration is changed.
- Boxer0/ContentView.swift: build 10A and compact per-fighter movement labels (GUARDED ADVANCE/RETREAT/HOLD). No gameplay controls were replaced.

### Presentation

Stage A only: existing final guard textures remain displayed while roots move. Root, baseline, scale, facing and guard effectiveness are preserved. Ordinary walk textures do not visually lower gloves under effective guard. The planted guard feet will appear to slide across the ring; this is the explicitly permitted temporary limitation. No guard_advance/guard_retreat artwork has been created. Dedicated guarded-footwork artwork requires a separate approved task if device review finds the sliding unacceptable.

### Tests and regression status

Boxer0Tests/CombatTests.swift adds GuardedMovementTests with 16 methods: speed modifier and smooth limit reduction, unchanged blue speed, entry timing and availability, held input across entry/release, retreat/opposite inputs, release-to-hold, boundaries/separation, CPU advance/retreat, moving out of contact, block zero-damage/stop/resume, recovery restriction, CPU OFF, pause/step/resume, Reset and alternate multiplier. The existing defeat/Rise scene test is extended to reject held movement while defeated and verify no root translation during Rise.

Total: 40 XCTest methods (previous 24 retained, 16 added). No old XCTest assertion was removed for the raised-guard movement policy. Historical Python 8D source checks were updated because they explicitly required raised guard to stop motion; they now require guard-entry braking, reduced guarded speed and stopping on BLOCK. Build-label assertions in earlier validators now expect 10A. Source assertions are not behavioral XCTest results.

Executed here: python Tests/validate_task10a.py, which runs project/scheme/source checks, the 9A/9B/9B.1/8A/8B/8C/8D checks and recovery-asset checks. All pass after the intended policy/source-label updates. Swift compiler/Xcode/Apple SDK are unavailable on this Windows host. Swift compilation and the complete 40-test XCTest run are NOT RUN here. The user's previously supplied Xcode result remains a confirmed baseline of 24 passed, zero failures before this change; it does not establish the new suite result.

On Mac: select shared Boxer0 scheme and an installed iPhone simulator, then Product > Test (Command-U). Run the whole suite, not only GuardedMovementTests. Record the new execution transcript before marking automated acceptance complete.

Manual iPhone observations: NOT RUN. Confirm simultaneous Guard+Advance/Retreat, release-to-hold, normal-speed return, CPU guarded repositioning, block recoil/zero damage, guard-entry HIT, defeat/Rise, ring limits, pause/resume and CPU OFF. Judge guard-pose sliding and whether movement/recoil labels remain readable on iPhone SE. No claim of full device or XCTest acceptance is made until those results are available.
