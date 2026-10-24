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
}
