# Boxer0 / Boxer6: agent brief (v2)

Repo: github.com/cmdcad/Boxer6, Xcode project at `swift/Boxer0` (SwiftUI + SpriteKit). Blue is the player and Orange is the CPU.
Phase 1 is delivered as `boxer6_phase1.patch` on branch `phase1-tuning-meters`. It adds `CombatTuning.swift`, `FighterMeters.swift` and `FighterMetersTests.swift`, and is not yet wired into the scene.

## Working rules
- Incremental: one focused task, one commit, one verification checkpoint.
- Test and improve the existing combat code. Do not rewrite `IdleTestScene` (1,827 lines) wholesale.
- Keep every existing test green unless a rule change deliberately alters it. Update such tests on purpose and say so.
- Implement only what current visual assets can show. Keep everything else as data in `CombatTuning` and the state enums.
- Prefer minimal, focused Swift files with clear inputs. Keep replies direct and concise.
- Do not invent rules. Ask when a rule is undefined or flagged OPEN below.
- No binary sprite uploads through the GitHub text workflow. Do not mark Body Hook or Uppercut implemented (see `tasks.md`).

## Requirements (consolidated)

### Fighters and levels
- Both fighters are level 1. Level stats and level codes are injected later. Variables to hold them exist (`FighterStats`).

### Meters
- **Health:** max 100. A fighter loses when health < 40. Health regenerates only at the start of each round (about +10, capped at max; the exact amount is tunable).
- **Stamina:** max 100.
- **Awareness:** 0 to 100, separate from stamina. Awareness 0 is a knockout. "Composure" and awareness are the same meter. Low awareness means a longer attack lockout and a slower CPU reaction. Guard, sway and withdraw stay available during the lockout.

### Attacks
- Current jab and cross are both head hits until body controls and art exist (decided). Left/right punch composition, one-two and duck are deferred.
- Attack cooldown is 1000ms at level 1 (faster at higher levels).
- There is no delay between throwing a punch and being able to start a guard.
- Simultaneous attack hits both land in full. A fighter mid-attack takes the full hit. If it is defending, the defense applies. (Already implemented.)

### Defense
- **Guard:** guards the last-attacked zone (head only for now). A successful guard costs a small point loss and about 5% stamina, scaled by a level multiplier. A guarded hit costs stamina only, with no awareness drop.
- **Sway:** head out of reach (head back). No stamina cost, no point loss. Art-gated.
- **Withdraw:** move to an out-of-reach distance state. It counts as defense, loses no points, regenerates stamina and awareness fast, and halves incoming awareness drops (interpretation, see assumptions).
- **Grab:** needs the too-close distance state and stamina < 50 (health plays no role). It is press-and-hold for 3s max. Once held it runs the full 3s even if stamina passes 50. It regenerates stamina (second fastest). Art-gated.
- Stamina regeneration: no guard is fastest, then grab. Withdraw is fast.

### Awareness and damage
- An unguarded hit drops awareness by 1/3 of max (1/2 for a heavy hit; heavy hits are not implemented).
- Consecutive head hits escalate the awareness drop by about 20% per hit (`1.2^(n-1)`). Body hits never escalate.
- Three consecutive unguarded head hits therefore reach awareness 0.
- Health: 2 or more consecutive head hits drop health by 10. Body-hit health damage uses a level multiplier built from both fighters' levels.

### Scoring and match
- 8 rounds of 2 minutes. KO ends the fight (awareness 0, or health < 40 loses). Otherwise points decide: head hit 3, body hit 1, guarded hit 1 (to the attacker). Equal points means a draw, with no winner.

### CPU
- Knows the player's attack window and defends with probability above 50% inside it (rises with level).
- Defends above 90% immediately after being attacked once. Withdraw counts as defense. Defends more often to keep or gain stamina.
- Auto-guards the last-attacked zone, gated by awareness.
- Reaction delay is driven by awareness, starting at 50ms at full awareness.
- After 3s with no attack, drops its guard with 50% chance, even when it knows the attack window.

## Corrections to earlier notes
- Grab is gated by stamina < 50 only. There is no health gate.
- Item #16 does not exist. Item #17 (low-health grab) is superseded by the stamina gate.
- Unguarded hits reduce awareness. They do not halve stamina.
- The earlier note "500ms guard activation" was dropped from the user's latest rules (see OPEN).
- The repo is no longer private to the agent: it can be cloned. Pushing needs the user's credentials.

## OPEN: confirm with the user before implementing
1. **Guard activation:** the user's earlier rule was 500ms, but their latest wording says the CPU auto-guards immediately depending on awareness. The code now uses 120ms (`GuardPlayback.entryDuration`). `CombatTuning.defenseActivation = 0.5` is unwired. Keep 120ms until confirmed.
2. **Guard stamina cost:** "(ld+1)/10 of 100" gives 20 at level 1, but the user says "like 5%". Phase 1 uses 5% × `(attackerLevel+1)/(defenderLevel+1)`. Confirm what "ld" means.
3. **Damage values:** single head-hit and body-hit health damage (placeholders 4 and 3). The existing code uses jab 5 and cross 10.
4. **Withdraw:** does "halving" mean incoming awareness drops are halved while withdrawing? (Assumed yes.)
5. **Streak reset:** a head-hit streak ends after 3s or after a successful defense (assumed).
6. **Grab end:** a held grab also ends on release, the 3s cap, or loss of closeness (assumed).
7. **Round reset:** do awareness and stamina reset between rounds? (Not assumed. Only health regenerates.)
8. **Loss precedence:** which applies first if awareness hits 0 and health is below 40 in the same hit?

## Existing code map (for wiring)
- Contact results: `PunchContactResult` (`.hit` is unguarded, `.block` is guarded, `.miss`). Applied in `IdleTestScene.applyContact`.
- Health and defeat: `FighterHealth`, `FighterCombatStatus.receiveHealth` (defeat at 0 today), `FighterHealthState.receive`. `PunchDamage` is hardcoded (jab 5, cross 10).
- Guard: `GuardPlayback` (120ms entry), `BlockFeedbackPlayback`.
- Timing: `PunchRecovery` (jab 0.12s, cross 0.22s), `CPUOffense` cooldowns (0.65s and 0.90s).
- CPU defense: `DefensiveAI` (jab chance 0.60 delay 0.02s, cross chance 0.75 delay 0.10s, max guard 1.5s). Randomness is injectable via `randomDraw`.
- Distance and reach: `FighterSpacing`, `PunchContactGeometry`, `predictedContact`, `CPUDistanceController`.
- KO visuals: `KnockdownPlayback`, `startKnockdownIfReady`, `startBlueRise`.
- Simulation entry point: `advanceSimulation(by:)` (deterministic, used by tests).

## Phases
1. **Done:** `CombatTuning`, `FighterStats`, `FighterMeters` plus unit tests (not wired).
2. **Wire meters:** add meters per fighter in the scene. `.hit` means an unguarded head hit and `.block` means guarded. Awareness 0 triggers the existing defeat and knockdown path. Change the health loss threshold from 0 to below 40, and update the affected tests deliberately. Regen by state (guarding, idle, retreat as withdraw). Show meters read-only in the debug HUD.
3. **Match layer:** new `MatchState` value type for the 2-minute round timer, 8 rounds, points (head 3, guarded 1), round-start health regen, and the result (KO, points win, draw). Add minimal UI.
4. **Timing and CPU:** 1000ms attack cooldown, awareness-driven attack lockout, CPU defend chances 0.5 and 0.9, awareness-driven reaction delay, 3s idle guard drop at 50%, guard on the last-attacked zone. Resolve OPEN item 1 first.
5. **Withdraw:** reuse the retreat clip plus an out-of-reach state from the distance model. Halve incoming awareness drops, regenerate stamina and awareness, and count it as CPU defense.
6. **Art-gated:** sway, grab, body zone with Body Hook and Uppercut, one-two and duck, left/right combos, heavy hits, and level injection.

## Definition of done per phase
- Existing tests pass, new rules have tests, and no unrelated files change.
- Report what could not be verified (Xcode build, simulator playback).