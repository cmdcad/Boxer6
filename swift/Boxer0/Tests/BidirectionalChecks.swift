import Foundation

@main
struct BidirectionalChecks {
    static func main() {
        let blue = SpriteCanvasTransform(rootPosition: .zero,scaleX:0.32,scaleY:0.32)
        let orange = SpriteCanvasTransform(rootPosition:CGPoint(x:55,y:0),scaleX:-0.32,scaleY:0.32)
        let farBlue = SpriteCanvasTransform(rootPosition:CGPoint(x:-100,y:0),scaleX:0.32,scaleY:0.32)
        var blueTracker = PunchContactTracker()
        var orangeTracker = PunchContactTracker()
        var health = FighterHealthState()
        blueTracker.begin(.jab,attackerID:.blue,attackID:1,startTime:1)
        let jab = blueTracker.evaluate(.jab,attacker:blue,defender:orange,geometry:PunchContactGeometry())!
        precondition(jab.result == .hit && jab.defenderID == .orange)
        precondition(health.receive(jab) && !health.receive(jab))
        precondition(health.orange.current == 95 && health.blue.current == 100)
        orangeTracker.begin(.cross,attackerID:.orange,attackID:2,startTime:2)
        let cross = orangeTracker.evaluate(.cross,attacker:orange,defender:blue,geometry:PunchContactGeometry())!
        precondition(cross.result == .hit && cross.defenderID == .blue)
        precondition(health.receive(cross) && !health.receive(cross))
        precondition(health.blue.current == 90)
        precondition(orangeTracker.context?.contactEvaluated == true)
        orangeTracker.finish()
        precondition(orangeTracker.context?.completed == true)
        orangeTracker.begin(.jab,attackerID:.orange,attackID:3,startTime:3)
        let miss = orangeTracker.evaluate(.jab,attacker:orange,defender:farBlue,geometry:PunchContactGeometry())!
        precondition(miss.result == .miss && !health.receive(miss))
        precondition(health.blue.current == 90)
        precondition(orangeTracker.evaluate(.jab,attacker:orange,defender:blue,geometry:PunchContactGeometry()) == nil)
        precondition(blueTracker.jabContacts+blueTracker.crossContacts == blueTracker.hits+blueTracker.blocks+blueTracker.misses)
        precondition(orangeTracker.jabContacts+orangeTracker.crossContacts == orangeTracker.hits+orangeTracker.misses)
        for n in 4...12 {
            orangeTracker.begin(.cross,attackerID:.orange,attackID:n,startTime:Double(n))
            health.receive(orangeTracker.evaluate(.cross,attacker:orange,defender:blue,geometry:PunchContactGeometry())!)
        }
        precondition(health.blue.current == 0 && health.blueCombat.state == .defeated)
        var reaction = HitReactionPlayback()
        var fall = KnockdownPlayback()
        reaction.receive(.hit,from:.cross)
        for _ in 0..<4 { reaction.step() }
        precondition(!reaction.isActive)
        fall.start()
        for _ in 0..<8 { fall.step() }
        precondition(fall.clip == .down && health.blue.current == 0)
        fall.startRise()
        for _ in 0..<8 { if fall.step() { health.recoverBlue() } }
        precondition(health.blue.current == 100 && health.canExchangePunches)
        precondition(health.orange.current == 95) // blue Rise does not reset orange

        var ai = CPUOffense()
        precondition(ai.advance(0.30,enabled:true,eligible:true,jabInRange:true,crossInRange:false) == nil)
        precondition(ai.state == .preparing && ai.kind == .jab)
        precondition(ai.advance(0,enabled:true,eligible:true,jabInRange:false,crossInRange:false) == nil)
        precondition(ai.advance(0.18,enabled:true,eligible:true,jabInRange:false,crossInRange:false) == .jab)
        precondition(ai.state == .attacking) // range change cannot cancel preparation
        ai.disable()
        precondition(ai.state == .attacking) // CPU OFF lets active punch finish
        ai.finished()
        precondition(ai.remaining == 0.65)
        ai.advance(0.65,enabled:true,eligible:true,jabInRange:true,crossInRange:true)
        precondition(ai.state == .ready)
        ai.cancel(reseed:true)
        ai.advance(0.30,enabled:true,eligible:true,jabInRange:false,crossInRange:true)
        precondition(ai.kind == .cross)
        ai.advance(0.28,enabled:true,eligible:true,jabInRange:false,crossInRange:false)
        precondition(ai.state == .attacking)
        ai.finished();precondition(ai.remaining == 0.90)
        ai.cancel();precondition(ai.state == .ready)
        var selection = CPUOffense()
        var jabSelections = 0
        var crossSelections = 0
        for _ in 0..<100 {
            selection.advance(0.30,enabled:true,eligible:true,jabInRange:true,crossInRange:true)
            if selection.kind == .jab { jabSelections += 1 } else { crossSelections += 1 }
            selection.cancel()
        }
        precondition(jabSelections > crossSelections && crossSelections > 0)
        var clock = PunchPlayback()
        for kind in [PunchKind.jab, .cross] {
            precondition(clock.start(kind))
            var contacts = 0
            for frame in 1...kind.frameCount {
                let marker = clock.advance(kind.frameDuration)
                if marker.contact {
                    contacts += 1
                    precondition(frame == kind.contactFrame)
                }
            }
            precondition(contacts == 1 && !clock.isActive)
        }
        print("PASS: mirrored shared HIT/MISS, both health targets, deduplication/context/counters, blue defeat/Rise, CPU prep/range/disable/cooldowns/reset")
    }
}
