import Foundation

@main
struct RecoveryChecks {
    static func main() {
        for kind in [PunchKind.jab,.cross] {
            var punch = PunchPlayback()
            var recovery = PunchRecovery()
            precondition(punch.start(kind))
            recovery.begin(kind)
            precondition(recovery.phase == .attacking)
            for _ in 0..<kind.frameCount {
                let event = punch.advance(kind.frameDuration)
                if event.completed { recovery.completeAttack() }
            }
            let duration = kind == .jab ? 0.12 : 0.22
            precondition(recovery.isRecovering && recovery.remaining == duration)
            recovery.completeAttack() // repeated completion cannot extend lock
            precondition(recovery.remaining == duration)
            precondition(!recovery.advance(0))
            precondition(!recovery.advance(duration-0.001))
            precondition(recovery.isRecovering)
            precondition(recovery.advance(0.001))
            precondition(recovery.phase == .ready && !recovery.advance(1))
            var guardPose = GuardPlayback()
            guardPose.toggle();guardPose.advance(0.12)
            precondition(guardPose.isEffective)
            let earliest = kind.duration+duration+0.12
            precondition(abs(earliest-(kind == .jab ? 0.54 : 0.82))<1e-9)
            recovery.begin(kind);recovery.completeAttack()
            recovery.cancel() // HIT/Reset/Rise invalidates old recovery
            precondition(!recovery.advance(10) && recovery.phase == .ready)
        }
        var tactical = CPUOffense()
        tactical.advance(0.30,enabled:true,eligible:true,jabInRange:true,crossInRange:false)
        tactical.advance(0.18,enabled:true,eligible:true,jabInRange:true,crossInRange:false)
        tactical.finished()
        var physical = PunchRecovery()
        physical.begin(.jab);physical.completeAttack()
        // Advance both clocks together; no sequential650+120ms delay.
        physical.advance(0.12)
        tactical.advance(0.12,enabled:true,eligible:false,jabInRange:true,crossInRange:false)
        precondition(physical.phase == .ready && abs(tactical.remaining-0.53)<1e-9)
        tactical.cancelPreparation() // defense must not erase tactical cooldown
        precondition(tactical.state == .cooldown && abs(tactical.remaining-0.53)<1e-9)
        tactical.advance(0.53,enabled:true,eligible:true,jabInRange:true,crossInRange:false)
        precondition(tactical.state == .ready)
        // Physical lock is independent of CPU mode.
        physical.begin(.cross);physical.completeAttack()
        tactical.disable()
        physical.advance(0.22)
        precondition(physical.phase == .ready)
        var recoil = BlockFeedbackPlayback()
        let transform=SpriteCanvasTransform(rootPosition:.zero,scaleX:1,scaleY:1)
        let block=PunchContactEvent(sequence:1,kind:.jab,result:.block,center:.zero,radius:20,target:.zero,attacker:transform,defender:transform)
        precondition(recoil.receive(block))
        var guardPose=GuardPlayback();guardPose.toggle();guardPose.advance(0.12)
        guardPose.cancel() // release removes protection, not physical response
        precondition(!guardPose.isEffective && recoil.isActive)
        for _ in 0..<3 { recoil.advance(0.04) }
        precondition(!recoil.isActive) // no extra cooldown
        print("PASS:420/700ms cycles,120/220ms locks,540/820ms earliest guard, pause/once-only/cancel, parallel CPU cooldown, mode independence, release during block response")
    }
}
