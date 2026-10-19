# Task 5A.1 — Diagnose and Correct Punch Contact Detection

## Reported failure and investigation

User reports H remains zero and M increases at the closest allowed position.
Traced the latest source from PunchPlayback contact entry through the once-only
tracker, attacking contact pose, canvas transform, mirrored defender rectangle,
intersection and movement limits. SVG-derived centers remain correct:

- Jab frame index 3: lead ellipse (364.5,192) + (20,-3) = (384.5,189).
- Cross index 4: rear ellipse (296,186) + (82,0) = (378,186).
- Target x220 y127 w88 h173, radii Jab20/Cross18 remain unchanged.
- Root (256,448) and Y inversion are correct. Mirrored target scene X bounds
  relative to orange's root are [-52,+36] times rendered scale.
- Circle/rectangle nearest-point distance is the correct intersection test.
- Deduplication still occurs once per accepted punch at its contact marker.

At a consistent scale, closest roots are 174.4 canvas units apart. Jab can reach
200.5 units and Cross192, so these defaults predict HIT for both at the boundary.
The reported phone failure therefore is NOT reproduced by the checked-in constants
alone. No constants or hitboxes were enlarged to force a result.

## Scale-consistency defect and remaining root-cause uncertainty

Found a structural inconsistency: the previous movement limits used fighterScale,
while contact used fighterScale multiplied by SKSpriteNode.size/512. The code had
not enforced the sprite's logical size to 512. If logical texture/node size differs
from that assumption, movement and detection use different effective units.

Independent reproduction with layout scale .32 and logical canvas factor .5:

| Punch | Old closest roots | Actual reach | Old result | Shared-scale closest roots | Corrected result |
| --- | --- | --- | --- | --- | --- |
| Jab | 55.808 pt | 32.080 pt | MISS | 27.904 pt | HIT |
| Cross | 55.808 pt | 30.720 pt | MISS | 27.904 pt | HIT |

This establishes a reproducible defect under a scale mismatch. It DOES NOT prove
that the user's phone has a 256-point texture or this exact runtime mismatch.
With a 512-point canvas the former source already predicts hits. A different
running boundary/configuration could produce the reported outcome too. The exact
phone cause remains unconfirmed pending runtime readouts/video. Do not report the
user-visible issue as fully diagnosed or validated until that evidence arrives.

## Corrected source

- Added FighterSpacing to PunchContact.swift. Movement limits now consume the
  same rendered SpriteCanvasTransform values as detection and debug overlays.
  Body gaps use actual transformed widths and mirrored bounds. Existing physical
  body bounds and gap factor .8 are unchanged.
- The SpriteKit adapter obtains its root and X/Y basis using node.convert to scene
  space instead of reconstructing scale independently. The prototype remains
  axis aligned, with roots directly attached to the scene.
- Explicitly normalize every rendered sprite canvas to 512×512 logical points at
  creation and after assigning textures. This enforces the established canvas
  contract rather than relying on texture logical dimensions. It leaves appearance
  unchanged if the prior node already had the intended 512-point size.
- Kept glove centers, radii, target geometry, animation timing, movement tuning,
  contact-frame markers, pause/input guards and once-only evaluation unchanged.
- Intersection now exposes nearest-point distance directly. Each event snapshots
  the attacker/defender transforms and exposes centerDistance and signedGap.
- Added a Guides line from the glove center to the nearest target point. The
  existing point, radius and target still align at the actual contact pose.
- Build label is “5A.1”. Latest-result overlay includes d (center-to-target distance),
  r (glove radius), signed gap=d-r, actual root separation, signed X scales and
  texture/canvas information. Values use scene points; gap<=0 means intersection.
  When the center is inside the rectangle, d=0 and gap=-r. No health or effects.
- Contact measurements persist as the last event while live markers appear only
  on the contact frame. Guides and production diagnostic visibility still hide
  these overlays. Counters preserve J+C=H+M.

## Validation results

Passed `python Tests/validate_task5a1.py` on Windows: SVG center checks, unchanged
geometry, shared-transform integration, explicit 512-point normalization,
scale-mismatch reproduction and near/far reach calculations. The prior Task 5A
source/metadata checks and Task 4B/4A/3B asset checks also pass.

Independent range calculations for both punches across effective scales .16,
.32 and .64:

| Root distance in canvas units | Jab | Cross |
| --- | --- | --- |
| 400 (far) | MISS | MISS |
| Respective reach +0.1 | MISS | MISS |
| Respective reach exactly (200.5 / 192) | HIT, tangent | HIT, tangent |
| Respective reach -0.1 | HIT | HIT |
| 174.4 (closest approved spacing) | HIT | HIT |

These are numerical/source checks, NOT execution of SpriteKit or the Swift types.
Expanded Tests/PunchContactChecks.swift to run the actual new spacing model,
logical-size factors .5/1/2, the former mixed-scale failure, range edges and
existing mirroring/anchor/counter/stepping checks. Could not run Swift on this
Windows host (swiftc and Xcode unavailable). On Mac:

```sh
swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Tests/PunchContactChecks.swift -o /tmp/contact-checks
/tmp/contact-checks
```

## Runtime evidence pending

User asked whether a video would suffice; confirmed yes. With Guides on, advance
until movement stops, release, then throw Jab and Cross. Keep build/status and
counters visible. Pausing at Jab frame4 or Cross frame5 is useful but not required.
The new 5A.1 readouts allow direct verification of measured distance vs radius,
root separation and effective scale. A 5A recording can still establish visible
positions and which previous configuration is running.

No artwork, punch extension, radius inflation, target enlargement, damage,
reactions, stamina, health or AI introduced. Device HIT/MISS behavior and exact
runtime root cause are still pending review of the user's recording/readouts.


## Recording review — October 19, 2026

Reviewed img_0158-1792434506489.mov (53.84 seconds). Recording consistently shows
build label “5A”, not the diagnostic/corrected “5A.1” build.

Observed evidence:

- Blue advances from x170 to the closest permitted x342 and stops at v0.
  Orange root is about x398. This approximately 56-point separation agrees with
  the intended 174.4 canvas units at the approximately .32 rendered scale.
  Therefore the close-range boundary in this recording is already the approved
  torso boundary, rather than the older overly distant silhouette boundary.
- Both punches repeatedly increment their marker and MISS counts, with H0.
  By the end J12+C12=H0+M24. Marker dispatch and counter totals are operating;
  geometry alignment is the visible failure.
- Critically, the orange target rectangle is located between the knees, below the
  shorts, instead of spanning head and torso. At 8 seconds its colored border is
  approximately x784…802, y224…260 in the 1136×640 landscape frame.
- For a 568×186 scene, the intended rendered scale is .88*186/512=.3196875.
  The 88×173 target should occupy about 56×111 video pixels, situated roughly
  y85…195 above the baseline at y290. The observed rectangle is only about
  19×37 pixels, positioned down toward the root. This is consistent with an
  extra factor of approximately the fighter scale being applied to the contact
  geometry. The overlay itself is demonstrably in the wrong scale/position.

Diagnosis update: the recording confirms a geometry-to-artwork scale mismatch,
not a need to enlarge the target, extend punches or reduce the close boundary.
The precise expression producing the extra scale in the running Mac project
cannot be proven from video alone; its target/source layout was previously shown
to differ from this checkout. Do not claim that SKSpriteNode.size inherently
includes xScale: Apple documents base sprite size separately from node scaling.
The earlier logical-size mismatch reproduction is an example of how divergent
transforms fail, not proof of the exact texture size on this phone.

The prepared 5A.1 source enforces the 512-point canvas and derives both spacing
and contact from the same SpriteKit-converted basis. No geometry constants or
artwork were enlarged. Install that updated build and confirm the label “5A.1”.
The target should move onto the torso/head, and measured d/r/gap should agree
with the visible overlap. Device success of this corrected build remains pending;
this recording demonstrates the original failure, not validation of the fix.

API reference used during review: Apple's Working with Sprites explains that
base sprite size is subsequently scaled by xScale/yScale:
https://developer-mdn.apple.com/library/archive/documentation/GraphicsAnimation/Conceptual/SpriteKit_PG/Sprites/Sprites.html
