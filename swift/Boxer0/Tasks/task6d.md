# Boxer0 — Task 6D: Manual Knockdown Recovery

## 1. Objective

Implement a manual knockdown-recovery mechanism using the existing eight-frame `rise` animation.

When the orange boxer is down, pressing a debug **Rise** button should play the recovery animation once and restore the boxer to a standing, combat-eligible state.

Preserve all functionality completed through Task 6C.

Do not introduce referee counts, automatic recovery, stamina, scoring, or match outcomes.

## 2. Required animation

Use the existing sprite specification.

| Animation | Frames | Duration |
|---|---:|---:|
| `knockdown` | 8 | 640 ms |
| `down` | 1 | Held |
| `rise` | 8 | 800 ms |
| `idle` | 4 | Existing timing |

The `rise` animation must:

- Play eight frames in order.
- Last approximately 800 ms.
- Play once, without looping.
- Transition smoothly into idle.
- Preserve the existing fighter scale, facing direction, root position, and baseline.

Verify that the orange `rise` assets exist before implementation. Report missing frames rather than substituting unrelated artwork.

## 3. Rise button

Add a debug button labeled `Rise` near the existing Reset Health control.

Button behavior:

- Enabled only when the orange boxer is in the static `down` pose.
- Disabled while standing.
- Disabled during `hit_react`, `knockdown`, or `rise`.
- Pressing it starts the recovery animation immediately.
- Repeated taps must not restart or queue the animation.

Keep the button visually consistent with the existing debug controls.

Do not add a new menu or redesign the interface.

## 4. Recovery sequence

The expected flow is:

`Standing → Defeated → Hit Reaction → Knockdown → Down → Rise → Standing`

When Rise is pressed:

1. Verify that the orange boxer is defeated and currently down.
2. Start the eight-frame `rise` animation.
3. Keep the boxer combat-ineligible throughout recovery.
4. After the final frame, restore the standing combat state.
5. Resume the orange boxer's idle animation.
6. Re-enable Jab and Cross.

The boxer must not become attackable midway through the rise animation.

## 5. Health restoration

For this debug milestone, Rise should restore the orange boxer's health to **100/100 only when recovery completes**.

This is a temporary testing rule, not a permanent boxing mechanic.

During the rise animation:

- Health remains at zero.
- Combat state remains defeated.
- Punch controls remain disabled.

Upon completion:

- Health becomes 100.
- Combat state becomes standing.
- Punch controls become enabled.

Do not gradually restore health during the animation.

Keep this debug recovery separate from the existing Reset Health function so a future recovery-health policy can replace it without changing animation playback.

## 6. Animation and combat states

Keep combat eligibility separate from visual animation.

Combat states:

- `standing`
- `defeated`

Orange animation states:

- `idle`
- `hit_react`
- `knockdown`
- `down`
- `rise`

During `rise`, the boxer remains combat-state `defeated`.

Only after recovery completes does the boxer become `standing`.

Avoid introducing unnecessary additional combat states.

## 7. Position and alignment

The orange boxer must recover at its existing root position.

Requirements:

- No horizontal movement.
- No change to sprite scale.
- No facing-direction changes.
- No arbitrary vertical offsets.
- No change to the blue boxer's position.
- No modification to punch-contact geometry.

The final rise frame should transition naturally into the existing idle pose.

If the artwork produces a visible jump, report the alignment issue rather than compensating with unexplained offsets.

## 8. Reset Health interaction

Reset Health remains available throughout recovery.

If Reset Health is pressed during `rise`:

- Cancel the recovery animation.
- Restore both fighters to 100 health.
- Restore standing combat states.
- Return the orange boxer to idle.
- Re-enable Jab and Cross.
- Preserve fighter positions and counters.

Any pending rise-completion callback must be invalidated.

Reset must not allow an old animation event to modify the newly restored state.

## 9. Debug diagnostics

Preserve existing counters, health bars, and state indicators.

During recovery, display:

- `Orange: rise 1/8`
- `Orange: rise 2/8`
- …
- `Orange: rise 8/8`

After completion:

- `Orange: idle`
- `Orange: standing`
- Health: `100/100`

The DEFEATED indicator should remain visible until recovery finishes.

## 10. Pause and frame stepping

Use the existing scene animation clock.

- Pause freezes the current rise frame.
- Resume continues from the same point.
- Frame stepping follows the existing playback rules.
- Rise cannot complete while scene time is paused unless deliberately advanced through the existing stepping mechanism.
- Repeated Rise input cannot duplicate completion events.

Do not introduce an independent timer.

## 11. Validation

| Test | Expected result |
|---|---|
| Orange standing | Rise disabled |
| Orange in hit reaction | Rise disabled |
| Orange falling | Rise disabled |
| Orange down | Rise enabled |
| Press Rise | Eight-frame recovery begins |
| Repeated Rise taps | No restart or queue |
| During Rise | Health 0, combat disabled |
| Rise completes | Health 100, standing, idle |
| Pause during Rise | Animation freezes |
| Resume | Animation continues |
| Reset during Rise | Immediate standing restoration |
| Knock down again after Rise | Full defeat sequence works again |

Additional checks:

- [ ] All eight rise frames play in order.
- [ ] Total playback is approximately 800 ms.
- [ ] Boxer remains at the same root position.
- [ ] Final frame transitions smoothly to idle.
- [ ] Jab and Cross remain disabled until recovery completes.
- [ ] Existing contact counters remain unchanged by Rise.
- [ ] No duplicate damage or defeat events occur.
- [ ] Reset cancels pending recovery events.
- [ ] Existing knockdown behavior remains functional.
- [ ] No referee counts, automatic recovery, or match outcomes are added.

## 12. Deliverables

Provide:

1. Updated Swift source files.
2. Integrated eight-frame `rise` animation.
3. Rise debug control.
4. Recovery-state transition logic.
5. Health restoration on recovery completion.
6. Device or simulator validation results.
7. Any remaining sprite-alignment issues.

## Completion criterion

After the orange boxer has fallen and entered the static down pose, pressing Rise plays the complete eight-frame recovery animation over approximately 800 ms.

The boxer then returns to idle with full health, becomes combat-eligible again, and can be knocked down in a subsequent test.

All existing movement, punching, damage, counters, and reset functionality remains intact.

## Task 6D implementation report

The user approved creation of eight missing rise poses. Integrated rise_b_0...7 universal image sets, with matching transparent512x512 source PNG/SVGs. IdleAnimation/generate_rise.py uses the existing rigid SVG rig and leg articulation with dedicated recovery staging; first pose matches down_b_0 exactly, last matches idle_b_0 exactly. Intermediate poses lift the torso and extend the legs. All frames retain the orange palette, root metadata(256,448), opaque support baseline448 and runtime mirroring. No canvas clipping or endpoint discontinuity was found in asset checks or the visually inspected mirrored contact sheet. The recovery is stylized: gloves remain near guard rather than depicting a hand pushing off the floor. Physical realism and device appearance remain subject to review.

Updated existing runtime files: HitReactionPlayback.swift, PunchContact.swift, IdleTestScene.swift, ContentView.swift. No new Swift target membership is required. Build label6D. Include all eight new image sets when copying this update to the Mac.

### Playback and state

Added DefenderClip.rise. Extended the existing KnockdownPlayback to handle the manual rise, retaining its fall/down behavior. startRise accepts only down, so repeated taps cannot restart or queue. Rise displays eight100ms poses, nominal800ms, then returns to idle and emits one synchronous completion result. Scene time controls advancement, focus/pause freezing and one-pose frame stepping; no independent timer/action/callback was introduced. Like the fall, severe render hitches preserve every pose and may extend nominal duration.

The scene enables Rise only when orange is defeated, currently down, rise assets are available and app has focus. The debug button sits beside Reset Health in the existing top strip. It can start while paused, presenting rise frame1 and waiting for Resume or deliberate Step. During all eight poses orange remains defeated at zero health and Jab/Cross remain disabled. Only the completion result calls the separate FighterHealthState.recoverOrange policy: restore orange health to100, clear its defeat flag and restore standing. Blue health and accepted-contact watermark are untouched. The scene resets orange idle phase to zero, making the exact last-rise/first-idle pixels continuous.

Reset Health still restores both fighters and cancels all pending reaction/fall/rise/punch playback. There are no delayed completion events to survive cancellation. Reset and Rise never change root positions, scales, facing, movement separation, spatial geometry or diagnostic counters. Blue debugging movement remains available.

Guides show Orange: rise1/8...8/8 and Orange: defeated until completion; afterward Orange: idle and Orange: standing. Health bars remain visible. Missing rise assets are explicitly reported in diagnostics.

### Validation results

PASS: python Tests/validate_task6d.py validates all eight asset sets, canvas/transparency/root/baseline, exact down/idle endpoints, down-only eligibility, shared scene clock, orange-only completion policy, Reset cancellation and HUD wiring.
PASS: validate_task6c.py, validate_task6b.py, validate_task6a.py, validate_task5c.py, validate_task5b.py and validate_task5a1.py source/asset/numerical regressions. Historical build-label assertions were advanced to6D.

Added Tests/RiseChecks.swift behavioral checks for unavailable standing/falling Rise, eight100ms frames/800ms, unchanged health until final completion, repeated-tap rejection, one completion, explicit stepping, reset at each rise frame, hitch visibility and two successive defeat/recovery cycles.

Swift behavioral tests, Xcode compilation and iPhone/simulator playback are UNVERIFIED on this Windows host because swiftc/Xcode/SpriteKit are unavailable. Source checks do not establish runtime success.

On Mac:

```sh
swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Boxer0/HitReactionPlayback.swift Tests/RiseChecks.swift -o /tmp/rise-checks
/tmp/rise-checks
```

Pending iPhone SE validation: rebuild and confirm6D; verify Rise disabled in standing/recoil/fall, enabled only down; press once/repeatedly and observe all eight poses, health0 and disabled punches until completion, then idle/standing/100 health. Pause mid-rise, wait and resume; step through final completion; Reset during rise both running and paused. Confirm root/floor alignment and top-strip readability, unchanged counters/blue position and ability to knock orange down again after recovering.

No automatic recovery, referee count, stamina, scoring or match outcomes were added.
