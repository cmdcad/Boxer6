# Boxer0 — Task 8C: CPU Offensive AI and Bidirectional Combat

**Milestone:** 8C  
**Platform:** iPhone landscape  
**Frameworks:** SpriteKit gameplay, SwiftUI debug controls  
**Scope:** CPU Jab and Cross attacks, shared contact detection, player damage, and combat-state integration

## 1. Objective

Allow the orange CPU boxer to initiate Jab and Cross attacks independently, using the existing sprite animations, punch timing, contact detection, damage model, and knockdown system.

The CPU should:

- Recognize when the blue boxer is within attacking range.
- Choose between Jab and Cross.
- Execute the appropriate punch animation.
- Register HIT or MISS at the existing contact marker.
- Reduce the blue boxer's health when a punch lands.
- Respect attack cooldowns and combat restrictions.
- Resume movement and defense after attacking.

**Do not introduce player guarding, stamina, scoring, rounds, combinations, or advanced tactics in this milestone.**

## 2. Inspect and preserve existing architecture

Before implementation, inspect the current project files and identify:

1. The player Jab and Cross execution paths.
2. The animation scheduler and contact-frame markers.
3. The existing glove-to-defender spatial contact detector.
4. Health, damage, and defeated-state transitions.
5. Hit reaction, knockdown, down, and Rise behavior.
6. CPU movement and defensive decision controllers.
7. CPU ON/OFF behavior.
8. Pause, frame stepping, and reset handling.

Preserve the existing public behavior and avoid duplicating combat systems.

Refactor only what is necessary to support attacks originating from either fighter.

## 3. Shared attack representation

Introduce or extend an attack context that identifies:

- Attacker: blue or orange.
- Defender: blue or orange.
- Punch type: Jab or Cross.
- Unique attack identifier.
- Attack start simulation time.
- Contact evaluation status.
- Attack completion status.

The same attack-processing pipeline should handle both directions.

Suggested conceptual interface:

`beginAttack(attacker, punchType)`

`evaluateContact(attackContext)`

`completeAttack(attackContext)`

Use existing project naming and architecture where possible.

**Critical requirement:** Each punch evaluates contact exactly once.

Do not create a separate CPU-only collision algorithm.

## 4. Punch animations and timing

Reuse the existing animation contract.

| Punch | Frames | Duration | Contact marker |
|---|---:|---:|---:|
| Jab | 6 | 300 ms | 150 ms |
| Cross | 8 | 480 ms | 240 ms |

The orange boxer uses the established mirrored orientation.

Requirements:

- Punches animate from the orange boxer's current position.
- Preserve its sprite root, baseline, scale, and facing direction.
- Do not flip the sprite a second time.
- Do not move the entire boxer to simulate glove reach.
- Prevent overlapping attacks from the same fighter.
- Return to the appropriate idle or movement state after completion.

Use the existing contact markers, not a newly estimated point of maximum extension.

## 5. CPU attack decision model

Add a simple offensive decision state:

- `ready`
- `preparing`
- `attacking`
- `cooldown`

Keep this separate from movement intentions, defensive decisions, and fighter combat eligibility.

The CPU should consider an attack only when:

- CPU mode is ON.
- The orange boxer is standing.
- It is not guarding or entering guard.
- It is not reacting to a hit or block.
- It is not knocked down or rising.
- No other orange punch is active.
- The blue boxer is standing and attackable.
- The relevant punch is plausibly within range.

Do not let the CPU attack simply because a timer expires.

## 6. Initial offensive tuning

Use the following configurable starting values:

| Parameter | Initial value |
|---|---:|
| Attack decision interval | 300 ms |
| Jab selection weight | 70% |
| Cross selection weight | 30% |
| Jab preparation delay | 180 ms |
| Cross preparation delay | 280 ms |
| Post-Jab cooldown | 650 ms |
| Post-Cross cooldown | 900 ms |
| Minimum interval between completed attacks | 400 ms |

Interpret Jab/Cross weights as conditional selection probabilities when both punches are valid.

If only one punch is valid, the CPU may choose that punch or hold.

Preparation is a delay before the punch begins, not an additional animation frame.

All delays and cooldowns must use the existing scene simulation clock.

The CPU should attack periodically, not continuously.

These values are provisional and should be tuned after iPhone testing.

## 7. Attack range and distance management

Use the existing reach/contact geometry for Jab and Cross.

Before preparing an attack, check whether the blue boxer is plausibly within the selected punch's range.

However, **do not guarantee contact based on that initial check**.

At the punch contact marker, reevaluate the actual fighter positions.

Examples:

- CPU starts a Jab in range; blue boxer retreats before contact → MISS.
- CPU starts a Cross in range; blue boxer stays in range → HIT.
- CPU prepares an attack; blue boxer moves away → CPU may complete the attack and MISS.

Do not automatically cancel an active punch because the defender moves out of range.

Do not automatically reposition the CPU to force contact.

## 8. CPU movement during attacks

Integrate offensive decisions with Task 8B.

Recommended initial behavior:

- While preparing to attack, CPU decelerates to a stop.
- While punching, CPU remains stationary.
- During attack cooldown, movement may resume if otherwise eligible.
- Defensive decisions resume once the CPU is eligible again.

Do not let advance, retreat, idle, or guard animations overwrite an active punch.

Do not allow a movement decision to cancel a punch that has already started.

## 9. Shared contact detection

Extend the current contact detector to support both attack directions.

For each attack:

1. Identify the attacker and defender.
2. Obtain their actual world-space positions.
3. Resolve the appropriate glove contact location.
4. Evaluate contact at the established punch contact marker.
5. Classify the result.
6. Apply the corresponding combat effect once.

For this milestone:

**Blue attacking orange**

- HIT
- BLOCK
- MISS

**Orange attacking blue**

- HIT
- MISS

The blue boxer does not yet have a defensive guard control.

Do not classify a CPU attack as BLOCK unless a functioning blue-boxer guard system has actually been implemented.

Preserve all existing player-to-CPU contact behavior.

## 10. Player health and damage

Use the existing damage values for both fighters.

| Punch | Damage on HIT |
|---|---:|
| Jab | 5 |
| Cross | 10 |

Requirements:

- CPU Jab HIT reduces blue health by 5.
- CPU Cross HIT reduces blue health by 10.
- CPU MISS causes zero damage.
- Health cannot fall below zero.
- Damage applies exactly once per punch.
- Both fighters' health bars update correctly.

Do not introduce separate damage rules for CPU punches.

## 11. Blue boxer hit reaction

When the CPU lands a punch:

- Trigger the blue boxer's existing `hit_react` animation.
- Play four frames over approximately 240 ms.
- Prevent the reaction from changing the fighter's root position.
- Return to idle or the appropriate movement state after recovery.

If the current blue-boxer implementation lacks the necessary reaction integration, extend the existing shared reaction mechanism.

Do not create a second unrelated hit-reaction controller.

## 12. Player defeat and knockdown

When blue health reaches zero:

1. Transition blue from standing to defeated exactly once.
2. Prevent new blue attacks.
3. Stop blue movement.
4. Finish the required final hit reaction.
5. Play blue knockdown: eight frames over approximately 640 ms.
6. Hold the blue down pose.

Once either fighter is defeated, the opponent must stop initiating new attacks.

The blue fighter should use the same established defeat sequence as the orange fighter, with the appropriate sprite assets.

Preserve orange defeat behavior.

## 13. Rise and reset

Preserve the existing manual Rise debug behavior.

If the blue fighter is down and its Rise control is available:

- Play eight Rise frames over approximately 800 ms.
- Keep blue defeated during the Rise animation.
- Restore health to 100 after Rise completes.
- Return blue to standing and idle.
- Restore attack and movement eligibility.

If both fighters have Rise controls, keep their behavior consistent.

Reset Health must cancel:

- Active attacks.
- Pending CPU attack preparations.
- Offensive cooldowns.
- Pending contact evaluations.
- Stale defensive decisions.
- Interrupted reactions and knockdowns, as already supported.

Do not leave an old scheduled CPU punch capable of firing after Reset or Rise.

## 14. CPU defensive and offensive arbitration

The CPU must never enter incompatible actions simultaneously.

Establish explicit priority rules.

Suggested order:

1. Defeated, knockdown, down, or Rise.
2. Hit reaction.
3. Active punch.
4. Active guard or guard entry.
5. Attack preparation.
6. Movement.
7. Idle.

An active punch should complete normally unless interrupted by an existing legitimate combat-state transition.

Do not allow defensive AI to cancel an already active punch merely because the blue boxer begins attacking.

Do not allow offensive AI to cancel an active guard simply because the blue boxer enters punching range.

After guard release, the CPU may consider attacking again.

## 15. CPU ON/OFF behavior

**CPU ON**

- Autonomous movement enabled.
- Autonomous defense enabled.
- Autonomous offense enabled.

**CPU OFF**

- No new CPU attack decisions.
- No new CPU guard decisions.
- No autonomous movement.

If CPU mode is turned OFF during an already-started punch, allow that punch to finish and resolve its contact normally.

Cancel any attack preparation that has not yet started.

Preserve existing manual controls.

## 16. Independent combat counters

Maintain separate statistics for each fighter.

Recommended diagnostics:

**Blue offense**

- Jab count
- Cross count
- HIT
- BLOCK
- MISS

**Orange offense**

- Jab count
- Cross count
- HIT
- MISS

The accounting invariants must remain:

`Blue J + Blue C = Blue HIT + Blue BLOCK + Blue MISS`

`Orange J + Orange C = Orange HIT + Orange MISS`

Counters should increment once per attack and once per resolved outcome.

If the existing UI already provides shared counters, preserve compatibility while adding clearly distinguished per-fighter statistics.

## 17. Pause and frame stepping

All CPU offensive timing must use simulation time.

Verify:

- Pausing during preparation freezes preparation.
- Pausing during a punch freezes animation and contact timing.
- Resuming does not produce duplicate punches.
- Frame stepping advances combat consistently.
- Cooldowns do not expire while the simulation is paused.
- No wall-clock timer bypasses scene pause.

## 18. Debug diagnostics

Add compact diagnostics for:

- `CPU Attack: READY`
- `CPU Attack: PREPARING JAB`
- `CPU Attack: PREPARING CROSS`
- `CPU Attack: JAB`
- `CPU Attack: CROSS`
- `CPU Attack: COOLDOWN`

Also show:

- Last CPU punch result.
- Remaining cooldown, if practical.
- Blue and orange offense counters.

Keep the debug overlay usable in landscape orientation.

## 19. Validation matrix

| Test | Expected result |
|---|---|
| CPU ON, blue in range | CPU eventually attacks |
| CPU ON, blue far away | CPU approaches before attacking |
| CPU Jab lands | Blue loses 5 health |
| CPU Cross lands | Blue loses 10 health |
| Blue retreats before contact | CPU punch can MISS |
| CPU attacks | Correct orange animation plays |
| CPU punches during guard | Not permitted |
| CPU guarding | Does not initiate attacks |
| CPU is hit | Appropriate reaction and arbitration |
| Blue health reaches zero | Blue knockdown sequence |
| Orange health reaches zero | CPU offense stops |
| Blue Rise | Blue recovers correctly |
| CPU OFF | No new autonomous punches |
| Reset during preparation | Pending attack canceled |
| Reset during active punch | No stale contact or damage |
| Pause during attack | Animation and contact freeze |
| Extended exchange | Counters remain consistent |

## 20. Acceptance criteria

- [ ] CPU independently chooses Jab and Cross.
- [ ] Both existing punch animations work correctly for orange.
- [ ] CPU attacks only when eligible.
- [ ] CPU attack pacing is controlled.
- [ ] CPU punches can HIT or MISS.
- [ ] Contact is evaluated at the correct animation marker.
- [ ] Blue health decreases by the correct amount.
- [ ] Blue hit reaction plays correctly.
- [ ] Blue knockdown occurs at zero health.
- [ ] Blue Rise restores combat eligibility.
- [ ] Orange defense and movement still work.
- [ ] Blue offense remains unchanged.
- [ ] Both fighters respect defeat and reset.
- [ ] No duplicate damage or contact evaluations.
- [ ] Independent punch counters reconcile.
- [ ] Pause and frame stepping remain correct.
- [ ] No new gameplay systems outside this milestone.

## 21. Deliverables

Report:

1. Files modified.
2. How the attack pipeline was generalized for both fighters.
3. CPU attack decision and cooldown implementation.
4. Contact and damage integration.
5. Blue hit reaction, defeat, and Rise integration.
6. Test results and counter reconciliation.
7. Any remaining limitations.

## Completion criterion

With CPU mode enabled, the orange boxer approaches the blue boxer, chooses and executes Jab or Cross attacks, and causes the correct damage when its punches land.

The blue boxer can also attack and defeat the orange boxer using the existing system.

Both fighters can independently lose health, react to hits, be knocked down, and recover through the established debug Rise mechanism.

All existing movement, guard, contact, reset, and pause behavior remains functional.

## Task8C implementation report

Build label8C. Updated runtime sources: IdleTestScene.swift, JabPlayback.swift, PunchContact.swift, HitReactionPlayback.swift, FootworkMotion.swift and ContentView.swift. New supporting files: generate_bidirectional.py, bidirectional_manifest.json,35 source PNG/SVG variants and universal image sets, Tests/BidirectionalChecks.swift and validate_task8c.py. No new Swift target membership is required. Copy ALL35 image sets to the Mac.

### Shared combat pipeline

FighterID and AttackContext identify attacker/defender, global scene attack ID, kind, simulation start time, contact evaluation and completion. Per-fighter PunchContactTracker instances retain the same once-per-punch guard and independent stats. Both beginAttack paths use PunchPlayback; both resolve through ONE resolveContact function and ONE tracker.evaluate implementation with actual transforms. The orange root is mirrored only by existing layout. The CPU never repositions itself to reach during a punch.

The event includes attackerID and derived defenderID. FighterHealthState applies the same5/10 damage values to the selected defender and independently guards event replay for each attacking fighter. Blue-to-orange classification retains HIT/BLOCK/MISS; orange-to-blue cannot use BLOCK because the resolver only passes effective guard for an orange defender. Geometry and marker timing are unchanged. CPU reach is checked before preparing, then reevaluated at contact using current positions; moving away can produce MISS. Accepted attacks do not cancel merely because range changed.

Stats preserve existing Blue J/C/H/B/M fields and add Orange J/C/H/M. As in earlier milestones, J/C count attacks that reach contact resolution, so each resolves into exactly one outcome. A punch interrupted by HIT before its contact or rejected after defeat creates no resolved counter entry. This keeps both requested accounting invariants without inventing a MISS for a canceled punch. Attack contexts still record starts/completion independently of those resolved counters.

### CPU offensive controller

CPUOffense is a separate seeded ready/preparing/attacking/cooldown model. Defaults:300ms decision interval,70/30 conditional Jab/Cross selection,180/280ms preparation,650/900ms cooldown and400ms minimum pacing floor. If only one kind is in range, it is selected. Preparations consume scene time, cancel on incompatible defense/hit/defeat or CPU OFF, and do not become punches while paused. Cooldowns are scene-clock durations. A newly started punch presents frame0 before consuming later ticks.

Eligible means both fighters standing, no orange reaction/knockdown/rise, no active guard/block recoil, no other CPU punch and no pending defensive action, with required assets loaded. Guard priority can cancel a preparation but cannot replace an active punch. Active punches interrupt on a legitimate received HIT. Simultaneous contact processing within one render tick has deterministic Blue-first priority; the project does not model sub-frame trades. This order can matter at very low frame rates and should be checked during device exchange testing.

Preparation decelerates via existing FootworkMotion; active punches freeze orange translation and have texture priority over guard/movement. Cooldown allows movement/defense when otherwise eligible. CPU OFF clears unstarted preparation and autonomous movement/guard intent while an active punch continues through its marker and recovery. Reset cancels both punches, tracker ownership, preparation/cooldown, both reactions/falls/rises, defense and block recoil, while preserving positions/counters and clearing held input.

Task8B could stop outside all punch reach. For8C the existing distance controller receives an optional maximum range factor0.99 of effective Cross reach, constrained above its physical minimum close band. This lets a CPU approach into useful attack range without changing collision sizes or body spacing. Original8B threshold behavior remains available when that optional cap is unset.

### Blue reactions and recovery

Blue uses additional INSTANCES of the same HitReactionPlayback and KnockdownPlayback types, not unrelated controllers. Confirmed CPU HIT cancels blue's active attack/held movement, presents recoil frame0, and preserves position. A zero-health HIT records blue defeat once, finishes recoil, plays the8-frame640ms fall and holds down. Movement/new attacks are prohibited until recovery. Existing orange defeat behavior remains.

The existing Rise control dynamically labels itself Blue Rise when blue is down, otherwise Rise for orange; both use the same eight-frame800ms playback and restore ONLY their own health after completion. Defeated state and zero health persist through Rise. If both are down, Blue Rise has priority, after which orange Rise remains available. Reset is available throughout. No stale completion closure exists: all clocks are value-state models canceled synchronously.

### Assets and diagnostics

35 approved palette variants: orange Jab6/Cross8, blue hit_react4/knockdown8/down1/rise8. PNG alpha is byte-identical to each original pose; canvas, roots, scale, baselines and silhouettes are preserved. SVG palette fills are updated too. These are palette-only variants, so markings/pose details are inherited from their source artwork. A mirrored punch/blue-recovery contact sheet was visually inspected. Color blending on anti-aliased edges uses a constrained palette-to-ink interpolation; physical-device appearance remains unreviewed.

HUD adds CPU Attack:READY/PREPARING JAB/PREPARING CROSS/JAB/CROSS/COOLDOWN, last CPU result, Orange offense totals and Blue animation state, preserving existing health/guard/recoil diagnostics and Blue counts. Missing bidirectional assets are reported explicitly; CPU attacks require both its punch and blue recovery sets. The overlay is denser and needs iPhone SE landscape usability review.

### Validation results

PASS: python Tests/validate_task8c.py verifies35 integrated palette variants, alpha/silhouette identity, a single bidirectional resolver/damage path, actor contexts, shared blue recovery, CPU clock/disable wiring, diagnostics and brace nesting.
PASS: updated8B,8A,7B.1,7A,6D,6C,6B,6A,5C,5B,5A.1 source/asset/numerical regressions. Historical source assertions now follow the generalized resolver rather than obsolete one-way handler text; no old contact geometry constants were changed.

Added Tests/BidirectionalChecks.swift for mirrored Blue/Orange HIT/MISS, defender-routed health, duplicate rejection, context status, per-fighter counter reconciliation, blue final damage/fall/Rise, CPU range/preparation/cooldown/OFF/reset, weighted selection and shared punch markers. These EXECUTABLE Swift tests were NOT run: Windows lacks swiftc/Xcode/SpriteKit. No simulator/device success is claimed.

On Mac:

```sh
swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Boxer0/HitReactionPlayback.swift Tests/BidirectionalChecks.swift -o /tmp/bidirectional-checks
/tmp/bidirectional-checks
```

Pending iPhone validation: confirm8C and all assets; CPU approaches/chooses both attacks, CPU HIT5/10 versus retreat MISS, orange root stationary during punch, guarding prevents attacks, legitimate HIT interrupts, CPU OFF during preparation and active punch, pause/step and Reset during every offensive phase, Blue defeat/final recoil/fall/down/Rise, Orange defeat/Rise, extended counter reconciliation, no stale events and landscape HUD readability. Orange punches retain300/480ms timings and150/240ms contact markers. Frame stepping uses the shorter active punch interval so an orange punch is not stepped by a whole idle-frame duration.

No blue guard, stamina, scoring, rounds, combos, referee logic or advanced tactics were added.
