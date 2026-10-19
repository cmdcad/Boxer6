import Foundation

/// Six 50 ms frames. No input queue, loops, movement, or gameplay effects.
struct JabPlayback {
    static let frameCount = 6
    static let frameDuration = 0.05
    static let contactFrame = 3 // Artist frame 4, zero-based in code.
    private(set) var isActive = false
    private(set) var frameIndex = 0
    private(set) var reachedContact = false
    private var accumulator = 0.0

    @discardableResult
    mutating func start() -> Bool {
        guard !isActive else { return false }
        isActive = true
        frameIndex = 0
        reachedContact = false
        accumulator = 0
        return true
    }

    mutating func advance(_ duration: Double) -> (contact: Bool, completed: Bool) {
        guard isActive, duration.isFinite, duration >= 0 else { return (false, false) }
        accumulator += duration
        var contact = false
        while accumulator + 1e-10 >= Self.frameDuration {
            accumulator = max(0, accumulator - Self.frameDuration)
            if frameIndex == Self.frameCount - 1 {
                isActive = false
                accumulator = 0
                return (contact, true)
            }
            frameIndex += 1
            if frameIndex == Self.contactFrame && !reachedContact {
                reachedContact = true
                contact = true
            }
            if frameIndex == Self.frameCount - 1 && accumulator + 1e-10 >= Self.frameDuration {
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
        return advance(Self.frameDuration)
    }

    mutating func cancel() {
        isActive = false
        frameIndex = 0
        accumulator = 0
        reachedContact = false
    }
}
