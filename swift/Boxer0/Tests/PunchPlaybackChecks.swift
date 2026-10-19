import Foundation

@main
struct PunchPlaybackChecks {
    static func main() {
        for kind in [PunchKind.jab, .cross] {
            var punch = PunchPlayback()
            precondition(punch.start(kind))
            let other: PunchKind = kind == .jab ? .cross : .jab
            precondition(!punch.start(other) && punch.kind == kind)
            precondition(!punch.start(kind))
            let contactTime = Double(kind.contactFrame) * kind.frameDuration
            precondition(!punch.advance(contactTime - 0.001).contact)
            precondition(punch.advance(0.001).contact)
            precondition(punch.frameIndex == kind.contactFrame)
            let untilRecovery = Double(kind.frameCount - 1 - kind.contactFrame) * kind.frameDuration
            precondition(!punch.advance(untilRecovery).contact)
            precondition(punch.frameIndex == kind.frameCount - 1 && punch.isActive)
            precondition(!punch.advance(kind.frameDuration - 0.001).completed)
            precondition(punch.advance(0.001).completed && !punch.isActive)
            precondition(!punch.advance(1).completed && !punch.isActive)
            precondition(punch.start(other), "Next distinct press may choose either punch")
            punch.cancel()

            _ = punch.start(kind)
            var contacts = 0
            for expected in 1..<kind.frameCount {
                let event = punch.step()
                if event.contact { contacts += 1 }
                precondition(punch.frameIndex == expected && !event.completed)
            }
            precondition(contacts == 1 && punch.step().completed)

            for fps in [30, 60, 120] {
                _ = punch.start(kind)
                var seen = Set([0])
                var contacts = 0
                var completions = 0
                for _ in 0..<fps {
                    let event = punch.advance(1.0 / Double(fps))
                    if punch.isActive { seen.insert(punch.frameIndex) }
                    if event.contact { contacts += 1 }
                    if event.completed { completions += 1 }
                }
                precondition(contacts == 1 && completions == 1)
                precondition(seen == Set(0..<kind.frameCount))
            }
            _ = punch.start(kind)
            let delayed = punch.advance(kind.duration + 0.1)
            precondition(delayed.contact && !delayed.completed && punch.isActive)
            precondition(punch.frameIndex == kind.frameCount - 1)
            precondition(punch.advance(kind.frameDuration).completed)
        }
        print("PASS: jab/cross timing, contact once, mutual exclusion, no queue, recovery, stepping and 30/60/120 fps")
    }
}
