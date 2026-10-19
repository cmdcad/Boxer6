# Boxer0 — Task 6C: Knockdown Animation

## 1. Objective

Implement the orange boxer's knockdown animation following the existing Task 6B defeat event.

When health reaches zero:

1. Register defeat exactly once.
2. Allow the final hit reaction to finish.
3. Play the knockdown animation once.
4. Transition to the static down pose.
5. Remain down until Reset Health.

Preserve all functionality from Tasks 2 through 6B.

Inspect the latest Swift source files, sprite assets, animation manifest, and existing defeat-state handling before modifying the implementation.

Do not rebuild completed systems.

## 2. Required sprite assets

Use the existing sprite specification:

| Animation | Frames | Duration | Playback |
|---|---:|---:|---|
| `hit_react` | 4 | 240 ms | Once |
| `knockdown` | 8 | 640 ms | Once |
| `down` | 1 | Hold | Static |

The knockdown frames must retain the established sprite contract:

- Canvas: 512 × 512 pixels.
- Transparent background.
- Root coordinate: (256, 448).
- Consistent fighter proportions.
- Orange boxer palette.
- Existing runtime mirroring.
- No baked-in movement of the fighter's root.

Verify that all eight `knockdown` frames and the `down` frame exist.

If any required assets are missing, report the missing files rather than substituting unrelated animations or creating replacement artwork without approval.

## 3. Defeat animation sequence

The sequence should be:

`Standing → Final HIT → Hit Reaction → Knockdown → Down`

When the final successful punch reduces health to zero:

- Apply damage once.
- Transition combat state to `defeated`.
- Disable Jab and Cross as established in Task 6B.
- Allow the final hit reaction to finish.
- Start the knockdown sequence immediately afterward.

Do not interrupt the final hit reaction unless a future design explicitly changes this behavior.

The knockdown animation must not generate additional contact or damage events.

## 4. Knockdown playback

Play the eight knockdown frames sequentially.

- Total duration: 640 ms.
- Frame duration: 80 ms.
- Playback: once.
- No looping.
- No frame skipping caused by repeated state transitions.
- No additional delay before the down pose.

Use the existing elapsed-time-based animation architecture.

Do not use a separate animation timer if the scene already manages frame progression.

## 5. Down state

After the knockdown animation finishes:

- Display the single `down` frame.
- Hold that frame indefinitely.
- Keep health at zero.
- Keep combat state as `defeated`.
- Keep Jab and Cross disabled.
- Keep the orange boxer stationary.

The down pose must not return automatically to idle.

Do not introduce a recovery countdown or standing-up animation.

## 6. Separate combat and animation states

Preserve the distinction established in Task 6B.

Combat state:

- `standing`
- `defeated`

Animation state:

- `idle`
- `hit_react`
- `knockdown`
- `down`

A boxer may be combat-state `defeated` while visually completing `hit_react` or `knockdown`.

Do not create additional combat states solely to represent animation frames.

## 7. Positioning and baseline stability

The orange boxer must remain anchored to its existing scene position.

Requirements:

- Do not move the SpriteKit node's root position.
- Do not change sprite scale.
- Do not change facing direction.
- Do not introduce automatic horizontal knockback.
- Do not modify the existing fighter-separation logic.
- Do not reposition the fighter when switching animations.

The artwork should depict the fall within the existing canvas.

If the down pose extends beyond the available sprite canvas or appears to float above the ring floor, report the asset-alignment problem rather than compensating with arbitrary scene offsets.

## 8. Reset behavior

Extend the existing Reset Health functionality.

Reset must work during:

- Final hit reaction.
- Knockdown animation.
- Static down pose.

When Reset Health is activated:

1. Restore both fighters to full health.
2. Restore combat state to `standing`.
3. Cancel the active knockdown or reaction playback.
4. Restore the orange boxer's idle animation.
5. Re-enable Jab and Cross.
6. Preserve fighter positions.
7. Preserve existing punch and contact counters.

Any pending animation completion events from the previous defeat must be invalidated so they cannot restart knockdown after reset.

## 9. Debug diagnostics

Preserve the existing health bars, counters, and debug controls.

Update the orange-boxer animation diagnostic to display:

- `Orange: hit_react 1/4` through `4/4`
- `Orange: knockdown 1/8` through `8/8`
- `Orange: down`

Keep the existing `DEFEATED` combat-state indicator while the knockdown sequence is playing.

The diagnostics should distinguish the combat state from the animation state.

## 10. Pause and frame stepping

Preserve the existing pause and frame-step functionality.

- Pausing freezes the current knockdown frame.
- Resuming continues from the same frame.
- Frame stepping advances according to the existing scene-time rules.
- Pausing does not restart the animation.
- Resuming does not duplicate defeat events.
- Reset during pause must restore a consistent standing state.

Do not introduce a second independent timing mechanism.

## 11. Validation

Test the following scenarios:

| Test | Expected result |
|---|---|
| Jab reduces health to zero | Final recoil, then knockdown |
| Cross reduces health to zero | Final recoil, then knockdown |
| Knockdown begins | Frame 1 of 8 |
| Knockdown completes | Static down pose |
| Wait several seconds | Boxer remains down |
| Punch after defeat | No damage or new contact event |
| Reset during recoil | Returns to standing idle |
| Reset during knockdown | Cancels fall and restores idle |
| Reset while down | Restores standing idle |
| Pause during knockdown | Current frame freezes |
| Resume | Animation continues normally |

Additional checks:

- [ ] Knockdown plays exactly once per defeat.
- [ ] All eight frames appear in the correct order.
- [ ] Knockdown duration is approximately 640 ms.
- [ ] Down pose remains visible until reset.
- [ ] Fighter scale and facing direction remain correct.
- [ ] No unexpected root movement or baseline jump occurs.
- [ ] Health remains clamped at zero.
- [ ] Jab and Cross remain disabled after defeat.
- [ ] HIT/MISS counters do not change after defeat.
- [ ] Reset preserves positions and counters.
- [ ] Existing movement and contact detection remain functional.
- [ ] No referee, recovery, scoring, or match-result logic is introduced.

## 12. Deliverables

Provide:

1. Updated Swift source files.
2. Integrated `knockdown` and `down` sprite assets.
3. Animation-state transition implementation.
4. Updated Reset Health behavior.
5. Device or simulator validation results.
6. Any missing assets or unresolved alignment issues.

## Completion criterion

When the orange boxer's health reaches zero, the final hit reaction completes, the eight-frame knockdown animation plays once over approximately 640 ms, and the boxer remains in the static down pose until Reset Health is activated.

All existing health, damage, contact-detection, movement, and debugging functionality remains intact.

## Task 6C implementation report

User approved creation of eight orange knockdown frames and one down pose. Inspected existing sources and assets; no knockdown/down sequence or existing animation manifest was present. The approved artwork is now integrated as knockdown_b_0...7 and down_b_0 image sets, with matching source PNG/SVG files in IdleAnimation/frames. IdleAnimation/knockdown_manifest.json records the canvas/root/timing contract. generate_knockdown.py uses the existing SVG body groups, rigid segment rotations and two-link knee articulation, without deforming limb lengths. Rendering requires Pillow and CairoSVG.

Assets: transparent512x512, orange palette, metadata root(256,448), original runtime facing/mirroring. The first fall frame reuses the original guard artwork exactly; the remaining poses articulate backward into a bent-knee down pose. Floor alignment is authored into the poses using the opaque support edge at y448, matching the original idle's support edge. Down is pixel-identical to fall frame8 to avoid a final transition jump. The mirrored contact sheet was visually inspected. No clipping or floating support edge was found in source assets. Artwork is a stylized rig-derived fall with the gloves retained near guard; on-device visual approval remains pending.

Updated existing runtime files only: HitReactionPlayback.swift, IdleTestScene.swift, ContentView.swift. No new Swift target membership is needed. Build label6C.

### Sequence and timing

Final accepted contact applies damage/defeat once as before, and now starts the final HIT recoil even though combat eligibility has just become defeated. This intentionally extends Task6B's static-defeat presentation. Post-defeat contact evaluation remains blocked, so no later damage, contacts or reactions can occur. Defeat remains a combat state, independent of hit_react/knockdown/down animation states.

After four60ms reaction frames, the scene starts KnockdownPlayback at frame0, without consuming the recoil-completion tick again. The existing scene update clock displays eight80ms frames (nominal640ms), then immediately switches to the down texture. Down holds indefinitely, including repeated elapsed updates and frame steps. start is guarded throughout knockdown/down, so it cannot restart on repeated transition checks. Pause/focus guards freeze playback; stepping advances one fall pose. No timers, actions, asynchronous completion callbacks or wall-clock mechanisms were added.

A render hitch advances at most one fall frame per render tick, preserving every visible pose. Consequently severe low frame rates can extend the nominal640ms duration. Normal display rates retain elapsed-time-based80ms intervals. This is a deliberate tradeoff to satisfy sequential visibility rather than skipping unseen poses.

The scene roots, scales, facing, movement boundaries and spatial geometry are unchanged. Reset cancels recoil and knockdown and pending blue-punch contact ownership, restores full health and standing state, clears defeat flags and returns orange to idle. It preserves positions, counters and pause status. Cancellation resets all local playback state, leaving no completion callback that can restart the old fall.

HUD: health/DEFEATED remain visible; Guides report Orange: hit_react1/4...4/4, knockdown1/8...8/8, or down. Missing knockdown/down assets are reported explicitly if a copied build lacks the new image sets.

### Validation

PASS: python Tests/validate_task6c.py checks all nine assets/image sets, alpha/canvas, opaque baseline448, no source-canvas clipping, matching last/down pixels, manifest, final-recoil wiring, scene-clock progression, reset, dynamic diagnostics and absence of transform changes in orange playback.
PASS: source/asset/numerical regressions validate_task6b.py, validate_task6a.py, validate_task5c.py, validate_task5b.py, validate_task5a1.py. Historical source assertions and the defeat behavioral fixture were adjusted for6C's final-recoil requirement.

Added Tests/KnockdownChecks.swift: ordered frames at80ms/640ms, one-shot start, indefinite down hold, hitch visibility, reset at every fall/down stage, no stale restart, final Jab/Cross health-depletion with recoil then fall. Swift tests and Xcode compilation remain UNEXECUTED on this Windows host (no swiftc/Xcode/SpriteKit). No simulator or physical-device validation is claimed.

On Mac:

```sh
swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Boxer0/HitReactionPlayback.swift Tests/KnockdownChecks.swift -o /tmp/knockdown-checks
/tmp/knockdown-checks
```

Pending iPhone SE validation: verify6C label, reach zero via Jab and separately Cross; final recoil then frames1...8 and persistent down; pause/resume and stepping through the fall; Reset Health during recoil, fall, paused fall and down; verify health100/100, standing, orange idle, same positions/counters and fresh input; ensure post-defeat attack attempts never alter counters or health. Check scene-level floor contact, proportions and screen-edge visibility in landscape. If copying sources to the Mac, include all nine new image sets, not just Swift files.

No recovery, referee, scoring or match-result system was introduced.
