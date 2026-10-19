# Boxer0 — Task 7B: Block Impact Feedback

## 1. Objective

Improve the visual feedback of successfully blocked punches.

When the blue boxer's Jab or Cross contacts the orange boxer's active guard, the orange boxer should display a brief, subtle impact response before returning to its held guard pose.

Preserve all functionality completed through Task 7A.

This task is visual-only. It must not change damage values, punch reach, collision geometry, or combat outcomes.

Inspect the latest Swift source files, animation system, and available sprite assets before implementation.

## 2. Expected behavior

The existing contact system produces three outcomes:

| Outcome | Damage | Visual response |
|---|---:|---|
| HIT | Existing damage | Existing hit reaction |
| BLOCK | 0 | New block impact feedback |
| MISS | 0 | No impact response |

Block feedback must be triggered exclusively by a confirmed BLOCK event.

A punch that misses while the defender is guarding must not produce impact feedback.

## 3. Block impact presentation

Use a subtle visual response that makes glove-to-guard contact noticeable without implying that the defender has been hurt.

Recommended initial implementation:

- Brief brightness emphasis on the orange boxer's gloves/guard area, if independently addressable.
- Otherwise, a small, localized impact indicator positioned at the contact point.
- Total duration: approximately 80–120 ms.
- No persistent visual changes.
- No changes to the fighter's root position.

The response should be restrained and consistent with the existing placeholder art style.

Do not add a full-body flash, large explosion, dramatic screen shake, or camera movement.

Do not translate the entire sprite backward to simulate arm recoil.

If the current full-frame sprite architecture does not support independent glove movement, do not introduce body-part rigging in this milestone.

## 4. Jab and Cross feedback

Both punches should produce block feedback.

Use the same underlying mechanism, with a modest distinction in visual emphasis:

| Property | Jab BLOCK | Cross BLOCK |
|---|---|---|
| Duration | 80 ms | 110 ms |
| Visual emphasis | Light | Slightly stronger |
| Damage | 0 | 0 |
| Guard interrupted | No | No |
| Root movement | None | None |

These are provisional presentation values and should be configurable.

Do not introduce separate damage or stamina calculations.

## 5. Contact-point positioning

Use the existing Task 5A.2 glove contact geometry as the basis for positioning localized feedback.

Requirements:

- Convert the confirmed contact position into the appropriate SpriteKit coordinate space.
- Account for sprite scale and runtime mirroring.
- Keep the effect visually close to the defender's raised gloves.
- Do not modify the existing collision or target calculations.
- Do not change the established Jab/Cross contact frames.

If the exact impact point is visually unsuitable, use a documented, fixed guard-area anchor derived from the existing sprite coordinate contract.

Avoid unexplained hard-coded screen offsets.

## 6. Guard animation behavior

Preserve the existing guard sequence:

`guard 1/3 → guard 2/3 → guard 3/3 → hold`

When a BLOCK occurs:

1. Keep the defender's guard state active.
2. Display the impact feedback.
3. Allow the feedback to expire.
4. Continue holding the final guard frame.

Do not restart the three-frame guard-entry animation after each block.

Do not switch to `hit_react`.

Do not return to idle after a block.

## 7. Repeated blocks

Use a simple deterministic policy.

- Each confirmed BLOCK triggers one feedback event.
- If another BLOCK occurs while feedback is active, restart the visual effect using the new punch's profile.
- Do not queue effects.
- Do not stack brightness or opacity adjustments.
- Do not create duplicate effects from the same punch contact event.

Repeated blocking must not leave the orange boxer permanently highlighted.

## 8. Debug diagnostics

Preserve existing counters:

- J: Jab
- C: Cross
- H: Hit
- B: Block
- M: Miss

The invariant remains:

`J + C = H + B + M`

Add a small diagnostic indicator when block feedback is active:

- `Block FX: Jab`
- `Block FX: Cross`
- `Block FX: OFF`

The diagnostic should reflect the actual effect state, not merely the guard toggle.

Do not add new gameplay counters.

## 9. Pause and frame stepping

Block feedback must use the existing scene-time system.

- Pause freezes the visual effect.
- Resume continues its remaining duration.
- Frame stepping advances it according to the existing scene-time rules.
- Repeated rendering of a contact frame must not retrigger the effect.
- No independent wall-clock timer should be introduced.

Keep the implementation consistent with existing animation playback.

## 10. State cleanup

Remove active block feedback when:

- The effect completes.
- Guard is released.
- The orange boxer is defeated.
- Reset Health is pressed.
- The orange boxer begins Rise or another incompatible animation.

Ensure temporary sprite properties and effect nodes return to their original values.

The cleanup must not alter existing fighter textures or animation states.

## 11. Validation

Test the following:

| Scenario | Expected behavior |
|---|---|
| Close-range Jab against guard | Brief light block feedback |
| Close-range Cross against guard | Slightly stronger block feedback |
| Long-range Jab while guarding | MISS, no feedback |
| Long-range Cross while guarding | MISS, no feedback |
| Repeated successful blocks | One effect per BLOCK |
| Guard released | Feedback cleared |
| Guard remains active after BLOCK | Final guard pose held |
| Reset during feedback | Effect removed |
| Pause during feedback | Effect freezes |
| Resume | Effect completes normally |
| Defeat | No stale feedback |

Additional acceptance checks:

- [ ] Jab and Cross BLOCK events both produce visible feedback.
- [ ] Feedback appears near the guard/contact area.
- [ ] Cross emphasis is modestly stronger than Jab.
- [ ] No health damage occurs on BLOCK.
- [ ] Guard remains active after BLOCK.
- [ ] No hit-reaction animation occurs on BLOCK.
- [ ] No effect occurs on MISS.
- [ ] Existing counters remain consistent.
- [ ] No sprite scale, position, or facing changes occur.
- [ ] No effect remains visible after reset or defeat.
- [ ] Existing knockdown and Rise behavior remains functional.
- [ ] No AI, stamina, guard-break, sound, particles, or camera shake is introduced.

## 12. Deliverables

Provide:

1. Updated Swift source files.
2. Block-feedback implementation.
3. Configurable Jab/Cross feedback durations.
4. Brief explanation of effect positioning and cleanup.
5. Device or simulator validation results.
6. Any remaining visual limitations.

## Completion criterion

A confirmed Jab or Cross BLOCK produces a brief, localized impact response near the orange boxer's guard.

The Cross has slightly stronger visual emphasis than the Jab.

The defender remains guarding, takes zero damage, and returns to the unchanged held guard pose after the effect ends.

MISS and HIT behavior remain unchanged, and all existing combat systems continue functioning correctly.

## Task 7B implementation report

Updated existing HitReactionPlayback.swift, IdleTestScene.swift and ContentView.swift. No new sprite assets or Swift target membership are required. Build label7B.

The full-frame sprite architecture cannot independently highlight gloves. A single small SKShapeNode instead displays a pale-gold ring and two short ticks at the raised guard. This is presentation only: no sprite tint, full-body flash, rigging, root movement, particles, sound or camera changes.

### Profiles and positioning

BlockFeedbackProfile centralizes duration, canvas radius and initial opacity. Jab defaults:80ms,18canvas pixels,opacity0.65. Cross:110ms,23pixels,opacity0.85. Playback stores editable Jab/Cross profiles. Cross is modestly larger/brighter/longer, using the same mechanism.

Position uses the specification's permitted fixed guard-area alternative because glove-to-target collision can be low on the torso. The confirmed event supplies the scene contact point and mirrored defender transform. The nearer of guard_b_2's authored glove centers is selected: rear(253,150), lead(303.5,152). Tests derive these exact centers from SVG ellipse centers plus glove transforms. The selected image anchor is converted through the live defender canvas transform every render/layout update; this handles scale, mirror and resizing without unexplained screen offsets. Radius uses the same scale conversion. Root positions and collision calculations are untouched.

### Trigger, clock and cleanup

BlockFeedbackPlayback accepts only confirmed BLOCK events, guarded by contact sequence. HIT/MISS never start or restart it. Each accepted BLOCK resets the one effect to elapsed zero and selects the new punch profile; no queue, stacking or additional counters. The existing tracker still owns one spatial resolution per punch. Damage remains zero on BLOCK, guard remains active, and hit_react accepts HIT only.

The scene advances OLD feedback before resolving the current blue contact, so a new effect appears on the BLOCK render tick at full initial opacity. It fades linearly over its profile duration. Pause/focus guards freeze that clock. Frame Step advances existing feedback by the blue punch frame interval (50/60ms) or the current normal blue clip step interval; an effect triggered by that step is not advanced again in the same call. No timers or completion callbacks were added.

Completion, guard release, HIT/incompatible recoil/defeat, Reset Health, scene removal and Rise start/completion clear the effect. Cancellation retains the contact watermark so a replayed old event cannot re-highlight the fighter. The one node is hidden, its alpha set to zero and path cleared when inactive. No fighter texture or temporary sprite property needs restoration. Guides do not control the effect; the new Block FX:Jab/Cross/OFF diagnostic mirrors actual playback state.

### Validation

PASS: python Tests/validate_task7b.py checks centralized profiles, authored SVG glove anchors, confirmed-event-only trigger, scene-clock ordering, cleanup hooks, localized-node isolation, FX diagnostics and actual runtime Swift brace nesting (not just brace counts).
PASS: validate_task7a.py, validate_task6d.py, validate_task6c.py, validate_task6b.py, validate_task6a.py, validate_task5c.py, validate_task5b.py, validate_task5a1.py source/asset/numerical regressions. Historical build-label/source assertions were adjusted for7B and expanded HIT cleanup.

Added Tests/BlockFeedbackChecks.swift behavioral fixtures for HIT/MISS rejection,80/110ms lifetimes, mirrored nearest anchor, fading, duplicate suppression, new-BLOCK replacement, cancellation/reset watermark, explicit clock stepping and configurable duration. These Swift tests have NOT run here because this Windows host lacks swiftc/Xcode/SpriteKit. Compilation and iPhone/simulator visual validation remain pending. Source/numerical checks do not establish live visual quality.

On Mac:

```sh
swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Boxer0/HitReactionPlayback.swift Tests/BlockFeedbackChecks.swift -o /tmp/block-feedback-checks
/tmp/block-feedback-checks
```

Pending iPhone SE checks: confirm7B, enable active guard, close Jab/Cross for restrained localized feedback and unchanged health/guard pose; verify Cross distinction; long-range misses must not trigger feedback; confirm J+C=H+B+M. Pause immediately after contact and verify mark/diagnostic freeze; step/resume to expiry. Release Guard or Reset while FX is visible and verify immediate removal. Exercise defeat/Rise afterward for stale-effect absence. Check visibility with Guides off and landscape root/glove alignment.

Visual limitation: the effect intentionally sits at the nearest authored raised-glove anchor rather than claiming the collision point is an exact glove-surface contact. Small-device readability and profile strength may need tuning after review; no geometry changes should be used to tune it.
