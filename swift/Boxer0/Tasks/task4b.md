# Boxer0 — Task 4B: Rear-Hand Cross Animation & Input

## Scope and acceptance

The complete Task 4B brief was received October 19, 2026. Task 4A was validated
by the user. Preserve Tasks 2–4A; add a distinct rear-hand cross with protective
lead glove, torso rotation and shoulder movement. Use explicit optional bindings
(`if let value = value`), not shorthand.

| Punch | Frames | Per frame | Total | Contact (zero-based) | Contact time |
| --- | --- | --- | --- | --- | --- |
| Jab | 6 | 50 ms | 300 ms | 3 | 150 ms |
| Cross | 8 | 60 ms | 480 ms | 4 | 240 ms |

Both are one-shot, elapsed-time actions. No interruption, hold repetition or queue.
Both must present final recovery, then idle frame 1. Movement is canceled and
velocity zeroed on start; root stays fixed during punches; fresh directional
input is required after completion. Orange stays idle. Preserve pause/resume,
frame stepping, guides, state/frame/position/velocity and diagnostic contact events.
Pause preserves punch progress; focus interruptions clear input and resume the
active punch without creating another. No damage, health, stamina, AI, hit regions,
collisions or opponent reactions. Normal gameplay is 1×; no speed button.

## Implemented

- Generalized the existing JabPlayback.swift into PunchKind and PunchPlayback,
  using one timer and recovery/contact mechanism. Kept its file/target membership
  to avoid an unnecessary migration. Jab's default timing is unchanged.
- Added cross state and matching touch-down Jab/Cross buttons side by side.
  Both reject presses during any active punch. Status shows “4B”, current frame
  and total, signed velocity, root X and independent J/C contact counters. Contact
  is highlighted while the active punch is at its contact pose.
- Shared start/completion handling clears movement touches and stops velocity.
  Active punches bypass translation. Completion selects idle frame zero (display
  frame 1) and clears input again. Direction presses during punches are ignored.
- Shared pause, step, interruption and removal handling retains Task 4A safeguards.
  A delayed tick must still show final recovery; severe stutter can extend a punch
  rather than consume its recovery pose offscreen. First-render seeding may add
  up to one render interval to nominal press-to-finish time.
- Removed remaining shorthand optional bindings. No new source file is needed
  for runtime: copy the updated JabPlayback.swift, IdleTestScene.swift and
  ContentView.swift if working in the separate Shared/iOS/macOS project.

## Approved cross assets

Repository inspection found no cross frames. The user separately approved creating
all eight from the existing editable rig. Added cross_a_0 through cross_a_7 as
PNG/SVG source frames and catalog image sets, with generate_cross.py and review
previews. No jab or footwork frames were substituted or overwritten.

Poses: ready; beginning rotation; weight transfer; rear-arm extension; contact;
withdrawal; recovery; guard. Blue only, 512×512 transparent, root (256,448), same
baseline, canvas and scale. Front guard glove closes toward the face while the
rear shoulder advances and the torso silhouette turns/leans over the planted
stance. The lower body/feet remain fixed. Arm segment lengths remain those of
the existing rig, using offline pose solving only. There is no runtime IK.

Ready and final guard are pixel-identical to idle_a_0. Offline rendering helpers
now accept optional rear-arm/torso/head pose parameters; existing default and jab
rendering still reproduce their original pixels. The short-armed, flat rig limits
reach and depth; this is a stylized projected turn rather than a 3D rotation.
Visual distinction and readability at phone size still need device review.

Artifacts:

- IdleAnimation/generate_cross.py
- IdleAnimation/frames/cross_a_0…7.png and .svg
- Boxer0/Assets.xcassets/cross_a_0…7.imageset
- IdleAnimation/preview/cross_contact_sheet.png
- IdleAnimation/preview/cross_a.gif (loops only for reviewing the poses)

All eight frames are now present. Runtime still checks for complete, correctly
sized sets and disables a punch with an asset notice if a set is incomplete.

## Validation results

Passed on Windows:

- `python Tests/validate_task4b.py`: shared playback integration, both consistent
  input controls, explicit optional bindings, structural checks, eight transparent
  frames, valid catalog/source pairs, fixed lower legs/feet, exact guard endpoints,
  original arm lengths and protective glove proximity. GIF has eight 60 ms frames.
- The same check re-renders all six existing jab poses with the extended renderer
  and confirms pixel equality to the validated jab PNGs.
- `python Tests/validate_task4a.py`: existing jab asset checks still pass.
- `python Tests/validate_task3b.py`: original 32 idle/footwork assets still match.
- Visually reviewed the cross contact sheet, including extension, lead guard,
  torso shift and guard recovery. This is not an iPhone runtime test.

Tests/PunchPlaybackChecks.swift exercises the actual shared Swift type for both
punches: nominal timing/contact, mutual exclusion, no queue, stepping, once-only
contact, final recovery and all poses at 30/60/120 fps. Swift tests cannot execute
on this Windows host without swiftc. On Mac, from this project directory:

```sh
swiftc Boxer0/JabPlayback.swift Tests/PunchPlaybackChecks.swift -o /tmp/punch-checks
/tmp/punch-checks
```

Xcode compilation and iPhone SE acceptance remain pending. Rebuild the iOS target
and check the “4B” status plus Jab and Cross buttons. Validate cross frames 1/8–8/8,
contact count at frame 5, jab regression, independent taps, holding, mixed rapid
taps, no queued actions, fresh movement input after recovery, pause/step/resume
for each punch and background/foreground. Confirm orange idle and phone-size
visual quality. Task 4B is implemented; device validation is not yet recorded.


## User acceptance — October 19, 2026

User confirmed Task 4B validated while supplying Task 5A. Device acceptance is
recorded; this does not assert that Swift tests executed on this Windows host.
