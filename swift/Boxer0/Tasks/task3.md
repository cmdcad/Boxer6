


# Boxer0 — Task 3A: Basic Fighter Movement and Footwork

## Objective

Extend the existing SpriteKit idle scene with horizontal movement and advance/retreat footwork animations.

Preserve all completed Task 2 functionality. Inspect the current project and asset catalog before modifying anything.

## Scope

1. **Asset inspection**
   - Check whether six-frame `advance` and `retreat` clips exist for both palettes.
   - If present, use them according to the existing sprite specification.
   - If absent, report the missing clips. Do not substitute idle frames or generate replacement artwork without approval.
2. **Fighter movement**
   - Enable player control of the blue boxer only.
   - Keep the orange boxer stationary and playing idle.
   - Move the blue boxer's SpriteKit root horizontally, independently of its animation frames.
   - Preserve vertical baseline alignment.
   - Use an initial configurable speed of 100 scene points per second.
3. **Footwork animation**
   - Advance: six frames, 480 ms per cycle.
   - Retreat: six frames, 480 ms per cycle.
   - Loop while the corresponding direction is held.
   - Return to the existing four-frame idle animation when released.
   - Keep animation transitions free of obvious snapping.
4. **Controls**
   - Add two clearly labeled press-and-hold controls: Retreat and Advance.
   - Support simultaneous touch handling without leaving movement stuck.
   - Stop movement when the app loses focus or the scene is interrupted.
   - Preserve existing debug controls for pause, frame stepping, speed, and overlays.
5. **Movement boundaries**
   - Prevent the blue boxer from leaving the visible playable area.
   - Maintain a minimum separation between fighters.
   - Use configurable boundaries based on boxer dimensions, not unexplained hard-coded screen coordinates.
   - Ensure both boxers remain on the same baseline.
6. **Debugging**
   - Display the active animation state: idle, advance, or retreat.
   - Optionally display horizontal root position.
   - Make the existing slow-playback control apply consistently to the animation clips.
   - Preserve frame stepping for the active clip.

## Acceptance criteria

- Blue boxer advances and retreats while the orange boxer remains idle.
- Movement is continuous and frame-rate independent.
- Footwork animation plays at the correct duration.
- Feet do not visibly slide or cross within the animation.
- Both fighters maintain consistent proportions and baseline alignment.
- Releasing movement returns the boxer to idle.
- Neither boxer overlaps improperly or leaves the permitted area.
- Existing Task 2 controls remain functional.
- No combat, health, stamina, AI, or attack systems are added.

## Validation

Test in landscape on an iPhone simulator or physical device where available.

Report which behaviors were verified and identify any that could not be tested. Preserve completed work and avoid unrelated refactoring.

### One important design decision

I recommend continuous root movement with looping shuffle animations, rather than moving the fighter a fixed distance every time a six-frame animation completes. This will give us smoother, more responsive controls and make future movement balancing easier.


## Continuation status — October 18, 2026

Task 3A code and assets are present. This continuation preserved the existing
artwork and movement design and addressed the following gaps:

- Replaced drag gestures with independent UIKit touch surfaces that track all
  touches per control and release on cancellation or removal. Holding both
  directions selects idle; releasing one leaves the other direction active.
- Reset the scene clock on focus loss, removal, presentation, and scene pause
  to prevent stale elapsed time from producing movement after interruption.
- Restored orange idle frame stepping alongside the blue active clip.
- Corrected collision/edge extents to the measured union of all 32 frame alpha
  bounds: x=149..<398 on the 512-pixel canvas. The existing dimension-based
  separation factor and configurable 100-point/second speed remain in use.

Validation performed on Windows:

- All 24 footwork and 8 idle catalog frames exist, are RGBA 512 × 512, have
  valid catalog JSON references, and match the corresponding source PNGs.
- Boundary equations preserve edge padding and minimum separation at
  568×320, 667×375, 844×390, 932×430, and 1024×768 scene sizes.
- Animation timing and continuous movement equations checked at 30, 60, and
  120 fps with normal and quarter animation playback. These are numerical
  checks of the equations, not execution of SpriteKit or compiled Swift.

Still requires Xcode on macOS / an iPhone:

- Compile and run the landscape scene; no Swift compiler or iOS simulator is
  installed in this Windows environment.
- Exercise simultaneous holds, release order, system touch cancellation,
  background/foreground, scene interruption, pause/resume, active-clip frame
  stepping, slow playback, and guide visibility on the actual app.
- Visually assess transition snapping, planted-foot sliding, limb proportions,
  baseline alignment, and fighter separation during movement. Existing in-place
  footwork is retained; absence of visible sliding has not been established.

Task 3A is implemented but device acceptance remains pending.


### Follow-up: movement controls missing on iPhone

The bottom controls contained a horizontal ScrollView with no height constraint.
That flexible view could consume the available vertical space and push the
movement row offscreen. Constrained the debug strip to 54 points and the control
stack to its content height. Added explicit 52-point movement targets labeled
“Hold Retreat” and “Hold Advance”, with explicit dark text for contrast. The
controls remain within the safe area while the SpriteKit background fills the
screen. No fighter layout or input semantics changed.

Source review confirms the bounded debug strip and both movement controls are
included in ContentView. iPhone rendering and interaction still require a rebuilt
app from Xcode; they cannot be verified on this Windows host.
