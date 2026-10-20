# Boxer0 — Task 9B.1: Visible Punch Recovery

**Milestone:** 9B.1  
**Platform:** iPhone landscape  
**Frameworks:** SpriteKit and SwiftUI  
**Scope:** Recovery poses, animation transitions, and recovery diagnostics  
**Status:** Ready for implementation

## 1. Objective

Make the existing Jab and Cross recovery periods visually distinguishable from the ready/idle stance.

Both blue and orange fighters must display a recognizable recovery posture after completing a punch.

The visual state must match the actual physical recovery state established in Task 9A.

This is a presentation and diagnostic refinement. Do not change combat rules.

## 2. Inspect existing implementation

Before making changes:

1. Inspect the latest sprite assets and animation-loading system.
2. Locate Jab and Cross animation completion handling.
3. Identify how recovery timing is represented.
4. Identify existing idle and guard animation transitions.
5. Inspect action-priority and animation-interruption handling.
6. Check the existing debug overlay.

Determine whether existing animation frames can provide acceptable temporary recovery poses.

Do not assume new sprite assets are already available.

## 3. Required visual sequence

### Jab

1. Play the existing six-frame Jab animation over 300 ms.
2. Display a distinct Jab recovery posture for 120 ms.
3. Return to idle or the next eligible action.

### Cross

1. Play the existing eight-frame Cross animation over 480 ms.
2. Display a distinct Cross recovery posture for 220 ms.
3. Return to idle or the next eligible action.

The recovery pose must remain visible for the entire applicable recovery period unless interrupted by a higher-priority action.

Do not shorten or extend the actual recovery duration.

## 4. Recovery pose design

The desired appearance is:

**Jab recovery**
- Lead arm partially extended or retracting.
- Lead shoulder slightly forward.
- Guard not fully restored.
- Feet remain planted on the existing baseline.

**Cross recovery**
- Rear shoulder and torso remain slightly rotated.
- Rear glove is returning toward the face.
- Body appears temporarily committed or off-balance.
- Feet remain planted on the existing baseline.

Both poses should be visibly different from the ordinary idle stance.

The Cross recovery pose should communicate a greater commitment than the Jab recovery pose.

## 5. Asset implementation strategy

Use a two-stage approach.

### Stage A — Existing assets

Inspect the current Jab and Cross frames.

If suitable frames already exist, reuse them as temporary recovery poses.

Prefer frames that visually suggest the arm retracting.

Avoid using a fully extended contact frame as the recovery pose.

If no suitable existing frame is available, report that limitation and proceed with the debug indicator.

Do not distort, rotate, or translate the entire fighter sprite to simulate recovery.

### Stage B — Dedicated recovery sprites

If existing frames are insufficient, prepare a small follow-up asset request.

Recommended initial assets:

- `jab_recovery` — one frame per boxer.
- `cross_recovery` — one frame per boxer.

Follow the established Boxer0 sprite contract:

- 512 × 512 pixels.
- Transparent RGBA.
- Shared root position `(256, 448)`.
- Identical fighter scale and baseline.
- Original blue and orange color palettes.
- Artwork faces right; preserve the established runtime mirroring for orange.

Do not generate or substitute unrelated boxer artwork.

Do not block Stage A or diagnostic implementation while waiting for new sprites.

## 6. Recovery animation integration

When the punch animation finishes:

1. Enter the existing recovery state.
2. Select the correct recovery pose.
3. Display the pose without changing the fighter's root position.
4. Maintain it while recovery remains active.
5. Return to idle or another eligible state when recovery completes.

The visual recovery pose must be driven by the existing recovery state.

Do not create a second independent recovery timer.

Avoid restarting the recovery pose on every frame update.

## 7. Action priority

Preserve the existing combat-state arbitration.

Higher-priority events must be able to replace the recovery pose.

Examples:

- A successful incoming HIT triggers the normal hit reaction.
- A knockout triggers the existing knockdown sequence.
- Reset clears recovery and restores the correct pose.
- Rise does not restore a stale recovery pose.

Guard entry must not visually or mechanically bypass punch recovery.

Movement must not overwrite the recovery pose while the fighter is still recovering.

## 8. Recovery diagnostics

Add a compact per-fighter debug readout.

Examples:

`BLUE: RECOVERING JAB — 80 ms`

`ORANGE: RECOVERING CROSS — 160 ms`

`BLUE: READY`

Requirements:

- Show the current action/recovery phase.
- Show remaining recovery time when applicable.
- Use the existing scene simulation clock.
- Freeze the displayed countdown during pause.
- Update correctly during frame stepping.
- Return to READY only when the fighter is genuinely eligible.

If another action restriction prevents readiness, display the appropriate actual state instead of incorrectly showing READY.

## 9. Preserve existing combat mechanics

Do not change:

- Jab animation: 300 ms.
- Cross animation: 480 ms.
- Jab contact marker: 150 ms.
- Cross contact marker: 240 ms.
- Jab additional recovery: 120 ms.
- Cross additional recovery: 220 ms.
- Jab damage: 5.
- Cross damage: 10.
- Guard entry: 120 ms.
- CPU attack preparation or cooldown values.
- CPU defensive probabilities.
- Counterpunch classification.
- Spatial contact detection.
- Fighter movement and distance management.

Do not introduce new damage, vulnerability, or recovery rules.

## 10. Validation

| Test | Expected result |
|---|---|
| Blue throws Jab | Distinct Jab recovery posture |
| Blue throws Cross | Distinct Cross recovery posture |
| Orange throws Jab | Same behavior for orange |
| Orange throws Cross | Same behavior for orange |
| Jab animation finishes | Recovery pose lasts 120 ms |
| Cross animation finishes | Recovery pose lasts 220 ms |
| Guard held during recovery | Guard waits until recovery ends |
| Fighter hit during recovery | Hit reaction takes priority |
| Fighter defeated | No stale recovery pose |
| Movement held during recovery | Movement resumes afterward |
| Pause during recovery | Pose and countdown freeze |
| Reset during recovery | Returns to valid standing state |
| Rise completes | No old recovery pose reappears |
| Extended combat exchange | No animation flicker or snapping |

## 11. Acceptance criteria

- [ ] Recovery is visually distinguishable from idle.
- [ ] Jab and Cross have distinguishable recovery postures.
- [ ] Both fighters use the same recovery presentation rules.
- [ ] Recovery visuals match the existing recovery timing.
- [ ] No sprite-root movement or foot sliding.
- [ ] Hit reactions and knockdowns correctly override recovery.
- [ ] Guard and movement do not bypass recovery.
- [ ] Debug countdown accurately reflects recovery.
- [ ] Pause, Reset, and Rise remain correct.
- [ ] No regression in HIT/BLOCK/MISS or counterpunch tracking.

If suitable recovery artwork is unavailable, complete the diagnostics and report visual acceptance as pending rather than claiming the full task is finished.

## 12. Deliverables

Provide:

1. Swift files modified.
2. Recovery frames selected or added.
3. Description of recovery-pose integration.
4. Debug countdown implementation.
5. Validation results.
6. Any additional sprite assets required.

## Completion criterion

After throwing a Jab or Cross, either fighter visibly enters the appropriate recovery posture and remains there until its existing recovery period ends.

The recovery state is also observable through the debug overlay.

The fighter returns to its normal ready stance only when eligible, with no changes to combat timing, damage, or existing gameplay mechanics.

---

## Implementation report

Build label: 9B.1. Implemented Stage A using existing approved artwork; no new assets generated.

Swift files modified:
- Boxer0/JabPlayback.swift: shared PunchKind.recoveryPoseFrame selects Jab index 4 (frame 5, withdrawal) and Cross index 5 (frame 6, withdrawal). PunchRecovery.diagnosticLabel derives remaining milliseconds directly from its existing remaining value, rounded upward to avoid displaying zero while locked.
- Boxer0/IdleTestScene.swift: both texture branches hold the selected pose only while the corresponding PunchRecovery.isRecovering is true. Hit reaction, knockdown/down/Rise and block response retain higher visual priority. Guard and locomotion remain below recovery. Orange frame diagnostics identify the actual selected source frame. Action diagnostics report countdown, guard, inactive/pause, opponent down, CPU preparation/cooldown/defense restrictions, unavailable assets and CPU OFF rather than false READY.
- Boxer0/ContentView.swift: build label and separate compact Blue Action / Orange Action lines (nine children in the existing combat readout, compatible with older SwiftUI ViewBuilder limits).

Countdown publishing uses the existing scene action-label change detection. Reading the label has no side effects. Pause advances neither physical clock nor countdown; frame stepping uses the existing common simulation duration. No second timer, SKAction, root translation, scale change or new combat state was introduced. Existing 300/480 ms punches, 120/220 ms physical recovery, contact markers, damage, guard delay, AI settings and counters are unchanged.

Asset review: inspected Jab and Cross contact sheets. Jab withdrawal has the lead shoulder forward and arm bent back toward guard; Cross withdrawal retains 85% of the generator's torso turn with rear glove withdrawing and lead glove high. Both differ from idle/contact, and the lower-body pixels from y=300 through 511 are identical to their ready frames for both palettes. Integrated imageset PNGs match source PNGs. Runtime orange mirroring is unchanged.

Validation: python Tests/validate_task9b1.py passes source/asset checks plus the existing 9A, 9B, 8C and 8D validators. Tests/RecoveryChecks.swift adds checks for selected non-contact withdrawal indices, initial/stepped countdown, side-effect-free paused reads and reset. Executable Swift checks were skipped because swiftc/Xcode are unavailable on this Windows host. No simulator/iPhone validation claimed.

Remaining validation: on iPhone at ordinary speed, confirm both colors' 120/220 ms pose holds, pause/step countdown, HIT/defeat overrides, held Guard and movement after recovery, Reset/Rise cleanup and extended exchanges. Reused frames are static holds. The existing punch ends in guard before switching back to withdrawal; this can produce a visible pose transition. Its naturalness and readability require device review. Dedicated jab_recovery/cross_recovery artwork is not currently required for Stage A; if that transition proves objectionable, request the four purpose-built poses as Stage B before creating them.
