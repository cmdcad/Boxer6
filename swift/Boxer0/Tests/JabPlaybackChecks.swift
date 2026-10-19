import Foundation

@main
struct JabPlaybackChecks {
    static func main() {
        var jab = PunchPlayback()
        precondition(jab.start() && jab.frameIndex == 0)
        precondition(!jab.start(), "No self interruption or queued press")
        precondition(!jab.advance(0.149).contact && jab.frameIndex == 2)
        precondition(jab.advance(0.001).contact && jab.frameIndex == 3)
        precondition(!jab.advance(0.1).contact && jab.frameIndex == 5 && jab.isActive)
        precondition(!jab.advance(0.049).completed && jab.isActive, "Recovery holds 50 ms")
        precondition(jab.advance(0.001).completed && !jab.isActive)
        precondition(!jab.advance(1).contact && !jab.advance(1).completed)
        // A completed punch never restarts without a distinct start call.
        precondition(!jab.isActive)

        precondition(jab.start())
        _ = jab.advance(0.025)
        // Pause is implemented by not advancing; stepping selects the next pose.
        precondition(jab.frameIndex == 0)
        var contacts = 0
        for expected in 1...5 {
            let event = jab.step()
            if event.contact { contacts += 1 }
            precondition(jab.frameIndex == expected && jab.isActive)
            precondition(!event.completed)
        }
        precondition(contacts == 1 && jab.step().completed)

        for fps in [30, 60, 120] {
            _ = jab.start()
            var contactCount = 0
            var completionCount = 0
            var observed = Set([0])
            for _ in 0..<(fps / 2) {
                let event = jab.advance(1.0 / Double(fps))
                if jab.isActive { observed.insert(jab.frameIndex) }
                if event.contact { contactCount += 1 }
                if event.completed { completionCount += 1 }
            }
            precondition(contactCount == 1 && completionCount == 1 && !jab.isActive)
            precondition(observed == Set(0..<6), "All six poses shown at supported rendering rates")
        }
        _ = jab.start()
        precondition(jab.advance(0.3).contact && jab.isActive && jab.frameIndex == 5,
                     "Delayed render must present recovery")
        precondition(jab.advance(0.05).completed && !jab.isActive)
        _ = jab.start()
        jab.cancel()
        precondition(!jab.isActive && jab.frameIndex == 0 && !jab.reachedContact)
        precondition(jab.start())
        print("PASS: 300 ms jab, frame-4 contact once, recovery duration, no repeat/queue, stepping, 30/60/120 fps, cancellation")
    }
}
