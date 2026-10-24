# Boxer0 / Boxer6 — Development Tasks

**Source of truth:** [new_direction.md](new_direction.md) (agent brief v2, added in commit `9eae3d4`). This roadmap supersedes the earlier seven-phase priority ordering where they conflict. The animation work remains valuable, but the next implementation milestone is **combat meters**. Blue is the player; Orange is the CPU. Xcode project: `swift/Boxer0`.

## Status — 2026-10-24

- **Current priority: Phase 2 — verify meter-driven defeat and finish HUD.** Phase 2A contact/guard/stamina wiring and Phase 2B awareness KO / health <40 defeat are committed on `phase1-v2`; Xcode regression tests remain pending.
- **Phase 1 — implemented on master, expanded tests on `phase1-v2`:** commit `1d0ffb3` introduced `CombatTuning.swift`, `FighterMeters.swift`, `FighterMetersTests.swift` and their Xcode project references on `master`. The separate `tools/phase1.patch` is a historical delivery artifact, not a missing integration prerequisite. `phase1-v2` was fast-forwarded from master, then expanded with three focused tests. **Xcode compilation and test execution are still pending on a Mac.**
- **Existing game:** jab and cross remain implemented as **head attacks** until body art and controls exist. Cross is a temporary legacy attack, not the final design. Do not remove it without replacing the functional gameplay path.
- **Video2 art:** 73 RGB screenshots across six Blue attack groups; extraction script `tools/extract_video2_sprites.py` committed. Draft masks are **not production-ready**, and matching Orange attack/reaction art is not yet integrated. Do not claim Body Hook or Uppercut playable.
- **Blue jab:** switched to the original `jab_a` and `jab_recovery_a` assets first to avoid Blue's reported bluish skin tint; corrected an escaped source-asset interpolation typo in the Orange-derived fallback. Direction/color must be rechecked in Xcode. A genuine lighter-build redraw is still pending.
- **Orange bounce:** changed numbered Orange bounce/reaction loading to per-frame Core Image rendering without per-frame UIKit bitmap renderer; intended to reduce the memory spike reported at `IdleTestScene.swift:1407` (formerly `SKTexture(image: corrected)`). **Not yet memory-profiled or device-verified.**
- **Tests:** no claim of passing Xcode tests or simulator/device verification.

## Working rules

1. One focused task, one commit, one verification checkpoint. Work within existing combat code; do not rewrite `IdleTestScene` wholesale.
2. Keep existing tests green unless an explicit rule change requires updating them; add focused tests for every new mechanic.
3. Implement only what available visuals can represent. Defer sway, grab, body attacks and unprovided animations; store tunables and states without pretending the visuals exist.
4. Use `CombatTuning` for parameters and separate value types for meters and match state. Keep Blue and Orange behavior symmetric unless a CPU rule explicitly differs.
5. Push completed, coherent changes for review under the existing workflow. Clearly state what was not compiled or visually tested. Avoid binary sprite uploads through the GitHub text-file workflow.
6. Do not invent answers to the OPEN rules below. Preserve existing behavior or isolate provisional values until resolved.

## Phase 1 — Foundation (source complete; Xcode verification pending)

- [x] Integrate `CombatTuning`, `FighterStats`, `FighterMeters` and meter tests in `master` (`1d0ffb3`). The patch is a historical copy.
- [x] Confirm Xcode project **text references** for both implementation files and `FighterMetersTests.swift`; runtime target compilation remains unverified.
- [x] Fast-forward `phase1-v2` from master (without rewriting master) and add three focused meter tests: default caps/level, guard and streak separation, and clamp/reaction limits.
- [x] Preserve both fighters at **level 1** via default `FighterStats`; level injection is deferred.
- [ ] **Mac checkpoint:** open `swift/Boxer0/Boxer0.xcodeproj`, build the app, run `FighterMetersTests` and the existing test suite; record actual results before marking verified.
- [ ] Confirm provisional tuning values with user before using them in live combat (especially guard activation and damage).

**Checkpoint:** Phase 1 implementation and test registration are source-complete; **do not claim test pass or phase verification** until Xcode runs. Phase 2 wiring is not part of Phase 1.

## Phase 2 — Wire health, stamina, and awareness (IN PROGRESS)

- [x] Add per-fighter `FighterMeters` in the scene, exposed read-only for diagnostics. Legacy `FighterHealthState` still owns health/defeat until the next checkpoint; meter state is not yet the sole combat source of truth.
- [x] Route `PunchContactResult.hit` to unguarded head awareness and `.block` to guarded stamina, with per-attacker contact-sequence deduplication. Existing simultaneous-contact order is retained.
- [x] Add idle/guarding stamina advancement per simulation tick and meter reset/recovery handling; withdraw/grab modes remain later phases.
- [x] Add scene-level tests for hit awareness in both directions, guarded stamina loss and reset (source committed; execution pending).
- [ ] Awareness: 0–100, independent of stamina; **0 = KO**. Unguarded head-hit awareness loss starts at one-third maximum and escalates by approximately `1.2^(n-1)` for consecutive head hits. Body hits never escalate. Low awareness prolongs attack lockout; guard/sway/withdraw remain eligible.
- [ ] Health: maximum 100; **health below 40 loses** (instead of existing zero threshold). Apply the new consecutive-head-hit rule, while keeping unresolved single-hit damage tunable.
- [ ] Stamina: maximum 100. Guarded hits consume stamina only, with **no awareness reduction**; account for guard's separate point cost in the match layer.
- [ ] Regenerate stamina by state: no guard fastest, grab second-fastest, withdraw fast. Art-gated grab/withdraw behavior must not be falsely shown as available.
- [ ] Regenerate health only at round start, approximately +10, capped at 100; implement the round boundary in Phase 3 rather than on arbitrary timers.
- [x] Feed awareness KO (zero) and strict health-below-40 loss into existing defeat/knockdown handling; both fighters supported. Existing jab/cross health damage remains provisional pending OPEN item 3.
- [ ] Display meters read-only in the development HUD; add focused hit/block/streak/KO/threshold tests and deliberately update affected old tests.

**Checkpoint:** Phase 2A and the Phase 2B defeat transition source are committed; legacy defeat tests updated deliberately, and new tests cover awareness KO and the 40-health boundary. **Mac build/tests and memory profiling remain the immediate gate**. Meter HUD, health-damage tuning, and final head-hit streak health rules are still pending; do not claim Phase 2 complete.

## Phase 3 — Match state and scoring

- [ ] Add standalone `MatchState` value type: **8 rounds × 2 minutes**, round clock, points, KO and end-of-match results.
- [ ] Points to attacker: head hit **3**, body hit **1** (when body art exists), guarded hit **1**. A tie is a **draw**, not a forced winner.
- [ ] Apply health regeneration at round start; do **not** assume stamina or awareness reset between rounds.
- [ ] Add minimal timer, points, round and result UI, without redesigning the full game screen.
- [ ] Test time boundaries, points, draw, KO, and round transitions.

**Checkpoint:** complete deterministic match progression and scoring.

## Phase 4 — Attack timing and CPU defense

- [ ] Introduce **1000ms attack cooldown at level 1**, faster with higher injected levels.
- [ ] Awareness-dependent attack lockout; do not impose a new delay before guard after a punch.
- [ ] Preserve full simultaneous-hit and mid-attack vulnerability semantics.
- [ ] CPU defense chance **above 50%** during the player's attack window; **above 90%** immediately after being attacked once; increase with level.
- [ ] Awareness-dependent CPU reaction delay, starting at **50ms** with full awareness; guard last-attacked zone (head only for now).
- [ ] After **3 seconds without attack**, CPU drops guard with **50% chance**; allow defensive stamina-preservation choices.
- [ ] Keep current **120ms guard entry** until OPEN guard-activation rule is resolved; do not silently wire `defenseActivation = 0.5`.
- [ ] Update CPU and guard tests with seeded/injected randomness.

**Checkpoint:** cooldown, reaction, and defensive choices pass deterministic tests.

## Phase 5 — Withdraw and distance defense

- [ ] Reuse retreat animation and distance controller to represent an **out-of-reach withdraw state**.
- [ ] Withdraw counts as defense; loses no points; regenerates stamina and awareness quickly.
- [ ] Provisionally halve incoming awareness loss while withdrawing **only after confirming OPEN item 4**.
- [ ] Test transition into/out of range, counterplay, and CPU defensive decisions.

**Checkpoint:** withdraw state is playable with existing art and consistent contact rules.

## Phase 6 — Art-gated mechanics and fighter animation completion

- [ ] Cleanly isolate Video2 frames: remove text, targeting graphics, background and overlaps; reconstruct missing limbs; align 512px transparent frames to consistent foot anchors.
- [ ] Author Blue as a genuinely **lighter-built** boxer, not merely a recolored Orange; check facing, glove colors and pose continuity. Keep Orange heavier-built.
- [ ] Create distinct **Jab, Body Hook and Uppercut** attack animations and attack-specific receiving reactions for **both** fighters, based on the video; existing Orange reactions may be replaced if mismatched.
- [ ] When verified artwork exists, replace **Cross/Heavy Punch** with Body Hook and Uppercut in controls, `PunchKind`, CPU selection, collision zones, recovery, meters, scoring, diagnostics and tests. Until then jab/cross remain head-only legacy functionality.
- [ ] Add body zone and body-hit level scaling when body attack art is ready. Uppercut targeting must be defined from actual glove path, not guessed from the old cross geometry.
- [ ] Defer **sway**, **grab** (stamina <50, held up to 3 seconds), one-two, duck, left/right combinations, heavy hits and level injection until rules/art support them.
- [ ] Verify Orange bounce normalization, Blue jab direction/color/size, guard transitions, both knockdown/rise sequences, and all punch-to-reaction handoffs on device.

**Checkpoint:** complete bilateral animations with no baked-in text and verified gameplay, not just extracted PNGs.

## Carry-forward register: legacy tasks and Video2

The new phases own the older tasks; this section prevents previously planned work from disappearing. Earlier "Phase 3E/3F" labels refer to the *old animation roadmap*, not the new combat Phase 3.

| Legacy task | New phase | Current state |
|---|---|---|
| Orange Reaction V2, bounce height, facing, feet, reaction differences and recovery | 6 | Source adjustments exist; device and asset verification pending |
| Blue jab facing, color, lighter proportions, recovery | 6 | Provisional code committed; visual review and independent lighter-build artwork pending |
| Guard/advance/retreat/idle handoffs, animation registry, knockdown/rise for both fighters | 6, then 7 regression | Partially refined; comprehensive verification pending |
| Video2 six groups / 73 Blue screenshot frames and extraction utility | 6 | Draft extraction tool committed; production sprites not complete |
| Jab, Body Hook, Uppercut attacks and reactions in both directions | 6 | Not implemented; no verified bilateral animation sets |
| Remove Cross/Heavy Punch from gameplay | 6 | Deferred until replacement art, contact and controls work; current cross remains head-only |
| Glove contact, hit/miss/block, counters, pushback, stun and recovery | 2, 4, 6, 7 | Existing logic needs new meter effects and attack-specific regression |
| CPU offense/defense, distance and levels | 4, 5, 6 | Planned |
| Touch UI, match HUD, pause/results, audio, arena and debug controls | 2, 3, 7 | Planned |
| iPhone testing, FPS/memory, full matches and TestFlight | 7 | Planned |

### Video2 execution checklist (Phase 6, not a separate phase)

- [x] Inventory the Video2 screenshot groups: three Blue punch groups (14 frames each), two low-hit groups (12 and 9), one uppercut group (10): 73 frames.
- [x] Add `tools/extract_video2_sprites.py` as a **draft** extraction utility; the local preview ZIP is not production-ready.
- [ ] Review source poses and identify contact, recovery, occlusions and target zones.
- [ ] Redraw and clean Blue Jab, **Body Hook** (low hit) and Uppercut on consistent transparent 512px canvases; fix backward facing, color and lighter body proportions.
- [ ] Produce Orange Jab, Body Hook and Uppercut poses with Orange's distinct heavier build and correct facing. Blue screenshots alone are insufficient as finished Orange frames.
- [ ] Produce matched Jab/head, Body Hook/body and Uppercut/upward hit reactions **for both receivers**; replace mismatched existing Orange reactions as needed.
- [ ] Remove baked-in text, HUD, reticles, arena and overlap artifacts; validate alpha, foot anchors and motion continuity frame by frame.
- [ ] Document frame counts, contact frames, timing, recovery, target zones, anchor points and facing in an animation manifest.
- [ ] Integrate the new attacks and reactions into `PunchKind`, collision geometry, player controls, CPU choices, meter effects, match scoring, recovery and diagnostics.
- [ ] Remove legacy Cross/Heavy Punch from the playable system **when** Jab, Body Hook and Uppercut are working; update tests and references together.
- [ ] Test hit, miss, block, counter, simultaneous contact, interruptions, knockdown and recovery in both directions; perform on-device visual verification.

**Scheduling:** Phase 1 Mac tests and Phases 2–5 remain the gameplay priority. Video2 art preparation can proceed separately, but animation integration is gated on cleaned bilateral sprites and compatible combat logic. Moving an item here does not mark it complete.

## Phase 7 — UI polish, system testing, and prototype release

- [ ] Touch control refinement, pause/restart/match result, arena and sound/impact polish.
- [ ] Debug overlay optional; readable health, stamina, awareness, score and round UI.
- [ ] Test iPhone screen sizes, FPS, memory, full eight-round matches and CPU levels.
- [ ] Xcode/simulator/device verification and TestFlight readiness.

## OPEN — user decisions required before affected rules are wired

These items come from `new_direction.md`. They are **not** settled by this task update.

| # | Rule | Current provisional interpretation / action |
|---|---|---|
| 1 | Guard activation: 500ms earlier vs immediate CPU wording | Keep existing 120ms; do not wire 500ms without confirmation |
| 2 | Guard stamina cost: `(ld+1)/10 of 100` vs about 5% | Patch uses 5% × `(attackerLevel+1)/(defenderLevel+1)`; confirm `ld` |
| 3 | Single head/body health damage | Patch placeholders 4/3; existing jab/cross damage 5/10; confirm |
| 4 | Withdraw halves incoming awareness loss? | Assumed yes in brief, not approved |
| 5 | Head-hit streak resets after 3s or successful defense? | Assumed, not approved |
| 6 | Grab ends on release, 3s cap or lost closeness? | Assumed, not approved |
| 7 | Stamina/awareness round reset? | No reset assumed; only health regen specified |
| 8 | Loss precedence when awareness 0 and health <40 on same hit | Unspecified; decide before implementing result resolution |

## Immediate next three agent tasks

1. **Mac regression checkpoint:** clean-build `phase1-v2`, run `FighterMetersTests` and `CombatTests`, and use Xcode Memory Graph/Instruments to retest the prior `IdleTestScene.swift:1407` crash. Capture the exact diagnostic if it recurs.
2. **Phase 2 remaining work:** add debug HUD meter readout and finish head-hit streak health damage after resolving OPEN damage/precedence rules; inspect any new Xcode test failures before further gameplay changes.
3. **Phase 3 match-state skeleton:** timer, eight rounds, points, draw/KO, and round-start health regen; defer body scoring in live gameplay until body art exists.

**Review discipline:** each task ends with a commit, focused verification results, and an explicit list of Xcode/device checks that remain unverified. This file tracks planned and completed work; it is not evidence that a feature has passed device testing.
