import Foundation

@main
struct KnockdownChecks {
    static func main() {
        var fall = KnockdownPlayback()
        precondition(fall.start() && !fall.start())
        precondition(fall.clip == .knockdown && fall.frameIndex == 0)
        for frame in 0..<8 {
            precondition(fall.frameIndex == frame)
            fall.advance(0.079)
            precondition(fall.clip == .knockdown && fall.frameIndex == frame)
            fall.advance(0.001)
        }
        precondition(fall.clip == .down && !fall.start())
        fall.advance(10)
        fall.step()
        precondition(fall.clip == .down && fall.frameIndex == 0)
        fall.cancel()
        precondition(!fall.hasStarted && fall.clip == .idle)
        fall.start()
        for frame in 1...7 {
            fall.advance(0.25) // delayed ticks still display each successive pose
            precondition(fall.frameIndex == frame && fall.clip == .knockdown)
        }
        fall.advance(0.08)
        precondition(fall.clip == .down)
        for stage in 0...8 {
            fall.cancel()
            fall.start()
            for _ in 0..<stage { fall.step() }
            fall.cancel()
            precondition(fall.clip == .idle && !fall.hasStarted && fall.frameIndex == 0)
            fall.advance(10)
            precondition(fall.clip == .idle) // stale elapsed updates cannot restart
        }
        let transform = SpriteCanvasTransform(rootPosition: .zero, scaleX: 1, scaleY: 1)
        for kind in [PunchKind.jab, .cross] {
            var health = FighterHealthState()
            var reaction = HitReactionPlayback()
            fall.cancel()
            let count = kind == .jab ? 20 : 10
            for sequence in 1...count {
                let contact = PunchContactEvent(sequence: sequence, kind: kind, result: .hit,
                    center: .zero, radius: 20, target: .zero, attacker: transform, defender: transform)
                precondition(health.receive(contact))
                reaction.receive(contact.result, from: contact.kind)
            }
            precondition(health.orangeCombat.state == .defeated && health.orangeCombat.defeatRecorded)
            precondition(reaction.frameIndex == 0 && !fall.hasStarted)
            // Scene first completes recoil and starts fall zero without advancing it.
            for _ in 0..<4 { reaction.step() }
            precondition(!reaction.isActive)
            fall.start()
            precondition(fall.frameIndex == 0)
            for _ in 0..<8 { fall.step() }
            precondition(fall.clip == .down && health.orange.current == 0)
            health.reset()
            reaction.cancel()
            fall.cancel()
            precondition(health.canExchangePunches && !health.orangeCombat.defeatRecorded)
            precondition(fall.clip == .idle && reaction.clip == .idle)
        }
        print("PASS: eight ordered 80ms poses/640ms, hold, no restart, hitch visibility, reset at every fall stage, final Jab/Cross recoil-to-down")
    }
}
