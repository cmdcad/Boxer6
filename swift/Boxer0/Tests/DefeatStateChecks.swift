import Foundation

@main
struct DefeatStateChecks {
    static func main() {
        let transform = SpriteCanvasTransform(rootPosition: .zero, scaleX: 1, scaleY: 1)
        func event(_ sequence: Int, _ kind: PunchKind, _ result: PunchContactResult = .hit) -> PunchContactEvent {
            PunchContactEvent(sequence: sequence, kind: kind, result: result,
                center: .zero, radius: 20, target: .zero, attacker: transform, defender: transform)
        }
        for kind in [PunchKind.jab, .cross] {
            var health = FighterHealthState()
            precondition(health.canExchangePunches)
            precondition(health.blueCombat.state == .standing && !health.blueCombat.defeatRecorded)
            let total = kind == .jab ? 20 : 10
            for sequence in 1...total {
                precondition(health.receive(event(sequence, kind)))
                precondition(health.orangeCombat.state == (sequence == total ? .defeated : .standing))
                precondition(health.orangeCombat.defeatRecorded == (sequence == total))
            }
            precondition(health.orange.current == 0 && !health.canExchangePunches)
            precondition(!health.receive(event(total, kind)))
            precondition(!health.receive(event(total + 1, .cross)))
            precondition(!health.receive(event(total + 2, .jab, .miss)))
            precondition(health.orange.current == 0 && health.orangeCombat.defeatRecorded)
            health.reset()
            precondition(health.orange.current == 100 && health.blue.current == 100)
            precondition(health.canExchangePunches && !health.orangeCombat.defeatRecorded)
            precondition(!health.receive(event(total, kind))) // stale accepted contact
            precondition(health.receive(event(total + 3, .jab)))
            precondition(health.orange.current == 95 && health.orangeCombat.state == .standing)
        }
        var zero = FighterHealth()
        zero.applyDamage(100)
        var combat = FighterCombatStatus()
        precondition(combat.receiveHealth(zero))
        precondition(!combat.receiveHealth(zero)) // transition recorded once
        combat.reset()
        precondition(!combat.defeatRecorded && combat.state == .standing)
        precondition(combat.receiveHealth(zero))

        // Final damage must not restart an existing reaction; it may finish.
        var health = FighterHealthState()
        for i in 1...9 { health.receive(event(i, .cross)) }
        var reaction = HitReactionPlayback()
        reaction.receive(.hit, from: .jab)
        reaction.step()
        precondition(reaction.frameIndex == 1)
        health.receive(event(10, .cross))
        if health.canExchangePunches { reaction.receive(.hit, from: .cross) }
        precondition(reaction.frameIndex == 1 && reaction.profile?.punch == .jab)
        while reaction.isActive { reaction.step() }
        precondition(reaction.frameIndex == 0 && health.orangeCombat.state == .defeated)
        health.reset()
        reaction.receive(.hit)
        reaction.cancel() // scene reset cancels any active reaction
        precondition(!reaction.isActive && reaction.frameIndex == 0)
        print("PASS: final Jab/Cross defeat, one transition, blocked damage, reset, stale contact rejection, existing reaction completion")
    }
}
