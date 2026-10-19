# Boxer0 — Task 9A: Combat Pacing and Recovery

**Milestone:** 9A  
**Platform:** iPhone landscape  
**Frameworks:** SpriteKit gameplay, SwiftUI controls  
**Scope:** Attack recovery, defensive transitions, action eligibility, and combat rhythm  
**Status:** Ready for implementation

## 1. Objective

Refine the existing combat system so both fighters have consistent, predictable recovery periods after attacking and blocking.

The implementation must improve combat pacing without changing the established punch animations, damage values, contact detection, or CPU decision probabilities.

The player should experience:

- Distinct timing differences between Jab and Cross.
- Brief recovery after each punch.
- Predictable transitions from punching to guarding.
- Smooth recovery after successful blocks.
- No unintended input delays or unresponsive controls.
- No overlapping or contradictory combat animations.

The CPU must follow the same physical recovery rules as the player.

**Do not introduce stamina, fatigue, new punches, combinations, dodging, scoring, or rounds.**

## 2. Inspect the existing implementation

Before making changes, inspect the latest project source and identify:

1. The shared attack execution pipeline.
2. Jab and Cross animation completion handling.
3. Existing attack cooldowns and CPU preparation delays.
4. Blue hold-to-guard input.
5. Orange autonomous guard behavior.
6. Guard-entry and block-reaction animation logic.
7. Hit reaction and knockdown transitions.
8. Movement eligibility and deceleration.
9. Pause, frame stepping, Reset, and Rise behavior.
10. Any existing recovery or action-lock mechanisms.

Do not add a second recovery system if equivalent functionality already exists.

Prefer one shared recovery mechanism used by both fighters.

## 3. Distinguish animation completion from combat readiness

Introduce an explicit recovery concept.

A fighter may finish a punch animation but remain temporarily unable to initiate another punch.

Suggested conceptual action phases:

- `ready`
- `attacking`
- `recovering`

Keep these distinct from fighter combat eligibility, movement intention, and guard state.

Do not replace the existing combat architecture unnecessarily.

A fighter is ready to initiate another attack only when all relevant conditions are satisfied:

- Standing.
- Not attacking.
- Not recovering.
- Not guarding or entering guard.
- Not in hit or block reaction.
- Not knocked down or rising.
- Not otherwise restricted by existing controls.

## 4. Initial recovery timing

Use configurable values:

| Action | Animation duration | Additional recovery |
|---|---:|---:|
| Jab | 300 ms | 120 ms |
| Cross | 480 ms | 220 ms |

The additional recovery begins **after** the punch animation completes.

This produces the following minimum attack cycles, before any CPU-specific preparation or cooldown:

| Punch | Total attack + recovery |
|---|---:|
| Jab | 420 ms |
| Cross | 700 ms |

These values are initial tuning parameters, not permanent gameplay constants.

The Jab should remain noticeably quicker than the Cross.

Do not slow down the existing punch animations themselves.

## 5. Recovery behavior

When a punch completes:

1. Mark the active attack as finished.
2. Enter the appropriate recovery period.
3. Preserve the established standing pose or transition to idle.
4. Prevent new attacks until recovery completes.
5. Return to the ready state when eligible.

Requirements:

- Recovery must not repeat the punch animation.
- Recovery must not introduce visible sprite snapping.
- Recovery must not move fighter roots.
- Recovery must not apply additional contact or damage.
- Recovery must complete exactly once.

Do not extend recovery indefinitely because an attack button remains pressed.

## 6. Player input during recovery

For Task 9A, use a conservative input policy.

**Jab and Cross**

- An attack pressed during recovery is ignored.
- No automatic attack is queued.
- The player must press again after recovery.

This prevents accidental rapid-fire punching and avoids introducing combination buffering prematurely.

**Guard**

- Guard input may be held during recovery.
- Guard cannot become effective until the recovery rules permit guard entry.
- If Guard is still held when guard entry becomes eligible, begin raising guard.
- If Guard was released during recovery, do not activate guard afterward.

Preserve the existing hold-to-guard behavior.

## 7. Defensive vulnerability after attacks

Recovery should create a short, understandable defensive opening.

Initial policy:

- During punch animation, the boxer cannot raise a new guard.
- During additional punch recovery, the boxer cannot raise a new guard.
- After recovery completes, guard entry may begin.
- Guard becomes effective only after its existing 120 ms entry animation.

Example: blue throws a Cross.

- Cross animation: 480 ms.
- Additional recovery: 220 ms.
- Guard entry: 120 ms.
- Earliest effective guard after starting the Cross: 820 ms.

This assumes the Cross is not interrupted by a higher-priority combat event.

Do not make recovery automatically block incoming attacks.

Do not allow guard input to bypass the recovery window.

## 8. Hit reaction priority

An incoming HIT must retain the existing reaction and damage behavior.

If a fighter is hit while recovering:

- Apply damage once through the existing contact system.
- Interrupt or supersede the pending recovery state as required by the established hit-reaction architecture.
- Play the existing hit reaction.
- Do not leave an outdated recovery callback that can overwrite the reaction.

After a nonfatal hit reaction, return to the appropriate eligible standing state.

For this milestone, do not stack a second full punch-recovery period after an interrupted hit reaction.

If the hit causes defeat, preserve the established knockdown sequence.

## 9. Block reaction recovery

Successful blocks should feel responsive but not mechanically abrupt.

Use the existing visual block reaction from Tasks 7B.1 and 8D.

Initial policy:

- Guard remains logically held during the block response.
- The block response finishes before normal standing actions resume.
- If Guard remains held, return to the protected guard pose.
- If Guard is released during the response, return to the appropriate unguarded standing state.
- Do not permit attacks while the block response is active.

Do not introduce an additional fixed block cooldown in this milestone.

The existing block-response animation provides the necessary recovery interval.

Do not create artificial delays after every successful block.

## 10. CPU offensive pacing

Preserve the existing Task 8C CPU parameters:

- Attack decision interval: 300 ms.
- Jab preparation delay: 180 ms.
- Cross preparation delay: 280 ms.
- Post-Jab cooldown: 650 ms.
- Post-Cross cooldown: 900 ms.

The new shared recovery system must not accidentally double the intended CPU delay.

**Integration rule:**

Keep CPU tactical cooldown and shared physical recovery as separate eligibility constraints.

The CPU may initiate another attack only when both have expired.

If the existing CPU cooldown begins after attack completion, calculate readiness using the later of:

- Physical recovery completion.
- CPU tactical cooldown completion.

Do not add the two delays together unless the current architecture explicitly requires sequential behavior and that choice is documented.

Report the resulting earliest CPU attack timings.

## 11. CPU defensive pacing

Preserve Task 8A.1:

- Jab guard reaction delay: 20 ms.
- Cross guard reaction delay: 100 ms.
- Guard entry: 120 ms.
- Guard attempt probabilities: Jab 60%, Cross 75%.

These parameters should remain unchanged.

However, CPU guard entry must respect the new physical recovery restrictions.

If the CPU is recovering from its own punch:

- It may recognize the incoming attack.
- It must not instantly raise guard.
- It must not bypass recovery.
- A defensive decision may be discarded if its opportunity expires before guard can be raised.

Do not queue indefinite defensive actions.

This creates meaningful openings for counterattacks without introducing a new counterpunch mechanic.

## 12. Movement during recovery

Use a simple initial policy:

- Movement remains disabled during active punch animations.
- During additional recovery, the boxer remains stationary.
- After recovery, normal movement eligibility returns.

For blue:

- Preserve existing held Advance and Retreat inputs.
- If movement remains held when recovery completes, resume according to existing movement rules.

For orange:

- Resume CPU distance management after recovery if otherwise eligible.

Do not add footwork during punch recovery in this milestone.

## 13. Action arbitration

Ensure a single coherent action-priority system.

Suggested priority:

1. Defeat, knockdown, down, and Rise.
2. Hit reaction.
3. Active punch.
4. Block reaction.
5. Punch recovery.
6. Guard entry and raised guard.
7. Movement.
8. Idle.

The order is conceptual; preserve existing legitimate transitions.

Important requirements:

- An active punch cannot be canceled by a lower-priority movement or guard request.
- Recovery cannot overwrite a knockdown.
- Guard entry cannot bypass recovery.
- A stale animation completion cannot change the current action unexpectedly.
- Movement animation cannot overwrite recovery or a hit reaction.

Use explicit state validation or generation tokens for delayed callbacks where appropriate.

## 14. Reset, Rise, and CPU mode

**Reset Health**

- Cancel active recovery.
- Invalidate pending recovery completions.
- Restore eligible standing states.
- Preserve the existing health and animation reset behavior.

**Rise**

- Do not resume stale pre-knockdown recovery.
- Once Rise completes, return to the normal ready state.
- Preserve the existing fresh-press requirement for blue Guard.

**CPU OFF**

- Stop new autonomous decisions as already implemented.
- Do not leave a fighter permanently locked in recovery.
- A legitimate active action should finish according to existing CPU OFF rules.

## 15. Pause and simulation timing

Use the existing SpriteKit simulation clock.

Requirements:

- Recovery freezes when the game is paused.
- Recovery resumes correctly.
- Frame stepping advances recovery consistently.
- No wall-clock timers bypass pause.
- No large time jumps after resume.
- Recovery completion occurs exactly once.

Use the same timing conventions already established for punches and guard entry.

## 16. Debug diagnostics

Add compact per-fighter recovery diagnostics.

Examples:

- `Blue Action: READY`
- `Blue Action: JAB`
- `Blue Action: RECOVERING JAB`
- `Orange Action: RECOVERING CROSS`

Optionally show remaining recovery time in milliseconds.

Preserve existing health, guard, CPU movement, attack-state, and combat-counter diagnostics.

Do not overcrowd the landscape display.

## 17. Validation matrix

| Scenario | Expected result |
|---|---|
| Blue Jab completes | 120 ms recovery |
| Blue Cross completes | 220 ms recovery |
| Jab pressed during recovery | Ignored |
| Cross pressed during recovery | Ignored |
| Guard held during recovery | Raises after recovery |
| Guard released during recovery | No delayed guard |
| Incoming HIT during recovery | Correct hit reaction |
| HIT causes zero health | Correct knockdown |
| Guarded CPU punch | Existing block reaction |
| Guard released during block response | No stale protected pose |
| CPU finishes Jab | Physical recovery respected |
| CPU finishes Cross | Physical recovery respected |
| CPU tactical cooldown active | No new CPU attack |
| CPU recovering when threatened | No instant guard |
| Blue movement held during recovery | Resumes afterward |
| CPU movement after recovery | Distance AI resumes |
| Reset during recovery | Recovery canceled |
| Rise after knockdown | No stale recovery |
| Pause during recovery | Remaining time freezes |
| Extended combat exchange | No overlapping animations |
| Extended combat exchange | Counters remain consistent |

## 18. Acceptance criteria

- [ ] Jab has 120 ms additional recovery.
- [ ] Cross has 220 ms additional recovery.
- [ ] Both fighters use the same physical recovery rules.
- [ ] No new attacks start during recovery.
- [ ] Player attacks during recovery are not queued.
- [ ] Guard cannot bypass recovery.
- [ ] Held Guard activates when recovery finishes, if still eligible.
- [ ] Existing block reactions remain smooth.
- [ ] CPU tactical cooldown is not accidentally added twice.
- [ ] CPU defensive AI respects recovery.
- [ ] Movement resumes appropriately after recovery.
- [ ] Hit reactions and knockdowns override stale recovery.
- [ ] Reset and Rise clear recovery correctly.
- [ ] Pause and frame stepping work correctly.
- [ ] Existing HIT/BLOCK/MISS and damage rules remain unchanged.
- [ ] No new animations or gameplay systems are introduced.

## 19. Deliverables

Provide:

1. Swift files modified.
2. Shared recovery state implementation.
3. Jab and Cross recovery timing integration.
4. Player Guard interaction during recovery.
5. CPU tactical cooldown integration and calculated earliest attack timings.
6. Action arbitration and stale-callback safeguards.
7. Debug diagnostic changes.
8. Simulator or iPhone validation results.
9. Any remaining limitations.

## Completion criterion

Both fighters now have distinct Jab and Cross recovery periods.

Punches cannot overlap, guarding cannot bypass recovery, and movement resumes smoothly once a boxer is ready.

The CPU retains its existing tactical behavior while respecting the same physical restrictions as the player.

Combat feels more deliberate without becoming sluggish, and all previously accepted mechanics remain functional.

## Task9A implementation report

Build label9A. Updated runtime Swift files: JabPlayback.swift, IdleTestScene.swift and ContentView.swift. Added Tests/RecoveryChecks.swift and validate_task9a.py; historical source fixtures were adapted to common-duration frame stepping and the9A block-release policy. No new assets, animation poses or target membership are required.

### Shared physical recovery

PunchRecovery stores ready/attacking/recovering, punch kind and remaining scene time. Both fighters use separate instances of this SAME model. Configurable Jab120ms/Cross220ms recovery begins only when the existing punch clock reports completion, after all300/480ms of animation. Repeated completion calls cannot restart it. Recovery holds the established idle/standing pose without another clip or any contact/damage/root movement.

Shared eligibility gates exclude recovery for new attacks and guard entry, plus the existing combat/reaction/guard/asset restrictions. Blue attacks during recovery are ignored without queuing. Held Guard survives but cannot raise or protect until recovery finishes, then the existing120ms entry begins. Release during recovery clears that intent. Nominal minimum blue attack cycles are420ms Jab/700ms Cross; earliest effective guard after starting them is540ms/820ms respectively, before interruption or render quantization.

Movement inputs are deliberately retained at blue punch start/completion and can be recorded during its punch/recovery; this supersedes the old fresh-direction-press behavior for those transitions. Translation remains zero until recovery ends, then an un-released direction resumes automatically. HIT, Reset, pause and lifecycle input cancellation retain their separate existing rules. Orange recovery immediately holds footwork stationary, resuming distance AI afterward when otherwise eligible.

### HIT, defense and block response

Confirmed HIT cancels the defender's physical recovery and starts the existing hit reaction/defeat sequence. No second punch recovery is appended after interrupted recoil. Reset, scene removal, Rise start and completion cancel obsolete recovery. CPU OFF does not stop the physical clock; an active punch and its legitimate recovery finish normally.

CPU canRequestGuard excludes physical recovery, so event-driven defense cannot bypass it or queue indefinite protection. Probabilities60%/75%,20/100ms reaction delays and120ms guard entry are unchanged.

The existing physical block-response animation is the ONLY block recovery. Guard release now removes protection immediately while allowing its short recoil to finish visually; attacks/movement remain restricted during the remaining response. Held Guard stays logically effective through BLOCK, returning to the held pose. Releasing/repressing during an unprotected response cannot skip a fresh guard entry. No fixed delay is appended after recoil. This intentionally refines the earlier8D immediate visual cancellation policy to satisfy9A's requirement that the response finish before standing actions resume.

### Parallel CPU tactical cooldown

CPU tactical parameters are unchanged:300ms decision interval,180/280ms preparations,650/900ms post-animation cooldowns,70/30 conditional selection and400ms pacing floor. Physical recovery and tactical cooldown begin at the SAME punch completion and advance concurrently. Eligibility uses the later expiry, not their sum. Defensive guard/preparation cancellation now cancels only PREPARING and preserves an already-running tactical cooldown; it cannot erase cooldown as a side effect of defending.

Nominal earliest follow-up starts, assuming uninterrupted eligibility, valid range and the next decision poll immediately after cooldown:

| Previous punch | Physical ready after its animation | Tactical ready after its animation | Next Jab start from previous attack start | Next Cross start from previous attack start |
|---|---:|---:|---:|---:|
| Jab |120ms|650ms|300+650+180=1130ms|300+650+280=1230ms|
| Cross |220ms|900ms|480+900+180=1560ms|480+900+280=1660ms|

The300ms decision interval remains the ready-state polling cadence; the existing controller does not add a mandatory extra300ms wait after an expired cooldown. Normal render/decision ticks can add small quantization; HIT, guard, range loss, missed decisions or other restrictions can delay these lower bounds. Recovery itself adds no extra650+120 or900+220 sequential delay.

### Simulation timing and diagnostics

Recovery advances before this tick's punch completion, so a newly started recovery cannot consume the punch-completion tick twice. Pausing freezes it; resume retains the existing large-delta guard. Frame Step now supplies ONE common duration to physical recovery, punches, guard, recoil, AI and reactions instead of silently stepping different models by50/60/40ms simultaneously. Its duration is chosen from active animation periods and remaining physical recovery; this preserves partial clocks and exact short final recovery steps. It no longer resets the punch/idle accumulator on each deliberate Step. No independent timers or asynchronous callbacks were introduced.

Compact Blue Action/Orange Action diagnostics show attack/recovery and higher-priority reaction/guard states while preserving existing HUD and counters. The large SwiftUI body remains split into small builders for older compiler compatibility.

### Validation

PASS: python Tests/validate_task9a.py checks shared120/220ms state, post-animation completion wiring, eligibility/guard/movement locks, held movement retention, CPU preparation cancellation and parallel clock wiring, block-response release presentation, diagnostics and brace nesting.
PASS: Task8D,8C,8B,8A,7B.1,7A,6D,6C,6B,6A,5C,5B,5A.1 source/asset/numerical regressions. Old source assertions now follow common scene-duration stepping rather than forced per-model frame advancement.

Tests/RecoveryChecks.swift exercises420/700ms nominal cycles, exact120/220ms durations,540/820ms earliest guard, repeat completion/no extension, pause, cancellation, parallel CPU cooldown and its preservation during defense, CPU mode independence and unprotected guard release while block response finishes. These Swift executable tests were NOT run: Windows lacks swiftc/Xcode/SpriteKit. No simulator or iPhone validation is claimed.

On Mac:

```sh
swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Boxer0/HitReactionPlayback.swift Tests/RecoveryChecks.swift -o /tmp/recovery-checks
/tmp/recovery-checks
```

Pending iPhone validation: confirm9A; measure Jab/Cross recovery; tap during recovery without queued punches; hold/release Guard through recovery; retain movement through punch/recovery; incoming HIT during recovery and final defeat; release Guard during BLOCK with immediate vulnerability but finishing response; verify CPU cooldown not doubled or canceled by defense, no CPU guard during physical recovery, Reset/Rise/CPU OFF, pause/resume and common-duration stepping. Reconcile both J+C=H+B+M counters during extended combat and check landscape HUD readability. Perceptual smoothness and real thumb responsiveness remain unverified; no damage, geometry, punch/guard animation duration or CPU probability tuning changed.
