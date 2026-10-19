import Foundation

@main
struct HealthDamageChecks {
    static func main() {
        let transform = SpriteCanvasTransform(rootPosition: .zero, scaleX: 1, scaleY: 1)
        func event(_ sequence: Int, _ kind: PunchKind, _ result: PunchContactResult) -> PunchContactEvent {
            return PunchContactEvent(sequence: sequence, kind: kind, result: result,
                center: .zero, radius: 20, target: .zero,
                attacker: transform, defender: transform)
        }
        var health = FighterHealthState()
        precondition(health.blue.current == 100 && health.orange.current == 100)
        let cases: [(PunchKind, PunchContactResult, Int)] = [
            (.jab, .hit, 95), (.cross, .hit, 85), (.jab, .miss, 85),
            (.cross, .miss, 85), (.jab, .hit, 80)]
        for (index, item) in cases.enumerated() {
            let contact = event(index + 1, item.0, item.1)
            health.receive(contact)
            precondition(health.orange.current == item.2)
            precondition(!health.receive(contact)) // replay/pause/step cannot double damage
            precondition(health.orange.current == item.2)
        }
        health.reset()
        precondition(health.blue.current == 100 && health.orange.current == 100)
        precondition(!health.receive(event(5, .jab, .hit))) // reset retains watermark
        precondition(health.orange.current == 100)
        for sequence in 6...25 { health.receive(event(sequence, .cross, .hit)) }
        precondition(health.orange.current == 0 && health.blue.current == 100)
        health.receive(event(26, .jab, .hit))
        precondition(health.orange.current == 0)
        var fighter = FighterHealth()
        fighter.applyDamage(-10)
        precondition(fighter.current == 100)
        fighter.applyDamage(95)
        fighter.applyDamage(10)
        precondition(fighter.current == 0)
        fighter.reset()
        fighter.applyDamage(Int.max)
        precondition(fighter.current == 0)

        // Exercise real tracker ownership and spatial HIT/MISS, including replay.
        var tracker = PunchContactTracker()
        var integrated = FighterHealthState()
        tracker.begin(.jab)
        let hit = tracker.evaluate(.jab, attacker: transform, defender: transform,
            geometry: PunchContactGeometry(defenderTarget: CGRect(x: 350, y: 160, width: 60, height: 60)))!
        precondition(hit.result == .hit)
        integrated.receive(hit)
        precondition(integrated.orange.current == 95)
        precondition(tracker.evaluate(.jab, attacker: transform, defender: transform,
            geometry: PunchContactGeometry()) == nil)
        precondition(!integrated.receive(hit))
        tracker.finish()
        tracker.begin(.cross)
        let miss = tracker.evaluate(.cross, attacker: transform, defender: transform,
            geometry: PunchContactGeometry(defenderTarget: CGRect(x: 0, y: 0, width: 10, height: 10)))!
        precondition(miss.result == .miss)
        integrated.receive(miss)
        precondition(integrated.orange.current == 95)
        precondition(tracker.jabContacts + tracker.crossContacts == tracker.hits + tracker.misses)
        print("PASS: health sequence 100/95/85/85/85/80/reset100; clamping; duplicate suppression; real HIT/MISS tracker integration")
    }
}
