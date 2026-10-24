import XCTest
import SpriteKit
@testable import Boxer0

/// Drives the actual SpriteKit scheduler. No sleeps or alternate combat model.
final class CombatDriver {
    let scene = IdleTestScene(size: CGSize(width: 900, height: 500))
    init(distance: CGFloat = 170) { scene.prepareForCombatTests(separation: distance) }
    func advance(_ duration: Double) {
        var remaining = duration
        while remaining > 1e-9 {
            let step = min(0.01, remaining)
            scene.advanceSimulation(by: step)
            remaining -= step
        }
    }
}

final class AttackTimingTests: XCTestCase {
    func testBothFightersTimingAndRecoveryEligibility() {
        for actor in [FighterID.blue, .orange] {
            for kind in [PunchKind.jab, .cross] {
                XCTAssertEqual(kind.duration,kind == .jab ? 0.300 : 0.480,accuracy:1e-9)
                XCTAssertEqual(Double(kind.contactFrame)*kind.frameDuration,kind == .jab ? 0.150 : 0.240,accuracy:1e-9)
                let driver = CombatDriver(distance: 400)
                let scene = driver.scene
                scene.setCombatLogging(true)
                XCTAssertTrue(scene.testBeginAttack(actor, kind))
                driver.advance(Double(kind.contactFrame) * kind.frameDuration - 0.001)
                let trackerBefore = actor == .blue ? scene.testBlueTracker : scene.testOrangeTracker
                XCTAssertNil(trackerBefore.latest)
                driver.advance(0.001)
                let tracker = actor == .blue ? scene.testBlueTracker : scene.testOrangeTracker
                XCTAssertEqual(tracker.misses, 1)
                driver.advance(kind.duration - Double(kind.contactFrame)*kind.frameDuration)
                var recovery = actor == .blue ? scene.testBlueRecovery : scene.testOrangeRecovery
                XCTAssertTrue(recovery.isRecovering)
                XCTAssertEqual(recovery.remaining, kind == .jab ? 0.12 : 0.22, accuracy: 1e-8)
                XCTAssertEqual(kind.duration+recovery.remaining,kind == .jab ? 0.420 : 0.700,accuracy:1e-9)
                XCTAssertFalse(scene.testBeginAttack(actor, kind))
                driver.advance(recovery.remaining - 0.001)
                recovery = actor == .blue ? scene.testBlueRecovery : scene.testOrangeRecovery
                XCTAssertTrue(recovery.isRecovering)
                driver.advance(0.001)
                XCTAssertFalse((actor == .blue ? scene.testBlueRecovery : scene.testOrangeRecovery).isRecovering)
                XCTAssertEqual(scene.combatLog.events.filter { $0.name == "CONTACT_MISS" }.count, 1)
            }
        }
    }
}

final class RecoveryTests: XCTestCase {
    func testHitOverridesPhysicalRecovery() {
        let d = CombatDriver(distance: 500)
        d.scene.startCross(); d.advance(0.48)
        XCTAssertTrue(d.scene.testBlueRecovery.isRecovering)
        d.scene.testSetSeparation(170)
        XCTAssertTrue(d.scene.testBeginAttack(.orange, .jab))
        d.advance(0.15)
        XCTAssertFalse(d.scene.testBlueRecovery.isRecovering)
        XCTAssertTrue(d.scene.blueAnimationLabel.contains("hit_react"))
        XCTAssertEqual(d.scene.testOrangeTracker.latest?.isSuccessfulCounter,true)
        XCTAssertTrue(d.scene.combatInvariantViolations.isEmpty)
    }
    func testBothRecoveryTexturesPersistAndReset() {
        for actor in [FighterID.blue, .orange] {
            for kind in [PunchKind.jab, .cross] {
                let driver = CombatDriver(distance: 400)
                let scene = driver.scene
                XCTAssertTrue(scene.testBeginAttack(actor, kind))
                driver.advance(kind.duration)
                let pose = actor == .blue ? scene.testBlueTexture : scene.testOrangeTexture
                XCTAssertNotNil(pose)
                if actor == .blue { XCTAssertTrue(scene.blueAnimationLabel.contains("recovery")) }
                else { XCTAssertTrue(scene.orangeAnimationName.contains("recovery")) }
                driver.advance(0.04)
                XCTAssertTrue(pose === (actor == .blue ? scene.testBlueTexture : scene.testOrangeTexture))
                scene.resetHealth()
                XCTAssertFalse((actor == .blue ? scene.testBlueRecovery : scene.testOrangeRecovery).isRecovering)
                XCTAssertFalse(pose === (actor == .blue ? scene.testBlueTexture : scene.testOrangeTexture))
            }
        }
    }
}

final class ContactResolutionTests: XCTestCase {
    func testProductionGeometryBothDirectionsAndDuplicateProtection() {
        for actor in [FighterID.blue, .orange] {
            for kind in [PunchKind.jab, .cross] {
                for distance in [CGFloat(170), 500] {
                    for guarding in [false, true] {
                        var tracker = PunchContactTracker()
                        tracker.begin(kind, attackerID: actor, attackID: 1)
                        let blue = SpriteCanvasTransform(rootPosition: .zero, scaleX: 1, scaleY: 1)
                        let orange = SpriteCanvasTransform(rootPosition: CGPoint(x: distance,y: 0), scaleX: -1, scaleY: 1)
                        let a = actor == .blue ? blue : orange
                        let b = actor == .blue ? orange : blue
                        let event = tracker.evaluate(kind, attacker: a, defender: b, geometry: PunchContactGeometry(), guardEffective: guarding)
                        XCTAssertNotNil(event)
                        XCTAssertEqual(event?.result, distance == 500 ? .miss : (guarding ? .block : .hit))
                        XCTAssertNil(tracker.evaluate(kind, attacker: a, defender: b, geometry: PunchContactGeometry(), guardEffective: guarding))
                        var health = FighterHealthState()
                        if let event = event {
                            health.receive(event); health.receive(event)
                            let current = actor == .blue ? health.orange.current : health.blue.current
                            XCTAssertEqual(current, 100 - (event.result == .hit ? PunchDamage.amount(for: kind) : 0))
                        }
                        XCTAssertEqual(tracker.jabContacts+tracker.crossContacts, tracker.hits+tracker.blocks+tracker.misses)
                    }
                }
            }
        }
    }

    func testMovementBeforeContactUsesCurrentGeometry() {
        for initialNear in [false, true] {
            let d = CombatDriver(distance: initialNear ? 170 : 500)
            d.scene.startJab(); d.advance(0.14)
            d.scene.testSetSeparation(initialNear ? 500 : 170)
            d.advance(0.01)
            XCTAssertEqual(d.scene.latestContact?.result, initialNear ? .miss : .hit)
        }
    }
}

final class GuardTests: XCTestCase {
    func testContactBeforeAfterAndReleasedGuard() {
        for actor in [FighterID.blue, .orange] {
            for raised in [false, true] {
                let d = CombatDriver()
                if actor == .blue { d.scene.setGuardHeld(true) } else { d.scene.testSetOrangeGuard(true) }
                if raised { d.advance(0.12) }
                XCTAssertTrue(d.scene.testBeginAttack(actor.opponent, .jab))
                if !raised { // Release before contact; stale entry must not protect.
                    if actor == .blue { d.scene.setGuardHeld(false) } else { d.scene.testSetOrangeGuard(false) }
                }
                d.advance(0.15)
                let tracker = actor == .blue ? d.scene.testOrangeTracker : d.scene.testBlueTracker
                XCTAssertEqual(tracker.latest?.result, raised ? .block : .hit)
                XCTAssertEqual(actor == .blue ? d.scene.blueHealth.current : d.scene.orangeHealth.current, raised ? 100 : 95)
            }
        }
    }
    func testEntryReleaseAndNoStaleActivationBothFighters() {
        for actor in [FighterID.blue, .orange] {
            let d = CombatDriver()
            if actor == .blue { d.scene.setGuardHeld(true) } else { d.scene.testSetOrangeGuard(true) }
            d.advance(0.119)
            XCTAssertFalse(actor == .blue ? d.scene.testBlueGuardEffective : d.scene.testOrangeGuardEffective)
            d.advance(0.001)
            XCTAssertTrue(actor == .blue ? d.scene.testBlueGuardEffective : d.scene.testOrangeGuardEffective)
            if actor == .blue { d.scene.setGuardHeld(false) } else { d.scene.testSetOrangeGuard(false) }
            XCTAssertFalse(actor == .blue ? d.scene.testBlueGuardEffective : d.scene.testOrangeGuardEffective)
            if actor == .blue { d.scene.setGuardHeld(true) } else { d.scene.testSetOrangeGuard(true) }
            d.advance(0.04)
            if actor == .blue { d.scene.setGuardHeld(false) } else { d.scene.testSetOrangeGuard(false) }
            d.advance(0.2)
            XCTAssertFalse(actor == .blue ? d.scene.testBlueGuardEffective : d.scene.testOrangeGuardEffective)
        }
    }
    func testHeldGuardWaitsForPunchAndRecovery() {
        let d = CombatDriver(distance: 500)
        d.scene.startJab(); d.scene.setGuardHeld(true)
        d.advance(0.419)
        XCTAssertFalse(d.scene.testBlueGuardEffective)
        XCTAssertEqual(d.scene.blueGuardStatus, "LOWERED")
        d.advance(0.001); d.advance(0.12)
        XCTAssertTrue(d.scene.testBlueGuardEffective)
        XCTAssertFalse(d.scene.canStartJab)
    }
}

final class CPUDecisionTests: XCTestCase {
    func testSceneDefenseEffectiveAt140And220Milliseconds() {
        for kind in [PunchKind.jab,.cross] {
            let d = CombatDriver()
            d.scene.testConfigureCPU(attackDraw:0,defenseDraw:0)
            d.scene.toggleCPU()
            if kind == .jab { d.scene.startJab() } else { d.scene.startCross() }
            let effectiveTime = kind == .jab ? 0.14 : 0.22
            d.advance(effectiveTime-0.001)
            XCTAssertFalse(d.scene.testOrangeGuardEffective)
            d.advance(0.001)
            XCTAssertTrue(d.scene.testOrangeGuardEffective)
            d.scene.resetHealth(); d.advance(0.2)
            XCTAssertFalse(d.scene.testOrangeGuardEffective)
        }
    }
    func testSceneEligibilityGuardReactionRecoveryAndCPUOff() {
        let d = CombatDriver(distance: 500)
        d.scene.testSetOrangeGuard(true)
        XCTAssertFalse(d.scene.testCanCPUAttack)
        d.scene.testSetOrangeGuard(false)
        XCTAssertTrue(d.scene.testBeginAttack(.orange,.cross))
        d.advance(0.48)
        XCTAssertFalse(d.scene.testCanCPUAttack)
        d.scene.toggleCPU() // disable autonomy, active recovery still completes
        d.advance(0.22)
        XCTAssertFalse(d.scene.cpuEnabled)
        let contacts = d.scene.testOrangeTracker.jabContacts + d.scene.testOrangeTracker.crossContacts
        d.advance(1)
        XCTAssertEqual(d.scene.testOrangeTracker.jabContacts + d.scene.testOrangeTracker.crossContacts, contacts)
    }
    func testInjectedDefenseAttemptAndDeclineAndTiming() {
        for kind in [PunchKind.jab, .cross] {
            for draw in [0.0, 0.99] {
                var ai = DefensiveAI(); ai.randomDraw = { draw }; ai.setEnabled(true)
                XCTAssertEqual(ai.jabProfile.chance,0.60)
                XCTAssertEqual(ai.crossProfile.chance,0.75)
                ai.observe(sequence: 1, kind: kind, inRange: true, eligible: true)
                if draw > 0.9 { XCTAssertEqual(ai.state, .idle); continue }
                let delay = kind == .jab ? 0.02 : 0.10
                XCTAssertNil(ai.advance(delay-0.001))
                XCTAssertNotNil(ai.advance(0.001))
                var guardPose = GuardPlayback(); guardPose.toggle(); guardPose.advance(0.119)
                XCTAssertFalse(guardPose.isEffective); guardPose.advance(0.001)
                XCTAssertTrue(guardPose.isEffective)
                ai.cancel(); XCTAssertEqual(ai.state, .idle)
            }
        }
    }
    func testOffenseRangePreparationCooldownAndIneligibleStates() {
        for draw in [0.0, 0.99] {
            var ai = CPUOffense(); ai.randomDraw = { draw }
            XCTAssertNil(ai.advance(1, enabled: true, eligible: true, jabInRange: false, crossInRange: false))
            XCTAssertEqual(ai.state, .ready)
            XCTAssertNil(ai.advance(0.30, enabled: true, eligible: true, jabInRange: true, crossInRange: true))
            XCTAssertEqual(ai.kind, draw == 0 ? .jab : .cross)
            let preparation = draw == 0 ? 0.18 : 0.28
            XCTAssertNil(ai.advance(preparation-0.001, enabled: true, eligible: true, jabInRange: true, crossInRange: true))
            XCTAssertNotNil(ai.advance(0.001, enabled: true, eligible: true, jabInRange: true, crossInRange: true))
            ai.finished()
            XCTAssertEqual(ai.remaining,draw == 0 ? 0.65 : 0.90,accuracy:1e-9)
            XCTAssertNil(ai.advance(0.1, enabled: true, eligible: true, jabInRange: true, crossInRange: true))
            XCTAssertEqual(ai.state, .cooldown)
            ai.advance(draw == 0 ? 0.55 : 0.80,enabled:true,eligible:true,jabInRange:true,crossInRange:true)
            XCTAssertEqual(ai.state,.ready)
            ai.cancel()
            XCTAssertNil(ai.advance(1, enabled: true, eligible: false, jabInRange: true, crossInRange: true))
            XCTAssertEqual(ai.state, .ready)
            XCTAssertNil(ai.advance(1, enabled: false, eligible: true, jabInRange: true, crossInRange: true))
        }
    }
}

final class DamageTests: XCTestCase {
    func testBothHealthWatermarksSurviveReset() {
        for actor in [FighterID.blue,.orange] {
            for kind in [PunchKind.jab,.cross] {
                XCTAssertEqual(PunchDamage.amount(for:kind),kind == .jab ? 5 : 10)
                var tracker = PunchContactTracker()
                tracker.begin(kind,attackerID:actor,attackID:1)
                let a = SpriteCanvasTransform(rootPosition:.zero,scaleX:1,scaleY:1)
                let b = SpriteCanvasTransform(rootPosition:CGPoint(x:170,y:0),scaleX:-1,scaleY:1)
                guard let event = tracker.evaluate(kind,attacker:a,defender:b,geometry:PunchContactGeometry()) else {
                    XCTFail("Expected production contact"); continue
                }
                var health = FighterHealthState()
                health.receive(event)
                XCTAssertEqual(actor == .blue ? health.orange.current : health.blue.current,100-PunchDamage.amount(for:kind))
                health.reset(); XCTAssertFalse(health.receive(event))
                XCTAssertEqual(health.blue.current,100); XCTAssertEqual(health.orange.current,100)
            }
        }
    }
}

final class CombatStateTests: XCTestCase {
    func testHitReactionCancelsGuardAndCannotBeOverwrittenByMovement() {
        let d = CombatDriver()
        XCTAssertTrue(d.scene.testBeginAttack(.orange,.jab))
        d.advance(0.10)
        d.scene.setGuardHeld(true) // still raising when Jab lands at150ms
        d.advance(0.05)
        XCTAssertEqual(d.scene.blueHealth.current,95)
        XCTAssertFalse(d.scene.testBlueGuardEffective)
        XCTAssertTrue(d.scene.blueAnimationLabel.contains("hit_react"))
        d.scene.setAdvanceHeld(true); d.advance(0.01)
        XCTAssertTrue(d.scene.blueAnimationLabel.contains("hit_react"))
        XCTAssertFalse(d.scene.canStartJab)
        XCTAssertTrue(d.scene.combatInvariantViolations.isEmpty)
    }
}

final class CombatStatisticsTests: XCTestCase {
    func testCanceledCounterAttemptHasNoInventedOutcome() {
        var tracker = PunchContactTracker()
        tracker.begin(.cross,attackerID:.orange,attackID:8,counterAttempt:true)
        tracker.finish()
        let transform = SpriteCanvasTransform(rootPosition:.zero,scaleX:1,scaleY:1)
        XCTAssertNil(tracker.evaluate(.cross,attacker:transform,defender:transform,geometry:PunchContactGeometry()))
        XCTAssertEqual(tracker.counterAttempts,1)
        XCTAssertEqual(tracker.successfulCounters,0)
        XCTAssertEqual(tracker.jabContacts+tracker.crossContacts,0)
        XCTAssertEqual(tracker.hits+tracker.blocks+tracker.misses,0)
    }
}

final class CounterpunchTests: XCTestCase {
    func testAttackAfterOpponentRecoveryIsOrdinary() {
        let d = CombatDriver(distance:500)
        d.scene.startJab(); d.advance(0.42)
        XCTAssertFalse(d.scene.isAttackVulnerable(.blue))
        d.scene.testSetSeparation(170)
        XCTAssertTrue(d.scene.testBeginAttack(.orange,.jab))
        d.advance(0.15)
        XCTAssertEqual(d.scene.testOrangeTracker.latest?.isCounterAttempt,false)
        XCTAssertEqual(d.scene.blueHealth.current,95)
    }
    func testEarlierContactCancelsLaterAttackWithoutFabricatedMiss() {
        for first in [FighterID.blue, .orange] {
            let d = CombatDriver()
            XCTAssertTrue(d.scene.testBeginAttack(first, .jab))
            XCTAssertTrue(d.scene.testBeginAttack(first.opponent, .cross))
            d.advance(0.25)
            let winner = first == .blue ? d.scene.testBlueTracker : d.scene.testOrangeTracker
            let interrupted = first == .blue ? d.scene.testOrangeTracker : d.scene.testBlueTracker
            XCTAssertEqual(winner.hits, 1)
            XCTAssertNil(interrupted.latest)
            XCTAssertEqual(interrupted.hits+interrupted.blocks+interrupted.misses,0)
            XCTAssertTrue(d.scene.combatInvariantViolations.isEmpty)
        }
    }
    func testInitiationSnapshotAndOutcomeSubsets() {
        for actor in [FighterID.blue, .orange] {
            for attempt in [false, true] {
                for outcome in [PunchContactResult.hit, .block, .miss] {
                    var tracker = PunchContactTracker()
                    tracker.begin(.jab, attackerID: actor, attackID: 1, counterAttempt: attempt)
                    let a = SpriteCanvasTransform(rootPosition: .zero, scaleX: 1, scaleY: 1)
                    let b = SpriteCanvasTransform(rootPosition: CGPoint(x: outcome == .miss ? 500 : 170,y: 0), scaleX: -1, scaleY: 1)
                    let event = tracker.evaluate(.jab, attacker: a, defender: b, geometry: PunchContactGeometry(), guardEffective: outcome == .block)
                    XCTAssertEqual(event?.isSuccessfulCounter, attempt && outcome == .hit)
                    XCTAssertLessThanOrEqual(tracker.successfulCounters, tracker.counterAttempts)
                    XCTAssertLessThanOrEqual(tracker.successfulCounters, tracker.hits)
                }
            }
        }
    }
    func testEqualContactTradesAndIndependentIdentities() {
        let d = CombatDriver()
        XCTAssertTrue(d.scene.testBeginAttack(.blue,.jab))
        XCTAssertTrue(d.scene.testBeginAttack(.orange,.jab))
        XCTAssertNotEqual(d.scene.testBlueTracker.context?.id, d.scene.testOrangeTracker.context?.id)
        d.advance(0.15)
        XCTAssertEqual(d.scene.blueHealth.current,95)
        XCTAssertEqual(d.scene.orangeHealth.current,95)
        XCTAssertEqual(d.scene.testOrangeTracker.successfulCounters,1)
    }
}

final class PauseResetRiseTests: XCTestCase {
    func testSceneDefeatRiseAndFreshGuardBothFighters() {
        for defender in [FighterID.blue, .orange] {
            let d = CombatDriver()
            d.scene.testConfigureCPU(attackDraw: 0, defenseDraw: 0.99)
            for _ in 0..<3 {
                d.scene.testSetSeparation(170)
                XCTAssertTrue(d.scene.testBeginAttack(defender.opponent, .cross))
                d.advance(0.70)
            }
            d.advance(1)
            XCTAssertEqual(defender == .blue ? d.scene.blueCombatState : d.scene.orangeCombatState,.defeated)
            XCTAssertFalse(d.scene.testBeginAttack(defender,.jab))
            if defender == .blue {
                d.scene.setGuardHeld(true)
                d.scene.setAdvanceHeld(true)
                XCTAssertFalse(d.scene.guardHeld)
                XCTAssertFalse(d.scene.advanceHeld)
                XCTAssertTrue(d.scene.canBlueRise); d.scene.startBlueRise()
            } else { XCTAssertTrue(d.scene.canRise); d.scene.startRise() }
            let risePosition = defender == .blue ? d.scene.testBluePosition : d.scene.testOrangePosition
            d.advance(0.79)
            XCTAssertEqual(defender == .blue ? d.scene.testBluePosition : d.scene.testOrangePosition,risePosition)
            XCTAssertEqual(defender == .blue ? d.scene.blueHealth.current : d.scene.orangeHealth.current,70)
            d.advance(0.01)
            XCTAssertEqual(defender == .blue ? d.scene.blueHealth.current : d.scene.orangeHealth.current,100)
            XCTAssertFalse(d.scene.guardHeld)
            XCTAssertFalse((defender == .blue ? d.scene.testBlueRecovery : d.scene.testOrangeRecovery).isRecovering)
            XCTAssertTrue(d.scene.combatInvariantViolations.isEmpty)
        }
    }
    func testPauseDuringGuardRecoveryAndCPUPreparation() {
        let d = CombatDriver(distance: 500)
        d.scene.setGuardHeld(true); d.advance(0.04); d.scene.togglePlayback()
        d.advance(1); XCTAssertFalse(d.scene.testBlueGuardEffective)
        d.scene.togglePlayback(); d.advance(0.08); XCTAssertTrue(d.scene.testBlueGuardEffective)
        d.scene.setGuardHeld(false); d.scene.startCross(); d.advance(0.48)
        d.scene.togglePlayback()
        let remaining = d.scene.testBlueRecovery.remaining
        d.advance(1); XCTAssertEqual(d.scene.testBlueRecovery.remaining, remaining)
        d.scene.stepFrame(); XCTAssertLessThan(d.scene.testBlueRecovery.remaining, remaining)
        // CPU model receives no elapsed simulation time while paused.
        var cpu = CPUOffense(); cpu.randomDraw = { 0 }
        cpu.advance(0.3,enabled:true,eligible:true,jabInRange:true,crossInRange:true)
        let preparation = cpu.remaining
        cpu.advance(0,enabled:true,eligible:true,jabInRange:true,crossInRange:true)
        XCTAssertEqual(cpu.remaining,preparation)
        cpu.finished(); let cooldown = cpu.remaining
        cpu.advance(0,enabled:true,eligible:true,jabInRange:true,crossInRange:true)
        XCTAssertEqual(cpu.remaining,cooldown)
    }
    func testPauseStepResetAndStaleContact() {
        let d = CombatDriver()
        d.scene.startJab(); d.advance(0.10)
        d.scene.togglePlayback()
        let time = d.scene.simulationTime
        d.advance(1)
        XCTAssertEqual(d.scene.simulationTime,time)
        XCTAssertNil(d.scene.latestContact)
        d.scene.stepFrame()
        XCTAssertEqual(d.scene.orangeHealth.current,95)
        d.scene.togglePlayback(); d.advance(0.30)
        XCTAssertEqual(d.scene.testBlueTracker.jabContacts,1)
        XCTAssertEqual(d.scene.orangeHealth.current,95)
        d.scene.resetHealth(); d.advance(1)
        XCTAssertEqual(d.scene.orangeHealth.current,100)
        XCTAssertEqual(d.scene.blueHealth.current,100)
        XCTAssertFalse(d.scene.testBlueRecovery.isRecovering)
        XCTAssertFalse(d.scene.guardHeld)
    }
    func testHealthClampDefeatAndRiseModel() {
        var health = FighterHealth()
        health.applyDamage(-50); XCTAssertEqual(health.current,100)
        health.applyDamage(1000); XCTAssertEqual(health.current,0)
        var fall = KnockdownPlayback()
        XCTAssertTrue(fall.start())
        for _ in 0..<8 { fall.advance(0.08) }
        XCTAssertEqual(fall.clip,.down)
        XCTAssertTrue(fall.startRise())
        for _ in 0..<8 { fall.advance(0.1) }
        XCTAssertFalse(fall.hasStarted)
        health.reset(); XCTAssertEqual(health.current,100)
    }
    func testBoundedOptInLog() {
        var log = CombatEventLog()
        log.record(time:0,name:"TEST",fighter:.blue)
        XCTAssertTrue(log.events.isEmpty)
        log.enabled = true
        for i in 0..<500 { log.record(time:Double(i),name:"TEST",fighter:.orange) }
        XCTAssertEqual(log.events.count,log.capacity)
        XCTAssertEqual(log.events.last?.time,499)
    }
}

final class GuardedMovementTests: XCTestCase {
    func testConfiguredSpeedAndSmoothLimitReduction() {
        var motion = FootworkMotion()
        motion.advance(duration:0.3,direction:1)
        XCTAssertEqual(motion.velocity,100,accuracy:1e-8)
        motion.advance(duration:0.01,direction:1,speedMultiplier:0.55)
        XCTAssertEqual(motion.velocity,91,accuracy:1e-8) // existing deceleration, no snap
        motion.advance(duration:0.3,direction:1,speedMultiplier:0.55)
        XCTAssertEqual(motion.velocity,55,accuracy:1e-8)
        motion.advance(duration:0.01,direction:1)
        XCTAssertEqual(motion.velocity,61,accuracy:1e-8)
    }
    func testNormalBlueSpeedUnchanged() {
        let d = CombatDriver(distance:500)
        d.scene.setAdvanceHeld(true); d.advance(0.3)
        XCTAssertEqual(d.scene.testBlueVelocity,100,accuracy:1e-8)
    }
    func testNoEarlyProtectionOrMovementDuringEntryFromRest() {
        let d = CombatDriver(distance:500)
        let start = d.scene.testBluePosition
        d.scene.setGuardHeld(true); d.scene.setAdvanceHeld(true)
        d.advance(0.119)
        XCTAssertFalse(d.scene.testBlueGuardEffective)
        XCTAssertEqual(d.scene.testBluePosition,start)
        d.advance(0.001)
        XCTAssertTrue(d.scene.testBlueGuardEffective)
        d.advance(0.15)
        XCTAssertGreaterThan(d.scene.testBluePosition,start)
        XCTAssertEqual(d.scene.testBlueVelocity,55,accuracy:1e-8)
    }
    func testHeldAdvanceSurvivesGuardEntryAndRelease() {
        let d = CombatDriver(distance:500)
        d.scene.setAdvanceHeld(true); d.advance(0.3)
        d.scene.setGuardHeld(true); d.advance(0.3)
        XCTAssertTrue(d.scene.advanceHeld)
        XCTAssertEqual(d.scene.testBlueVelocity,55,accuracy:1e-8)
        let position = d.scene.testBluePosition
        d.scene.setGuardHeld(false)
        XCTAssertEqual(d.scene.testBluePosition,position)
        XCTAssertEqual(d.scene.testBlueVelocity,55,accuracy:1e-8)
        d.advance(0.1)
        XCTAssertEqual(d.scene.testBlueVelocity,100,accuracy:1e-8)
    }
    func testGuardedRetreatAndBothDirectionsHeld() {
        let d = CombatDriver(distance:500)
        d.scene.setGuardHeld(true); d.advance(0.12)
        d.scene.setRetreatHeld(true); d.advance(0.2)
        XCTAssertEqual(d.scene.testBlueVelocity,-55,accuracy:1e-8)
        d.scene.setAdvanceHeld(true); d.advance(0.1)
        XCTAssertEqual(d.scene.testBlueVelocity,0,accuracy:1e-8)
        XCTAssertTrue(d.scene.testBlueGuardEffective)
    }
    func testReleaseMovementRetainsGuard() {
        let d = CombatDriver(distance:500)
        d.scene.setGuardHeld(true); d.advance(0.12)
        d.scene.setAdvanceHeld(true); d.advance(0.2)
        d.scene.setAdvanceHeld(false); d.advance(0.1)
        XCTAssertEqual(d.scene.testBlueVelocity,0)
        XCTAssertTrue(d.scene.testBlueGuardEffective)
        XCTAssertEqual(d.scene.blueMovementLabel,"GUARDED HOLD")
    }
    func testBlueBoundariesAndMinimumSeparation() {
        let d = CombatDriver(distance:400)
        d.scene.setGuardHeld(true); d.advance(0.12)
        d.scene.setAdvanceHeld(true); d.advance(8)
        XCTAssertTrue(d.scene.testBlueLimits.contains(d.scene.testBluePosition))
        XCTAssertLessThan(d.scene.testBluePosition,d.scene.testOrangePosition)
        d.scene.setAdvanceHeld(false); d.scene.setRetreatHeld(true); d.advance(15)
        XCTAssertTrue(d.scene.testBlueLimits.contains(d.scene.testBluePosition))
        XCTAssertEqual(d.scene.testBlueVelocity,0)
    }
    func testOrangeGuardedAdvanceUsesCPUBaseSpeed() {
        let d = CombatDriver(distance:400)
        d.scene.toggleCPU(); d.scene.testSetOrangeGuard(true)
        d.advance(0.4)
        XCTAssertTrue(d.scene.testOrangeGuardEffective)
        XCTAssertEqual(d.scene.testOrangeVelocity,-35.75,accuracy:1e-8)
        XCTAssertEqual(d.scene.orangeClip,.guardPose)
        XCTAssertFalse(d.scene.testCanCPUAttack)
    }
    func testOrangeGuardedRetreatAndBoundaries() {
        let d = CombatDriver(distance:175)
        d.scene.toggleCPU(); d.scene.testSetOrangeGuard(true)
        d.advance(0.22)
        XCTAssertGreaterThan(d.scene.testOrangeVelocity,0)
        XCTAssertLessThanOrEqual(d.scene.testOrangeVelocity,35.75+1e-8)
        XCTAssertTrue(d.scene.testOrangeLimits.contains(d.scene.testOrangePosition))
        d.advance(1)
        XCTAssertTrue(d.scene.testOrangeLimits.contains(d.scene.testOrangePosition))
    }
    func testGuardedRetreatChangesContactToMiss() {
        let d = CombatDriver(distance:200)
        d.scene.setGuardHeld(true); d.advance(0.12)
        d.scene.setRetreatHeld(true)
        XCTAssertTrue(d.scene.testBeginAttack(.orange,.jab))
        d.advance(0.15)
        XCTAssertEqual(d.scene.testOrangeTracker.latest?.result,.miss)
        XCTAssertEqual(d.scene.blueHealth.current,100)
    }
    func testBlockStopsThenResumesGuardedMovementWithoutDamage() {
        let d = CombatDriver(distance:175)
        d.scene.setGuardHeld(true); d.advance(0.12)
        d.scene.setRetreatHeld(true)
        XCTAssertTrue(d.scene.testBeginAttack(.orange,.jab))
        d.advance(0.15)
        XCTAssertEqual(d.scene.testOrangeTracker.latest?.result,.block)
        XCTAssertEqual(d.scene.blueHealth.current,100)
        XCTAssertEqual(d.scene.testBlueVelocity,0)
        let stopped = d.scene.testBluePosition
        d.advance(0.08)
        XCTAssertEqual(d.scene.testBluePosition,stopped)
        d.advance(0.2)
        XCTAssertLessThan(d.scene.testBlueVelocity,0)
        XCTAssertTrue(d.scene.testBlueGuardEffective)
    }
    func testRecoveryStillPreventsGuardedMovement() {
        let d = CombatDriver(distance:500)
        d.scene.startCross(); d.scene.setGuardHeld(true); d.scene.setAdvanceHeld(true)
        let position = d.scene.testBluePosition
        d.advance(0.699)
        XCTAssertFalse(d.scene.testBlueGuardEffective)
        XCTAssertEqual(d.scene.testBluePosition,position)
        XCTAssertTrue(d.scene.isAttackVulnerable(.blue))
    }
    func testCPUOffClearsGuardedMovement() {
        let d = CombatDriver(distance:400)
        d.scene.toggleCPU(); d.scene.testSetOrangeGuard(true); d.advance(0.4)
        XCTAssertLessThan(d.scene.testOrangeVelocity,0)
        d.scene.toggleCPU()
        let position = d.scene.testOrangePosition
        d.advance(0.5)
        XCTAssertEqual(d.scene.testOrangePosition,position)
        XCTAssertEqual(d.scene.testOrangeVelocity,0)
    }
    func testPauseStepAndResumePreserveHeldMovement() {
        let d = CombatDriver(distance:500)
        d.scene.setGuardHeld(true); d.advance(0.12)
        d.scene.setAdvanceHeld(true); d.advance(0.2)
        d.scene.togglePlayback()
        let position = d.scene.testBluePosition
        d.advance(1)
        XCTAssertEqual(d.scene.testBluePosition,position)
        d.scene.stepFrame()
        XCTAssertGreaterThan(d.scene.testBluePosition,position)
        let stepped = d.scene.testBluePosition
        d.scene.togglePlayback(); d.advance(0.01)
        XCTAssertEqual(Double(d.scene.testBluePosition-stepped),0.55,accuracy:1e-6)
    }
    func testResetClearsHeldGuardedMovement() {
        let d = CombatDriver(distance:500)
        d.scene.setGuardHeld(true); d.advance(0.12)
        d.scene.setAdvanceHeld(true); d.advance(0.2)
        d.scene.resetHealth()
        let position = d.scene.testBluePosition
        d.advance(0.5)
        XCTAssertEqual(d.scene.testBluePosition,position)
        XCTAssertFalse(d.scene.guardHeld); XCTAssertFalse(d.scene.advanceHeld)
    }
    func testMultiplierIsConfigurableWithoutChangingNormalSpeed() {
        let d = CombatDriver(distance:500)
        d.scene.guardedMovementMultiplier = 0.4
        d.scene.setGuardHeld(true); d.advance(0.12)
        d.scene.setAdvanceHeld(true); d.advance(0.2)
        XCTAssertEqual(d.scene.testBlueVelocity,40,accuracy:1e-8)
        d.scene.setGuardHeld(false); d.advance(0.2)
        XCTAssertEqual(d.scene.testBlueVelocity,100,accuracy:1e-8)
    }
}
