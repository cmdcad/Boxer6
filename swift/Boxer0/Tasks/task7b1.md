# Task 7B.1 - Physical block recoil

Implemented the six user-approved frames: block_jab_b_0...2 and block_cross_b_0...2, source SVG/PNG and universal image sets. Build label:7B.1. Copy all six new image sets to the Mac together with ContentView.swift, IdleTestScene.swift and HitReactionPlayback.swift. No new Swift target membership is needed.

## Cause

The previous effect was attached to the scene as an SKShapeNode at z7 (above fighter z2), and was updated after texture assignment. It was not merely a diagnostic or a layer hidden behind the fighter. However it only drew a small fading ring, never changed the guarding posture, and the normal guard texture continued to be assigned every tick. At typical scale0.32, its18/23canvas-pixel radius was only about6/7screen points, fading over80/110ms. This explains why the debug state could activate without perceptible physical absorption. Actual device visibility of the former ring was not measured here.

## Correction

Removed the ring node and anchor/fade implementation. BlockFeedbackPlayback now owns three dedicated texture poses per punch: immediate recoil, partial recovery and exact held guard. Jab lasts120ms (40ms per pose); Cross160ms (53.333ms per pose). Jab head recoil is10source pixels, Cross18; shoulder/arms recoil by80% of that amount, while the torso tapers toward its stationary waist. The runtime mirror makes negative source-X recoil move away from the incoming blue punch. Both sequences retain raised gloves and end pixel-identical to guard_b_2.

All lower-body pixels from y305 down are unchanged from held guard, including feet and baseline448. The root(256,448), canvas512x512, scale and facing remain unchanged. Artwork derives from the existing editable rig. No full-fighter translation, flash or substitute hit reaction is used.

Texture selection now gives active block recoil priority over ordinary guard playback, after incompatible knockdown/rise/hit-reaction clips. Only loaded recoil assets allow playback to start. Missing assets are explicitly reported, and Block FX remains OFF rather than claiming a visible recoil is playing. Jab recoil/Cross recoil/OFF diagnostics match this playback.

The confirmed BLOCK handler still triggers the effect on the contact render tick. Guard's effective state stays active. Health, damage values, contact geometry and J/C/H/B/M counting code are unchanged. Repeated new BLOCK events restart at recoil frame0; duplicates are rejected and no poses are queued. Guard release, HIT/defeat, reset, scene removal and Rise clear temporary recoil as before. Expiry returns directly to held guard without replaying entry. Pause/focus and frame stepping use the existing scene clock. Severe render hitches preserve each pose and can extend nominal duration.

## Validation

PASS: python Tests/validate_task7b1.py checks all six integrated assets, actual changed upper-body pixels/head displacement, unchanged lower-body pixels/baseline, exact recovery pixels, texture priority, no ring/root-motion fallback, and runtime brace nesting.
PASS: Task7A,6D,6C,6B,6A,5C,5B and5A.1 source/asset/numerical regressions. Task7B's obsolete ring checks now delegate to the corrected recoil checks.

Tests/BlockFeedbackChecks.swift was updated to cover BLOCK-only triggering,120/160ms ordered playback, pause, duplicate rejection, restart, MISS non-triggering, hitch visibility, cleanup and stale-event rejection. These executable Swift checks remain UNEXECUTED because this Windows host lacks swiftc/Xcode/SpriteKit.

On Mac:

```sh
swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Boxer0/HitReactionPlayback.swift Tests/BlockFeedbackChecks.swift -o /tmp/block-feedback-checks
/tmp/block-feedback-checks
```

The mirrored contact sheet was visually inspected. Ordinary-speed device rendering is still UNVERIFIED. Acceptance requires an iPhone run showing close Jab/Cross recoil with stronger Cross, unchanged health and raised guard, stationary feet, far MISS without recoil, correct counters, repeated blocks, pause/step, guard release and Reset cleanup. The stylized three-pose motion may still need strength tuning after that review. At scale0.32, head motion is about3.2screen points for Jab and5.8 for Cross; device perceptibility cannot be established by source checks or diagnostics alone.

Review artwork: IdleAnimation/preview/block_recoil_contact_sheet.png. Generation: IdleAnimation/generate_block_recoil.py. Timing/asset metadata: IdleAnimation/block_recoil_manifest.json.
