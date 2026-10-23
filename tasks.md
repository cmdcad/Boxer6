## Boxer0 — Remaining Development Tasks

With Orange's bounce and hit reactions integrated, the next goal is to move Boxer0 from an animation test scene toward a polished, playable boxing game.

The following roadmap separates implemented features that still need verification from new development work.

Overall roadmap

Phase 2 of 7

Estimated project progression, not a measured completion percentage.

### Phase 2 — Finish Orange animation integration

Current priority

- Install the Orange Reaction V2 image sets.
- Verify Orange faces Blue during bounce, punches, guarding, and recovery.
- Confirm normal and heavy reactions are visibly different.
- Verify smooth transitions back to bounce.
- Check animation alignment, feet placement, and unwanted jumps.
- Commit the approved V2 assets to GitHub.

Deliverable: Orange has reliable, visually distinct reactions throughout gameplay.

### Phase 3 — Complete both fighters' animation systems

- Audit Blue's jab, cross, recovery, guard, and movement animations.
- Audit Orange's corresponding animations.
- Standardize sprite dimensions, anchor points, and animation transitions.
- Eliminate visual glitches when actions interrupt one another.
- Verify knockdown and getting-up sequences.
- Establish a consistent animation registry for both fighters.

Deliverable: Two complete, consistently animated boxers.

### Phase 4 — Refine combat mechanics

Existing combat logic should be tested and improved rather than rewritten.

- Verify jab and cross contact detection.
- Refine hit distance and glove-to-target accuracy.
- Distinguish light and heavy punch damage, recoil, and recovery.
- Validate blocking, counterattacks, and stun.
- Refine knockback and fighter spacing.
- Verify knockdowns and round-ending conditions.

Deliverable: Responsive, predictable boxing interactions.

### Phase 5 — Improve computer opponent intelligence

- Refine Orange's attack selection.
- Improve advancing, retreating, and defensive positioning.
- Add readable attack preparation and recovery.
- Prevent repetitive attacks and unnatural movement.
- Tune AI difficulty across levels.
- Test defensive and aggressive fighting behavior.

Deliverable: An opponent that behaves like a boxer rather than a scripted animation sequence.

### Phase 6 — Build the finished gameplay interface

- Refine movement, punch, and guard controls for touch.
- Add or polish the round timer, health indicators, and score display.
- Introduce round-start and round-end presentations.
- Add pause, resume, restart, and match-result flows.
- Replace development diagnostics with an optional debug overlay.
- Polish the arena, background, and visual effects.

Deliverable: A playable game interface suitable for testing outside development mode.

### Phase 7 — Testing and release preparation

- Test on different iPhone screen sizes.
- Verify frame rate and memory performance.
- Fix animation timing inconsistencies.
- Add sound effects and impact feedback.
- Test complete matches and difficulty progression.
- Prepare a TestFlight build.

Deliverable: A stable, playable Boxer0 prototype.

## Recommended next three agent tasks

| Order | Task                                   | Scope                                                                         |
| ----- | -------------------------------------- | ----------------------------------------------------------------------------- |
| 1     | Orange V2 integration and verification | Replace assets, test facing, reactions, and transitions                       |
| 2     | Full fighter animation audit           | Identify missing, inconsistent, or visually weak animation sequences          |
| 3     | Combat responsiveness pass             | Improve contact feedback, hit accuracy, and timing without rewriting gameplay |

I recommend keeping the development incremental: one focused task, one GitHub commit, and one verification checkpoint at a time.

We should finish Orange V2 integration first, then perform the full animation audit before introducing additional gameplay features.