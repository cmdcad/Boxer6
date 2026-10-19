# Boxer0 — Task 5B: Basic Hit Reactions

## 1. Objective

Extend the existing Swift/SpriteKit boxing prototype so the orange boxer visibly reacts when the blue boxer successfully lands a Jab or Cross.

Preserve all completed functionality from Tasks 2 through 5A.2.

Before making changes, inspect the latest Swift source files, asset catalog, animation metadata, and contact-detection implementation.

Do not rebuild or unnecessarily refactor completed systems.

## 2. Hit reaction animation

Use the existing `hit_react` animation defined in the Boxing Placeholder Sprite Specification.

| Frame | Purpose |
|---|---|
| 1 | Initial reaction |
| 2 | Head and torso recoil |
| 3 | Recovery begins |
| 4 | Return toward guard |

Animation requirements:

- Four frames.
- Total duration: 240 ms.
- Frame duration: 60 ms.
- Non-looping.
- Return to idle after completion.
- Preserve the existing 512 × 512 canvas and root `(256, 448)`.

The animation should show a small head and torso recoil without moving the boxer's root.

Use the orange palette's hit-reaction frames.

If these assets are missing, report the dependency. Do not substitute idle frames or create new artwork without approval.

## 3. Triggering reactions

Connect hit reactions to the existing Task 5A.2 contact-detection results.

When a punch reaches its contact frame:

**If the result is HIT:**
- Trigger the orange boxer's hit-reaction animation.
- Start from reaction frame 1.
- Play the four frames once.
- Return to idle after completion.

**If the result is MISS:**
- Do not trigger a reaction.
- Continue the orange boxer's existing idle animation.

The reaction must be triggered by the confirmed spatial contact result, not simply by the punch animation reaching its contact frame.

## 4. Reaction state management

Introduce a minimal animation state for the orange boxer:

- `idle`
- `hit_react`

The orange boxer remains stationary throughout Task 5B.

Requirements:

- Hit reactions have priority over idle.
- Reaction playback must not loop.
- After completion, return to idle deterministically.
- Do not alter the orange boxer's position, scale, facing direction, or baseline.
- Do not change the blue boxer's existing punch behavior.

Avoid introducing a complex combat-state architecture.

## 5. Multiple-hit handling

For this milestone, use a simple policy:

- A successful HIT triggers a reaction if the orange boxer is idle.
- If another HIT occurs while a reaction is already playing, restart the reaction from frame 1.
- Do not queue reactions.
- A MISS never interrupts a reaction.
- A reaction must not generate another HIT or MISS event.

This policy is intended for the prototype and can be revised when we introduce combat timing.

## 6. Animation timing

Use elapsed-time-based playback.

- Reaction begins immediately when HIT is confirmed.
- Each reaction frame lasts approximately 60 ms.
- After 240 ms, the orange boxer returns to idle.
- The existing blue boxer animation continues independently.

Do not use fixed-frame-count assumptions tied to the display refresh rate.

## 7. Debug diagnostics

Preserve all existing debug controls and counters.

Add a small orange-boxer state readout:

- `Orange: idle`
- `Orange: hit_react`

Optionally show the current reaction frame, such as `hit_react 2/4`.

The existing HIT and MISS counters must continue functioning without modification to their meaning.

Debug overlays should remain controlled by the existing Guides setting.

## 8. Pause and interruption handling

- Pausing freezes both boxers' animations.
- Resuming continues the active reaction without restarting it.
- Frame stepping should advance the active animation frames without generating additional punch contacts.
- App interruptions must not leave the orange boxer permanently stuck in `hit_react`.
- Preserve existing movement-input cancellation behavior.

## 9. Validation

Test on an iPhone simulator or physical device where available.

Acceptance criteria:

- [ ] Jab HIT triggers the orange boxer's reaction.
- [ ] Cross HIT triggers the orange boxer's reaction.
- [ ] Jab MISS does not trigger a reaction.
- [ ] Cross MISS does not trigger a reaction.
- [ ] Reaction plays four frames in order.
- [ ] Reaction completes in approximately 240 ms.
- [ ] Orange boxer returns to idle afterward.
- [ ] Orange boxer remains stationary and correctly mirrored.
- [ ] Repeated HIT during an active reaction restarts it without queuing.
- [ ] MISS does not interrupt an active reaction.
- [ ] Pause/resume preserves reaction playback.
- [ ] Frame stepping does not duplicate contact results.
- [ ] Existing movement and punch systems remain functional.
- [ ] HIT and MISS counters remain consistent.
- [ ] No damage, health, stamina, blocking, AI, or knockdown systems are introduced.

## 10. Deliverables

1. Updated Swift source files.
2. Integrated orange hit-reaction animation assets.
3. Minimal reaction-state handling.
4. Brief implementation summary.
5. Device or simulator validation results.
6. Any missing assets or unverified behavior.

**Completion criterion:** Successful Jab and Cross contacts visibly trigger a brief orange-boxer reaction, while missed punches leave the orange boxer idling. All existing movement, punching, and contact-detection functionality remains intact.

## Implementation report — October 19, 2026

Priority: the reaction must look connected to the contact pose, not just move
sometime after the punch. Task 5A.2's corrected root/child rendering and contact
geometry remain intact. No reaction assets existed; the user separately approved
creation of four orange reaction frames with visible recoil already in frame 1.

### Same-render contact/reaction synchronization

The render update now advances the previous orange animation first, then advances
blue's punch and processes its confirmed spatial contact event. A HIT synchronously
starts/restarts HitReactionPlayback at frame zero. applyFrames then assigns both
the blue contact texture and orange's initial recoil texture in that same update.
No asynchronous callback, timer dispatch or deferred SKAction triggers the reaction.
The reaction is not advanced again with the triggering tick's elapsed time, which
would otherwise consume or skip its initial pose.

Frame stepping uses the identical ordering: step the old orange animation, then
step blue and process contact, then apply both textures. Stepping blue into Jab
frame4 or Cross frame5 should therefore display orange hit_react 1/4 immediately.
The next step advances the reaction normally. Counters/detection still use the
existing once-only event; reaction playback cannot create another contact.

Added optional preserveContactPose to PunchPlayback.advance, enabled by the scene:
only when a delayed tick would skip the entire contact pose, it holds that pose
rather than rendering withdrawal alongside a just-starting recoil. At normal
30/60/120 fps the original Jab/Cross timing is unchanged. Under a severe render
hitch, the action may extend instead of skipping its contact pose, consistent with
the existing recovery-pose protection. This occurs for HIT or MISS; it does not
alter reach, contact frame, damage or input rules.

### Orange playback and lifecycle

- New HitReactionPlayback.swift defines minimal idle/hit_react state, four frames
  at60ms (240ms nominal), no looping and no queue.
- HIT starts or restarts frame1, clearing fractional reaction time. MISS has no
  effect, including while another reaction is in progress.
- At completion, orange selects idle frame1 with a reset idle accumulator before
  the regular four-frame/800ms breathing cycle continues.
- Orange's root, facing, scale and baseline are never changed by reaction code.
  Blue's movement lockout, contact geometry, hit/miss counting and punch inputs
  are retained. Reaction runs independently while blue recovers or later moves.
- Pause freezes reaction and punch clocks. Resume preserves the reaction; focus
  loss clears held movement and suspends playback until active again. Scene
  removal explicitly cancels reaction to idle, avoiding a stuck state on reuse.
- The 5B HUD adds Orange: idle or hit_react with frame/4 under the existing Guides
  visibility. No new buttons or quarter-speed control were added.
- Runtime requires all four correctly sized reaction textures. If incomplete,
  reaction is disabled and its missing-assets notice is shown; idle frames are
  never passed off as a reaction. Existing HIT/MISS counters remain meaningful.

### Approved assets and visual limits

Added hit_react_b_0…3 as 512×512 transparent PNG/SVG frames and catalog entries,
plus generate_hit_react.py and review previews. Root remains (256,448).

| Frame | Head/neck image-X offset | Upper-torso/arms X | Purpose |
| --- | --- | --- | --- |
| 1 | −6px | −4px | Immediate visible impact recoil |
| 2 | −14px | −9px | Peak recoil |
| 3 | −7px | −4px | Recovery begins |
| 4 | −1px | −0.5px | Near guard |

Negative source-image X becomes positive scene X under orange's existing mirror,
so the head and upper body recoil away from blue. Torso lean tapers into stationary
hips; feet, pelvis and lower body stay unchanged. Arm segment lengths and head size
are preserved. First frame is deliberately not idle. Final near-guard pose differs
only slightly from idle, reducing the return snap.

The generator uses the existing offline rig/Pillow renderer, extended only with an
optional rear-arm layer-order setting. Existing default rendering is unchanged.
No runtime per-limb animation, root knockback, health, damage, blocking, AI, stamina,
knockdowns or camera/flash effects were introduced. The recoil is intentionally
small; phone-size readability and perceived impact still require a recording.

Preview artifacts:

- IdleAnimation/preview/hit_react_contact_sheet.png (source right-facing view).
- IdleAnimation/preview/hit_react_b.gif (mirrored runtime-facing view, loops only
  for inspecting the four poses; the actual game reaction never loops).

### Checks performed

Passed `python Tests/validate_task5b.py`:

- Four RGBA512×512 frames with valid catalog/source pairs, transparent margins,
  distinct initial recoil, unchanged lower body/feet/pelvis and original arm lengths.
- Recoil direction under mirroring, four60ms GIF frames, target source membership.
- Scene update/step ordering starts reaction before both textures are applied;
  pause guard precedes animation advancement; only layout assigns orange root.
- Re-rendering every validated cross with the extended renderer remains pixel
  identical. Previous Task4A/4B/3B and Task5A.2 geometry checks also still pass.

These are source, asset and numerical checks, not execution of SwiftUI/SpriteKit.
Added Tests/HitReactionChecks.swift to exercise the actual Swift clocks for HIT,
MISS, restart, completion, step/cancel and same-tick contact/recoil at30/60/120fps,
including a delayed contact tick. Could not run Swift tests here: this Windows
host has no swiftc, Xcode or iOS runtime. On Mac:

```sh
swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Boxer0/HitReactionPlayback.swift Tests/HitReactionChecks.swift -o /tmp/reaction-checks
/tmp/reaction-checks
```

### Installation and pending device validation

Rebuild the iOS target and verify the “5B” label. If copying into the separate
Shared/iOS/macOS project, include the new HitReactionPlayback.swift in the iOS
target, plus updated IdleTestScene.swift, ContentView.swift, JabPlayback.swift and
the four hit_react_b image sets. This checkout's Xcode membership is already set.

At close range, record one Jab and one Cross with Guides enabled. The first
orange recoil should be visible in the same rendered frame as blue's contact
pose/HIT marker. Inspect that relationship, not just whether orange moves later.
Retreat and confirm both misses leave orange idle. Pause/step into each contact
frame, verify hit_react1/4 immediately, then step/resume through four poses and
idle. Check stationary orange root, matching scale/facing, counters J+C=H+M and
background/foreground. Restart-on-new-HIT policy is covered by the pure test;
normal one-shot blue punches may be too far apart to overlap the240ms reaction.

Swift compilation, on-device visual timing/readability, pause/step touch behavior,
interruption handling and full acceptance are pending. No device validation of
Task5B has yet been recorded.
