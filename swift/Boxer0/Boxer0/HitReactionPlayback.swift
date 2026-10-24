import Foundation

enum DefenderClip: String {
    case idle
    case advance
    case retreat
    case jab
    case cross
    case hitReact = "hit_react"
    case knockdown
    case down
    case rise
    case guardPose = "guard"
}

/// Profile metadata does not deform complete-character textures.
/// Cross can use a slightly stronger optional visual emphasis, not root motion.
struct HitFeedbackProfile {
    let punch: PunchKind
    var label: String { punch == .jab ? "Jab" : "Cross" }
    var intensity: String { punch == .jab ? "light" : "moderate" }
    var emphasisDuration: Double { 0.06 }
    var emphasisStrength: Double { punch == .jab ? 0.04 : 0.075 }
}

/// Four 60 ms poses. Every HIT restarts immediately; MISS has no effect.
struct HitReactionPlayback {
    static let frameCount = 4
    static let frameDuration = 0.06
    static let duration = 0.24
    private(set) var isActive = false
    private(set) var frameIndex = 0
    private var accumulator = 0.0
    private var elapsed = 0.0
    // Orange-only approved art. Blue retains the original four 60ms poses.
    private(set) var approvedOrangeArt = false
    var activeFrameCount: Int { approvedOrangeArt ? (profile?.punch == .cross ? 14 : 18) : Self.frameCount }
    var activeFrameDuration: Double { approvedOrangeArt ? (profile?.punch == .cross ? 1.0 / 18.0 : 1.0 / 20.0) : Self.frameDuration }
    mutating func setApprovedOrangeArt(_ available: Bool) { approvedOrangeArt = available }
    private(set) var profile: HitFeedbackProfile?
    var emphasisAmount: Double {
        guard isActive, let profile = profile else { return 0 }
        return profile.emphasisStrength * max(0, 1 - elapsed / profile.emphasisDuration)
    }
    var clip: DefenderClip { isActive ? .hitReact : .idle }

    @discardableResult
    mutating func receive(_ result: PunchContactResult, from punch: PunchKind = .jab) -> Bool {
        guard result == .hit else { return false }
        isActive = true
        frameIndex = 0
        accumulator = 0
        elapsed = 0
        profile = HitFeedbackProfile(punch: punch)
        return true
    }

    @discardableResult
    mutating func advance(_ dt: Double) -> Bool {
        guard isActive, dt.isFinite, dt >= 0 else { return false }
        accumulator += dt
        elapsed += dt
        while accumulator + 1e-10 >= activeFrameDuration {
            accumulator = max(0, accumulator - activeFrameDuration)
            if frameIndex == activeFrameCount - 1 {
                cancel()
                return true
            }
            frameIndex += 1
            if frameIndex == activeFrameCount - 1 && accumulator + 1e-10 >= activeFrameDuration {
                // Keep final recovery visible on a delayed render tick.
                accumulator = 0
                return false
            }
        }
        return false
    }

    @discardableResult
    mutating func step() -> Bool {
        accumulator = 0
        return advance(activeFrameDuration)
    }

    mutating func cancel() {
        isActive = false
        frameIndex = 0
        accumulator = 0
        elapsed = 0
        profile = nil
    }
}

/// Shares the scene clock with punches/recoil; no timers or completion closures.
struct KnockdownPlayback {
    static let frameCount = 8
    static let frameDuration = 0.08
    static let duration = 0.64
    static let riseFrameDuration = 0.10
    static let riseDuration = 0.80
    private(set) var clip: DefenderClip = .idle
    private(set) var frameIndex = 0
    private var accumulator = 0.0
    var hasStarted: Bool { clip != .idle }

    @discardableResult
    mutating func start() -> Bool {
        guard !hasStarted else { return false }
        clip = .knockdown
        frameIndex = 0
        accumulator = 0
        return true
    }

    @discardableResult
    mutating func startRise() -> Bool {
        guard clip == .down else { return false }
        clip = .rise
        frameIndex = 0
        accumulator = 0
        return true
    }

    /// Returns true once, only on manual rise completion.
    @discardableResult
    mutating func advance(_ dt: Double) -> Bool {
        guard clip == .knockdown || clip == .rise,
              dt.isFinite, dt >= 0 else { return false }
        let interval = clip == .rise ? Self.riseFrameDuration : Self.frameDuration
        accumulator += dt
        guard accumulator + 1e-10 >= interval else { return false }
        accumulator = max(0, accumulator - interval)
        // Under a hitch present every fall/recovery pose rather than skip it.
        // Nominal durations are 640/800 ms; a slow render loop can extend them.
        if accumulator + 1e-10 >= interval { accumulator = 0 }
        if frameIndex == Self.frameCount - 1 {
            let recovered = clip == .rise
            clip = recovered ? .idle : .down
            frameIndex = 0
            accumulator = 0
            return recovered
        } else {
            frameIndex += 1
        }
        return false
    }

    @discardableResult
    mutating func step() -> Bool {
        accumulator = 0
        return advance(clip == .rise ? Self.riseFrameDuration : Self.frameDuration)
    }

    mutating func cancel() {
        clip = .idle
        frameIndex = 0
        accumulator = 0
    }
}

/// Selected defense is separate from combat eligibility and displayed clip.
enum FighterDefenseState {
    case unguarded
    case guarding
}

struct GuardPlayback {
    static let frameCount = 3
    static let frameDuration = 0.04
    static let entryDuration = 0.12
    private(set) var state: FighterDefenseState = .unguarded
    private var elapsed = 0.0
    var isSelected: Bool { state == .guarding }
    var frameIndex: Int { min(2, Int((elapsed + 1e-10) / Self.frameDuration)) }
    // All three 40 ms entry intervals must elapse; final pose then holds.
    var isEffective: Bool { isSelected && elapsed + 1e-10 >= Self.entryDuration }
    var status: String { !isSelected ? "OFF" : (isEffective ? "ACTIVE" : "RAISING") }

    mutating func toggle() {
        if isSelected { cancel() } else { state = .guarding; elapsed = 0 }
    }
    mutating func advance(_ dt: Double) {
        guard isSelected, dt.isFinite, dt >= 0 else { return }
        elapsed = min(Self.entryDuration, elapsed + dt)
    }
    mutating func step() { advance(Self.frameDuration) }
    mutating func cancel() { state = .unguarded; elapsed = 0 }
}

struct BlockFeedbackProfile {
    var duration: Double
    static let jab = BlockFeedbackProfile(duration: 0.12)
    static let cross = BlockFeedbackProfile(duration: 0.16)
}

/// Dedicated whole-frame guard recoil with fixed-foot artwork, never root motion.
struct BlockFeedbackPlayback {
    static let frameCount = 3
    var jabProfile = BlockFeedbackProfile.jab
    var crossProfile = BlockFeedbackProfile.cross
    private(set) var kind: PunchKind?
    private(set) var frameIndex = 0
    private var accumulator = 0.0
    private var lastSequence = 0
    var isActive: Bool { kind != nil }
    var profile: BlockFeedbackProfile { kind == .cross ? crossProfile : jabProfile }
    var frameDuration: Double { max(profile.duration, 1e-6) / Double(Self.frameCount) }
    var label: String { kind == nil ? "OFF" : (kind == .jab ? "Jab recoil" : "Cross recoil") }

    @discardableResult
    mutating func receive(_ event: PunchContactEvent) -> Bool {
        guard event.result == .block, event.sequence > lastSequence else { return false }
        lastSequence = event.sequence
        kind = event.kind
        frameIndex = 0
        accumulator = 0
        return true
    }

    mutating func advance(_ dt: Double) {
        guard isActive, dt.isFinite, dt >= 0 else { return }
        accumulator += dt
        guard accumulator + 1e-10 >= frameDuration else { return }
        accumulator = max(0, accumulator - frameDuration)
        // Preserve each authored pose under a render hitch; low FPS may extend
        // nominal duration. Never skip the visible return-to-guard pose.
        if accumulator + 1e-10 >= frameDuration { accumulator = 0 }
        if frameIndex == Self.frameCount - 1 { cancel() }
        else { frameIndex += 1 }
    }
    mutating func cancel() {
        kind = nil
        frameIndex = 0
        accumulator = 0
        // Retain watermark so reset/repeated rendering cannot replay a BLOCK.
    }
}

struct DefensiveAIProfile {
    var chance: Double
    var reactionDelay: Double
    var holdDuration: Double
    static let jab = DefensiveAIProfile(chance: 0.60, reactionDelay: 0.02, holdDuration: 0.50)
    static let cross = DefensiveAIProfile(chance: 0.75, reactionDelay: 0.10, holdDuration: 0.65)
}

enum DefensiveAIState: String { case idle, reacting, guarding }
enum DefensiveAIRequest: Equatable { case raise, release }

/// Receives accepted punch-start identities, never random per-frame polling.
struct DefensiveAI {
    var randomDraw: (() -> Double)?
    var jabProfile = DefensiveAIProfile.jab
    var crossProfile = DefensiveAIProfile.cross
    var maximumGuardDuration = 9.0
    var idleGuardDropAfter = CombatTuning().idleGuardDropAfter
    var idleGuardDropChance = CombatTuning().idleGuardDropChance
    /// At level 1, after an actual incoming contact the next defense attempt
    /// succeeds with 95% probability. The base profiles stay unchanged.
    var attackedDefenseChance = 0.95
    var fighterLevel = 1
    private(set) var wasAttacked = false
    private(set) var enabled = false
    private(set) var state: DefensiveAIState = .idle
    private(set) var remaining = 0.0
    private var pendingHold = 0.0
    private var continuousGuardTime = 0.0
    private var timeWithoutAttack = 0.0
    private var lastSequence = 0
    private var randomState: UInt64
    private let initialSeed: UInt64
    init(seed: UInt64 = 12345) { initialSeed = seed; randomState = seed }
    var label: String { enabled ? state.rawValue : "OFF" }
    var timeToTransition: Double { state == .idle ? .infinity : remaining }

    mutating func setEnabled(_ value: Bool) { enabled = value; cancel() }

    /// Call only for a confirmed hit or block, not for a missed punch.
    mutating func recordIncomingContact() { wasAttacked = true }
    mutating func cancel(reseed: Bool = false) {
        state = .idle
        remaining = 0
        pendingHold = 0
        continuousGuardTime = 0
        timeWithoutAttack = 0
        if reseed {
            randomState = initialSeed
            wasAttacked = false
        }
    }
    mutating func observe(sequence: Int, kind: PunchKind, inRange: Bool, eligible: Bool,
                          awarenessPenalty: Double = 0) {
        guard sequence > lastSequence else { return }
        lastSequence = sequence
        guard enabled, eligible, inRange else { return }
        let profile = kind == .jab ? jabProfile : crossProfile
        if state == .guarding {
            // A new attack resets the idle-drop clock, not the guard pose.
            timeWithoutAttack = 0
            remaining = min(max(0, idleGuardDropAfter),
                            max(0, maximumGuardDuration - continuousGuardTime))
            return
        }
        guard state == .idle else { return } // earliest pending reaction wins
        randomState = randomState &* 6364136223846793005 &+ 1442695040888963407
        let draw = Double(randomState >> 11) / 9007199254740992.0
        let baseChance = wasAttacked ? max(profile.chance, attackedDefenseChance) : profile.chance
        // Higher fighter levels raise the chance slightly, capped at certainty.
        let chance = min(1, max(0, baseChance + 0.01 * Double(max(0, fighterLevel - 1))))
        guard (randomDraw?() ?? draw) < chance else { return }
        state = .reacting
        // At full awareness the existing defensive timing is unchanged.
        // Reduced awareness adds a bounded delay to the guard decision.
        let penalty = awarenessPenalty.isFinite ? min(0.55, max(0, awarenessPenalty)) : 0
        remaining = max(0, profile.reactionDelay + penalty)
        pendingHold = max(0, profile.holdDuration)
    }
    mutating func advance(_ dt: Double) -> DefensiveAIRequest? {
        guard enabled, state != .idle, dt.isFinite, dt >= 0 else { return nil }
        if state == .guarding {
            continuousGuardTime += dt
            timeWithoutAttack += dt
        }
        remaining = max(0, remaining - dt)
        guard remaining <= 1e-10 else { return nil }
        if state == .reacting {
            state = .guarding
            continuousGuardTime = 0
            // Hold through the first idle decision instead of releasing after
            // the short jab/cross pose. GuardPlayback still owns entry timing.
            remaining = min(max(pendingHold, idleGuardDropAfter), max(0, maximumGuardDuration))
            return .raise
        }
        // Every 3 seconds of no attack, decide whether to drop guard.
        // A hard duration limit prevents indefinite guard lockout.
        randomState = randomState &* 6364136223846793005 &+ 1442695040888963407
        let draw = Double(randomState >> 11) / 9007199254740992.0
        if continuousGuardTime < maximumGuardDuration &&
            (randomDraw?() ?? draw) >= idleGuardDropChance {
            timeWithoutAttack = 0
            remaining = min(max(0, idleGuardDropAfter),
                            max(0, maximumGuardDuration - continuousGuardTime))
            return nil
        }
        cancel()
        return .release
    }
}
