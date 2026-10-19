# Boxer0 — Task 6B: Health Depletion and Defeat State

## 1. Objective

Extend the existing Swift/SpriteKit boxing prototype with a minimal defeat-state system.

When a boxer's health reaches zero, the boxer should enter a defeated state and stop participating in combat.

Preserve all completed functionality from Tasks 2 through 6A.

Inspect the latest Swift source files, health model, punch-contact system, and animation architecture before implementing changes.

Do not introduce knockdown animations, recovery sequences, referees, scoring, or match outcomes.

## 2. Fighter combat states

Introduce two basic combat states:

- `standing`
- `defeated`

These states describe combat eligibility, not animation playback.

The existing animation states, including `idle`, `jab`, `cross`, and `hit_react`, must remain separate.

A boxer is `standing` while health is greater than zero.

A boxer becomes `defeated` when health reaches zero.

The transition must occur exactly once.

## 3. Defeat trigger

When confirmed damage reduces health to zero:

1. Apply the final damage.
2. Clamp health to zero.
3. Transition the affected boxer to `defeated`.
4. Record the defeat event once.
5. Prevent further combat actions involving the defeated boxer.

Do not repeatedly trigger defeat on subsequent updates or contact evaluations.

## 4. Behavior after defeat

For this milestone, a defeated boxer remains visually upright.

The orange boxer should:

- Stop responding to new punches.
- Stop starting new hit-reaction animations.
- Remain stationary.
- Display zero health.
- Remain in the defeated state until reset.

If a hit reaction is already active when the final blow lands, allow the current reaction to finish and then return to a static idle pose.

Do not use the `knockdown`, `down`, or `rise` sprite sequences yet.

## 5. Punch handling after defeat

Once the orange boxer is defeated:

- New punches must not cause damage.
- New punches must not trigger hit reactions.
- New punches must not increment HIT or MISS contact-result counters.
- Existing punch counters must retain their previous values.

The blue boxer's attack buttons should be disabled while the opponent is defeated.

The blue boxer's movement may remain available for debugging.

Do not change the existing spatial contact geometry.

## 6. Health reset and state restoration

Extend the existing Reset Health debug control.

When activated:

- Restore both fighters to 100 health.
- Restore both combat states to `standing`.
- Clear the defeat event flag.
- Return the orange boxer to idle.
- Re-enable Jab and Cross controls.
- Preserve fighter positions.
- Preserve existing diagnostic counters.

Reset must work even if invoked during an active animation.

Avoid duplicate animation callbacks or stale defeat events after reset.

## 7. HUD and diagnostics

Preserve the existing health bars.

When a fighter is defeated, display a simple status indicator:

`ORANGE — DEFEATED`

Keep this diagnostic separate from future match-result presentation.

Do not display:

- KO
- TKO
- Winner
- Round Over
- Match Over

These concepts will be introduced in later milestones.

## 8. Architecture requirements

Keep the implementation lightweight.

Recommended separation:

- Health model: current and maximum health.
- Combat state: standing or defeated.
- Animation state: idle, punch, hit reaction, etc.
- Contact system: existing HIT/MISS evaluation.
- Damage handler: confirmed damage and defeat transition.
- HUD: health and combat-state presentation.

Avoid coupling defeat transitions directly to UI rendering or animation frame counters.

Do not introduce a full boxing rules engine.

## 9. Validation

Test the following scenarios:

| Scenario | Expected behavior |
|---|---|
| Health above zero | Boxer remains standing |
| Final Jab reduces health to zero | Defeated once |
| Final Cross reduces health to zero | Defeated once |
| Additional punch after defeat | No damage or contact result |
| Orange defeated | Jab and Cross disabled |
| Reset Health | Both standing at 100 |
| Reset during reaction | Clean return to idle |
| Resume after pause | No duplicate defeat event |

Additional acceptance checks:

- [ ] Defeat occurs exactly once.
- [ ] Health remains clamped at zero.
- [ ] Defeated boxer cannot receive further damage.
- [ ] No new hit reactions occur after defeat.
- [ ] Existing counters remain consistent.
- [ ] Fighter positions and proportions remain unchanged.
- [ ] Reset restores combat eligibility.
- [ ] No knockdown or recovery animation is introduced.
- [ ] No referee, scoring, round, or match-result system is introduced.

## 10. Deliverables

Provide:

1. Updated Swift source files.
2. Minimal combat-state implementation.
3. Defeat-event handling.
4. Updated Reset Health behavior.
5. HUD state indicator.
6. Validation results.
7. Any remaining limitations.

## Completion criterion

A boxer transitions from `standing` to `defeated` exactly once when health reaches zero.

Further combat interactions are disabled, health remains at zero, and Reset Health restores normal operation without disrupting existing systems.

## Task 6B implementation report

Updated existing runtime sources: PunchContact.swift, IdleTestScene.swift, ContentView.swift. No new source target membership or artwork is required. Build label: 6B.

FighterCombatState (standing/defeated) and FighterCombatStatus are separate from health values and animation clips. A guarded transition records defeat once when confirmed damage reaches zero. Each fighter has an independent combat status; the current one-way contact handler damages orange only. Both begin standing. The defeatRecorded flag persists until reset, independently of animation playback. The existing sequence watermark still prevents repeated accepted contacts from applying damage.

Both standing states are required to start Jab/Cross. The scene repeats this eligibility check BEFORE contact evaluation, so interactions after defeat never increment J/C/H/M. The final accepted HIT still counts and applies damage. Reaction eligibility is checked AFTER final damage: the final blow does not start or restart recoil. If an older reaction is still active, it completes normally, then selects idle frame zero. Otherwise the final blow immediately selects idle zero. Both playback and frame stepping leave a defeated idle boxer static. Blue movement remains available for debugging. No root positions, sprite proportions or contact geometry were changed.

Reset Health restores both health values and standing states and clears both defeat flags. It cancels the active blue punch, finishes pending contact ownership without changing counters, cancels orange recoil, returns both to idle and clears held input. This deliberately extends the Task 6A reset behavior to prevent an unresolved pre-reset punch from producing stale post-reset damage. It preserves positions, pause status and diagnostic counts. New attacks become available when normal playback/focus conditions permit; a fresh press is required. There are no delayed animation callbacks to survive reset.

The top health strip now labels a defeated fighter with DEFEATED, retaining numeric health and proportional bars. It remains a diagnostic rather than a match-result panel.

### Validation results and limits

PASS: python Tests/validate_task6b.py source checks: guarded one-shot transition, eligibility before contact counters, post-damage reaction gate, standing-only idle advancement, clean reset and HUD.
PASS: python Tests/validate_task6a.py, Tests/validate_task5c.py, Tests/validate_task5b.py and Tests/validate_task5a1.py source/asset/numerical regressions. Older source assertions were updated for the Task 6B eligibility guard, build label and extended reset contract.

Added Tests/DefeatStateChecks.swift behavioral tests: final Jab and final Cross, health/state correspondence at each accepted punch, duplicate damage rejection, one defeat transition, blocked subsequent HIT/MISS, reset/re-entry, old accepted event rejection, and allowing an existing recoil to finish without restarting it. These Swift tests could not be executed on this Windows host because swiftc/Xcode/SpriteKit are unavailable. No simulator or device result is claimed.

On Mac:

```sh
swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Boxer0/HitReactionPlayback.swift Tests/DefeatStateChecks.swift -o /tmp/defeat-checks
/tmp/defeat-checks
```

Pending iPhone SE acceptance:

- Rebuild and confirm 6B. At close range, use 20 Jab HITs or 10 Cross HITs from full health; orange reaches zero and shows DEFEATED once.
- Try both attacks afterward: buttons disabled, health and all contact counters unchanged. Blue movement remains available.
- Pause and step across the final contact/recovery; orange freezes upright at idle after any already-active recoil completes. Resuming does not add defeat/contact results.
- Reset during recoil, an unresolved punch, and after defeat: health100/100, standing, orange idle, positions/counters retained, no old contact fires. Resume if paused, then press Jab/Cross freshly.
- Confirm both bars/status remain readable on iPhone SE landscape.

No knockdown/down/rise art, recovery sequence, referee, scoring, round or match outcome was introduced.
