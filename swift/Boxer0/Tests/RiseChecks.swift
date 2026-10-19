import Foundation

@main
struct RiseChecks {
    static func main() {
        let transform = SpriteCanvasTransform(rootPosition: .zero, scaleX: 1, scaleY: 1)
        var health = FighterHealthState()
        var playback = KnockdownPlayback()
        var sequence = 0
        func knockOut(_ health: inout FighterHealthState) {
            for _ in 0..<10 {
                sequence += 1
                let event = PunchContactEvent(sequence: sequence, kind: .cross, result: .hit,
                    center: .zero, radius: 20, target: .zero, attacker: transform, defender: transform)
                precondition(health.receive(event))
            }
        }
        precondition(!playback.startRise()) // standing
        for _ in 0..<2 { // another complete defeat is allowed after recovery
            knockOut(&health)
            precondition(health.orange.current == 0 && !health.canExchangePunches)
            precondition(playback.start())
            precondition(!playback.startRise()) // falling
            for _ in 0..<8 { precondition(!playback.step()) }
            precondition(playback.clip == .down)
            precondition(playback.startRise() && !playback.startRise())
            for frame in 0..<8 {
                precondition(playback.clip == .rise && playback.frameIndex == frame)
                precondition(!playback.startRise()) // no restart/queue
                precondition(health.orange.current == 0 && health.orangeCombat.state == .defeated)
                // No clock calls while paused: state/health cannot progress.
                precondition(!playback.advance(0))
                precondition(!playback.advance(0.099))
                precondition(playback.frameIndex == frame)
                let completed = playback.advance(0.001)
                precondition(completed == (frame == 7))
                if completed { precondition(health.recoverOrange()) }
            }
            precondition(playback.clip == .idle && health.orange.current == 100)
            precondition(health.blue.current == 100 && health.canExchangePunches)
            precondition(!health.orangeCombat.defeatRecorded)
            precondition(!playback.advance(10) && !health.recoverOrange())
        }
        for stage in 0..<8 { // reset during every possible rise frame
            playback.cancel()
            playback.start()
            for _ in 0..<8 { playback.step() }
            playback.startRise()
            for _ in 0..<stage { precondition(!playback.step()) }
            playback.cancel()
            health.reset()
            precondition(!playback.advance(10) && playback.clip == .idle)
            precondition(health.canExchangePunches && health.orange.current == 100)
        }
        playback.start()
        for _ in 0..<8 { playback.step() }
        playback.startRise()
        for frame in 1...7 {
            precondition(!playback.advance(0.25))
            precondition(playback.frameIndex == frame && playback.clip == .rise)
        }
        precondition(playback.step()) // explicit step completes final recovery
        precondition(!playback.step()) // no duplicate completion
        print("PASS: rise eligibility, eight 100ms frames/800ms, health only on completion, repeat-tap rejection, reset every frame, second defeat, hitch visibility and one-shot stepping completion")
    }
}
