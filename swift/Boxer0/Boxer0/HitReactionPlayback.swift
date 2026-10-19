import Foundation

enum DefenderClip: String {
    case idle
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
        while accumulator + 1e-10 >= Self.frameDuration {
            accumulator = max(0, accumulator - Self.frameDuration)
            if frameIndex == Self.frameCount - 1 {
                cancel()
                return true
            }
            frameIndex += 1
            if frameIndex == Self.frameCount - 1 && accumulator + 1e-10 >= Self.frameDuration {
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
        return advance(Self.frameDuration)
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
    var radius: CGFloat
    var opacity: Double
    static let jab = BlockFeedbackProfile(duration: 0.08, radius: 18, opacity: 0.65)
    static let cross = BlockFeedbackProfile(duration: 0.11, radius: 23, opacity: 0.85)
}

/// Presentation only. Confirmed BLOCK events own this single restartable effect.
struct BlockFeedbackPlayback {
    var jabProfile = BlockFeedbackProfile.jab
    var crossProfile = BlockFeedbackProfile.cross
    private(set) var kind: PunchKind?
    private(set) var imageAnchor = CGPoint.zero
    private(set) var elapsed = 0.0
    private var lastSequence = 0
    var isActive: Bool { kind != nil }
    var profile: BlockFeedbackProfile { kind == .cross ? crossProfile : jabProfile }
    var label: String { kind == nil ? "OFF" : (kind == .jab ? "Jab" : "Cross") }
    var opacity: Double {
        guard isActive else { return 0 }
        return profile.opacity * max(0, 1 - elapsed / max(profile.duration, 1e-10))
    }

    @discardableResult
    mutating func receive(_ event: PunchContactEvent) -> Bool {
        guard event.result == .block, event.sequence > lastSequence else { return false }
        lastSequence = event.sequence
        kind = event.kind
        elapsed = 0
        // Fixed source-canvas anchors are the centers of guard_b_2's gloves:
        // rear (296-43,186-36), lead (364.5-61,192-40).
        // Choose the one nearest the confirmed scene contact center.
        let anchors = [CGPoint(x: 253, y: 150), CGPoint(x: 303.5, y: 152)]
        imageAnchor = anchors.min { a, b in
            let pa = event.defender.scenePoint(fromImage: a)
            let pb = event.defender.scenePoint(fromImage: b)
            return hypot(pa.x - event.center.x, pa.y - event.center.y)
                < hypot(pb.x - event.center.x, pb.y - event.center.y)
        } ?? anchors[0]
        return true
    }

    mutating func advance(_ dt: Double) {
        guard isActive, dt.isFinite, dt >= 0 else { return }
        elapsed += dt
        if elapsed + 1e-10 >= profile.duration { cancel() }
    }
    mutating func cancel() {
        kind = nil
        elapsed = 0
        imageAnchor = .zero
        // Retain watermark: cancellation/reset must not replay an old BLOCK.
    }
}
