# Boxer0 — Task 6A: Basic Health and Damage

## 1. Objective

Introduce a basic health and damage system into the existing Swift/SpriteKit boxing prototype.

Successful punches should reduce the orange boxer's health. Missed punches should not.

Preserve all existing movement, punch animations, spatial contact detection, hit reactions, and debugging controls.

Inspect the latest implementation before modifying any files.

This task introduces health tracking only. It does not introduce knockdowns, stamina, blocking, AI, or match outcomes.

## 2. Fighter health

Introduce a simple health model for both fighters.

Initial configuration:

| Property | Value |
|---|---|
| Blue boxer maximum health | 100 |
| Orange boxer maximum health | 100 |
| Starting health | 100 |
| Minimum health | 0 |
| Maximum health | 100 |

Health should be stored as gameplay state, not derived from sprite animations.

Although only the blue boxer currently attacks, both fighters should have health values so the system can eventually support two-way combat.

## 3. Punch damage

Use provisional damage values:

| Punch | Damage on HIT |
|---|---|
| Jab | 5 |
| Cross | 10 |
| MISS | 0 |

These values are temporary balancing constants, not final boxing-game rules.

Keep them centralized and easy to adjust.

## 4. Damage application

Extend the existing confirmed contact-event handling.

When the blue boxer lands a punch:

1. The punch reaches its established contact frame.
2. The existing contact detector evaluates the glove-to-target intersection.
3. If the result is HIT, apply the corresponding damage to the orange boxer.
4. Trigger the existing hit reaction.
5. Update the health display.

If the result is MISS:

- Apply no damage.
- Trigger no new reaction.
- Preserve the existing MISS counter behavior.

Do not calculate damage independently from the existing contact result.

**Each punch must apply damage at most once.**

## 5. Health boundaries

Health must always remain within the valid range:

`0...100`

Examples:

- Orange health 100, Jab HIT → 95.
- Orange health 95, Cross HIT → 85.
- Orange health 85, MISS → 85.
- Orange health 5, Cross HIT → 0.

Never allow negative health or values above maximum health.

## 6. Health display

Add a simple health indicator for each boxer near the top of the gameplay interface.

Suggested layout:

`BLUE  [██████████] 100`

`ORANGE [██████████] 100`

Requirements:

- Clearly identify both fighters.
- Display remaining health numerically.
- Include a proportional health bar.
- Update immediately after confirmed damage.
- Preserve readability in landscape orientation.
- Avoid covering fighters, punch controls, or debugging information.

Use the existing SwiftUI or SpriteKit interface architecture, whichever is already responsible for gameplay HUD elements.

Do not redesign the entire interface.

## 7. Zero-health behavior

When orange health reaches zero:

- Clamp health at zero.
- Continue displaying zero health.
- Do not trigger a knockdown animation.
- Do not declare a winner.
- Do not end the match.
- Do not introduce a new combat state.

For this prototype, the orange boxer may continue its existing hit-reaction behavior, but additional punches must not reduce health below zero.

This intentionally separates damage tracking from future knockout mechanics.

## 8. Reset functionality

Add a minimal `Reset Health` debug control.

When activated:

- Restore both fighters to 100 health.
- Leave their current positions unchanged.
- Preserve existing punch counters unless the current debugging architecture explicitly supports a separate full-session reset.
- Do not restart the entire scene.

The reset must not interrupt or corrupt active animation playback.

## 9. State and architecture

Keep the implementation lightweight.

Recommended responsibilities:

- Fighter health model: stores current and maximum health.
- Punch damage configuration: maps Jab and Cross to damage values.
- Existing contact system: determines HIT or MISS.
- Damage handler: applies damage exactly once per confirmed HIT.
- HUD: observes and displays health changes.

Avoid coupling health directly to animation frame changes or UI rendering.

Do not introduce a comprehensive combat engine or unnecessary abstractions.

## 10. Validation

Test the following:

| Action | Expected orange health |
|---|---|
| Start | 100 |
| Jab HIT | 95 |
| Cross HIT | 85 |
| Jab MISS | 85 |
| Cross MISS | 85 |
| Jab HIT | 80 |
| Reset Health | 100 |

Additional checks:

- [ ] Both fighters start at 100 health.
- [ ] Jab HIT applies exactly 5 damage.
- [ ] Cross HIT applies exactly 10 damage.
- [ ] MISS applies zero damage.
- [ ] Each punch applies damage at most once.
- [ ] Health cannot fall below zero.
- [ ] Health bars reflect numerical values.
- [ ] Orange hit reactions still function.
- [ ] Pause and frame stepping do not duplicate damage.
- [ ] Reset restores health without resetting the scene.
- [ ] Existing movement and punch behavior remain unchanged.
- [ ] No stamina, blocking, knockdowns, AI, or match outcomes are introduced.

## 11. Deliverables

Provide:

1. Updated Swift source files.
2. Health and damage model.
3. Health HUD implementation.
4. Reset Health debug control.
5. Test results demonstrating Jab, Cross, MISS, and Reset behavior.
6. Brief explanation of how duplicate damage is prevented.

## Completion criterion

The orange boxer's health decreases by 5 for every confirmed Jab HIT and 10 for every confirmed Cross HIT.

Misses cause no damage. Health never falls below zero, the HUD updates correctly, and all previously implemented gameplay behavior remains functional.


Design direction
The values Jab = 5 and Cross = 10 are deliberately simple. They let us verify the mechanics before introducing more realistic boxing factors such as punch effectiveness, defensive positioning, fatigue, and damage accumulation.

## Implementation report

Implemented Task 6A in the existing PunchContact.swift, IdleTestScene.swift and ContentView.swift. No new runtime source files or target membership changes are needed.

FighterHealth stores bounded integer health (maximum 100, starting 100). FighterHealthState owns separate blue/orange values. Central PunchDamage constants set Jab to 5 and Cross to 10. Damage is applied synchronously after the existing contact detector returns its result, before the existing reaction starts. MISS changes neither health nor reaction behavior. Zero health has no effect on combat states or ability to punch.

Duplicate prevention has two layers: PunchContactTracker already emits only one event per accepted punch; FighterHealthState additionally accepts each monotonic contact sequence at most once. Health reset retains that sequence watermark. Pause, frame stepping, HUD refreshes and reset therefore cannot replay an event to cause extra damage.

The reserved 44-point top HUD strip displays named blue/orange numeric health and proportional ProgressView bars. It sits above SpriteView, so it does not cover fighters or Guides. The existing responsive scene may scale to the slightly shorter viewport. The bottom controls are unchanged. Reset Health is a 44-point debug button in the top strip and remains available while paused or punching. It changes only health and publishes the HUD; positions, counters, input, playback clocks and scene identity are untouched. Build label: 6A.

### Validation

PASS: python Tests/validate_task6a.py source checks for damage/contact wiring, sequence guard, bounded health, isolated reset, numeric/bar HUD.
PASS: python Tests/validate_task5c.py, python Tests/validate_task5b.py, python Tests/validate_task5a1.py regression source/asset/numerical checks.

Tests/HealthDamageChecks.swift adds executable behavioral checks for 100 -> 95 -> 85 -> 85 -> 85 -> 80 -> reset 100; duplicate/reordered event suppression, reset watermark, zero/negative/large damage boundaries and actual spatial HIT/MISS tracker integration. These Swift tests were NOT executed: swiftc/Xcode/SpriteKit are unavailable on this Windows host. Source checks are not a substitute for compilation or device testing.

On Mac:

```sh
swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Tests/HealthDamageChecks.swift -o /tmp/health-checks
/tmp/health-checks
```

Pending iPhone SE/Xcode checks: rebuild and confirm 6A; verify the sequence above using close HITs and distant MISSes; pause/step through contact without repeated damage; reset before and after contact during an active punch; confirm counters and positions unchanged by reset; hit repeatedly through zero; confirm top HUD readability, bottom controls, movement and reactions. A reset before an unresolved contact correctly allows that future contact to damage the freshly restored health. A reset after contact does not replay its damage.

No new artwork, stamina, blocking, knockdowns, AI or match outcomes were added.
