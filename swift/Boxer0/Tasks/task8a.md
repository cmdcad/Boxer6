# Boxer0 — Task 8A: Basic Opponent AI

## 1. Objective

Implement a lightweight defensive AI controller for the orange boxer using the existing Swift/SpriteKit architecture.

The CPU should autonomously:

1. Observe the blue boxer's actions.
2. Decide whether to defend.
3. Raise its guard using the existing animation.
4. Maintain guard for a short interval.
5. Release guard and return to idle.

The CPU must remain stationary and must not throw punches.

Preserve all completed functionality through Task 7B.1, including health, damage, knockdown, manual Rise, HIT/BLOCK/MISS detection, and visible guard-impact recoil.

Inspect the latest Swift source files before implementation. Reuse existing guard logic rather than creating a second blocking system.

## 2. AI operating modes

Introduce a simple control mode for the orange boxer:

- `Manual`
- `CPU`

**Manual mode**

Preserve the existing Task 7A Guard toggle behavior.

**CPU mode**

The AI controls guard activation and release automatically.

The manual Guard control should be disabled while CPU mode is active.

Add a compact debug control:

`CPU: OFF / ON`

Default to CPU OFF initially so existing tests remain reproducible.

Switching modes must clear pending AI decisions and avoid leaving the boxer in an inconsistent guard state.

## 3. AI responsibilities

The AI is responsible only for defensive decisions.

It may:

- Observe the blue boxer's current punch.
- Check whether the fighters are within potential punching range.
- Decide whether to raise guard.
- Hold guard temporarily.
- Release guard after its defensive interval.

It must not:

- Move the orange boxer.
- Initiate Jab or Cross.
- Modify health directly.
- Change contact geometry.
- Override the existing punch outcome system.
- Trigger hit reactions independently.

All defensive outcomes must continue to use the established contact-resolution pipeline.

## 4. Defensive decision model

Use a simple event-driven approach rather than checking random decisions every rendered frame.

When the blue boxer starts a Jab or Cross, the CPU may attempt to defend if the opponent is within potential punching range.

Recommended provisional settings:

| Parameter | Jab | Cross |
|---|---:|---:|
| Chance to attempt guard | 60% | 75% |
| Reaction delay | 100 ms | 140 ms |
| Guard hold after activation | 500 ms | 650 ms |

These are prototype tuning values, not final difficulty settings.

The reaction delay represents how long the CPU takes to respond after recognizing the incoming attack.

The existing guard-entry animation still takes 120 ms.

**Important:** A defensive decision does not guarantee a successful block.

For example, the established Jab contact marker occurs approximately 150 ms after punch initiation. A 100 ms reaction delay plus 120 ms of guard entry means a CPU starting unguarded cannot fully block that Jab in time.

That is acceptable and intentional. The CPU should sometimes react too late.

Do not shorten the existing guard animation or move punch contact markers to manufacture successful blocks.

## 5. Range awareness

The CPU should not automatically guard every time the player punches from the opposite side of the ring.

Before deciding to guard:

- Evaluate the existing fighter separation.
- Use established punch reach/contact geometry where practical.
- Determine whether the punch could plausibly reach the defender.

Do not modify the contact detector.

A CPU guard decision is based on anticipated danger, while the actual HIT/BLOCK/MISS outcome remains determined at the punch contact frame.

Do not treat predicted range as a confirmed contact.

## 6. AI state management

Introduce a small defensive AI state machine.

Suggested states:

- `idle`
- `reacting`
- `guarding`

**Idle**

CPU is observing and waiting.

**Reacting**

CPU has decided to guard but is waiting for its reaction delay.

**Guarding**

CPU has requested guard activation and is maintaining its defensive interval.

The existing orange-boxer animation system remains responsible for displaying guard entry and the held guard pose.

Do not duplicate the animation state machine inside the AI controller.

Keep AI decision state separate from:

- Combat eligibility.
- Defensive guard state.
- Sprite animation playback.

## 7. Guard activation

When the CPU's reaction delay expires:

1. Verify CPU mode is still enabled.
2. Verify the orange boxer is standing.
3. Verify the boxer is not in an incompatible animation.
4. Request guard activation through the existing guard system.
5. Allow the normal three-frame guard-entry animation to play.

The CPU must not directly force `Guard: ACTIVE`.

Guard protection becomes effective only when the existing entry animation completes.

If the CPU is hit before guard becomes effective, preserve Task 7A's existing behavior: cancel guard entry, play the hit reaction, and clear the pending defensive action.

## 8. Guard duration and release

Once the CPU requests guard activation, maintain it for the configured defensive interval.

Use scene time for all durations.

After the hold interval:

- Request guard release.
- Return to idle.
- Resume observing player actions.

Do not leave the CPU permanently guarding.

If another threatening punch begins while the CPU is already guarding, extend the current guard interval rather than restarting the guard-entry animation.

Keep a maximum continuous guard duration of approximately 1.5 seconds for this prototype.

This prevents repeated attacks from keeping the CPU in guard indefinitely.

## 9. Repeated punch handling

The AI must respond to punch-start events, not every rendered frame of the punch animation.

Requirements:

- Evaluate each new punch once.
- Do not create duplicate reaction decisions.
- Do not queue multiple guard activations.
- Do not restart guard entry unnecessarily.
- If already guarding, extend the hold interval within the configured maximum.
- If already reacting, preserve the earliest pending reaction unless a clearly documented replacement policy is needed.

Use the existing punch identity or event mechanism where available.

Avoid adding an independent polling loop that repeatedly schedules the same decision.

## 10. Defeat, knockdown, and recovery

The CPU must not make defensive decisions while the orange boxer is defeated.

When health reaches zero:

- Cancel pending AI reactions.
- Clear AI guard intent.
- Preserve the existing hit-reaction and knockdown sequence.
- Remain inactive while down.

During Rise:

- Do not activate guard.
- Do not initiate new AI decisions.

After Rise completes:

- Resume CPU defensive behavior if CPU mode is enabled.
- Start from the idle AI state.
- Leave guard OFF until a new defensive decision occurs.

Reset Health should also clear pending decisions and restore a consistent idle state.

## 11. Pause and frame stepping

Use the existing SpriteKit scene-time system for all AI timing.

- Pause freezes pending reaction delays.
- Pause freezes guard-hold intervals.
- Resume continues from the remaining time.
- Frame stepping advances AI timing consistently with the existing scene clock.
- No wall-clock timers or `DispatchQueue.asyncAfter` for combat decisions.
- No duplicate guard activations when resuming.

Keep decision execution deterministic for a given event sequence and random-number seed.

## 12. Debug diagnostics

Preserve the existing HUD, counters, health bars, and animation diagnostics.

Add a compact AI status readout:

- `CPU: OFF`
- `CPU: idle`
- `CPU: reacting`
- `CPU: guarding`

Optionally show:

- Current reaction delay remaining.
- Guard hold time remaining.
- Last decision: `Guard` or `Ignore`.
- Observed punch: `Jab` or `Cross`.

Keep the diagnostics unobtrusive in landscape orientation.

The AI state should not be confused with the existing guard state.

For example:

`CPU: guarding | Guard: RAISING`

is valid while the guard animation is still playing.

## 13. Validation

Test the following scenarios:

| Scenario | Expected result |
|---|---|
| CPU OFF | Manual Guard works normally |
| CPU ON | Manual Guard disabled |
| Player idle | CPU remains idle |
| Jab from long range | CPU generally ignores threat |
| Cross from long range | CPU generally ignores threat |
| Jab within range | CPU sometimes attempts guard |
| Cross within range | CPU frequently attempts guard |
| CPU reacts too late | Normal HIT occurs |
| CPU guard fully active at contact | BLOCK occurs |
| Punch misses | MISS, regardless of AI decision |
| CPU blocks punch | Existing block recoil plays |
| Guard hold expires | CPU releases guard |
| Repeated punches | No duplicate decisions |
| CPU defeated | AI stops |
| CPU rises | AI resumes idle observation |
| Reset Health | Pending AI decisions cleared |
| Pause during reaction delay | Countdown freezes |

Additional acceptance checks:

- [ ] CPU mode can be enabled and disabled.
- [ ] Manual Guard remains functional when CPU is OFF.
- [ ] CPU does not move or attack.
- [ ] AI decisions occur once per punch-start event.
- [ ] Reaction delay and guard-entry timing remain independent.
- [ ] AI cannot bypass the established guard activation rules.
- [ ] Guard eventually releases.
- [ ] Guard is cleared on defeat.
- [ ] No pending AI decision survives Reset Health.
- [ ] HIT/BLOCK/MISS counters remain consistent.
- [ ] Blocked punches still cause zero damage.
- [ ] Unblocked punches still cause normal damage.
- [ ] Existing hit reactions, knockdowns, and Rise remain functional.
- [ ] No stamina, scoring, referee counts, or match outcomes are introduced.

## 14. Deliverables

Provide:

1. Updated Swift source files.
2. Basic defensive AI controller.
3. CPU ON/OFF debug control.
4. Configurable reaction and guard-hold parameters.
5. AI state diagnostics.
6. Device or simulator validation results.
7. Brief explanation of how AI decisions integrate with the existing guard system.
8. Any remaining limitations.

## Completion criterion

With CPU mode enabled, the orange boxer autonomously recognizes potentially threatening Jab and Cross attacks, sometimes attempts to guard, visibly raises its gloves, holds guard briefly, and returns to idle.

Successful blocks use the existing BLOCK outcome and block-impact animation.

Late reactions can result in HIT, while out-of-range punches remain MISS.

The CPU does not move or attack, and all previously implemented gameplay functionality remains intact.

## Task 8A implementation report

Updated existing HitReactionPlayback.swift, IdleTestScene.swift, ContentView.swift and JabPlayback.swift. No new runtime target membership or assets are required. Build label8A.

DefensiveAI is a Foundation-only idle/reacting/guarding controller, separate from health, guard and animation. CPU defaults OFF. A compact CPU ON/OFF control sits beside Guard; manual Guard is disabled in CPU mode. Switching either direction clears pending AI state and releases guard/recoil. CPU never moves, punches, applies health changes, edits contact geometry or directly emits combat outcomes.

Each accepted blue punch increments a scene-local monotonic start identity and calls observe once. Rejected punch taps create no decisions. Existing contact geometry supplies a pure predicted-overlap test using the extended attacking-glove position and current mirrored defender target; this does not increment contact counters. Out-of-range or incompatible/defeated observations are ignored. In idle, seeded random sampling chooses one attempt with Jab60%/Cross75% probability. Duplicate starts are ignored, reacting preserves the earliest pending decision, and guarding extends the existing hold within the cap rather than replaying entry.

Settings are centralized in DefensiveAIProfile: Jab delay100ms/hold500ms, Cross140ms/650ms; maximum continuous guard1.5s. Seed defaults12345. Reset Health restores the seed while retaining monotonic start identities; other cancellations retain RNG progression. Equal seeds and accepted event sequences produce equal decisions.

When delay expires, the scene rechecks normal guard eligibility and calls the SAME requestGuard method used by Manual mode. Guard protection is never forced on. Its existing120ms entry, hit interruption, BLOCK classification and visible recoil remain intact. Hold starts on requested activation and includes entry time. Expiry releases guard; repeated threatening punches cannot extend beyond1.5s since that activation. AI and guard transition time are split at their boundaries within a scene tick so an activation does not receive a full tick of free entry progression.

JabPlayback now exposes read-only timeUntilContact. In CPU mode, the scene samples protection at that exact contact-time boundary before finishing a delayed render tick. Resolution still occurs once through the existing tracker and unchanged spatial geometry; this avoids a render hitch granting a late guard protection retroactively.

HIT cancels pending AI and guard intent before the existing recoil. Defeat/down/Rise never accept new decisions. Reset, scene removal, Rise start/completion and mode changes clear pending actions. CPU remains enabled through Reset/Rise, resumes idle, and waits for a fresh accepted punch. Pause/focus freezes clocks. In compatible CPU defense states, Step advances AI and guard by the blue frame-step interval; incompatible recoil/fall/Rise preserve their existing per-pose step logic. No timers or asynchronous decisions were added.

HUD distinguishes CPU:OFF/idle/reacting/guarding from Guard:OFF/RAISING/ACTIVE. Existing counters and health remain unchanged.

### Important default-timing limitation

Both supplied defaults are too late to block a FIRST in-range punch from an unguarded stance: Jab100+120=220ms versus150ms contact; Cross140+120=260ms versus240ms contact. The resulting HIT cancels that guard attempt, as Task7A requires. With exact predicted range, stationary fighters and no manual guard carryover, default CPU mode will generally show short RAISING attempts interrupted by HIT rather than successful sustained blocks. This is the direct consequence of the requested values; no punch marker or guard-entry duration was shortened to manufacture BLOCK.

The controller supports completed guard holds, extensions and normal BLOCK/recoil with a sufficiently fast configurable reaction profile. The Swift fixture exercises that using a100ms Cross delay. Product tuning for a mixture of initial successful blocks and late hits remains a separate decision; the runtime defaults remain exactly those requested. These defaults cannot by themselves demonstrate every guard-hold/block acceptance scenario in normal play.

### Validation

PASS: python Tests/validate_task8a.py source checks for seeded event-only decisions, defaults/cap, range prediction, shared guard requests, protection snapshot, cancellation, controls and runtime brace nesting.
PASS: validate_task7b1.py, validate_task7a.py, validate_task6d.py, validate_task5b.py and validate_task5a1.py source/asset/numerical regressions.

Added Tests/DefensiveAIChecks.swift for default/manual mode, range and eligibility rejection, deterministic seed replay, duplicate/earliest decision policy, reaction delay, pause, late Jab, hold extension cap/release, cancellation and ordinary guard activation with tuned reaction timing.

Swift behavioral tests and Xcode compilation remain UNEXECUTED because this Windows host has no swiftc/Xcode/SpriteKit. No device/simulator validation is claimed.

On Mac:

```sh
swiftc Boxer0/JabPlayback.swift Boxer0/PunchContact.swift Boxer0/HitReactionPlayback.swift Tests/DefensiveAIChecks.swift -o /tmp/ai-checks
/tmp/ai-checks
```

Pending iPhone SE validation: rebuild8A; CPU OFF manual guard/recoil regressions; CPU ON disables manual Guard; idle/far punches cause no defense; close punches sometimes trigger reacting/RAISING and default late HIT; pause during delay and Step/Resume without duplicate decisions; mode switch while reacting/raising, Reset, defeat/down and Rise leave AI idle and guard OFF. With explicitly tuned response, validate held guard/BLOCK/recoil, release, repeated attacks and1.5s cap. Confirm J+C=H+B+M, no CPU movement/attacks and landscape top-strip readability.


## Task8A.1 tuning correction

The user confirmed that the original timing produced no blocks before health reached zero. Updated production reaction delays: Jab20ms, Cross100ms. The120ms guard entry remains unchanged, so protection completes at140ms/220ms, before150ms/240ms contact. Attempt probabilities remain60%/75%, preserving ignored attacks and HITs. Range awareness,500ms/650ms holds,1.5s cap, geometry, damage and contact timing are unchanged. Build label8A.1.

The earlier default-timing limitation above describes the superseded8A settings. Added executable Swift fixtures for first-punch protection with both new defaults, alongside the explicit slower-profile late-HIT fixture. Source and timing checks pass; Swift compilation and device validation remain pending.
