import Foundation

@main
struct BlockFeedbackChecks {
    static func main() {
        let defender = SpriteCanvasTransform(rootPosition: CGPoint(x: 400,y: 100), scaleX: -0.32, scaleY: 0.32)
        func event(_ sequence: Int, _ kind: PunchKind, _ result: PunchContactResult) -> PunchContactEvent {
            PunchContactEvent(sequence: sequence, kind: kind, result: result,
                center: defender.scenePoint(fromImage: CGPoint(x: 303.5,y: 152)), radius: 6,
                target: .zero, attacker: defender, defender: defender)
        }
        var fx = BlockFeedbackPlayback()
        precondition(!fx.receive(event(1,.jab,.hit)) && !fx.isActive)
        precondition(!fx.receive(event(2,.cross,.miss)) && !fx.isActive)
        for (index,kind) in [PunchKind.jab,.cross].enumerated() {
            let contact = event(index+3,kind,.block)
            precondition(fx.receive(contact))
            precondition(fx.imageAnchor == CGPoint(x:303.5,y:152))
            precondition(fx.label == (kind == .jab ? "Jab" : "Cross"))
            let duration = kind == .jab ? 0.08 : 0.11
            precondition(fx.profile.duration == duration)
            let initialOpacity = fx.opacity
            fx.advance(duration/2)
            precondition(abs(fx.opacity-initialOpacity/2)<1e-9)
            precondition(!fx.receive(contact)) // same marker/render cannot restart
            precondition(abs(fx.elapsed-duration/2)<1e-9)
            fx.advance(0) // paused clock: no progress
            precondition(fx.isActive)
            fx.advance(duration/2)
            precondition(!fx.isActive && fx.label == "OFF" && fx.opacity == 0)
        }
        precondition(fx.crossProfile.radius > fx.jabProfile.radius)
        precondition(fx.crossProfile.opacity > fx.jabProfile.opacity)
        fx.receive(event(5,.jab,.block));fx.advance(0.04)
        precondition(fx.receive(event(6,.cross,.block)))
        precondition(fx.kind == .cross && fx.elapsed == 0) // replacement, no stacking/queue
        let beforeMiss = fx.elapsed
        precondition(!fx.receive(event(7,.jab,.miss)) && fx.elapsed == beforeMiss)
        fx.cancel() // release/reset/defeat/Rise cleanup
        precondition(!fx.isActive && fx.imageAnchor == .zero)
        precondition(!fx.receive(event(6,.cross,.block))) // reset cannot replay old event
        fx.advance(1)
        precondition(!fx.isActive)
        fx.receive(event(8,.jab,.block))
        fx.advance(0.05) // one existing jab-contact frame step
        precondition(fx.isActive)
        fx.advance(0.05)
        precondition(!fx.isActive)
        // Configurable presentation values do not require damage/contact changes.
        fx.jabProfile.duration = 0.10
        fx.receive(event(9,.jab,.block))
        fx.advance(0.09)
        precondition(fx.isActive)
        fx.advance(0.01)
        precondition(!fx.isActive)
        print("PASS: BLOCK-only, Jab80ms/Cross110ms, mirrored anchor, fade, duplicate suppression, restart without stacking, MISS unchanged, cancel/watermark, step and configurable duration")
    }
}
