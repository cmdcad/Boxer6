# Orange reactions — approved V1 / integration staging

Status: **approved animation assets; integration package prepared; not merged into current game scene**.

## Approved animations
| Animation | Frames | FPS | Loop | End |
| --- | ---: | ---: | --- | --- |
| Orange Normal Hit Reaction V1 | 18 | 20 | No | Orange Bounce V3 guard |
| Orange Heavy Hit Recovery V1 | 14 | 18 | No | Orange Bounce V3 guard |
| Orange Bounce V3 | 17 | 17 / 1.105 (~15.38) | Yes | Continuous |

The heavy recovery is the **recovery portion only**; the preceding heavy-impact sequence is separate. Both approved V1 animations are deformation-based prototypes derived from actual Orange sprite imagery, not independently articulated frames.

## Source package
Local approved package: `Boxer0_Orange_SpriteKit_Integration_V1.zip`.
Contents: `Source/IdleTestScene.swift`, `Source/ContentView.swift`, 49 `orange_*.imageset` directories (17 bounce + 18 normal + 14 heavy), `verify_package.py`, and `README.md`.
The package was statically verified for 512×512 RGBA frames, named image sets and exact ending guard pixels. **It has not been compiled or run in Xcode.**

**IMPORTANT:** The package's two Swift files were derived from an older local test scene (Task 3A movement) and are **not safe to overwrite** onto the current repository's `swift/Boxer0/Boxer0/IdleTestScene.swift` and `ContentView.swift`, which include later combat, health, punch, guard, CPU and other features. Integrate only the Orange clip loading/selection/playback and UI triggers into the latest sources. Do not replace existing scene/control files wholesale.

## Integration plan (control rearrangement deferred)
1. Preserve the current game's controls and combat states.
2. Add the 49 `orange_*.imageset` directories to `swift/Boxer0/Boxer0/Assets.xcassets`, after checking existing names for collisions. Do not replace the whole asset catalog.
3. Add Orange bounce, normal-hit and heavy-recovery texture arrays to the **current** scene.
4. Give Orange a separate animation accumulator. Run normal hit at 20 FPS and heavy recovery at 18 FPS, both once; transition to the exact Bounce V3 guard and resume bounce.
5. Keep current combat hit reaction, block, knockdown and recovery priority intact. Trigger the new animations through the existing state machine; avoid bypassing combat rules. Debug controls may be added without rearranging the interface.
6. Build on iOS and verify animation handoff, Pause/Step, 1/4×, trigger restart, and unchanged blue movement/combat behavior.

## Repository tracking
This commit records the approved animation definitions and integration instructions only. The local ZIP, PNG binaries, and replacement Swift files **have not been uploaded or committed**. Do not mark the SpriteKit integration as merged or device-tested until these steps are completed.

## October 22 integration update
The current `swift/Boxer0/Boxer0/HitReactionPlayback.swift` and `IdleTestScene.swift` now contain approved Orange V1 playback wiring on this branch (commits `cda715c`, `ec4fbea`, `c03939c`). Blue retains its original four-frame reaction. The new Orange image sets are **not yet in GitHub**. An asset-only local ZIP `Boxer0_Orange_V1_Assets_For_Current_Game.zip` contains the 49 image sets to copy into the existing asset catalog. Existing `ContentView.swift` controls are unchanged; the animations trigger from real jab/cross hit events. This is an unbuilt, untested source merge; not a verified playable release.
