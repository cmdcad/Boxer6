import Foundation

@main
struct PlayerGuardChecks {
    static func main() {
        var guardPose = GuardPlayback()
        guardPose.toggle()
        guardPose.advance(0.04)
        precondition(guardPose.frameIndex == 1 && !guardPose.isEffective)
        guardPose.advance(0.04)
        precondition(guardPose.frameIndex == 2 && !guardPose.isEffective)
        guardPose.advance(0.04)
        precondition(guardPose.isEffective)
        let blue = SpriteCanvasTransform(rootPosition: .zero,scaleX:0.32,scaleY:0.32)
        let orange = SpriteCanvasTransform(rootPosition:CGPoint(x:55,y:0),scaleX:-0.32,scaleY:0.32)
        let farBlue = SpriteCanvasTransform(rootPosition:CGPoint(x:-100,y:0),scaleX:0.32,scaleY:0.32)
        var tracker = PunchContactTracker()
        var health = FighterHealthState()
        var reaction = HitReactionPlayback()
        var recoil = BlockFeedbackPlayback()
        for (index,kind) in [PunchKind.jab,.cross].enumerated() {
            tracker.begin(kind,attackerID:.orange,attackID:index+1)
            let block = tracker.evaluate(kind,attacker:orange,defender:blue,
                geometry:PunchContactGeometry(),guardEffective:guardPose.isEffective)!
            precondition(block.result == .block)
            precondition(!health.receive(block) && health.blue.current == 100)
            precondition(!reaction.receive(block.result,from:kind))
            precondition(recoil.receive(block))
            precondition(!recoil.receive(block))
            precondition(guardPose.isEffective)
        }
        tracker.begin(.cross,attackerID:.orange,attackID:3)
        let miss=tracker.evaluate(.cross,attacker:orange,defender:farBlue,
            geometry:PunchContactGeometry(),guardEffective:true)!
        precondition(miss.result == .miss && !recoil.receive(miss))
        guardPose.cancel();recoil.cancel()
        guardPose.advance(1)
        precondition(!guardPose.isEffective && !recoil.isActive)
        guardPose.toggle();guardPose.advance(0.08)
        tracker.begin(.cross,attackerID:.orange,attackID:4)
        let hit=tracker.evaluate(.cross,attacker:orange,defender:blue,
            geometry:PunchContactGeometry(),guardEffective:guardPose.isEffective)!
        precondition(hit.result == .hit && health.receive(hit))
        precondition(health.blue.current == 90 && reaction.receive(hit.result,from:.cross))
        guardPose.cancel()
        precondition(tracker.hits == 1 && tracker.blocks == 2 && tracker.misses == 1)
        precondition(tracker.jabContacts+tracker.crossContacts == tracker.hits+tracker.blocks+tracker.misses)
        var movement = FootworkMotion()
        for _ in 0..<60 { movement.advance(duration:1.0/60,direction:1) }
        precondition(movement.velocity > 0)
        for _ in 0..<8 { movement.advance(duration:0.016,direction:0) }
        precondition(movement.velocity == 0)
        let resumed=movement.advance(duration:0.016,direction:1)
        precondition(resumed.reduce(0) { $0+$1.displacement } > 0)
        print("PASS:120ms shared guard, both incoming CPU BLOCKs/no damage/no hit reaction, recoil, guarded MISS, entry HIT, counter reconciliation and braking/resume")
    }
}
