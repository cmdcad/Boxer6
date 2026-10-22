# Boxer0 animation registry

Repository asset branch: `assets/boxer0-animation-registry`.

| Animation | Source | Frames | Playback | Status |
| --- | --- | --- | --- | --- |
| Blue Opening Burst V2 | video 41–53 | 13 | 18 FPS, once | Approved |
| Blue Advance V3 | selected frames 0–12 (video 55–67) | 13 | Independently adjustable, looping | Selected; minor artifacts accepted |
| Orange Bounce V3 | 17-frame cleaned cycle | 17 | ~1.105 s per cycle | Candidate, awaiting final approval |
| Blue Punch | video 185–225 extracted | 41 source frames | TBD | Extraction only, not approved |
| Orange Hit Reaction | TBD | TBD | TBD | Pending |

## Sprite conventions
- 512×512 RGBA PNG, transparent background.
- Root at (256, 448) in top-left image coordinates.
- SpriteKit controls world-space forward displacement; avoid double-counting movement embedded in poses.
- Burst plays once, then Advance repeats. The Burst→Advance handoff needs visual testing (source frame 54 absent).
- A separate Advance recovery/reverse action may be made later; do not alter the approved 0–12 selection for that purpose.

## Asset storage
Store approved source ZIPs in `AnimationAssets/Approved/`, candidate ZIPs in `AnimationAssets/Candidates/`, and raw extractions in `AnimationAssets/Source/`. Do not mark candidate/source footage as approved.

## Integration status
No SpriteKit scene integration verified yet. This registry documents decisions; it is not evidence of in-app playback.
