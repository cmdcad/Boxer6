# Boxer0 — Task 3B: Footwork Refinement

## 1. Objective

Refine the existing SpriteKit movement system to produce smoother, more convincing boxing footwork.

The blue boxer remains player-controlled. The orange boxer remains stationary and continues its idle animation.

**Important:** Inspect the current source code and assets before making changes. Preserve all completed Task 2 and Task 3A functionality.

Do not introduce attacks, AI, health, stamina, or combat mechanics.

## 2. Movement acceleration and deceleration

Replace instantaneous movement-speed changes with controlled acceleration and deceleration.

Initial tuning values:

| Property | Initial value |
|---|---|
| Maximum movement speed | 100 scene points/second |
| Acceleration | 600 points/second² |
| Deceleration | 900 points/second² |
| Direction reversal | Decelerate before accelerating in the opposite direction |
| Dead zone | 2 points/second |

These values are configurable prototype defaults.

Requirements:
- Movement begins smoothly when a direction is pressed.
- Releasing movement brings the boxer to a quick, controlled stop.
- Reversing direction should not produce an abrupt position jump.
- Horizontal movement must remain frame-rate independent.
- Preserve the existing boundaries and minimum fighter separation.

## 3. Footwork and animation synchronization

Continue using the existing six-frame advance and retreat clips.

- Advance: 480 ms per cycle.
- Retreat: 480 ms per cycle.
- Idle: four frames, 800 ms per cycle.

Movement and animation must remain coordinated.

Requirements:
- Advance and retreat animations play while the fighter moves in their respective directions.
- Animation playback responds appropriately to acceleration and deceleration.
- Avoid rapid switching between idle and movement states near zero velocity.
- Keep both feet visually connected to the floor during planted phases.
- Do not move the sprite vertically to simulate steps.
- Preserve the original canvas, anchor point, and sprite proportions.

Use the existing artwork initially. If its poses cannot produce convincing planted-foot movement, document the limitation rather than silently changing the assets.

## 4. Foot planting and sliding reduction

Improve the relationship between root translation and footwork frames.

The current implementation translates the fighter continuously while cycling through six animation frames. This may cause visible sliding when a foot is supposed to be planted.

For this milestone:

1. Inspect the existing footwork frames and identify their planted-foot phases.
2. Determine whether the root displacement across the animation cycle reasonably matches the visible steps.
3. Adjust animation timing or movement tuning to reduce obvious sliding.
4. Preserve smooth horizontal movement without abrupt frame-by-frame position jumps.

Do not introduce a full inverse-kinematics system, physics-based locomotion, or per-limb runtime animation.

If precise foot locking requires revised sprite frames or additional pose metadata, report that dependency for a later asset task.

## 5. Animation transitions

Improve transitions between:

- Idle → Advance
- Advance → Idle
- Idle → Retreat
- Retreat → Idle
- Advance → Retreat
- Retreat → Advance

Requirements:
- Avoid unnecessary resets of animation frames.
- Prevent visible snapping or sudden changes in body posture where practical.
- Ensure a stopped fighter returns to a stable guard.
- Keep transitions deterministic and straightforward to debug.

Do not add elaborate blending systems or extra animation clips at this stage.

## 6. Controls and playback

Preserve the existing press-and-hold Advance and Retreat controls.

- Normal gameplay uses **1× playback only**.
- Remove the quarter-speed button from the visible interface.
- Quarter-speed functionality may remain internally for development purposes.
- Preserve pause/resume, frame stepping, and guide overlays as development diagnostics.
- Prevent held movement input from unexpectedly restarting movement after pause/resume.
- Cancel movement safely when the app loses focus or the scene disappears.
- If both movement buttons are held, use neutral directional input and decelerate normally.

Keep controls responsive on an iPhone touchscreen.

## 7. Boundaries and collision spacing

Retain the existing horizontal movement constraints.

Improve their reliability where necessary:

- The boxer cannot move outside the playable area.
- The blue boxer cannot pass through or overlap the orange boxer.
- Minimum spacing is calculated from the fighters' visible dimensions.
- Velocity must reset appropriately when reaching a movement boundary.
- No jitter or repeated pushing against boundaries.
- Preserve baseline alignment at all times.

This is movement spacing only, not a combat collision system.

## 8. Development diagnostics

Preserve the existing development controls and position display.

Add a horizontal velocity readout if useful for tuning.

Diagnostics should be isolated from gameplay behavior so they can later be hidden or disabled in production builds.

Avoid adding unnecessary on-screen controls.

## 9. Validation and acceptance

Test the implementation in landscape on an iPhone simulator or physical device where available.

Confirm:

- [ ] Acceleration is smooth and responsive.
- [ ] Releasing movement produces controlled deceleration.
- [ ] Direction reversal does not cause a position jump.
- [ ] Idle and movement transitions remain visually stable.
- [ ] Foot sliding is reduced compared with Task 3A.
- [ ] Boxer proportions, facing, and baseline remain unchanged.
- [ ] Movement boundaries work without jitter.
- [ ] Simultaneous directional input is handled correctly.
- [ ] Pause/resume does not unexpectedly restart movement.
- [ ] The quarter-speed control is no longer visible.
- [ ] Existing debug controls remain functional.
- [ ] No combat or AI functionality has been introduced.

## 10. Deliverables

1. Updated Swift source files containing the refined movement implementation.
2. A concise explanation of the movement and animation changes.
3. Any asset limitations discovered during foot-planting analysis.
4. Simulator/device validation results, identifying unverified behavior.

Do not replace completed functionality unnecessarily.

**Completion criterion:** The blue boxer advances, retreats, stops, and changes direction smoothly, with visibly improved footwork and stable positioning.


Implementation priority
I recommend implementing Task 3B in this order: acceleration/deceleration → animation transitions → foot sliding reduction → boundary verification.

One important distinction: acceleration alone will not fix foot sliding. The six-frame artwork must also depict believable weight transfer, and the animation timing must correspond reasonably to the distance traveled.

## Implementation report — October 19, 2026

Implemented in FootworkMotion.swift, IdleTestScene.swift, and ContentView.swift.
FootworkMotion.swift is registered in the checked-in Xcode target's Sources phase.
If using the separate Shared/iOS/macOS project shown in the earlier screenshot,
include this new Swift file in its iOS target along with the updated existing files.

### Motion and transitions

- Defaults: maximum 100 points/s, acceleration 600 points/s², deceleration
  900 points/s², braking dead zone 2 points/s. Scene properties expose tuning.
- Exact constant-acceleration integration splits a tick at target speed and
  braking endpoints. Opposite input first decelerates to the dead zone, zeros
  velocity, then accelerates in the new direction with the remaining tick time.
- Full-speed acceleration takes about 167 ms. Full-speed release braking takes
  about 109 ms and travels about 5.55 points. Release/both-held neutral uses this
  normal braking. Focus loss, disappearance, pause, and frame stepping stop
  immediately and invalidate held input for safety.
- Blue animation follows actual displacement direction, including during reversal
  braking. Its clock advances by actual distance / maximum speed, so cadence
  slows during acceleration/deceleration and stops at walls. The 480 ms cycle
  applies at full speed. Orange idle remains four frames / 800 ms, with no travel.
- Phase is retained while the clip stays the same. Actual clip changes use the
  shared guard frame zero; pixel comparison confirms footwork frame zero equals
  idle frame zero. Pause freezes the active clip for frame stepping. Resume goes
  to stable idle and requires fresh input. No additional clips or blending added.
- Existing union-alpha bounds, spacing factor, anchor, mirroring, proportions and
  baseline are retained. Clamping resets velocity, including when a held input
  keeps pushing at a wall. Root Y is never animated.

### Foot-planting analysis and limitations

Inspected the existing contact sheet, PNGs and editable generator pose data.
The following applies identically to both palettes (frame numbers are zero-based):

| Frame | Advance | Retreat |
|---|---|---|
| 0 | Both planted; shared rest | Both planted; shared rest |
| 1 | Rear planted, lead lifted 11 px | Lead planted, rear lifted 11 px |
| 2 | Both planted, lead offset +10 px | Both planted, rear offset −10 px |
| 3 | Lead planted, rear lifted 10 px | Rear planted, lead lifted 10 px |
| 4 | Both planted, feet recovering | Both planted, feet recovering |
| 5 | Both planted, near rest | Both planted, near rest |

Timing changed from 80 ms each to [40, 140, 40, 140, 60, 60] ms, still totaling
480 ms at full speed. Double-support exposure decreases from 320 to 200 ms per
cycle. This is a conservative timing adjustment intended to reduce obvious
all-feet-planted gliding; it is not proof of better visual foot locking.

At 100 points/s a full cycle translates the root 48 points. The greatest local
foot offset is only 10 canvas pixels (10 × fighterScale scene points); it returns
to zero each loop. On the compact SE layout this is only a few scene points.
The artwork therefore does not encode a stride matching the requested speed.
Advance also moves some planted-foot offsets in the same direction as root
travel. Retiming alone cannot keep those feet fixed on the floor.

No artwork was changed. Precise locking requires a later asset task: larger,
direction-correct support-foot offsets and weight transfer, plus support-foot and
stride-distance metadata. Remaining sliding and a possible foot pose snap when
stopping mid-lift must be judged on device. No visual improvement is claimed as
verified yet. No IK, runtime limb animation, physics, attacks, combat or AI added.

### UI and input

- Visible speed control removed; gameplay defaults to 1×. Internal setSpeed remains
  available for development. Pause/Resume, active-clip Step and Guides remain.
- Status reads “3B”, animation state, X position, and signed velocity (points/s).
- ContentView.showsDevelopmentDiagnostics hides status/debug controls without
  changing locomotion. Press-and-hold movement controls remain visible.
- Pause/step/focus cancellation clears scene input and changes an input generation
  token. Native touch surfaces discard prior fingers on token changes; continued
  holding cannot restart motion. Inputs begun while paused are rejected.

### Validation

Run: python Tests/validate_task3b.py (requires Pillow).

Passed here: all 32 catalog/source PNG pairs still match, RGBA/512×512 validation,
480 ms timing sum, visible speed-button removal and Xcode motion source membership.
Reviewed dimension constraints at SE and larger landscape sizes, including the
reserved bottom panel. These checks do not execute SwiftUI or SpriteKit.

Tests/FootworkMotionChecks.swift exercises the actual pure Swift motion model:
acceleration distance/speed, neutral stopping distance, dead-zone settling,
stop-before-reversal, explicit stop reset and matching trajectories at 30/60/120
fps. The tests could not run here: no swiftc, Xcode, or iOS runtime is installed.
On the Mac, from this project's directory:

```sh
swiftc Boxer0/FootworkMotion.swift Tests/FootworkMotionChecks.swift -o /tmp/footwork-checks
/tmp/footwork-checks
```

Device acceptance is pending for Task 3B (Task 3A's earlier video is not evidence
for the new tuning). Rebuild the iOS target and verify the “3B” status, hold/release,
reversal, both-held neutral, both walls, pause while holding followed by resume,
frame stepping and guides. Also test focus loss and judge sliding/transitions
against the Task 3A recording. Record results before marking visual acceptance.


## User acceptance — October 19, 2026

User confirmed Task 3B validated while supplying Task 4A. Proceeding with Task 4A;
this records device acceptance, not an assertion that Windows ran Swift tests.
