# Boxer0 — Task 9B: Counterpunching and Vulnerability Windows

**Milestone:** 9B  
**Platform:** iPhone landscape  
**Frameworks:** SpriteKit gameplay, SwiftUI controls  
**Status:** Ready for implementation

## 1. Objective

Extend the existing combat system to recognize counterpunching opportunities during an opponent's attack and recovery phases.

Both fighters should be able to exploit these opportunities using their existing Jab and Cross attacks.

The implementation must:

- Identify when a fighter is temporarily vulnerable.
- Allow legal attacks to land during vulnerability windows.
- Recognize successful counterpunches.
- Preserve the existing spatial contact system.
- Preserve normal punch damage.
- Integrate counterpunching into CPU offensive decisions.
- Provide useful debug diagnostics.

Do not introduce new punch animations, damage multipliers, stamina, dodging, parrying, combinations, or scoring.

## 2. Inspect existing architecture

Before implementation, inspect the latest project source and identify:

1. Shared bidirectional attack execution.
2. Jab and Cross animation timelines.
3. Punch contact markers.
4. Physical recovery states from Task 9A.
5. Guard-entry and effective-guard rules.
6. Hit and block reaction handling.
7. CPU attack preparation and tactical cooldowns.
8. CPU movement and defensive decision logic.
9. Pause, Reset, Rise, and defeat behavior.
10. Independent combat statistics.

Reuse the existing systems.

Do not build a separate counterpunch collision engine.

## 3. Define vulnerability

A fighter is considered **attack-vulnerable** while executing a punch or completing its physical punch recovery.

The vulnerability period begins when the punch animation starts and ends when physical recovery finishes.

| Action | Animation | Additional recovery | Total vulnerability |
|---|---:|---:|---:|
| Jab | 300 ms | 120 ms | 420 ms |
| Cross | 480 ms | 220 ms | 700 ms |

These values come from Task 9A and must remain unchanged.

Vulnerability means the fighter cannot initiate a new guard under the existing action restrictions.

It does **not** mean:

- Every incoming punch automatically hits.
- The fighter takes additional damage.
- The defender's hitbox becomes larger.
- The fighter loses health without contact.
- The attacker gains extra reach.

All hits still require valid spatial contact at the established punch contact marker.

## 4. Vulnerability state

Provide a reliable way to query whether a fighter is vulnerable.

Suggested conceptual interface:

`isAttackVulnerable(fighter)`

The result should be derived from existing action and recovery states.

Avoid maintaining a separate vulnerability timer that can become inconsistent with the actual animation state.

A fighter is attack-vulnerable when:

- Its Jab or Cross animation is active, or
- Its post-punch physical recovery is active.

Once the fighter leaves those states, attack vulnerability ends.

Being hit, knocked down, or rising is governed by existing combat eligibility and reaction rules, not by this counterpunch vulnerability classification.

## 5. Counterpunch definition

For Task 9B, a **successful counterpunch** is an attack that:

1. Was initiated while the opponent was attack-vulnerable.
2. Makes valid spatial contact.
3. Is classified as HIT.
4. Applies normal damage.

Record the opponent's vulnerability state at the instant the counterattack begins.

Do not classify a punch as a successful counter solely because the opponent was vulnerable at some unrelated point in the animation.

An attack started against a vulnerable opponent may be tagged as a counter attempt.

It becomes a successful counter only if its contact outcome is HIT.

If the punch misses, it remains a failed counter attempt.

If the punch is blocked, it is not a successful counter.

**Important:** The counter label is diagnostic in this milestone. It does not change damage, collision geometry, or animation behavior.

## 6. Preserve normal punch damage

All successful attacks continue to use the established damage model.

| Punch | Normal HIT | Counter HIT |
|---|---:|---:|
| Jab | 5 | 5 |
| Cross | 10 | 10 |

Requirements:

- Counter HIT applies damage exactly once.
- Counter MISS applies zero damage.
- Counter BLOCK applies zero damage.
- No critical-hit or counter-damage multiplier.
- No additional hit reaction duration.
- No special knockdown behavior.

A counterpunch is a strategically timed normal punch.

## 7. Counterpunch timing

Use the existing attack and contact timelines.

| Punch | Animation | Contact marker |
|---|---:|---:|
| Jab | 300 ms | 150 ms |
| Cross | 480 ms | 240 ms |

Example:

- Orange begins Cross at 0 ms.
- Orange enters physical recovery at 480 ms.
- Orange becomes ready at 700 ms.
- Blue starts Jab at 500 ms.
- Blue Jab reaches contact at 650 ms.

If the fighters remain in contact range and orange has not entered a higher-priority state, the Jab can land during orange's recovery.

It deals 5 damage and is recorded as a successful counter.

Do not accelerate the Jab animation to make the counter succeed.

Do not extend the orange fighter's recovery to guarantee contact.

## 8. Guard interaction

Preserve the existing defensive rules.

A boxer executing a punch or completing physical punch recovery cannot raise a new guard.

Therefore, a fighter cannot immediately block a counterpunch while still recovering.

However:

- A punch outside contact range remains MISS.
- An already valid defensive state must be respected.
- Counter status must not bypass the ordinary BLOCK classification.
- Guard entry must not become effective earlier than its established 120 ms duration.

Do not disable the opponent's guard artificially beyond the existing action restrictions.

## 9. Simultaneous attacks

Both fighters may legally have active punches at the same time if their existing action states permit it.

Do not introduce a global attack lock that allows only one fighter to punch.

Each fighter's attack must:

- Have its own attack identifier.
- Evaluate contact at its own contact marker.
- Apply its own damage at most once.
- Resolve independently of the other fighter's attack.

If both punches make contact, both may register HIT, subject to the existing reaction and interruption rules.

If a hit legitimately interrupts an attack before its contact marker, that canceled attack must not subsequently apply damage.

Do not invent a universal rule that the player or CPU always wins simultaneous exchanges.

## 10. CPU counterpunch decisions

Extend the existing CPU offensive decision process to recognize when the blue boxer is attack-vulnerable.

The CPU should remain governed by:

- Its existing attack eligibility.
- Punch range.
- Attack preparation delays.
- Tactical cooldowns.
- Physical recovery.
- Guard and hit reaction restrictions.

When the blue boxer is vulnerable, the CPU may favor initiating an attack.

Use a configurable counter-opportunity bias rather than a guaranteed response.

Recommended initial parameter:

`counterOpportunityAttackChance = 65%`

This probability applies only when the CPU is otherwise eligible to begin an attack decision.

It must not:

- Override cooldowns.
- Interrupt active guard.
- Cancel an existing punch.
- Ignore distance.
- Teleport into range.
- Guarantee a HIT.

Preserve the existing Jab/Cross selection weights unless there is a documented reason to change them.

The CPU should not automatically know whether an attack will land.

## 11. CPU preparation and counter windows

The existing CPU preparation delays remain:

- Jab: 180 ms.
- Cross: 280 ms.

These delays matter.

A CPU may recognize a counter opportunity but still begin its punch too late to land before the opponent recovers.

This is acceptable and intentional.

Do not silently shorten CPU preparation delays for counterattacks.

Do not create perfect reflexes or guaranteed counters.

For this milestone, CPU counter decisions use the same information already available to its existing combat controller.

## 12. Movement and positioning

Preserve Task 8B movement behavior.

The CPU may approach or retreat according to its normal distance-management rules.

Do not add a special counterpunch dash or automatic forward lunge.

A counter opportunity should only produce an attack when the existing range and action eligibility rules permit it.

The player retains full control over movement.

A fighter moving away from an incoming counterpunch may cause it to MISS.

Spatial contact remains authoritative.

## 13. Hit reaction and interruptions

Preserve the established reaction priority.

When a counterpunch lands:

- Apply normal damage.
- Trigger the normal hit reaction.
- Interrupt or supersede incompatible states according to the existing combat architecture.
- Invalidate stale animation and recovery callbacks.
- Preserve knockdown behavior if health reaches zero.

A successful counter must not produce a second damage event or an extra reaction.

If an attack is interrupted before its contact marker, cancel its pending contact evaluation.

If an attack has already resolved contact, do not retroactively change its outcome.

## 14. Counter statistics

Keep the existing per-fighter punch and outcome counters.

Add separate counterpunch diagnostics:

**Blue**

- Counter attempts.
- Successful counters.

**Orange**

- Counter attempts.
- Successful counters.

Definitions:

- Counter attempt: attack initiated while the defender is attack-vulnerable.
- Successful counter: counter attempt that resolves as HIT.

Required invariants:

`Blue Jab + Blue Cross = Blue HIT + Blue BLOCK + Blue MISS`

`Orange Jab + Orange Cross = Orange HIT + Orange BLOCK + Orange MISS`

`Successful counters <= Counter attempts`

`Successful counters <= Total HIT`

Counter statistics must be subsets of existing punch statistics, not additional contact outcomes.

Do not increment the ordinary HIT count twice for a successful counter.

If the current combat engine can cancel an attack before contact, preserve its existing counter accounting convention and document how canceled attempts are represented. Do not force canceled punches into HIT, BLOCK, or MISS merely to satisfy an equation.

## 15. Debug diagnostics

Add compact diagnostics such as:

- `Blue Vulnerable: YES/NO`
- `Orange Vulnerable: YES/NO`
- `Blue Counters: 3/5`
- `Orange Counters: 2/4`
- `Last Counter: BLUE JAB HIT`

Keep the existing health, guard, recovery, CPU, and contact diagnostics.

Counter information must not obscure the fighters or controls.

## 16. Reset, Rise, and CPU mode

**Reset Health**

- Clear vulnerability derived from canceled attacks or recovery.
- Cancel stale counter-related callbacks.
- Reset counter statistics according to the existing combat-counter reset policy.
- Preserve existing health and position behavior.

**Rise**

- A rising fighter is not classified as attack-vulnerable merely because it is unable to guard.
- No counter opportunity carries over from before knockdown.
- Restore ordinary combat eligibility after Rise completes.

**CPU OFF**

- Disable new autonomous counter decisions.
- Preserve normal manual blue attacks and counter classification.
- Allow already-started legitimate attacks to resolve according to existing rules.

## 17. Pause and frame stepping

Use the existing simulation clock.

Requirements:

- Vulnerability timing freezes during pause.
- Counter-related attack preparation freezes.
- Frame stepping preserves event ordering.
- Contact is evaluated exactly once.
- No counter window expires using wall-clock time.
- No delayed counter decision fires unexpectedly after Reset or Rise.

## 18. Validation matrix

| Scenario | Expected behavior |
|---|---|
| Blue attacks orange during Cross recovery | Eligible counter attempt |
| Blue counter Jab lands | HIT + successful counter |
| Blue counter Jab misses | MISS, not successful counter |
| Blue attacks orange while idle | Ordinary attack |
| CPU attacks blue during recovery | Eligible CPU counter attempt |
| CPU counter lands | Normal damage |
| CPU counter misses | No damage |
| Counter attack meets raised guard | BLOCK, not successful counter |
| Both fighters punch simultaneously | Independent resolution |
| Attack interrupted before contact | No stale damage |
| Counter HIT causes zero health | Normal knockdown |
| Fighter rises | No stale vulnerability |
| CPU OFF | No autonomous counters |
| Reset during recovery | Vulnerability cleared |
| Pause during counter | Timing freezes |
| Extended exchange | Counters remain consistent |

## 19. Acceptance criteria

- [ ] Both fighters expose correct attack-vulnerability states.
- [ ] Jab vulnerability lasts through its 420 ms attack/recovery cycle.
- [ ] Cross vulnerability lasts through its 700 ms attack/recovery cycle.
- [ ] Counter attempts are recognized at attack initiation.
- [ ] Successful counters require actual HIT.
- [ ] Counter status does not alter damage.
- [ ] Counter status does not alter hitboxes or reach.
- [ ] CPU can recognize counter opportunities.
- [ ] CPU respects existing preparation and cooldown timing.
- [ ] Simultaneous attacks remain independently resolvable.
- [ ] Hit reaction and knockdown work correctly.
- [ ] Guard and movement behavior remain unchanged.
- [ ] Counter statistics are accurate.
- [ ] Existing HIT/BLOCK/MISS accounting remains correct.
- [ ] Pause, Reset, and Rise do not leave stale counter states.
- [ ] No new artwork or gameplay systems are introduced.

## 20. Deliverables

Provide:

1. Swift files modified.
2. How vulnerability is derived from existing action states.
3. Counter-attempt identification and successful-counter classification.
4. CPU counter-opportunity decision integration.
5. Handling of simultaneous attacks and interruptions.
6. Counter statistics and debug readouts.
7. Simulator or iPhone validation results.
8. Any remaining limitations.

## Completion criterion

Both fighters can exploit an opponent's active attack or recovery period using ordinary Jab and Cross punches.

Successful counterpunches are identified and tracked without additional damage or guaranteed contact.

The CPU occasionally takes advantage of openings while continuing to respect normal reaction, preparation, recovery, and distance rules.

All previously accepted combat mechanics remain functional.

## Task9B implementation report

Build label9B. Updated runtime sources: JabPlayback.swift, PunchContact.swift, IdleTestScene.swift and ContentView.swift. Added Tests/CounterChecks.swift and validate_task9b.py. No new assets or target membership are required.

### Vulnerability and counter metadata

isAttackVulnerable derives directly from each fighter's active PunchPlayback or physical PunchRecovery. Combat standing and incompatible-reaction/fall/Rise checks exclude unrelated inability to guard. There is no separate vulnerability countdown. The nominal uninterrupted windows remain420ms Jab/700ms Cross from9A.

At beginAttack, the existing AttackContext captures the opponent's vulnerability as isCounterAttempt. The flag is not changed when the defender later recovers or starts another action. PunchContactEvent carries the snapshot; a successful counter is simply that flag AND ordinary HIT. Spatial-first contact, BLOCK and normal5/10 damage are unchanged. Counter status adds no damage/reaction/knockdown calls.

Each tracker counts attempts at initiation and successes during its existing once-only contact evaluation. Thus successfulCounters<=counterAttempts and successfulCounters<=hits. J/C and H/B/M still count resolved punches only. If a counter is canceled by a legitimate HIT before contact, its attempt remains recorded but no ordinary outcome is fabricated. A blocked or missed attempt is not a success. Reset Health retains cumulative counter stats and last historical counter readout, matching the existing diagnostics policy; it cancels all pending attacks/recoveries so derived vulnerability clears. Rise starts from cleared action states. No attempt flag or opportunity timer carries into the next attack.

### CPU opportunity decisions

CPUOffense adds counterOpportunityAttackChance0.65. It is sampled using the existing seeded RNG only at an otherwise legal ready-state attack decision with a vulnerable blue opponent and valid punch range. Failure waits for the next ordinary300ms decision poll. It never bypasses eligibility, preparation, physical recovery, tactical cooldown, guard, hit reaction or range. Conditional Jab/Cross selection remains70/30 and preparation180/280ms. The final counter-attempt tag is captured at actual punch initiation, not at preparation start; an opportunity may expire during preparation.

Interpretation:65% is a conditional opportunity gate, not a guaranteed counter or shortened response. The previous ordinary ready/in-range policy already always attempted an attack, so it was not possible to increase that100% baseline without changing unrelated behavior. Ordinary non-vulnerable decisions remain unchanged; this parameter limits reaction to vulnerable-opponent opportunities as requested rather than claiming an extra attack-rate bonus.

### Simultaneous contacts and interruption

Replaced the old fixed Blue-first per-tick attack processing with advanceActiveAttacks, sharing the same elapsed duration across both existing clocks. Each pending marker's timeUntilContact is captured before advancing. Different contact times resolve in chronological order; an earlier legitimate HIT cancels the other attack, and its later unprocessed contact is skipped. Outcomes already evaluated remain immutable.

For equal marker times within1e-9s, both contacts and guard classifications are snapshotted BEFORE either reaction is applied. Both may resolve, including a mutual final HIT. The damage handler's explicit simultaneous flag is used only for those already-validated tied contacts, so a first fatal result cannot incorrectly suppress the other contact that occurred at the same time. Per-attacker event replay guards remain active. This is not a global attack lock or a universal player/CPU winner. Both fighters retain independent identities and resolved stats.

The existing detector is still called from one shared resolver; no counter collision geometry was added. Contact ordering is marker-based within the render tick, while existing movement/guard pose rendering remains governed by the prior scene update order. Severe low-FPS rendering still inherits existing contact/recovery-pose preservation and can extend visible animation duration; live exchange behavior needs device review.

### Diagnostics and validation

A small separately typed counterReadout shows derived vulnerability, successful/attempt totals for both fighters and Last Counter actor/kind/outcome, preserving the existing small SwiftUI builder structure. All data is presentation only. Landscape overlay density remains subject to iPhone SE review.

PASS: python Tests/validate_task9b.py checks derived vulnerability, initiation snapshots, HIT-only subset counters,65% opportunity gate, chronological/symmetric contact branches, interruption gates, diagnostics and brace nesting.
PASS: Task9A,8D,8C,8B,8A,7B.1,7A,6D,6C,6B,6A,5C,5B,5A.1 source/asset/numerical regressions. Historical source checks now follow the shared attack scheduler and optional contact result; they do not assume a fixed player-first processing order.

Tests/CounterChecks.swift adds executable fixtures for counter HIT/MISS/BLOCK/cancellation, normal5 damage, duplicate suppression, subset/invariant reconciliation,420/700ms windows, both prevalidated fatal hits resolving, and conditional CPU opportunity selection without shortened preparation. These Swift tests are UNEXECUTED: this Windows host lacks swiftc/Xcode/SpriteKit. No simulator/iPhone acceptance is claimed.

On Mac:

```sh
swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Boxer0/HitReactionPlayback.swift Tests/CounterChecks.swift -o /tmp/counter-checks
/tmp/counter-checks
```

Pending iPhone matrix: counter Jab into Cross recovery for normal5 damage; counter MISS after retreat; counter BLOCK after opponent becomes guarded; ordinary idle-target attack not counted; CPU opportunity/prep window expiry; both active punches with CPU earlier/player earlier/tied contacts; canceled pending marker never damages; final counter knockdown and both Rise controls; CPU OFF, Reset, pause/step and extended exchange. Reconcile each J+C=H+B+M and success<=attempt/HIT. Verify new diagnostics do not cover critical action visibility or controls. No new artwork, multipliers, reach, animation timing, stamina or scoring was introduced.
