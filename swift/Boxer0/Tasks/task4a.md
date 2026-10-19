# Boxer0 — Task 4A: Jab Animation and Input

## 1. Objective

Extend the existing Swift/SpriteKit boxing prototype with a basic jab action for the blue boxer.

Preserve all completed functionality from Tasks 2, 3A, and 3B.

Inspect the current Swift source files, asset catalog, and existing animation specification before modifying anything. Do not rebuild working systems unnecessarily.

## 2. Asset requirements

Use the existing six-frame jab animation if available.

According to the established sprite specification:

| Frame | Pose |
|---|---|
| 1 | Ready stance |
| 2 | Preparation |
| 3 | Extension |
| 4 | Contact position |
| 5 | Withdrawal |
| 6 | Return to guard |

Total animation duration: **300 ms**, with each frame lasting 50 ms.

The contact position occurs on frame 4, approximately 150 ms after the action begins.

Requirements:
- Maintain the existing 512 × 512 transparent canvas.
- Preserve the established root at (256, 448).
- Keep the fighter on the same baseline.
- Keep the rear glove in a defensive position.
- Maintain connected joints and consistent proportions.
- Do not mirror the blue boxer.
- Do not introduce new artwork unless the jab frames are missing and asset creation is separately approved.

If the jab frames are missing, report that dependency rather than silently substituting another animation.

## 3. Jab input

Add one clearly labeled **Jab** button to the existing development interface.

Behavior:
- A tap initiates one jab.
- Holding the button does not automatically repeat punches.
- Additional taps during an active jab are ignored.
- The jab cannot interrupt itself.
- The action completes before another jab can begin.
- Keep the existing Advance and Retreat controls.

Use a touch-down trigger for responsiveness where practical, while ensuring one punch per distinct press.

## 4. Jab playback

Implement the jab as a non-looping action.

- Begin at jab frame 1.
- Advance through all six frames once.
- Play at normal speed.
- Return to the existing idle animation after completion.
- Do not skip the recovery frame.
- Preserve the current SpriteKit texture-based animation architecture.

Use elapsed time rather than assuming a fixed rendering frame rate.

The contact frame is an animation marker only. It does not cause damage or determine whether a punch lands.

## 5. Interaction with movement

For this initial implementation, punching and movement are mutually exclusive.

When a jab begins:
- Cancel active horizontal movement.
- Set horizontal velocity to zero.
- Keep the fighter at his current horizontal position.
- Disable further horizontal translation until the jab finishes.
- Do not allow held directional input to restart movement during the jab.

When the jab finishes:
- Return to idle.
- Resume normal movement input only after a new directional press.
- Do not automatically restart a previously held direction.

This deliberately simple rule avoids combining footwork and punching before we have designed that interaction.

## 6. Animation state management

Extend the existing fighter animation state to include `jab`.

Requirements:
- Preserve idle, advance, and retreat.
- Jab has priority over movement states.
- Jab is non-looping.
- Movement states continue looping normally.
- Return from jab to idle is deterministic.
- Avoid unnecessary resets or abrupt changes to the fighter's root position.

Do not implement a complex animation state machine or animation blending framework at this stage.

## 7. Debug diagnostics

Preserve the existing development diagnostics.

Display:
- Active animation state.
- Current frame and total frames.
- Horizontal position.
- Horizontal velocity.

Add an optional visual indication when the jab reaches its contact frame.

The contact marker must fire once per jab and must not trigger gameplay effects.

Remove no existing useful development controls.

## 8. Pause, interruption, and safety

- Pausing freezes the jab at its current frame.
- Resuming continues the same jab without restarting it.
- Frame stepping remains functional.
- Losing app focus cancels movement input.
- Avoid unexpected repeated punches when the app resumes.
- Ensure the jab state cannot become permanently stuck.

## 9. Validation

Test in landscape on an iPhone simulator or physical device when available.

Acceptance criteria:

- [ ] Tapping Jab produces exactly one punch.
- [ ] All six jab frames play in order.
- [ ] Jab completes in approximately 300 ms.
- [ ] The boxer returns to idle after recovery.
- [ ] Holding Jab does not repeat punches.
- [ ] Repeated taps during the jab do not queue punches.
- [ ] Horizontal movement stops when a jab begins.
- [ ] Movement does not restart from an old held input.
- [ ] Pause/resume preserves the jab's animation state.
- [ ] Frame stepping works during the jab.
- [ ] The contact marker occurs once at frame 4.
- [ ] Orange boxer remains idle.
- [ ] No damage, stamina, health, AI, or collision systems are introduced.

## 10. Deliverables

1. Updated Swift source files.
2. Integration of the existing jab sprite frames.
3. A short implementation summary.
4. A list of any missing assets or unresolved limitations.
5. Simulator or device validation results.

**Completion criterion:** The blue boxer can execute one complete, responsive jab and recover to idle without breaking the existing footwork system.

## Implementation report — October 19, 2026

Task 3B was validated by the user before this task began. No jab assets existed
in the repository. The user separately approved creation of the six jab frames.

### Assets

- Added jab_a_0 through jab_a_5 to the asset catalog and IdleAnimation/frames,
  with matching editable SVGs, reproducible generate_jab.py, contact sheet and GIF.
  Blue only: the orange fighter does not punch in this milestone.
- Each frame is transparent RGBA 512×512, rooted at (256,448), baseline unchanged.
  Ready and recovery are pixel-identical to idle_a_0. Legs, feet, head, pelvis,
  torso and rear defensive glove are unchanged. Blue is not mirrored.
- Reused the existing offline rig and rendering helpers. The idle renderer gained
  an optional lead-arm pose; all existing calls retain their original defaults.
  No existing frame PNGs were regenerated or replaced.
- Arm segments retain original lengths through offline two-segment pose solving;
  this is asset generation, not runtime IK. Shoulder protraction is limited to
  12 canvas pixels. The rig starts with a nearly extended, short lead arm, so the
  punch has a restrained reach: lead glove center extends 20 pixels beyond its
  idle position. A longer jab would need an explicitly revised rig/guard pose,
  rather than stretching limbs. Rear glove remains in guard throughout.
- Preview: IdleAnimation/preview/jab_contact_sheet.png and jab_a.gif. The GIF loops
  for review; the in-app action is single-shot.

### Runtime and input

- Added pure JabPlayback.swift: six 50 ms frames, no looping or queued input.
  Contact event occurs once on zero-based frame 3 (artist frame 4, 150 ms).
  Recovery frame 6 is held for the final 50 ms before deterministic idle return.
- Added .jab to FighterClip and a touch-down Jab control beside the existing
  Pause/Resume, Step and Guides controls. Advance and Retreat remain in place.
  The status identifies this build as “4A” and includes state, frame/total, X,
  velocity and a contact count highlighted while the contact pose is active.
  The contact count has no gameplay effect.
- Starting a jab zeros velocity and invalidates movement touches. While active,
  update bypasses the entire translation path and directional presses are
  rejected. Completion invalidates held input again, so only a fresh directional
  press can move. Extra jab presses are ignored; holding does not auto-repeat.
- Jab uses normal speed independently of the internal slow-playback setting.
  Timing is elapsed-time based. The first render tick seeds the ready pose, so
  observed press-to-finish time can include up to one extra rendering interval
  beyond the 300 ms clip duration. A delayed tick that would consume recovery
  offscreen instead presents the recovery pose for 50 ms, so a severe stutter can
  extend the action rather than skipping recovery.
- Pause preserves jab frame and fractional timing. Resume continues that same
  action. Frame stepping advances one jab pose, including recovery; the following
  step finishes it. Orange idle continues independently during normal jab playback
  and follows the existing pause/frame-step diagnostics.
- Focus loss clears movement input and suspends animation advancement; reactivation
  resets the render clock and continues an interrupted jab without starting a new
  punch. Scene removal cancels the action back to idle. Long render gaps are
  treated as interruptions, avoiding huge catch-up changes or stuck state.
- Runtime requires all six correctly sized jab textures. Missing/incomplete assets
  disable Jab and show “Jab assets missing”; no placeholder or idle substitution.
- Added JabPlayback.swift to this Xcode project's Sources phase. If continuing in
  the separate Shared/iOS/macOS project shown earlier, add that new file and the
  six catalog image sets to its iOS target as well as copying the updated sources.

### Validation and remaining checks

Passed here with python Tests/validate_task4a.py:

- Six RGBA 512×512 frames and valid catalog references; source/catalog pixel match.
- Transparent margins, unchanging feet/lower body and rear-guard center pixels.
- Exact guard endpoints, original upper/lower arm lengths in every generated pose.
- Six 50 ms GIF frames and Xcode target membership for JabPlayback.swift.

Also compared editable SVG groups: rear glove, feet, head, torso and pelvis are
unchanged. Visually reviewed the generated contact sheet. Existing Task 3B asset
and source checks still pass with python Tests/validate_task3b.py.

Tests/JabPlaybackChecks.swift tests the actual pure Swift playback type: 300 ms
completion, contact at 150 ms exactly once, full recovery duration, refusal to
restart during playback, no automatic repeat after completion, frame stepping,
all six frames observed at 30/60/120 fps, mandatory recovery on a delayed tick,
and cancellation.
Swift tests could not execute on this Windows host (no swiftc). On the Mac:

```sh
swiftc Boxer0/JabPlayback.swift Tests/JabPlaybackChecks.swift -o /tmp/jab-checks
/tmp/jab-checks
```

Xcode compilation and landscape iPhone SE acceptance remain pending. Rebuild the
Boxer0 iOS target and verify the “4A” status. Exercise single tap, held Jab, rapid
taps, moving-then-Jab, holding a direction across completion, pause/step/resume
mid-jab, focus loss, contact count and orange idle. Inspect joint connection and
readability at phone size. No damage, health, stamina, AI or combat collisions
have been added. Task 4A is implemented; device validation is not yet recorded.


## User acceptance — October 19, 2026

User confirmed Task 4A validated and requested Task 4B. New Swift code must use
explicit optional binding (if let value = value), not shorthand if let value.
