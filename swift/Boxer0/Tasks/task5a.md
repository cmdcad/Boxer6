# Boxer0 — Task 5A: Punch Range and Contact Detection

## 1. Objective

Extend the existing Swift/SpriteKit boxing prototype with basic spatial punch-contact detection.

The blue boxer remains player-controlled. The orange boxer remains stationary and idle.

When the blue boxer throws a jab or cross, the system must determine whether the punch reaches the orange boxer's target region at the designated contact frame.

Preserve all completed functionality from Tasks 2, 3A, 3B, 4A, and 4B.

Inspect the latest Swift source files, animation assets, and existing punch-contact marker implementation before modifying anything.

Do not rebuild working systems unnecessarily.

**Do not add damage, health, stamina, blocking, AI, knockdowns, or hit reactions.**

## 2. Detection model

Use a lightweight, deterministic geometric detection system.

For this milestone, implement:

- A punch-contact point associated with the attacking glove.
- A target region associated with the defending boxer's upper body.
- A range check evaluated when the punch reaches its designated contact frame.

Use SpriteKit scene coordinates for all calculations.

Do not use SpriteKit physics bodies or a full collision engine yet.

Detection must remain independent of the visible sprite's alpha pixels.

## 3. Punch contact points

The existing sprite specification defines named glove-center points for animation frames.

Use these points if the corresponding metadata is available.

For each punch:

| Punch | Contact frame | Zero-based index |
|---|---|---|
| Jab | Frame 4 of 6 | 3 |
| Cross | Frame 5 of 8 | 4 |

Requirements:

1. Identify the attacking glove's center at the contact frame.
2. Transform the point from the 512 × 512 sprite canvas into SpriteKit scene coordinates.
3. Account for sprite scaling, anchor position, and horizontal mirroring.
4. Evaluate contact using the actual attacking glove location.

If the existing assets lack reliable glove-center metadata, use explicitly documented provisional offsets.

Do not claim provisional offsets are artist-authored metadata.

Keep jab and cross contact positions separately configurable.

## 4. Defender target region

Define one provisional upper-body target region for the orange boxer.

For Task 5A, use a simple ellipse or rectangle covering the torso and head area.

The region must:

- Follow the orange boxer's SpriteKit root position.
- Respect sprite scaling and mirroring.
- Remain independent of transparent image padding.
- Be configurable for future tuning.
- Avoid extending unrealistically into the empty space between fighters.

Prefer a single torso-centered region initially.

Do not introduce separate head and body damage zones yet.

## 5. Contact evaluation

Evaluate a punch exactly once when its contact frame is entered.

A punch connects when the attacking glove's contact region intersects the defender's target region.

Use a small configurable glove radius rather than treating the glove as an infinitely small point.

The result must be one of:

- **Hit:** Contact regions overlap.
- **Miss:** Contact regions do not overlap.

A punch must not register multiple hits while its contact frame remains displayed.

Do not continuously evaluate contact throughout the entire punch animation.

For this prototype, only the designated contact frame can produce a hit.

## 6. Range and movement interaction

Preserve the existing movement restrictions.

- Punching stops the blue boxer's horizontal movement.
- The boxer remains stationary during the punch.
- The orange boxer remains stationary.
- Movement resumes only after the punch completes and the player presses a direction again.

Test contact at different fighter separations.

Expected behavior:

- Far apart: Jab and Cross miss.
- Within jab reach: Jab may connect.
- Within cross reach: Cross may connect.
- At the existing minimum separation: Contact detection remains stable.

Do not automatically move either boxer into punching range.

Do not extend a punch artificially to guarantee contact.

## 7. Shared contact result

Introduce a small reusable result type.

Suggested structure:

```swift
enum PunchContactResult {
    case hit
    case miss
}
```

Associate the result with the active punch type and contact event.

Keep the implementation extensible so later tasks can use the result for hit reactions and damage without rewriting detection.

Do not implement those effects now.

## 8. Debug visualization

Add optional debug overlays showing:

- The blue boxer's attacking glove contact point.
- The orange boxer's target region.
- The attacking glove's contact radius.
- The latest punch result: HIT or MISS.

Use different visual treatments for successful and unsuccessful contact.

The debug overlays must follow the fighter positions and respect the current scene scale.

Integrate the overlays with the existing Guides control.

Keep them out of production gameplay rendering.

## 9. Debug counters

Preserve the existing jab and cross contact-frame counters.

Add separate hit and miss counters.

Suggested display:

| Counter | Meaning |
|---|---|
| Jab contacts | Jab contact frames reached |
| Cross contacts | Cross contact frames reached |
| Hits | Successful spatial contacts |
| Misses | Unsuccessful spatial contacts |

The counters must remain logically consistent.

For example, after five completed punches whose contact frames were reached:

`Jab contacts + Cross contacts = Hits + Misses`

Frame stepping must not accidentally duplicate results.

A punch cancelled before reaching its contact frame must not count as either a hit or a miss.

## 10. Coordinate correctness

The original sprite contract uses:

- Canvas: 512 × 512 pixels.
- Root: (256, 448).
- Image coordinates: origin at top-left, positive Y downward.
- Runtime: SpriteKit scene coordinates, positive Y upward.

Implement a reusable coordinate conversion method.

It must account for:

1. Image-space coordinates.
2. Root offset.
3. Fighter scale.
4. Horizontal mirroring.
5. Current SpriteKit root position.

Avoid scattering coordinate-conversion calculations throughout the contact system.

## 11. Pause and interruption behavior

- Pausing must freeze punch playback.
- Resuming must not generate a duplicate contact event.
- Frame stepping into the designated contact frame may evaluate contact once.
- Stepping repeatedly while on the same frame must not duplicate the result.
- App interruptions must not leave input or detection state stuck.
- A new punch must reset its own contact-evaluation state.

## 12. Validation

Test on an iPhone simulator or physical device where available.

Acceptance criteria:

- [ ] Jab contact is evaluated at frame 4.
- [ ] Cross contact is evaluated at frame 5.
- [ ] Contact uses the attacking glove position.
- [ ] Defender target follows the orange boxer.
- [ ] Contact works correctly with mirrored sprites.
- [ ] Distant punches register MISS.
- [ ] In-range punches register HIT.
- [ ] Every punch produces at most one result.
- [ ] Pausing does not duplicate contact.
- [ ] Frame stepping does not duplicate contact.
- [ ] Debug overlays align with the actual sprites.
- [ ] Hit and miss counters remain consistent.
- [ ] Movement and existing punch playback still work.
- [ ] No damage, health, stamina, AI, or hit reactions are introduced.

## 13. Deliverables

1. Updated Swift source files.
2. Reusable punch-contact detection logic.
3. Configurable provisional glove and defender target geometry.
4. Debug overlays and hit/miss counters.
5. Brief implementation summary.
6. Device/simulator validation results.
7. A list of unverified behaviors or geometry limitations.

**Completion criterion:** The blue boxer can throw a jab or cross at different distances, and the system reliably reports HIT or MISS based on the attacking glove's actual contact position relative to the orange boxer's target region.

## Implementation report — October 19, 2026

Task 4B was validated by the user before this milestone. Implemented Task 5A in
PunchContact.swift, IdleTestScene.swift and ContentView.swift. PunchContact.swift is
registered in this Xcode project's Sources phase. If copying to the separate
Shared/iOS/macOS project, add the new file to its iOS target too.

### Reusable geometry and contact event

SpriteCanvasTransform converts top-left image coordinates to scene coordinates
using the actual node anchor, node size relative to the 512-pixel canvas, signed
X scale (including mirroring), Y scale and scene root position. Image Y is inverted.
For the standard anchor, this is:

```
sceneX = rootX + (imageX - 256) * signedScaleX
sceneY = rootY + (448 - imageY) * scaleY
```

The same converter transforms the defender rectangle and glove radius. Current
fighters are axis aligned and uniformly scaled. Non-uniform scale uses the smaller
absolute axis for a conservative circular radius; future rotated/parent-transformed
fighters would require extending the transform. Current roots are direct scene
children with no runtime rotation.

Configurable provisional image-space geometry (canvas pixels):

| Geometry | Default | Provenance |
| --- | --- | --- |
| Jab center | (384.5,189) | jab_a_3.svg lead-glove ellipse + translate(20,-3) |
| Cross center | (378,186) | cross_a_4.svg rear-glove ellipse + translate(82,0) |
| Jab radius | 20 | Provisional tuning, within the drawn glove |
| Cross radius | 18 | Provisional tuning, approximately the drawn glove |
| Defender upper body | Rect x220 y127 w88 h173 | Provisional head/torso envelope |

These are documented prototype defaults derived from generated artwork, not an
artist-authored sprite-contract metadata file. No runtime alpha-pixel tests occur.
The target is a single rectangle and does not track every idle-pose contour.

Circle-vs-rectangle detection uses the nearest point on the rectangle, including
correct corner distances and tangent contact. PunchContactResult is HIT or MISS.
PunchContactEvent associates result, punch type, sequence and sampled scene geometry.
The optional scene onPunchContact callback exposes that event for future tasks;
no gameplay effects subscribe to it in this milestone.

### One result per punch

The existing PunchPlayback contact marker is the only evaluation trigger: Jab
frame index 3 and Cross index 4. PunchContactTracker begins on an accepted punch,
rejects duplicate/wrong-kind evaluations, and finishes on completion or explicit
scene removal. New punches reset their evaluation flag. Pause, stepping and focus
interruptions retain the active punch's evaluation state. Cancellation before
contact yields no result; cancellation after contact retains the recorded result.

Jab/Cross marker counters and Hit/Miss counters now share the same guarded update:
`jabContacts + crossContacts == hits + misses`. Returning to an active contact
pose cannot duplicate a result. No detection polling occurs during other punch
frames or throughout ordinary idle/movement updates.

### User-approved spacing change

The earlier glove/silhouette spacing required a root separation of 338.78 canvas
units. Actual reach against the chosen target is only 200.5 units for Jab and
192 for Cross, including glove radius. Accurate contact would therefore always
miss at every legal position. The user approved switching to torso-based spacing.

Movement now uses physical torso X bounds 220…308 and a configurable minimum body
gap factor of 0.8 times torso width. Minimum root separation is:
`2*(308-256) + 0.8*(308-220) = 174.4` canvas units, scaled into scene points.
Bodies remain apart; movement does not cross the orange root. Existing visible
edge padding, velocity reset at boundaries, baseline, root positioning during
punches and fresh-input rules are preserved. This spacing configuration is
separate from contact target tuning, so resizing a target does not move a boundary.

No punch reach, artwork or target geometry was enlarged to guarantee hits. Both
punches miss at their original starting separation and can hit near the new close
boundary. Jab currently reaches slightly farther than Cross because that is what
the validated artwork depicts. The flat, wide-footed sprites may visually overlap
feet or guard gloves at close range; torso separation is now the positioning rule.
No automatic movement into range or physics/combat collision engine was added.

### Diagnostics and presentation

- Status identifies this build as “5A” and preserves state, frame/total, position
  and signed velocity. Counters read J (jab), C (cross), H (hits), M (misses).
- Guides now includes the orange upper-body target rectangle, blue glove-center
  dot and glove-radius circle. The attacking marker appears only while its
  contact-frame pose is displayed so it does not float away during withdrawal.
  HIT uses green; MISS uses red. The target remains orange.
- The latest result label (“JAB · HIT”, “CROSS · MISS”, etc.) persists in the scene's
  top-left corner. Toggling Guides hides contact overlays and this result label.
- Contact overlay geometry follows current root positions and scale. It does not
  re-evaluate a past result after movement or a resize.
- ContentView.showsDevelopmentDiagnostics also disables scene guides/overlays when
  diagnostics are hidden for production presentation. No additional on-screen
  buttons or speed controls were added.

### Verification results

Passed here with `python Tests/validate_task5a.py`:

- Both configured glove centers exactly match the attacking SVG ellipses and
  transforms at the correct contact frames.
- Independent image-space reach calculations establish original-spacing misses
  and close-range overlap at the approved torso-based minimum for both punches.
- Starting distance misses, edge visibility and valid movement intervals at five
  landscape scene sizes, including the reserved control panel on iPhone SE.
- Exactly one scene evaluation call, inside contact-marker handling; target source
  membership, explicit optional bindings, structural checks, and no physics bodies.

Existing checks also pass:

- `python Tests/validate_task4b.py`: eight cross assets, defensive glove, fixed
  feet, segment lengths, recovery and original jab rendering.
- `python Tests/validate_task4a.py`: six original jab assets and timing preview.
- `python Tests/validate_task3b.py`: original 32 idle/footwork assets and metadata.

Tests/PunchContactChecks.swift tests the actual Swift geometry/tracker types:
root/Y inversion, custom anchors, scale, mirrored attacker and defender, circle
corners/tangency, near/far cases, four scales, once-only results, cancellation,
frame-stepping integration and counter consistency. It was not run here because
this Windows host lacks swiftc, Xcode and an iOS runtime. On Mac:

```sh
swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Tests/PunchContactChecks.swift -o /tmp/contact-checks
/tmp/contact-checks
```

### Device acceptance pending

Rebuild the iOS target and check “5A”. From starting positions, Jab and Cross should
report MISS. Hold Advance to the close boundary, release and punch: both should
report HIT. Retreat and test the reach edge. With Guides enabled, pause and step
into Jab frame 4 or Cross frame 5 to inspect circle/target alignment and the one
counter increment. Resume or step through recovery and confirm no duplicate.
Check Guides off, fresh movement input after punches, interruptions and orange
idle. Confirm the invariant J+C=H+M throughout. Visual geometry tuning, iPhone
layout, touch behavior and Swift compilation remain unverified here.

No artwork changes, damage, health, stamina, blocking, AI, knockdowns, opponent
reactions or combat effects were introduced. Task 5A is implemented; device
validation has not yet been recorded.


## Device recording verification — October 19, 2026

Reviewed img_0161-1792435602181.mov (14.22 seconds), showing build 5A.2.
The core all-MISS defect and the blue sizing regression are resolved in this
recording:

- Fighters have matching proportions and size. Defender target covers head/torso.
- Both transforms report matching magnitude: Ax≈0.320, Bx≈−0.320.
  Child widths and texture widths both report 512 for A and B.
- At blue x342 / roots55.76pt: Jab HIT, d0.00 r6.39 gap−6.39pt.
- At the same close separation: Cross HIT, d0.13 r5.75 gap−5.63pt.
- After retreat to blue x265 / roots132.98pt: Jab MISS, d75.28 r6.39
  gap+68.88pt; Cross MISS, d77.35 r5.75 gap+71.60pt.
- Final visible totals J2 C2 H2 M2 satisfy J+C=H+M. Each demonstrated punch
  increments its contact/result counts once. Orange remains stationary/idle.

This validates the corrected rendered-coordinate mapping, close hits for both
punches, distant misses and matching fighter scale on the user's iPhone.
The recording does not independently establish precise threshold tangency,
pause/frame-step deduplication or resumption after an interruption; those remain
covered by source/Swift tests awaiting execution or further device checks.
No additional source changes were needed after this successful recording.
