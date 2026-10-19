import Foundation

enum DefenderClip: String {
    case idle
    case hitReact = "hit_react"
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
