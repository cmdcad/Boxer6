import Foundation

enum HitZone { case head, body }
enum RegenMode { case guarding, idle, grab, withdraw }

/// Stamina and awareness for one fighter. Pure value type, not yet wired into the scene.
/// Awareness 0 is a knockout. Consecutive-hit escalation applies to unguarded head hits only.
struct FighterMeters {
    let tuning: CombatTuning
    private(set) var stamina: Double
    private(set) var awareness: Double
    private(set) var consecutiveHeadHits = 0
    private var sinceHeadHit = 0.0

    init(tuning: CombatTuning = CombatTuning()) {
        self.tuning = tuning
        stamina = tuning.maxStamina
        awareness = tuning.maxAwareness
    }

    var isKnockedOut: Bool { awareness <= 0 }

    /// Grab needs low stamina and the too-close distance state.
    func canStartGrab(isTooClose: Bool) -> Bool {
        isTooClose && stamina < tuning.grabStaminaBelow
    }

    /// Returns the awareness dropped. A guarded hit costs stamina only.
    @discardableResult
    mutating func receiveHit(zone: HitZone, guarded: Bool, heavy: Bool = false,
                             withdrawing: Bool = false, levelMultiplier: Double = 1) -> Double {
        if guarded {
            let cost = tuning.maxStamina * tuning.guardCostPercent / 100 * levelMultiplier
            stamina = max(0, stamina - cost)
            return 0
        }
        var n = 1
        if zone == .head {
            consecutiveHeadHits += 1
            sinceHeadHit = 0
            n = consecutiveHeadHits
        }
        let fraction = heavy ? tuning.heavyUnguardedFraction : tuning.unguardedFraction
        var drop = tuning.maxAwareness * fraction * pow(tuning.consecutiveGrowth, Double(n - 1))
        if withdrawing { drop *= tuning.withdrawDropFactor }
        let before = awareness
        awareness = max(0, awareness - drop)
        return before - awareness
    }

    /// Call when a defense succeeds (sway, withdraw, block) to end a head-hit streak.
    mutating func endHeadHitStreak() { consecutiveHeadHits = 0; sinceHeadHit = 0 }

    mutating func spendSway() { stamina = max(0, stamina - tuning.swayCost) }

    mutating func advance(_ dt: Double, mode: RegenMode) {
        guard dt.isFinite, dt > 0 else { return }
        if consecutiveHeadHits > 0 {
            sinceHeadHit += dt
            if sinceHeadHit >= tuning.consecutiveHeadHitReset { endHeadHitStreak() }
        }
        switch mode {
        case .guarding: break
        case .idle: stamina = min(tuning.maxStamina, stamina + tuning.regenIdle * dt)
        case .grab: stamina = min(tuning.maxStamina, stamina + tuning.regenGrab * dt)
        case .withdraw:
            stamina = min(tuning.maxStamina, stamina + tuning.regenWithdraw * dt)
            awareness = min(tuning.maxAwareness, awareness + tuning.regenWithdraw * dt)
        }
    }

    /// Awareness-driven delay: baseReaction at full awareness, slower as it drops.
    /// Also usable as the attack lockout. Clamped to maxReaction.
    var reactionDelay: Double {
        guard awareness > 0 else { return tuning.maxReaction }
        return min(tuning.maxReaction,
                   tuning.baseReaction * tuning.maxAwareness / awareness)
    }
}

 
/// Phase 2A bridge: receives accepted contact events exactly once per attacker.
/// Health/knockdown integration is a separate Phase 2 checkpoint.
struct CombatMetersState {
    private(set) var blue = FighterMeters()
    private(set) var orange = FighterMeters()
    private var blueSequence = 0
    private var orangeSequence = 0

    @discardableResult
    mutating func receive(_ event: PunchContactEvent) -> Bool {
        guard event.result != .miss else { return false }
        if event.attackerID == .blue {
            guard event.sequence > blueSequence else { return false }
            blueSequence = event.sequence
        } else {
            guard event.sequence > orangeSequence else { return false }
            orangeSequence = event.sequence
        }
        if event.defenderID == .blue {
            blue.receiveHit(zone: .head, guarded: event.result == .block)
            if event.result == .block { blue.endHeadHitStreak() }
        } else {
            orange.receiveHit(zone: .head, guarded: event.result == .block)
            if event.result == .block { orange.endHeadHitStreak() }
        }
        return true
    }

    /// Withdrawal is an out-of-range retreat, never ordinary idle or guard.
    /// Guard has precedence so holding guard cannot regenerate awareness.
    mutating func advance(_ dt: Double, blueGuarding: Bool, orangeGuarding: Bool,
                          blueWithdrawing: Bool = false, orangeWithdrawing: Bool = false) {
        blue.advance(dt, mode: blueGuarding ? .guarding : (blueWithdrawing ? .withdraw : .idle))
        orange.advance(dt, mode: orangeGuarding ? .guarding : (orangeWithdrawing ? .withdraw : .idle))
    }

    /// Preserve accepted sequence watermarks when resetting for debug recovery.
    mutating func reset() {
        blue = FighterMeters()
        orange = FighterMeters()
    }

    mutating func recoverBlue() { blue = FighterMeters() }
    mutating func recoverOrange() { orange = FighterMeters() }

#if DEBUG
    mutating func testDamageOrangeAwareness() {
        orange.receiveHit(zone: .head, guarded: false)
    }
#endif
}
