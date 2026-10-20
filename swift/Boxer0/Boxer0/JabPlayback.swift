import Foundation

enum PunchKind {
    case jab
    case cross

    var frameCount: Int { self == .jab ? 6 : 8 }
    var frameDuration: Double { self == .jab ? 0.05 : 0.06 }
    var contactFrame: Int { self == .jab ? 3 : 4 }
    var duration: Double { Double(frameCount) * frameDuration }
    // Existing withdrawal artwork, zero-based. Presentation only.
    var recoveryPoseFrame: Int { self == .jab ? 4 : 5 }
}

/// Shared one-shot clock; kept in the existing project source file.
/// No input queue, loops, movement, or gameplay effects.
struct PunchPlayback {
    private(set) var kind: PunchKind = .jab
    private(set) var isActive = false
    private(set) var frameIndex = 0
    private(set) var reachedContact = false
    private var accumulator = 0.0
    var timeUntilContact: Double? {
        guard isActive, !reachedContact else { return nil }
        return max(0, Double(kind.contactFrame - frameIndex) * kind.frameDuration - accumulator)
    }

    @discardableResult
    mutating func start(_ kind: PunchKind = .jab) -> Bool {
        guard !isActive else { return false }
        self.kind = kind
        isActive = true
        frameIndex = 0
        reachedContact = false
        accumulator = 0
        return true
    }

    mutating func advance(_ duration: Double, preserveContactPose: Bool = false) -> (contact: Bool, completed: Bool) {
        guard isActive, duration.isFinite, duration >= 0 else { return (false, false) }
        accumulator += duration
        var contact = false
        while accumulator + 1e-10 >= kind.frameDuration {
            accumulator = max(0, accumulator - kind.frameDuration)
            if frameIndex == kind.frameCount - 1 {
                isActive = false
                accumulator = 0
                return (contact, true)
            }
            frameIndex += 1
            if frameIndex == kind.contactFrame && !reachedContact {
                reachedContact = true
                contact = true
                if preserveContactPose && accumulator + 1e-10 >= kind.frameDuration {
                    // On a hitch, present contact rather than reacting against
                    // a punch already rendered in withdrawal. Normal FPS timing
                    // is unchanged; only an otherwise skipped contact is held.
                    accumulator = 0
                    return (true, false)
                }
            }
            if frameIndex == kind.frameCount - 1 && accumulator + 1e-10 >= kind.frameDuration {
                // A delayed render tick must still present recovery, rather
                // than consuming the entire final pose offscreen.
                accumulator = 0
                return (contact, false)
            }
        }
        return (contact, false)
    }

    mutating func step() -> (contact: Bool, completed: Bool) {
        accumulator = 0
        return advance(kind.frameDuration)
    }

    mutating func cancel() {
        isActive = false
        frameIndex = 0
        accumulator = 0
        reachedContact = false
    }
}

enum FighterID { case blue, orange
    var opponent: FighterID { self == .blue ? .orange : .blue }
}
struct AttackContext {
    let id: Int
    let attacker: FighterID
    let defender: FighterID
    let kind: PunchKind
    let startTime: Double
    var isCounterAttempt = false
    var contactEvaluated = false
    var completed = false
}

enum CPUOffenseState: String { case ready, preparing, attacking, cooldown }
struct CPUOffense {
    var decisionInterval = 0.30
    var jabWeight = 0.70
    var counterOpportunityAttackChance = 0.65
    var jabPreparation = 0.18
    var crossPreparation = 0.28
    var jabCooldown = 0.65
    var crossCooldown = 0.90
    var minimumCompletedInterval = 0.40
    private(set) var state: CPUOffenseState = .ready
    private(set) var kind: PunchKind = .jab
    private(set) var remaining = 0.30
    private var randomState: UInt64 = 98765
    var label: String {
        switch state {
        case .ready: return "READY"
        case .preparing: return kind == .jab ? "PREPARING JAB" : "PREPARING CROSS"
        case .attacking: return kind == .jab ? "JAB" : "CROSS"
        case .cooldown: return "COOLDOWN"
        }
    }
    mutating func cancel(reseed: Bool = false) {
        state = .ready; remaining = decisionInterval
        if reseed { randomState = 98765 }
    }
    mutating func disable() { if state != .attacking { cancel() } }
    mutating func cancelPreparation() { if state == .preparing { cancel() } }
    mutating func finished() {
        state = .cooldown
        remaining = max(minimumCompletedInterval, kind == .jab ? jabCooldown : crossCooldown)
    }
    mutating func advance(_ dt: Double, enabled: Bool, eligible: Bool,
                          jabInRange: Bool, crossInRange: Bool, opponentVulnerable: Bool = false) -> PunchKind? {
        guard dt.isFinite, dt >= 0 else { return nil }
        if state == .attacking { return nil }
        if state == .cooldown {
            remaining = max(0, remaining-dt)
            if remaining == 0 { state = .ready }
            return nil
        }
        guard enabled, eligible else { cancel(); return nil }
        remaining -= dt
        guard remaining <= 1e-10 else { return nil }
        if state == .preparing {
            state = .attacking
            return kind
        }
        remaining = decisionInterval
        guard jabInRange || crossInRange else { return nil }
        if opponentVulnerable {
            randomState = randomState &* 6364136223846793005 &+ 1442695040888963407
            let opportunityDraw = Double(randomState >> 11) / 9007199254740992.0
            guard opportunityDraw < min(1, max(0, counterOpportunityAttackChance)) else { return nil }
        }
        randomState = randomState &* 6364136223846793005 &+ 1442695040888963407
        let draw = Double(randomState >> 11) / 9007199254740992.0
        kind = !crossInRange ? .jab : (!jabInRange ? .cross : (draw < jabWeight ? .jab : .cross))
        state = .preparing
        remaining = kind == .jab ? jabPreparation : crossPreparation
        return nil
    }
}

enum PhysicalActionPhase { case ready, attacking, recovering }

/// Shared physical action lock, independent of CPU tactical pacing.
struct PunchRecovery {
    var jabDuration = 0.12
    var crossDuration = 0.22
    private(set) var phase: PhysicalActionPhase = .ready
    private(set) var kind: PunchKind = .jab
    private(set) var remaining = 0.0
    var isRecovering: Bool { phase == .recovering }
    var label: String {
        switch phase {
        case .ready: return "READY"
        case .attacking: return kind == .jab ? "JAB" : "CROSS"
        case .recovering: return kind == .jab ? "RECOVERING JAB" : "RECOVERING CROSS"
        }
    }
    var diagnosticLabel: String {
        isRecovering ? "\(label) - \(Int(ceil(remaining * 1000 - 1e-7))) ms" : label
    }
    mutating func begin(_ punch: PunchKind) { kind = punch; phase = .attacking; remaining = 0 }
    mutating func completeAttack() {
        guard phase == .attacking else { return }
        phase = .recovering
        remaining = kind == .jab ? jabDuration : crossDuration
    }
    @discardableResult
    mutating func advance(_ dt: Double) -> Bool {
        guard isRecovering, dt.isFinite, dt >= 0 else { return false }
        remaining = max(0, remaining-dt)
        guard remaining <= 1e-10 else { return false }
        cancel()
        return true
    }
    mutating func cancel() { phase = .ready; remaining = 0 }
}
