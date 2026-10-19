# Boxer0 — Task 5C: Hit Feedback Refinement

## 1. Objective

Refine the existing punch-impact feedback so successful Jab and Cross contacts feel responsive, visually convincing, and distinct.

Task 5B already provides:
- Confirmed HIT/MISS contact detection.
- A four-frame orange-boxer hit reaction.
- Visible backward sway on successful contact.
- Automatic return to idle.

Preserve all completed functionality.

Inspect the latest Swift source files and sprite assets before implementing changes.

Do not rebuild the existing animation or collision systems.

## 2. Synchronize impact and reaction

Ensure the orange boxer's hit reaction begins on the same logical contact event that registers HIT.

Requirements:

- Trigger the reaction immediately when contact is confirmed.
- Do not introduce an artificial delay.
- Do not trigger reactions on MISS.
- Do not evaluate contact more than once per punch.
- Preserve existing Jab and Cross contact-frame timing.

The visual response should appear connected to the attacking glove.

## 3. Differentiate Jab and Cross feedback

Introduce two lightweight reaction profiles using the existing `hit_react` animation.

| Property | Jab | Cross |
|---|---|---|
| Reaction animation | Existing 4 frames | Existing 4 frames |
| Duration | 240 ms | 240 ms |
| Visual intensity | Light | Moderate |
| Root displacement | None | None |
| Damage | None | None |

The Jab should feel like a quick, controlled impact.

The Cross should feel slightly heavier, without becoming exaggerated.

For this milestone, use subtle, temporary visual adjustments to the reaction artwork, such as a small additional upper-body recoil only if the current sprite architecture supports it.

Do not shift the entire boxer sprite away from its root position merely to simulate upper-body movement. This would create foot sliding and baseline inconsistencies.

If separate body-part movement is not supported, retain the existing reaction artwork for both punches and report the limitation rather than introducing a misleading whole-body translation.

## 4. Improve reaction recovery

The orange boxer must return naturally to idle after the reaction completes.

Requirements:

- Play all four reaction frames in order.
- Preserve the established 240 ms playback duration.
- Avoid an additional idle delay.
- Avoid a visible position jump when returning to idle.
- Preserve scale, facing direction, and baseline alignment.

Do not add recovery animations beyond the existing four frames.

## 5. Optional impact emphasis

If supported cleanly by the existing implementation, introduce a very subtle, short-lived impact emphasis on confirmed HIT.

For example, a brief brightness adjustment lasting approximately 50–70 ms.

Constraints:

- Apply only to confirmed HIT.
- Do not obscure the boxer artwork.
- Do not affect MISS.
- Do not alter contact geometry.
- Do not create permanent tint or brightness changes.
- Respect pause/resume behavior.

Keep this effect disabled by default if it makes the placeholder artwork less readable.

Do not add screen shake, particles, sound effects, or camera movement.

## 6. Reaction state handling

Preserve Task 5B's existing behavior:

- HIT while idle starts the reaction.
- HIT during an active reaction restarts it.
- MISS never interrupts a reaction.
- Reactions are not queued.
- The orange boxer returns to idle after completion.

Do not introduce new combat states.

## 7. Debugging and diagnostics

Preserve the existing counters and debug controls.

The orange-boxer diagnostic should continue to show:

- `Orange: idle`
- `Orange: hit_react 1/4` through `4/4`

Optionally include the triggering punch type:

- `Orange: hit_react (Jab)`
- `Orange: hit_react (Cross)`

Keep diagnostics separate from gameplay rendering.

## 8. Validation

Test the following scenarios:

| Test | Expected result |
|---|---|
| Close-range Jab HIT | Immediate, light reaction |
| Close-range Cross HIT | Immediate, slightly heavier reaction if supported |
| Long-range Jab MISS | No reaction |
| Long-range Cross MISS | No reaction |
| Consecutive successful punches | Reaction restarts correctly |
| Reaction completion | Smooth return to idle |
| Pause during reaction | Reaction freezes |
| Resume | Reaction continues |
| Frame stepping | No duplicate HIT events |

Also verify that:

- [ ] Fighters remain the same size.
- [ ] Feet remain aligned with the baseline.
- [ ] Contact geometry is unchanged.
- [ ] HIT/MISS counters remain accurate.
- [ ] Existing movement and punching remain functional.
- [ ] No health, damage, stamina, blocking, AI, knockback, or knockdown functionality is added.

## 9. Deliverables

Provide:

1. Updated Swift source files.
2. Brief explanation of any visual feedback changes.
3. Confirmation of whether distinct Jab/Cross recoil intensity is technically supported by the current sprite architecture.
4. Device or simulator validation results.
5. Any remaining limitations.

## Completion criterion

Successful Jab and Cross contacts produce immediate, visually coherent reactions, with the Cross feeling slightly heavier where the existing artwork permits.

The orange boxer returns smoothly to idle, misses produce no reactions, and all existing gameplay systems remain intact.


One design consideration
Our current sprites use complete character frames rather than independently animated body parts. That limits how much recoil intensity we can vary without creating unnatural movement.

For that reason, I would prioritize impact synchronization and smooth recovery over exaggerated recoil. The game should feel responsive before we make it more visually elaborate.

## Implementation report — October 19, 2026

Updated HitReactionPlayback.swift, IdleTestScene.swift and ContentView.swift.
No source files or asset sets were added to the application target. Build label
is now “5C”. All existing reaction textures and contact geometry are retained.

### What the current renderer supports

The runtime draws complete-character textures, with no independent head/torso
nodes or body-part masks. It therefore cannot increase only Cross's upper-body
recoil without different artwork or a different rendering architecture. Whole-body
translation, scale changes and root motion were not used to fake this distinction.

Both punches retain the same four reaction poses and 240 ms playback. Distinct
upper-body recoil intensity is NOT implemented/supported by this architecture.
This is the fallback explicitly requested in Task 5C. Cross does not have stronger
physical recoil than Jab in the default configuration.

### Feedback profiles and optional emphasis

HitFeedbackProfile records the triggering punch:

| Profile | Recoil artwork/time | Optional emphasis |
| --- | --- | --- |
| Jab / light | Same hit_react, 4×60 ms | Up to4% white blend, linear decay over60ms |
| Cross / moderate | Same hit_react, 4×60 ms | Up to7.5% white blend, linear decay over60ms |

The optional emphasis uses SKSpriteNode.colorBlendFactor on the existing orange
texture. It is a subtle brightness/tint blend, not additional recoil or a physics
response. It is disabled by default with `scene.impactEmphasisEnabled = false`.
No on-screen toggle was added. To review it on the Mac/iPhone, enable the scene
property in development code; readability has not been verified on the device.

The emphasis begins on the confirmed HIT event and uses the same elapsed reaction
clock. Pause/focus loss freezes it; stepping advances it; HIT restart resets its
60 ms window and profile; MISS does not change an active HIT's feedback. Completing
or canceling the reaction clears the profile and emphasis. Disabling the property
also immediately sets blend to zero. There are no SKAction/wall-clock timers,
permanent visible tints, particles, sounds, screen shake or camera changes.

### Timing and recovery

- The existing same-update synchronization is preserved: advance the previous
  orange animation, process blue's contact/HIT, start reaction frame1, apply both
  textures. Reaction does not depend on SwiftUI diagnostics or delayed dispatch.
- The actual confirmed contact event supplies the punch profile. MISS returns
  before any reaction/profile/elapsed state is changed. No extra evaluations.
- All four frames retain60ms each. Reaction completion selects idle frame1 and
  resets its accumulator in the same update, with no added idle/recovery delay.
- Existing pose4 is already within1 canvas pixel of idle head/neck position and
  0.5px at the upper torso. At the SE's approximately.32 scale, that is at most
  about.32 scene points. No new recovery animation or transform jump was added.
- The established delayed-render safeguard still presents final recovery rather
  than consuming it offscreen; on a severe hitch, wall-clock completion can exceed
  nominal240ms. Normal30/60/120fps ordering is unchanged.
- Orange diagnostic now identifies the source: hit_react (Jab) or (Cross), plus
  frame1/4 through4/4. It remains under Guides/development visibility. Contact
  counters, movement, punch inputs and root/child transforms are unchanged.

### Checks and evidence

Passed on Windows:

- `python Tests/validate_task5c.py`: profile wiring, shared240ms duration, default-off
  60ms emphasis, texture-only color helper, no root/scale/geometry mutations,
  once-only contact integration and punch-type HUD.
- `python Tests/validate_task5b.py`: same-update/step ordering, fixed orange root,
  four approved reaction frames, recoil direction, preserved arm lengths/lower
  body and original Cross rendering.
- `python Tests/validate_task5a1.py`: established contact/spacing transform and
  far/near range calculations remain valid; glove geometry unchanged.

Added Tests/HitFeedbackChecks.swift for the actual Swift model: both profiles,
initial/halfway/expired emphasis, MISS immunity, profile changes on new HIT,
240ms completion without an extra idle wait, step/cancel cleanup and reset.
Swift could not execute here (no swiftc/Xcode/iOS runtime on this Windows host).
On Mac, from this project directory:

```sh
swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Boxer0/HitReactionPlayback.swift Tests/HitFeedbackChecks.swift -o /tmp/feedback-checks
/tmp/feedback-checks
```

### Device validation pending and limitations

Rebuild the iOS target and check “5C”. For close Jab/Cross hits, inspect the first
recoil against the contact pose and check the diagnostic's triggering punch. At
long range, confirm misses leave idle or an existing reaction unchanged. Check
recovery, pause/resume, stepping, fixed feet/roots and J+C=H+M. If the optional
emphasis is enabled for review, verify Cross is only subtly brighter, both tints
clear after60ms, and paused highlights continue correctly.

No new Task5C recording has been reviewed. Phone-size readability, perceived
impact/recovery, optional emphasis appearance, compilation and the full device
acceptance matrix remain unverified. The same recoil artwork is used for both
punches; stronger upper-body-only Cross recoil would require an approved asset or
body-part architecture task. No damage, health, stamina, blocking, AI, knockback,
knockdown, root motion or new combat states were added.
