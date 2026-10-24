# Phase 3D — Sprite proportion correction and deferred punch art

User-reviewed priorities:
1. Orange bounce figure is too tall compared with Orange's other modes.
2. Orange cross and Blue punch sequences appear to use older artwork; inspect and replace separately.
3. Orange Jab V2 is accepted: **do not modify it**.
4. Improve guard/movement continuity and make diagnostic overlay less obstructive.
5. Defer contact/block feedback redesign. Do not retune CPU difficulty without controlled verification.

## Prepared art replacement
Deliverable: `Boxer0_Orange_Bounce_Height_Corrected.zip` (distributed in chat, **not committed to GitHub**).

Source: Orange Bounce V3, 17 images. Original bounce frame 00 alpha bounds
(139,96)-(372,450), approximately 354 px high. Orange Jab V2 frame 0 alpha
bounds (136,153)-(365,448), approximately 295 px high. Scale all bounce
figures uniformly to 295/354 = 0.83333 of their prior silhouette dimensions,
anchored at image-space foot baseline y=448. Output remains 512×512 RGBA
with unchanged asset names `orange_bounce_00` through `orange_bounce_16`.

Install: extract the ZIP and replace the matching 17 `.imageset`
directories in the game's `Assets.xcassets`; preserve all other imagesets.
Do not resize SpriteKit child nodes because contact transforms expect +1
child scales. No animation timings or combat code should change.

## Verification
- Compare `orange_bounce_00` to `jab_b_0` in the game at the same scene
  scale; feet should share ground line and standing heights should be close.
- Check bounce loop for jitter, clipped gloves and floor drift.
- Test bounce -> guard -> guarded advance/retreat -> bounce, and
  bounce -> jab -> recovery -> bounce.
- Check cross and Blue punch sequences for stale artwork, but do not
  overwrite the approved Orange jab.
- Keep visual contact/block-feedback redesign deferred.
- Xcode runtime and visual testing remain outstanding.
