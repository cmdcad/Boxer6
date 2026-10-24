import XCTest
@testable import Boxer0

final class FighterMetersTests: XCTestCase {
    func testThreeConsecutiveUnguardedHeadHitsKnockOut() {
        var m = FighterMeters()
        XCTAssertEqual(m.receiveHit(zone: .head, guarded: false), 100.0 / 3.0, accuracy: 1e-9)
        XCTAssertEqual(m.receiveHit(zone: .head, guarded: false), 40.0, accuracy: 1e-9)
        XCTAssertFalse(m.isKnockedOut)
        m.receiveHit(zone: .head, guarded: false)
        XCTAssertTrue(m.isKnockedOut)
    }

    func testBodyHitsDoNotEscalate() {
        var m = FighterMeters()
        let a = m.receiveHit(zone: .body, guarded: false)
        let b = m.receiveHit(zone: .body, guarded: false)
        XCTAssertEqual(a, b, accuracy: 1e-9)
        XCTAssertEqual(m.consecutiveHeadHits, 0)
    }

    func testHeavyAndWithdrawFactors() {
        var heavy = FighterMeters()
        XCTAssertEqual(heavy.receiveHit(zone: .body, guarded: false, heavy: true), 50, accuracy: 1e-9)
        var away = FighterMeters()
        XCTAssertEqual(away.receiveHit(zone: .body, guarded: false, withdrawing: true), 100.0 / 6.0, accuracy: 1e-9)
    }

    func testGuardedHitCostsStaminaOnly() {
        var m = FighterMeters()
        XCTAssertEqual(m.receiveHit(zone: .head, guarded: true), 0)
        XCTAssertEqual(m.stamina, 95, accuracy: 1e-9)
        XCTAssertEqual(m.awareness, 100)
    }

    func testGrabGate() {
        var m = FighterMeters()
        XCTAssertFalse(m.canStartGrab(isTooClose: true))
        for _ in 0..<10 { m.receiveHit(zone: .head, guarded: true, levelMultiplier: 2) }
        XCTAssertLessThan(m.stamina, 50)
        XCTAssertTrue(m.canStartGrab(isTooClose: true))
        XCTAssertFalse(m.canStartGrab(isTooClose: false))
    }

    func testRegenAndClamp() {
        var m = FighterMeters()
        m.receiveHit(zone: .head, guarded: false)
        m.advance(1, mode: .guarding)
        XCTAssertEqual(m.awareness, 100.0 - 100.0 / 3.0, accuracy: 1e-9)
        m.advance(10, mode: .withdraw)
        XCTAssertEqual(m.awareness, 100, accuracy: 1e-9)
        XCTAssertEqual(m.stamina, 100, accuracy: 1e-9)
    }

    func testHeadHitStreakExpires() {
        var m = FighterMeters()
        m.receiveHit(zone: .head, guarded: false)
        m.advance(3.1, mode: .idle)
        XCTAssertEqual(m.consecutiveHeadHits, 0)
    }

    func testReactionDelayScalesWithAwareness() {
        var m = FighterMeters()
        XCTAssertEqual(m.reactionDelay, 0.05, accuracy: 1e-9)
        m.receiveHit(zone: .body, guarded: false)
        XCTAssertGreaterThan(m.reactionDelay, 0.05)
        XCTAssertLessThanOrEqual(m.reactionDelay, 0.6)
    }
    func testDefaultCapsAndLevelOneStats() {
        let tuning = CombatTuning()
        let meters = FighterMeters(tuning: tuning)
        XCTAssertEqual(FighterStats().level, 1)
        XCTAssertEqual(meters.stamina, tuning.maxStamina)
        XCTAssertEqual(meters.awareness, tuning.maxAwareness)
        XCTAssertFalse(meters.isKnockedOut)
        XCTAssertEqual(tuning.rounds, 8)
        XCTAssertEqual(tuning.roundSeconds, 120)
        XCTAssertEqual(tuning.levelMultiplier(attacker: 1, defender: 1), 1)
    }

    func testGuardedHitPreservesHeadStreakUntilDefenseReset() {
        var meters = FighterMeters()
        meters.receiveHit(zone: .head, guarded: false)
        XCTAssertEqual(meters.consecutiveHeadHits, 1)
        let awarenessAfterHead = meters.awareness
        meters.receiveHit(zone: .head, guarded: true)
        XCTAssertEqual(meters.awareness, awarenessAfterHead, accuracy: 1e-9)
        // Guard stamina loss and streak termination are separate operations:
        // the combat layer explicitly calls endHeadHitStreak on defense.
        XCTAssertEqual(meters.consecutiveHeadHits, 1)
        meters.endHeadHitStreak()
        XCTAssertEqual(meters.consecutiveHeadHits, 0)
        XCTAssertEqual(meters.receiveHit(zone: .head, guarded: false),
                       100.0 / 3.0, accuracy: 1e-9)
    }

    func testStaminaClampsAndReactionDelayCaps() {
        var meters = FighterMeters()
        for _ in 0..<30 {
            meters.receiveHit(zone: .body, guarded: true)
        }
        XCTAssertEqual(meters.stamina, 0, accuracy: 1e-9)
        meters.advance(1000, mode: .idle)
        XCTAssertEqual(meters.stamina, 100, accuracy: 1e-9)
        meters.receiveHit(zone: .head, guarded: false)
        meters.receiveHit(zone: .head, guarded: false)
        meters.receiveHit(zone: .head, guarded: false)
        XCTAssertTrue(meters.isKnockedOut)
        XCTAssertEqual(meters.reactionDelay, CombatTuning().maxReaction, accuracy: 1e-9)
    }

    func testSceneContactWiresHeadAwarenessBothDirections() {
        for attacker in [FighterID.blue, .orange] {
            let driver = CombatDriver(distance: 170)
            let scene = driver.scene
            XCTAssertTrue(scene.testBeginAttack(attacker, .jab))
            driver.advance(0.15)
            let defenderAwareness = attacker == .blue ? scene.orangeMeters.awareness : scene.blueMeters.awareness
            let attackerAwareness = attacker == .blue ? scene.blueMeters.awareness : scene.orangeMeters.awareness
            XCTAssertEqual(defenderAwareness, 100 - 100.0 / 3, accuracy: 1e-8)
            XCTAssertEqual(attackerAwareness, 100, accuracy: 1e-8)
        }
    }

    func testSceneGuardCostsStaminaButNotAwareness() {
        let driver = CombatDriver(distance: 170)
        let scene = driver.scene
        scene.testSetOrangeGuard(true)
        driver.advance(0.12)
        XCTAssertTrue(scene.testBeginAttack(.blue, .jab))
        driver.advance(0.15)
        XCTAssertEqual(scene.orangeMeters.awareness, 100, accuracy: 1e-8)
        XCTAssertEqual(scene.orangeMeters.stamina, 95, accuracy: 1e-8)
        XCTAssertEqual(scene.orangeMeters.consecutiveHeadHits, 0)
    }

    func testSceneResetRestoresMeters() {
        let driver = CombatDriver(distance: 170)
        let scene = driver.scene
        XCTAssertTrue(scene.testBeginAttack(.blue, .jab))
        driver.advance(0.15)
        XCTAssertLessThan(scene.orangeMeters.awareness, 100)
        scene.resetHealth()
        XCTAssertEqual(scene.orangeMeters.awareness, 100, accuracy: 1e-8)
        XCTAssertEqual(scene.orangeMeters.stamina, 100, accuracy: 1e-8)
    }

    func testThreeConsecutiveHeadHitsKnockOutAtPositiveHealth() {
        var meters = FighterMeters()
        XCTAssertEqual(meters.receiveHit(zone: .head, guarded: false),
                       100.0 / 3.0, accuracy: 1e-8)
        XCTAssertFalse(meters.isKnockedOut)
        meters.receiveHit(zone: .head, guarded: false)
        XCTAssertFalse(meters.isKnockedOut)
        meters.receiveHit(zone: .head, guarded: false)
        XCTAssertTrue(meters.isKnockedOut)

        var health = FighterHealthState()
        XCTAssertTrue(health.receiveAwarenessKO(for: .orange))
        XCTAssertEqual(health.orange.current, 100)
        XCTAssertEqual(health.orangeCombat.state, .defeated)
        XCTAssertFalse(health.receiveAwarenessKO(for: .orange))
        XCTAssertFalse(health.canExchangePunches)
        XCTAssertTrue(health.recoverOrange())
        XCTAssertTrue(health.canExchangePunches)
    }

    func testHealthBelowFortyButNotAtForty() {
        var health = FighterHealth()
        var status = FighterCombatStatus()
        health.applyDamage(60)
        XCTAssertEqual(health.current, 40)
        XCTAssertFalse(status.receiveHealth(health))
        health.applyDamage(1)
        XCTAssertEqual(health.current, 39)
        XCTAssertTrue(status.receiveHealth(health))
        XCTAssertFalse(status.receiveHealth(health))
    }

    func testMatchRoundBoundariesAndDraw() {
        var match = MatchState()
        XCTAssertEqual(match.round, 1)
        XCTAssertEqual(match.advance(119.75), 0)
        XCTAssertEqual(match.remaining, 0.25, accuracy: 1e-8)
        XCTAssertEqual(match.advance(0.25), 1)
        XCTAssertEqual(match.round, 2)
        XCTAssertEqual(match.remaining, 120, accuracy: 1e-8)
        XCTAssertEqual(match.advance(6 * 120), 6)
        XCTAssertEqual(match.round, 8)
        XCTAssertEqual(match.advance(120), 0)
        XCTAssertEqual(match.result, .draw)
        XCTAssertTrue(match.isFinished)
        XCTAssertEqual(match.advance(20), 0)
    }

    func testMatchScoringDedupAndKnockout() {
        let transform = SpriteCanvasTransform(rootPosition: .zero, scaleX: 1, scaleY: 1)
        func contact(_ id: Int, _ result: PunchContactResult, _ attacker: FighterID) -> PunchContactEvent {
            var event = PunchContactEvent(sequence: id, kind: .jab, result: result,
                center: .zero, radius: 20, target: .zero,
                attacker: transform, defender: transform)
            event.attackerID = attacker
            return event
        }
        var match = MatchState()
        XCTAssertTrue(match.score(contact(1, .hit, .blue)))
        XCTAssertFalse(match.score(contact(1, .hit, .blue)))
        XCTAssertTrue(match.score(contact(2, .block, .blue)))
        XCTAssertFalse(match.score(contact(3, .miss, .blue)))
        XCTAssertTrue(match.score(contact(4, .hit, .orange)))
        XCTAssertEqual(match.bluePoints, 4)
        XCTAssertEqual(match.orangePoints, 3)
        match.knockout(winner: .orange)
        XCTAssertEqual(match.result, .orangeKO)
        XCTAssertFalse(match.score(contact(5, .hit, .blue)))
        match.reset()
        XCTAssertEqual(match.bluePoints, 0)
        XCTAssertNil(match.result)
    }

    func testRoundHealingCapsAndPreservesAwareness() {
        var health = FighterHealthState()
        var meters = CombatMetersState()
        let transform = SpriteCanvasTransform(rootPosition: .zero, scaleX: 1, scaleY: 1)
        var event = PunchContactEvent(sequence: 1, kind: .jab, result: .hit,
            center: .zero, radius: 20, target: .zero,
            attacker: transform, defender: transform)
        event.attackerID = .blue
        XCTAssertTrue(health.receive(event))
        XCTAssertTrue(meters.receive(event))
        XCTAssertEqual(health.orange.current, 95)
        let awareness = meters.orange.awareness
        health.beginNextRound(heal: 10)
        XCTAssertEqual(health.orange.current, 100)
        XCTAssertEqual(meters.orange.awareness, awareness, accuracy: 1e-8)
    }

    func testLevelOneAttackCooldownAndReset() {
        var cooldown = AttackCooldown()
        XCTAssertTrue(cooldown.canAttack)
        XCTAssertEqual(cooldown.duration, 1, accuracy: 1e-10)
        cooldown.begin()
        XCTAssertFalse(cooldown.canAttack)
        cooldown.advance(0.999)
        XCTAssertFalse(cooldown.canAttack)
        cooldown.advance(0.001)
        XCTAssertTrue(cooldown.canAttack)
        cooldown.begin()
        cooldown.reset()
        XCTAssertTrue(cooldown.canAttack)
    }

    func testHigherLevelCooldownAndInvalidDelta() {
        var cooldown = AttackCooldown()
        cooldown.level = 2
        XCTAssertEqual(cooldown.duration, 0.5, accuracy: 1e-10)
        cooldown.begin()
        cooldown.advance(-10)
        XCTAssertEqual(cooldown.remaining, 0.5, accuracy: 1e-10)
        cooldown.advance(.nan)
        XCTAssertEqual(cooldown.remaining, 0.5, accuracy: 1e-10)
        cooldown.advance(0.5)
        XCTAssertTrue(cooldown.canAttack)
        cooldown.level = 99
        XCTAssertEqual(cooldown.duration, 0.25, accuracy: 1e-10)
    }

    func testSceneAttackCooldownDoesNotBlockGuardInput() {
        let driver = CombatDriver(distance: 400)
        let scene = driver.scene
        XCTAssertTrue(scene.testBeginAttack(.blue, .jab))
        XCTAssertEqual(scene.testBlueCooldown, 1, accuracy: 1e-8)
        driver.advance(0.42)
        XCTAssertFalse(scene.testBeginAttack(.blue, .jab))
        XCTAssertGreaterThan(scene.testBlueCooldown, 0.5)
        // Guard input remains independent of the attack cooldown.
        scene.setGuardHeld(true)
        XCTAssertTrue(scene.guardHeld)
        scene.setGuardHeld(false)
        driver.advance(0.58)
        XCTAssertEqual(scene.testBlueCooldown, 0, accuracy: 1e-8)
        XCTAssertTrue(scene.testBeginAttack(.blue, .jab))
    }

    func testCPUDefenseSlowsWhenAwarenessDrops() {
        var full = DefensiveAI()
        full.randomDraw = { 0 }
        full.setEnabled(true)
        full.observe(sequence: 1, kind: .cross, inRange: true, eligible: true)
        XCTAssertEqual(full.timeToTransition, 0.10, accuracy: 1e-8)

        var tired = DefensiveAI()
        tired.randomDraw = { 0 }
        tired.setEnabled(true)
        tired.observe(sequence: 1, kind: .cross, inRange: true, eligible: true,
                      awarenessPenalty: 0.15)
        XCTAssertEqual(tired.timeToTransition, 0.25, accuracy: 1e-8)
        XCTAssertNil(tired.advance(0.10))
        XCTAssertNil(tired.advance(0.149))
        XCTAssertNotNil(tired.advance(0.001))
    }

    func testDefensiveReactionPenaltyIsBounded() {
        var ai = DefensiveAI()
        ai.randomDraw = { 0 }
        ai.setEnabled(true)
        ai.observe(sequence: 1, kind: .jab, inRange: true, eligible: true,
                   awarenessPenalty: 100)
        XCTAssertEqual(ai.timeToTransition, 0.57, accuracy: 1e-8)
    }

    func testCPUDefenseChanceBoostsOnlyAfterConfirmedContact() {
        var ai = DefensiveAI()
        ai.randomDraw = { 0.90 }
        ai.setEnabled(true)
        ai.observe(sequence: 1, kind: .jab, inRange: true, eligible: true)
        XCTAssertEqual(ai.state, .idle) // Base jab chance = 60%.
        ai.recordIncomingContact()
        XCTAssertTrue(ai.wasAttacked)
        ai.observe(sequence: 2, kind: .jab, inRange: true, eligible: true)
        XCTAssertEqual(ai.state, .reacting) // Boosted chance = 95%.
        ai.cancel(reseed: true)
        XCTAssertFalse(ai.wasAttacked)
        ai.observe(sequence: 3, kind: .jab, inRange: true, eligible: true)
        XCTAssertEqual(ai.state, .idle)
    }

    func testCPUDefenseBoostIsBoundedAndLevelAware() {
        var ai = DefensiveAI()
        ai.randomDraw = { 0.995 }
        ai.setEnabled(true)
        ai.recordIncomingContact()
        ai.observe(sequence: 1, kind: .cross, inRange: true, eligible: true)
        XCTAssertEqual(ai.state, .idle) // 99.5% draw exceeds 95% threshold.
        ai.fighterLevel = 6
        ai.observe(sequence: 2, kind: .cross, inRange: true, eligible: true)
        XCTAssertEqual(ai.state, .reacting) // Level bonus capped at 100%.
    }

    func testWithdrawalRestoresAwarenessButGrabAndIdleDoNot() {
        var fighter = FighterMeters()
        fighter.receiveHit(zone: .head, guarded: false)
        let reduced = fighter.awareness
        fighter.advance(1, mode: .idle)
        fighter.advance(1, mode: .grab)
        fighter.advance(1, mode: .guarding)
        XCTAssertEqual(fighter.awareness, reduced, accuracy: 1e-9)
        fighter.advance(1, mode: .withdraw)
        XCTAssertEqual(fighter.awareness, reduced + 12, accuracy: 1e-9)
        fighter.advance(100, mode: .withdraw)
        XCTAssertEqual(fighter.awareness, 100, accuracy: 1e-9)
    }

    func testGuardTakesPrecedenceOverWithdrawalRecovery() {
        var state = CombatMetersState()
        // Accepted contact decreases Orange's awareness before regeneration.
        let driver = CombatDriver(distance: 170)
        XCTAssertTrue(driver.scene.testBeginAttack(.blue, .jab))
        driver.advance(0.15)
        let damaged = driver.scene.orangeMeters.awareness
        XCTAssertLessThan(damaged, 100)
        // Exercise the bridge's recovery selection with a contact-damaged copy
        // by checking direct state transitions on both fighters.
        state.advance(1, blueGuarding: true, orangeGuarding: true,
                      blueWithdrawing: true, orangeWithdrawing: true)
        XCTAssertEqual(state.blue.awareness, 100, accuracy: 1e-9)
        XCTAssertEqual(state.orange.awareness, 100, accuracy: 1e-9)
    }

    func testAwarenessAttackLockoutAddsOnlyLostReactionTime() {
        var cooldown = AttackCooldown()
        cooldown.begin(reactionDelay: 0.05)
        XCTAssertEqual(cooldown.remaining, 1.0, accuracy: 1e-8)
        cooldown.reset()
        cooldown.begin(reactionDelay: 0.25)
        XCTAssertEqual(cooldown.remaining, 1.20, accuracy: 1e-8)
        cooldown.advance(1.0)
        XCTAssertFalse(cooldown.canAttack)
        cooldown.advance(0.20)
        XCTAssertTrue(cooldown.canAttack)
    }

    func testAwarenessAttackLockoutCapsAndKeepsLevelScaling() {
        var cooldown = AttackCooldown()
        cooldown.level = 4
        cooldown.begin(reactionDelay: 100)
        XCTAssertEqual(cooldown.remaining, 0.80, accuracy: 1e-8)
        cooldown.reset()
        cooldown.begin()
        XCTAssertEqual(cooldown.remaining, 0.25, accuracy: 1e-8)
    }

    func testCPUIdleGuardDropsAtThreeSecondsOnLowDraw() {
        var ai = DefensiveAI()
        ai.randomDraw = { 0.0 }
        ai.setEnabled(true)
        ai.observe(sequence: 1, kind: .jab, inRange: true, eligible: true)
        XCTAssertEqual(ai.advance(0.02), .raise)
        XCTAssertNil(ai.advance(2.99))
        XCTAssertEqual(ai.state, .guarding)
        XCTAssertEqual(ai.advance(0.01), .release)
        XCTAssertEqual(ai.state, .idle)
    }

    func testCPUIdleGuardMayHoldUntilNextThreeSecondDecision() {
        var ai = DefensiveAI()
        var draws = [0.0, 0.75, 0.0]
        ai.randomDraw = { draws.removeFirst() }
        ai.setEnabled(true)
        ai.observe(sequence: 1, kind: .cross, inRange: true, eligible: true)
        XCTAssertEqual(ai.advance(0.10), .raise)
        XCTAssertNil(ai.advance(3))
        XCTAssertEqual(ai.state, .guarding)
        XCTAssertNil(ai.advance(2.99))
        XCTAssertEqual(ai.advance(0.01), .release)
    }


}
