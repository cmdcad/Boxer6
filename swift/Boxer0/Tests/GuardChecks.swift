import Foundation

@main
struct GuardChecks {
    static func main() {
        var guardPose = GuardPlayback()
        precondition(guardPose.status == "OFF" && !guardPose.isEffective)
        guardPose.toggle()
        precondition(guardPose.state == .guarding && guardPose.frameIndex == 0)
        guardPose.advance(0.04)
        precondition(guardPose.frameIndex == 1 && !guardPose.isEffective)
        guardPose.advance(0.04)
        precondition(guardPose.frameIndex == 2 && !guardPose.isEffective)
        guardPose.advance(0.039)
        precondition(!guardPose.isEffective)
        guardPose.advance(0.001)
        precondition(guardPose.isEffective && guardPose.status == "ACTIVE")
        guardPose.advance(20)
        precondition(guardPose.frameIndex == 2 && guardPose.isEffective)
        guardPose.toggle()
        precondition(!guardPose.isSelected && !guardPose.isEffective)
        guardPose.toggle()
        guardPose.step()
        guardPose.step()
        precondition(!guardPose.isEffective)
        guardPose.step()
        precondition(guardPose.isEffective)
        guardPose.cancel()
        guardPose.advance(20)
        precondition(guardPose.status == "OFF") // no stale completion

        let transform = SpriteCanvasTransform(rootPosition: .zero, scaleX: 1, scaleY: 1)
        let far = SpriteCanvasTransform(rootPosition: CGPoint(x: 1000, y: 0), scaleX: 1, scaleY: 1)
        let geometry = PunchContactGeometry(defenderTarget: CGRect(x: 350, y: 160, width: 60, height: 60))
        var tracker = PunchContactTracker()
        var health = FighterHealthState()
        var reaction = HitReactionPlayback()
        let cases: [(PunchKind, Bool, Bool, PunchContactResult)] = [
            (.jab,false,false,.hit), (.cross,true,false,.block),
            (.jab,true,false,.block), (.cross,true,true,.miss)]
        for item in cases {
            tracker.begin(item.0)
            let event = tracker.evaluate(item.0, attacker: transform, defender: item.2 ? far : transform,
                geometry: geometry, guardEffective: item.1)!
            precondition(event.result == item.3)
            health.receive(event)
            let started = reaction.receive(event.result, from: event.kind)
            precondition(started == (event.result == .hit))
            precondition(health.orange.current == 95)
            precondition(tracker.evaluate(item.0, attacker: transform, defender: transform,
                geometry: geometry, guardEffective: item.1) == nil)
            tracker.finish()
        }
        precondition(tracker.jabContacts == 2 && tracker.crossContacts == 2)
        precondition(tracker.hits == 1 && tracker.blocks == 2 && tracker.misses == 1)
        precondition(tracker.jabContacts + tracker.crossContacts == tracker.hits + tracker.blocks + tracker.misses)
        // An entry HIT cancels selection and cannot later gain protection.
        guardPose.toggle()
        guardPose.step()
        tracker.begin(.cross)
        let entryHit = tracker.evaluate(.cross, attacker: transform, defender: transform,
            geometry: geometry, guardEffective: guardPose.isEffective)!
        precondition(entryHit.result == .hit)
        health.receive(entryHit)
        if entryHit.result == .hit { guardPose.cancel() }
        guardPose.advance(1)
        precondition(health.orange.current == 85 && !guardPose.isEffective)
        health.reset()
        guardPose.cancel()
        precondition(health.orange.current == 100 && guardPose.status == "OFF")
        print("PASS: 120ms entry/hold/off, stepping, no stale guard, spatial HIT/BLOCK/MISS, zero block damage/recoil, one outcome, counter invariant, entry HIT cancellation")
    }
}
