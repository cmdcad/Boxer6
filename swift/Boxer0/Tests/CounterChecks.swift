import Foundation

@main
struct CounterChecks {
    static func main() {
        let blue = SpriteCanvasTransform(rootPosition:.zero,scaleX:0.32,scaleY:0.32)
        let orange = SpriteCanvasTransform(rootPosition:CGPoint(x:55,y:0),scaleX:-0.32,scaleY:0.32)
        let far = SpriteCanvasTransform(rootPosition:CGPoint(x:500,y:0),scaleX:-0.32,scaleY:0.32)
        var tracker=PunchContactTracker()
        var health=FighterHealthState()
        tracker.begin(.jab,attackerID:.blue,attackID:1,counterAttempt:true)
        let hit=tracker.evaluate(.jab,attacker:blue,defender:orange,geometry:PunchContactGeometry())!
        precondition(hit.isCounterAttempt && hit.isSuccessfulCounter && health.receive(hit))
        precondition(health.orange.current==95 && tracker.successfulCounters==1)
        precondition(tracker.evaluate(.jab,attacker:blue,defender:orange,geometry:PunchContactGeometry())==nil)
        tracker.begin(.cross,attackerID:.blue,attackID:2,counterAttempt:true)
        let miss=tracker.evaluate(.cross,attacker:blue,defender:far,geometry:PunchContactGeometry())!
        precondition(miss.result == .miss && !miss.isSuccessfulCounter && !health.receive(miss))
        tracker.begin(.jab,attackerID:.blue,attackID:3,counterAttempt:true)
        let block=tracker.evaluate(.jab,attacker:blue,defender:orange,geometry:PunchContactGeometry(),guardEffective:true)!
        precondition(block.result == .block && !block.isSuccessfulCounter && !health.receive(block))
        tracker.begin(.cross,attackerID:.blue,attackID:4,counterAttempt:true)
        tracker.finish() // canceled attempt stays an attempt, creates no outcome
        precondition(tracker.counterAttempts==4 && tracker.successfulCounters==1)
        tracker.begin(.jab,attackerID:.blue,attackID:5,counterAttempt:false)
        let ordinary=tracker.evaluate(.jab,attacker:blue,defender:orange,geometry:PunchContactGeometry())!
        precondition(!ordinary.isCounterAttempt && !ordinary.isSuccessfulCounter)
        precondition(tracker.jabContacts+tracker.crossContacts==tracker.hits+tracker.blocks+tracker.misses)
        precondition(tracker.successfulCounters<=tracker.counterAttempts && tracker.successfulCounters<=tracker.hits)
        for kind in [PunchKind.jab,.cross] {
            var punch=PunchPlayback();var recovery=PunchRecovery()
            punch.start(kind);recovery.begin(kind)
            let ticks=kind == .jab ? 42 : 70
            for tick in 1...ticks {
                precondition(punch.isActive || recovery.isRecovering)
                recovery.advance(0.01)
                let event=punch.advance(0.01)
                if event.completed { recovery.completeAttack() }
                if tick==ticks { precondition(!punch.isActive && !recovery.isRecovering) }
            }
        }
        // Both legal contacts are snapshotted before simultaneous fatal impacts.
        var a=PunchContactTracker();var b=PunchContactTracker();var exchange=FighterHealthState()
        for n in 1...20 {
            a.begin(.jab,attackerID:.blue,attackID:n*2-1,counterAttempt:n==20)
            b.begin(.jab,attackerID:.orange,attackID:n*2,counterAttempt:n==20)
            let x=a.evaluate(.jab,attacker:blue,defender:orange,geometry:PunchContactGeometry())!
            let y=b.evaluate(.jab,attacker:orange,defender:blue,geometry:PunchContactGeometry())!
            precondition(exchange.receive(x,simultaneous:true))
            precondition(exchange.receive(y,simultaneous:true))
        }
        precondition(exchange.blue.current==0 && exchange.orange.current==0)
        precondition(exchange.blueCombat.defeatRecorded && exchange.orangeCombat.defeatRecorded)
        precondition(a.successfulCounters==1 && b.successfulCounters==1)
        var cpu=CPUOffense();cpu.counterOpportunityAttackChance=0
        cpu.advance(0.30,enabled:true,eligible:true,jabInRange:true,crossInRange:false,opponentVulnerable:true)
        precondition(cpu.state == .ready)
        cpu.counterOpportunityAttackChance=1
        cpu.advance(0.30,enabled:true,eligible:true,jabInRange:true,crossInRange:false,opponentVulnerable:true)
        precondition(cpu.state == .preparing && cpu.remaining==0.18)
        precondition(cpu.advance(0.18,enabled:true,eligible:true,jabInRange:false,crossInRange:false,opponentVulnerable:false) == .jab)
        print("PASS:counter snapshot/HIT-only success, normal damage, MISS/BLOCK/cancel accounting,420/700ms vulnerability, symmetric simultaneous fatal hits and gated CPU opportunity with unchanged prep")
    }
}
