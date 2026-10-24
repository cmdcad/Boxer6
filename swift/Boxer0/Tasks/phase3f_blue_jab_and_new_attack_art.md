# Phase 3F — Blue jab correction and new punch-art handoff

## Source changes committed (not yet Xcode/device verified)

- The Orange-derived Blue jab no longer receives an indiscriminate 180-degree hue shift.
- A selective 32³ Core Image color cube maps strongly saturated red/orange kit pixels to blue while preserving skin and neutrals.
- Blue's Orange-derived jab and recovery are narrowed to 88% width and 94% height around the shared foot baseline. This is a temporary silhouette correction, **not** a substitute for artist-authored lightweight Blue frames.
- The previous extra horizontal mirror was removed in response to Blue's jab facing backward.
- The Orange jab source, contact timing, and original Orange art are unchanged.

## Required device review

1. Pull master and clean-build the iOS app.
2. Verify Blue's jab extends **toward Orange**. If it still faces away, inspect the actual texture orientation and root transforms before another flip.
3. Inspect Blue gloves, shorts, skin, and hair: ensure the color cube does not leave red/orange kit patches or tint skin blue.
4. Compare Blue's jab size with Blue idle/guard/footwork and Orange jab; look for sudden growth, foot shifts, or glove-contact offsets.
5. Check Blue recovery returns cleanly to Blue idle and guarded locomotion.
6. Confirm Orange jab remains visually unchanged.

## Next gameplay milestone: Jab + Body Hook + Uppercut

The user requested replacing the Cross/Heavy Punch attack model with **Jab**, **Body Hook** (pending confirmation from motion if needed), and **Uppercut**, in both attack directions. The video is a **visual reference**, not a source of clean alpha-isolated, frame-by-frame art. Both fighters must have distinct proportions, matching attack-specific receiving reactions, and no baked-in captions/text.

**Not implemented in this commit:** Body Hook or Uppercut sprite sequences, per-attack collision geometry, new CPU choices, UI buttons, or new defender reaction sets. Existing Cross remains functional until replacement animations and combat wiring are ready. Do not describe the new attacks as shipped.

Implementation checklist:
- [ ] Prepare alpha-isolated frame groups for each fighter and each new attack, with common 512px canvas/foot anchors.
- [ ] Prepare matching body-hook and uppercut hit reactions for **both** Blue and Orange; do not force the old heavy reaction.
- [ ] Add distinct `PunchKind.bodyHook` and `PunchKind.uppercut` with timings and per-attack targets.
- [ ] Update Blue and CPU attack selection and playback/recovery.
- [ ] Remove Cross from gameplay/UI and migrate diagnostics/tests.
- [ ] Remove baked-in text from new sprite frames; keep legitimate HUD text.
- [ ] Test hit, miss, block, counters, knockdown, and recovery for each attack in both directions.
- [ ] Confirm Blue remains lighter-built across every new pose.
