# Task8B - CPU movement and distance management

Implemented the supplied sections1-3. Build label8B. Existing source files updated: FootworkMotion.swift, IdleTestScene.swift, HitReactionPlayback.swift, ContentView.swift. No new artwork or target membership needed; existing advance_b_0...5 and retreat_b_0...5 are used.

CPUDistanceController stores advance/retreat/hold intention, sampled every200ms. It does not integrate motion or select combat outcomes. The scene reuses a second instance of the SAME FootworkMotion model for orange, configured65scene points/second and the existing acceleration/deceleration. Mirrored orange advances toward decreasingX and retreats toward increasingX. Actual travel drives footwork clips and phase; braking uses actual travel direction, not the new input. Holding decelerates into idle.

Effective Cross reach is derived from current transformed contact center/radius and mirrored defender target, rather than a fixed screen distance. The physical minimum spacing is derived from the same torso bounds and gap factor as blue. Requested90% reach preferred,115% far and75% close factors are configurable. The existing minimum root spacing174.4canvas pixels exceeds the nominal close threshold129.6 for192pixel Cross reach, so the nominal retreat threshold is unreachable. The distance policy therefore floors close at minimum+4%reach and preferred at close+6%reach; far is115% of adjusted preferred. This keeps a reachable retreat zone and a broad hold band without reducing body separation or enlarging contact geometry.

Orange is clamped against the right viewport margin and blue's transformed torso plus existing body gap. Blue's existing bounds continue to track orange's current position. Orange's horizontal fraction is retained through layout changes instead of resetting to70%screen width each layout. CPU OFF holds orange still and preserves Manual Guard. Mode switches and Reset stop velocity and clear movement intent, preserving positions. Guard activation and HIT immediately stop CPU footwork; guarding, block recoil, hit reaction, knockdown/down and Rise do not translate orange. CPU defensive decisions continue using8A.1 timing and the normal guard system. No CPU punches are initiated.

CPU-compatible frame stepping advances movement using the existing blue step interval; pause/focus guards freeze scene progression. HUD includes movement intention alongside defensive AI status. Movement/animation/combat/defense states remain separate.

Validation: python Tests/validate_task8b.py PASS for twelve integrated512RGBA footwork assets, shared movement model, sampled intentions, torso/edge boundary wiring, priorities, layout preservation, diagnostics and brace nesting. Existing8A,7B.1,7A,6D,5B,5A.1 source/asset/numerical regressions pass. Tests/CPUMovementChecks.swift adds executable checks for reachable distance bands,200ms decisions, advance/retreat/hold,65pt/s analytic integration and stop/reset. Swift tests and Xcode compilation are UNEXECUTED: this Windows host lacks swiftc/Xcode/SpriteKit.

On Mac:

```sh
swiftc Boxer0/FootworkMotion.swift Tests/CPUMovementChecks.swift -o /tmp/cpu-movement-checks
/tmp/cpu-movement-checks
```

Pending iPhone SE validation: confirm8B; CPU OFF stationary/manual guard, CPU ON approach from far, hold within band and retreat when blue approaches physical minimum. Verify both viewport edges and body separation, no constant oscillation, pauses/steps, Reset position retention, guard/recoil/HIT motion priority, defeat/down/Rise then resumed movement, and existing HIT/BLOCK/MISS/counter behavior. Movement may change a punch's actual contact range, so a predicted threat is not a guaranteed contact. Equal advance/retreat speeds remain provisional pending observation, as requested. Landscape HUD density and boundary behavior on very narrow viewports remain unverified.
