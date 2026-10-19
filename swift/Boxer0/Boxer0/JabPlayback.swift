import Foundation

enum PunchKind {
    case jab
    case cross

    var frameCount: Int { self == .jab ? 6 : 8 }
    var frameDuration: Double { self == .jab ? 0.05 : 0.06 }
    var contactFrame: Int { self == .jab ? 3 : 4 }
    var duration: Double { Double(frameCount) * frameDuration }
}

/// Shared one-shot clock; kept in the existing project source file.
/// No input queue, loops, movement, or gameplay effects.
struct PunchPlayback {
    private(set) var kind: PunchKind = .jab
    private(set) var isActive = false
    private(set) var frameIndex = 0
    private(set) var reachedContact = false
    private var accumulator = 0.0

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
