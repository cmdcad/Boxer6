import Foundation

@main
struct HitReactionChecks {
    static func main() {
        var reaction = HitReactionPlayback()
        precondition(!reaction.receive(.miss) && reaction.clip == .idle)
        precondition(reaction.receive(.hit) && reaction.frameIndex == 0)
        precondition(!reaction.advance(0.059) && reaction.frameIndex == 0)
        precondition(!reaction.advance(0.001) && reaction.frameIndex == 1)
        precondition(!reaction.advance(0.06) && reaction.frameIndex == 2)
        precondition(!reaction.receive(.miss) && reaction.frameIndex == 2)
        precondition(reaction.receive(.hit) && reaction.frameIndex == 0, "New HIT restarts, no queue")
        for expected in 1...3 {
            precondition(!reaction.advance(0.06) && reaction.frameIndex == expected)
        }
        precondition(reaction.advance(0.06) && reaction.clip == .idle && reaction.frameIndex == 0)
        precondition(!reaction.advance(1) && !reaction.isActive)

        _ = reaction.receive(.hit)
        _ = reaction.advance(0.025)
        precondition(!reaction.step() && reaction.frameIndex == 1)
        precondition(!reaction.step() && reaction.frameIndex == 2)
        precondition(!reaction.step() && reaction.frameIndex == 3)
        precondition(reaction.step() && !reaction.isActive)
        _ = reaction.receive(.hit)
        reaction.cancel()
        precondition(reaction.clip == .idle)

        let rates = [30,60,120]
        for kind in [PunchKind.jab, .cross] {
            for fps in rates {
                for result in [PunchContactResult.hit, .miss] {
                    var punch = PunchPlayback()
                    var orange = HitReactionPlayback()
                    _ = punch.start(kind)
                    var received = 0
                    var reactionSeen = Set<Int>()
                    for _ in 0..<fps {
                        // Same synchronization contract as the render loop:
                        // advance old orange time, then deliver this tick's contact.
                        _ = orange.advance(1.0 / Double(fps))
                        let event = punch.advance(1.0 / Double(fps), preserveContactPose: true)
                        if event.contact {
                            received += 1
                            precondition(punch.frameIndex == kind.contactFrame)
                            _ = orange.receive(result)
                            if result == .hit {
                                precondition(orange.isActive && orange.frameIndex == 0,
                                             "Reaction frame 1 must coincide with punch contact")
                            } else {
                                precondition(orange.clip == .idle)
                            }
                        }
                        if orange.isActive { reactionSeen.insert(orange.frameIndex) }
                    }
                    precondition(received == 1 && !orange.isActive && !punch.isActive)
                    if result == .hit { precondition(reactionSeen == Set(0..<4)) }
                }
            }
            // Catch-up must not render recoil against an already withdrawn punch.
            var delayed = PunchPlayback()
            _ = delayed.start(kind)
            let event = delayed.advance(kind.duration, preserveContactPose: true)
            precondition(event.contact && delayed.frameIndex == kind.contactFrame)
            _ = reaction.receive(.hit)
            precondition(reaction.frameIndex == 0)
        }
        print("PASS: 240 ms reaction, frame order, restart/no queue, MISS immunity, step/cancel, same-tick jab/cross contact+reaction at 30/60/120 fps and delayed ticks")
    }
}
