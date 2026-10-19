import Foundation

@main
struct BlockFeedbackChecks {
    static func main() {
        let transform = SpriteCanvasTransform(rootPosition: .zero, scaleX: -0.32, scaleY: 0.32)
        func event(_ sequence: Int, _ kind: PunchKind, _ result: PunchContactResult) -> PunchContactEvent {
            PunchContactEvent(sequence: sequence, kind: kind, result: result,
                center: .zero, radius: 6, target: .zero, attacker: transform, defender: transform)
        }
        var recoil = BlockFeedbackPlayback()
        precondition(!recoil.receive(event(1,.jab,.hit)))
        precondition(!recoil.receive(event(2,.cross,.miss)))
        for (index,kind) in [PunchKind.jab,.cross].enumerated() {
            let contact=event(index+3,kind,.block)
            precondition(recoil.receive(contact))
            precondition(recoil.frameIndex==0)
            precondition(recoil.profile.duration == (kind == .jab ? 0.12 : 0.16))
            let interval=recoil.frameDuration
            for frame in 0..<3 {
                precondition(recoil.frameIndex==frame && recoil.isActive)
                precondition(!recoil.receive(contact))
                recoil.advance(0) // paused clock
                recoil.advance(interval-0.001)
                precondition(recoil.frameIndex==frame && recoil.isActive)
                recoil.advance(0.001)
            }
            precondition(!recoil.isActive && recoil.label=="OFF")
        }
        recoil.receive(event(5,.jab,.block))
        recoil.advance(0.04)
        precondition(recoil.frameIndex==1)
        recoil.receive(event(6,.cross,.block))
        precondition(recoil.kind == .cross && recoil.frameIndex==0)
        precondition(!recoil.receive(event(7,.cross,.miss)))
        for frame in 1...2 {
            recoil.advance(0.25)
            precondition(recoil.isActive && recoil.frameIndex==frame)
        }
        recoil.advance(0.25)
        precondition(!recoil.isActive)
        recoil.receive(event(8,.jab,.block))
        recoil.cancel()
        precondition(!recoil.receive(event(8,.jab,.block)))
        recoil.advance(1)
        precondition(!recoil.isActive)
        print("PASS: BLOCK-only, ordered120/160ms recoil, pause, duplicate suppression, replacement, MISS unchanged, visible recovery under hitch, cancel and stale-event rejection")
    }
}
