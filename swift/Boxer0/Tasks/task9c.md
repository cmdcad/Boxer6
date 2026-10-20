# Boxer0 — Task 9C: Combat Diagnostics and Automated Validation

**Milestone:** 9C  
**Platform:** iPhone landscape  
**Frameworks:** Swift, SpriteKit, SwiftUI, XCTest  
**Scope:** Automated combat tests, event diagnostics, and regression validation  
**Status:** Ready for implementation

## 1. Objective

Introduce a reliable testing and diagnostic system for the existing Boxer0 combat engine.

The implementation must verify that combat rules behave consistently across both fighters.

Primary goals:

- Automatically validate attack and recovery timing.
- Verify HIT, BLOCK, and MISS classification.
- Verify health and damage calculations.
- Verify guard activation and release.
- Verify counterpunch classification.
- Detect invalid combat-state transitions.
- Detect duplicate damage and contact events.
- Validate pause, reset, defeat, and Rise behavior.
- Provide readable diagnostics when a test fails.

Do not introduce new gameplay mechanics.

## 2. Inspect the existing project

Before implementation, inspect the latest project files and identify:

1. Shared bidirectional attack pipeline.
2. Fighter action and combat states.
3. SpriteKit animation scheduler.
4. Simulation clock and frame-stepping system.
5. Contact and damage resolution.
6. Blue hold-to-guard input.
7. Orange defensive AI.
8. CPU offensive AI and movement.
9. Physical recovery and visible recovery poses.
10. Counterpunch detection and statistics.
11. Existing debug controls and XCTest targets.

Reuse the current architecture.

Do not replace working gameplay code solely to make testing easier.

## 3. Test architecture

Create a lightweight automated test layer using XCTest.

Prefer testing the existing combat logic through small, deterministic interfaces.

Where necessary, extract pure combat calculations from SpriteKit scene presentation.

Examples include:

- Damage calculation.
- Guard effectiveness.
- Contact classification.
- Recovery eligibility.
- Counterpunch classification.
- Combat-state transition validation.

Avoid creating a second simulated combat engine with different rules.

**Tests must exercise production logic, not duplicate it.**

## 4. Deterministic simulation clock

Tests must control simulation time explicitly.

Introduce or reuse a testable simulation-time interface.

The test harness should be able to:

- Start an attack at a known simulation time.
- Advance simulation by a specified duration.
- Observe state transitions.
- Reach exact contact markers.
- Pause and resume.
- Trigger Reset.
- Trigger defeat and Rise.

Avoid real-time sleeps and wall-clock timers.

Use deterministic random-number injection for CPU decision tests.

A test should produce the same result every time it runs.

## 5. Punch timing tests

Validate the established animation contract.

| Property | Jab | Cross |
|---|---:|---:|
| Animation duration | 300 ms | 480 ms |
| Contact marker | 150 ms | 240 ms |
| Additional recovery | 120 ms | 220 ms |
| Total attack + recovery | 420 ms | 700 ms |

Required tests:

- Contact cannot resolve before the contact marker.
- Contact resolves once when the marker is reached.
- Attack completion occurs at the correct time.
- Recovery begins after animation completion.
- Recovery ends at the correct time.
- No second punch starts during recovery.
- A punch becomes eligible after recovery when no other restrictions exist.

Use the simulation clock rather than approximate real-time delays.

## 6. Recovery visual-state tests

Validate Task 9B.1.

For both fighters:

- Jab completion selects the Jab recovery pose.
- Cross completion selects the Cross recovery pose.
- Recovery pose persists while physical recovery is active.
- Recovery pose ends when recovery finishes.
- Hit reaction overrides recovery pose.
- Knockdown overrides recovery pose.
- Reset clears stale recovery presentation.

Verify animation-state selection through the production animation controller.

Do not require pixel-by-pixel screenshot comparisons for this milestone.

## 7. Contact classification tests

Test both attack directions.

### HIT

- Defender within valid contact geometry.
- Defender not effectively guarding.
- Result is HIT.
- Correct damage applies once.

### BLOCK

- Defender within contact geometry.
- Defender's guard is fully effective.
- Result is BLOCK.
- No damage applies.

### MISS

- Defender outside valid contact geometry.
- Result is MISS.
- No damage applies.

Additional tests:

- Defender moves out of range before contact.
- Defender moves into range before contact.
- Guard is raised after contact.
- Guard is released before contact.
- Contact resolution cannot run twice for the same attack.

Preserve existing spatial geometry and reach calculations.

Do not introduce simplified test-only hitboxes.

## 8. Damage and health tests

Use the existing damage model.

| Punch | HIT damage | BLOCK damage | MISS damage |
|---|---:|---:|---:|
| Jab | 5 | 0 | 0 |
| Cross | 10 | 0 | 0 |

Required tests:

- Jab HIT reduces health by 5.
- Cross HIT reduces health by 10.
- BLOCK reduces health by 0.
- MISS reduces health by 0.
- Health never falls below 0.
- Health never exceeds 100.
- Damage cannot apply twice from the same attack.
- Blue and orange follow identical damage rules.

## 9. Guard timing tests

Validate guard entry for both fighters.

Established guard entry:

**120 ms**

Required tests:

- Guard is ineffective at entry start.
- Guard remains ineffective before 120 ms.
- Guard becomes effective when entry completes.
- Guard remains effective while held or maintained.
- Guard release removes protection immediately.
- Release during entry prevents delayed activation.
- Guard cannot bypass active punch recovery.
- Hit reaction interrupts incompatible guard entry.
- Defeat clears guard effectiveness.

For blue, test hold-to-guard input semantics.

For orange, test autonomous guard-state transitions.

## 10. CPU defensive AI tests

Preserve the established Task 8A.1 parameters.

| Parameter | Jab | Cross |
|---|---:|---:|
| Guard reaction delay | 20 ms | 100 ms |
| Guard entry | 120 ms | 120 ms |
| Guard attempt probability | 60% | 75% |

Use injected deterministic random values.

Verify:

- CPU sometimes attempts guard.
- CPU sometimes declines guard.
- Jab guard can become effective at 140 ms.
- Cross guard can become effective at 220 ms.
- Guard cannot bypass physical recovery.
- CPU does not defend while defeated.
- Reset cancels pending guard decisions.

Do not alter CPU probabilities to make tests pass.

## 11. CPU offensive AI tests

Validate the existing Task 8C offensive rules.

Test:

- CPU does not attack outside valid range.
- CPU can choose Jab or Cross when eligible.
- Attack preparation uses simulation time.
- Physical recovery is respected.
- Tactical cooldown is respected.
- Guarding prevents CPU attack initiation.
- Hit reaction prevents CPU attack initiation.
- Defeat prevents CPU attacks.
- CPU OFF prevents new autonomous attacks.
- Pending preparations are canceled by Reset.

Use deterministic random injection.

Do not require exact Jab/Cross ratios in small test samples.

## 12. Counterpunch tests

Validate Task 9B.

A counter attempt occurs when an attack begins while its opponent is attack-vulnerable.

A successful counter requires the attempt to resolve as HIT.

Required scenarios:

| Scenario | Expected classification |
|---|---|
| Attack starts against recovering opponent and lands | Successful counter |
| Attack starts against recovering opponent and misses | Counter attempt, unsuccessful |
| Attack starts against idle opponent and lands | Ordinary HIT |
| Attack starts during opponent's active punch | Counter attempt |
| Attack starts after opponent's recovery ends | Ordinary attack |
| Counter attempt resolves BLOCK | Unsuccessful counter |
| Counter HIT causes knockdown | Normal knockdown rules |

Verify:

- Counter status does not change damage.
- Counter status does not change reach.
- Counter statistics are not additional HIT outcomes.
- Counter classification is consistent for both fighters.

## 13. Simultaneous attacks and interruption tests

Test both fighters attacking during overlapping time windows.

Requirements:

- Each attack has an independent identifier.
- Each attack has its own contact marker.
- Both attacks can resolve independently when permitted.
- No global punch lock prevents legitimate simultaneous attacks.
- A canceled attack cannot cause delayed damage.
- A completed contact cannot resolve again.

Test equal-time event ordering explicitly.

If two contacts are scheduled for the same simulation instant, use a deterministic ordering policy that preserves the established combat rules and does not arbitrarily favor blue or orange.

Document the policy.

## 14. Combat-state transition tests

Validate transitions involving:

- Standing.
- Attacking.
- Recovering.
- Guard entry.
- Guard raised.
- Hit reaction.
- Knockdown.
- Down.
- Rise.
- Defeated.

Tests should reject incompatible combinations such as:

- Punching while down.
- Guarding effectively during knockdown.
- Starting a new attack during recovery.
- Movement overwriting hit reaction.
- Recovery callback restoring idle during Rise.
- Defeated fighter initiating a new attack.

Use the existing production state model.

Do not invent replacement states merely for tests.

## 15. Reset and Rise tests

Verify that Reset:

- Cancels active attacks.
- Cancels pending contact evaluations.
- Cancels recovery callbacks.
- Clears guard-entry callbacks.
- Clears pending CPU decisions.
- Restores health to 100.
- Restores valid standing animations.
- Prevents stale damage after Reset.

Verify that Rise:

- Runs the existing animation.
- Does not activate stale guard input.
- Does not restore old recovery.
- Restores health and eligibility at the established completion point.
- Allows CPU decisions to resume when enabled.

## 16. Pause and frame-step tests

Test simulation timing under pause and resume.

Required checks:

- Paused punches do not progress.
- Paused recovery does not expire.
- Paused guard entry does not complete.
- Paused CPU preparation does not finish.
- Paused cooldown does not expire.
- Frame stepping advances events correctly.
- Resume does not cause duplicate events.
- Resume does not create large movement jumps.

Do not use wall-clock waiting as the primary validation method.

## 17. Combat statistics invariants

Validate independent counters.

**Blue offense**

`Blue Jab + Blue Cross = Blue HIT + Blue BLOCK + Blue MISS`

**Orange offense**

`Orange Jab + Orange Cross = Orange HIT + Orange BLOCK + Orange MISS`

Also verify:

`Successful counters <= Counter attempts`

`Successful counters <= Total HIT`

**Important:** If the production system permits attacks to be canceled before contact, the test must account for those canceled or unresolved attacks explicitly. Do not misclassify them as MISS just to force the equality.

Use the same counter conventions as the existing implementation.

## 18. Combat event log

Add a lightweight structured diagnostic event log.

Suggested events:

- `ATTACK_START`
- `CONTACT_HIT`
- `CONTACT_BLOCK`
- `CONTACT_MISS`
- `ATTACK_INTERRUPTED`
- `ATTACK_END`
- `RECOVERY_START`
- `RECOVERY_END`
- `GUARD_START`
- `GUARD_EFFECTIVE`
- `GUARD_RELEASE`
- `COUNTER_ATTEMPT`
- `COUNTER_SUCCESS`
- `HEALTH_CHANGED`
- `KNOCKDOWN`
- `RISE_START`
- `RISE_END`

Each event should include, where applicable:

- Simulation timestamp.
- Fighter identifier.
- Attack identifier.
- Punch type.
- Relevant state transition.
- Contact outcome.

Keep the event log bounded to avoid unnecessary memory growth.

Do not print large volumes of diagnostics continuously during normal gameplay.

## 19. Debug controls

Add a development-only option to enable combat event logging.

Recommended behavior:

- Logging OFF by default.
- Logging ON captures recent combat events.
- A compact display shows the most recent events.
- Developers can inspect or copy the event log for troubleshooting.

Preserve the existing gameplay debug controls.

Avoid blocking the main SpriteKit update loop with excessive logging.

## 20. Test execution

Organize tests into logical groups.

Suggested structure:

- `AttackTimingTests`
- `RecoveryTests`
- `ContactResolutionTests`
- `GuardTests`
- `DamageTests`
- `CPUDecisionTests`
- `CounterpunchTests`
- `CombatStateTests`
- `PauseResetRiseTests`
- `CombatStatisticsTests`

Use existing project naming conventions where practical.

Tests must be executable through the project's normal Xcode test workflow.

Do not add external testing dependencies unless strictly necessary.

## 21. Acceptance criteria

- [ ] XCTest target builds successfully.
- [ ] Tests use production combat logic.
- [ ] Simulation timing is deterministic.
- [ ] Random CPU decisions can be reproduced.
- [ ] Jab and Cross timing tests pass.
- [ ] Recovery timing and presentation tests pass.
- [ ] HIT/BLOCK/MISS tests pass in both directions.
- [ ] Damage and health tests pass.
- [ ] Guard timing and release tests pass.
- [ ] CPU offensive and defensive tests pass.
- [ ] Counterpunch classification tests pass.
- [ ] Simultaneous-attack tests pass.
- [ ] Reset and Rise tests pass.
- [ ] Pause and frame-step tests pass.
- [ ] Combat statistics reconcile.
- [ ] Event logging can be enabled and disabled.
- [ ] Existing iPhone gameplay remains unchanged.
- [ ] No gameplay mechanics are introduced or altered.

## 22. Deliverables

Provide:

1. Swift files created or modified.
2. XCTest files added.
3. Description of the deterministic test harness.
4. Explanation of how production combat logic is exercised.
5. Automated test results, including passed, failed, and skipped tests.
6. Sample combat event log.
7. Any discovered defects and fixes.
8. Any mechanics that remain untested.

Do not claim tests passed unless they were actually executed.

If XCTest cannot be run in the available environment, distinguish compilation checks from executed tests and report the limitation.

## Completion criterion

Boxer0 has a repeatable automated validation system capable of detecting regressions in its established combat mechanics.

Punch timing, guard effectiveness, damage, recovery, counterpunching, and major state transitions can be tested without relying entirely on visual observation.

The combat event log provides sufficient information to diagnose unexpected behavior.

Existing gameplay remains unchanged.

---

## Implementation and validation report

Build label: 9C. Gameplay values and artwork remain unchanged.

### Files and architecture

- Boxer0/IdleTestScene.swift: exposes advanceSimulation(by:) containing the existing production render-tick body. update(_:) still validates render timestamps and suspension gaps before calling it. Tests control elapsed simulation time, not wall time. The shared production stepping implementation remains intact. Debug-only fixture methods initialize real textures/nodes without an SKView, place roots and initiate accepted attacks through beginAttack. The test driver subdivides durations into at most 10 ms ticks so the established every-pose hitch policy does not stretch nominal durations. This is not another combat engine.
- Boxer0/JabPlayback.swift: optional CPU randomDraw injection (nil preserves the existing seeded generator), structured CombatDiagnosticEvent and a bounded CombatEventLog (160 events, disabled by default).
- Boxer0/HitReactionPlayback.swift: optional defensive AI randomDraw injection; unchanged 60%/75% and 20/100 ms production parameters.
- Boxer0/ContentView.swift: Debug-only Log menu, enable/disable and clipboard copy. Enabled diagnostics show the last three events; no continuous console output. The full bounded trace is copied, not only those three rows.
- Boxer0Tests/CombatTests.swift: 24 XCTest methods grouped for timing, recovery, geometry/contact, guard, CPU decisions, counters/overlap, damage, combat states, statistics and pause/reset/Rise. All exercise production models or the actual SpriteKit scene, including texture identity for recovery overrides.
- Boxer0.xcodeproj/project.pbxproj: hosted iOS Boxer0Tests unit-test target, app dependency, source membership and configurations.
- Boxer0.xcodeproj/xcshareddata/xcschemes/Boxer0.xcscheme: shared Boxer0 scheme with Debug test action.
- Tests/validate_task9c.py: parses the OpenStep project structure and object references, reads the scheme XML and checks driver/log/source structure. It is not a Swift compiler or XCTest replacement.

### Diagnostics and ordering

Events include simulation time, actor, attack identity/type where applicable, contact result and health transition. Attack starts/ends, confirmed HIT/BLOCK/MISS, interruption, counter attempt/success, reset, health changes, recovery, guard and knockdown/Rise transitions are captured. Contact timestamps use the marker offset within the production scheduler tick. Presentation/state transitions are sampled at applyFrames and use that simulation tick's timestamp; they do not claim sub-tick guard timestamps. Repeated identical transitions are suppressed. Enabling logging mid-action begins a fresh transition baseline.

State/statistics validation reports incompatible attack/recovery/guard/reaction/fall combinations, effective guard while reacting/down/defeated, contact-total mismatches and invalid counter subsets through INVARIANT_FAILURE events. This observes existing states and never changes gameplay decisions.

The established equal-time policy is preserved: snapshot both legal contact results before applying either impact. True ties may trade hits, including lethal hits. For different marker times, the earlier contact resolves first; its HIT can cancel the later attack. Merely overlapping attacks are not automatically treated as simultaneous. Per-fighter contact/damage ownership still prevents duplicate results.

Counters count resolved contact events: J+C=H+B+M. Attacks canceled before contact retain their start/counter-attempt context but contribute no HIT/BLOCK/MISS. Cancellation tests explicitly expect zero outcomes rather than inventing MISS. Reset keeps cumulative statistics and monotonic attack/replay watermarks as before.

### Run in Xcode

Open Boxer0.xcodeproj, choose the shared Boxer0 scheme and an available iPhone simulator, then Product > Test (Command-U). The test action uses Debug, where fixture APIs and the Log menu exist. The hosted test target depends on Boxer0. On a Mac, the command-line equivalent is:

```sh
xcodebuild -project Boxer0.xcodeproj -scheme Boxer0 -showdestinations
xcodebuild -project Boxer0.xcodeproj -scheme Boxer0 -destination 'platform=iOS Simulator,name=iPhone SE (3rd generation)' test
```

Use an installed destination from the first command if that named simulator is unavailable. XCTest failures identify the test, assertion source line and expected/actual values; enable the combat log in scene tests for a bounded timeline when investigating.

### Results and limits

Executed on Windows: Tests/validate_task9c.py, Tests/validate_task9b1.py (which runs 9A, 9B, 8C and 8D validators) Tests/validate_task8a.py, Tests/validate_task8b.py and Tests/validate_recovery_assets.py. All source/asset/project-structure checks passed. Two older validators initially rejected the changed build label; their label assertions were updated from 9B to 9C and rerun successfully. These checks do not execute Swift combat rules.

Swift compilation: NOT RUN; swiftc/Xcode/Apple SDKs are unavailable. XCTest: NOT RUN, so no passed or failed XCTest claim is made. Simulator/iPhone gameplay, render-loop continuity, touch cancellation and full-speed visual acceptance are unverified. The XCTest suite is added and wired, but the acceptance criteria requiring a successful build and executed tests remain pending on Mac. Scene tests control CPU random inputs; physical multitouch and lifecycle notifications still require device validation. The tests cover representative legal/illegal transitions, not every possible interleaving or long-running random exchange. No gameplay defect has been confirmed by executed Swift tests on this host, and no gameplay rule was changed to satisfy a test.

Illustrative event format only (not an executed capture):

```text
0.000 blue ATTACK_START #1 JAB
0.150 blue CONTACT_HIT #1 JAB defender=orange
0.150 orange HEALTH_CHANGED #1 JAB 100->95
0.300 blue ATTACK_END #1 JAB
0.300 blue RECOVERY_START #1 JAB
0.420 blue RECOVERY_END #1 JAB
```
