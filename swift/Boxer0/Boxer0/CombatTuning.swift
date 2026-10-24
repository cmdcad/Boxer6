import Foundation

/// Single home for combat numbers. Placeholder values for feel-testing.
/// Phase 1: defined only; nothing reads these yet. Times are in seconds.
struct CombatTuning {
    // Match
    var rounds = 8
    var roundSeconds = 120.0

    // Fighter caps
    var maxStamina = 100.0
    var maxHealth = 100.0
    var maxAwareness = 100.0
    var loseHealthBelow = 40.0
    var roundStartHealthRegen = 10.0

    // Timing
    var attackCooldown = 1.0
    var defenseActivation = 0.5
    var baseReaction = 0.05
    var maxReaction = 0.6
    var grabHoldMax = 3.0
    var consecutiveHeadHitReset = 3.0   // assumption: streak expires after this long

    // Awareness
    var consecutiveGrowth = 1.2
    var unguardedFraction = 1.0 / 3.0
    var heavyUnguardedFraction = 1.0 / 2.0
    var withdrawDropFactor = 0.5

    // Health damage (used from phase 2)
    var bodyHealthDamage = 3.0
    var headHealthDamage = 4.0
    var consecutiveHeadDamage = 10.0

    // Stamina
    var guardCostPercent = 5.0
    var swayCost = 0.0
    var regenIdle = 8.0, regenGrab = 5.0, regenWithdraw = 12.0   // per second
    var grabStaminaBelow = 50.0

    // Points
    var headPoints = 3, bodyPoints = 1, guardedPoints = 1

    // CPU
    var defendInWindow = 0.5
    var defendAfterHit = 0.9
    var idleGuardDropAfter = 3.0
    var idleGuardDropChance = 0.5

    func levelMultiplier(attacker: Int, defender: Int) -> Double {
        Double(attacker + 1) / Double(defender + 1)
    }
}

/// Per-fighter level holder. Level stats are injected later; both fighters are level 1.
struct FighterStats {
    var level = 1
}


/// Phase 3 match rules, independent of SpriteKit and the presentation layer.
/// A round ends on its time boundary; any leftover dt belongs to the next round.
enum MatchResult: Equatable {
    case bluePoints, orangePoints, draw, blueKO, orangeKO
}

struct MatchState {
    let tuning: CombatTuning
    private(set) var round = 1
    private(set) var remaining: Double
    private(set) var bluePoints = 0
    private(set) var orangePoints = 0
    private(set) var result: MatchResult?
    private var blueSequence = 0
    private var orangeSequence = 0

    init(tuning: CombatTuning = CombatTuning()) {
        self.tuning = tuning
        remaining = tuning.roundSeconds
    }

    var isFinished: Bool { result != nil }

    /// Returns the number of newly entered rounds (for round-start health regen).
    @discardableResult
    mutating func advance(_ dt: Double) -> Int {
        guard !isFinished, dt.isFinite, dt > 0 else { return 0 }
        var time = dt
        var started = 0
        while time > 0 && !isFinished {
            if time < remaining {
                remaining -= time
                break
            }
            time -= remaining
            if round >= tuning.rounds {
                remaining = 0
                if bluePoints == orangePoints { result = .draw }
                else { result = bluePoints > orangePoints ? .bluePoints : .orangePoints }
            } else {
                round += 1
                remaining = tuning.roundSeconds
                started += 1
            }
        }
        return started
    }

    /// Contact sequences are monotonic per attacker, even across round boundaries.
    @discardableResult
    mutating func score(_ event: PunchContactEvent) -> Bool {
        guard !isFinished else { return false }
        if event.attackerID == .blue {
            guard event.sequence > blueSequence else { return false }
            blueSequence = event.sequence
        } else {
            guard event.sequence > orangeSequence else { return false }
            orangeSequence = event.sequence
        }
        let points: Int
        switch event.result {
        case .miss: return false
        case .block: points = tuning.guardedPoints
        case .hit: points = tuning.headPoints // Jab and Cross remain head-only.
        }
        if event.attackerID == .blue { bluePoints += points }
        else { orangePoints += points }
        return true
    }

    mutating func knockout(winner: FighterID) {
        guard !isFinished else { return }
        result = winner == .blue ? .blueKO : .orangeKO
    }

    /// Provisional double-KO policy: draw.
    mutating func simultaneousKnockout() {
        guard !isFinished else { return }
        result = .draw
    }

    mutating func reset() { self = MatchState(tuning: tuning) }
}
