import Foundation

@main
struct DefensiveAIChecks {
    static func main() {
        var ai = DefensiveAI(seed: 42)
        precondition(!ai.enabled && ai.state == .idle)
        ai.observe(sequence: 1, kind: .jab, inRange: true, eligible: true)
        precondition(ai.state == .idle)
        ai.setEnabled(true)
        ai.jabProfile.reactionDelay = 0.10 // explicit slow profile tests late HIT
        ai.crossProfile.reactionDelay = 0.14
        ai.jabProfile.chance = 1
        ai.crossProfile.chance = 1
        ai.observe(sequence: 2, kind: .cross, inRange: false, eligible: true)
        precondition(ai.state == .idle)
        ai.observe(sequence: 3, kind: .jab, inRange: true, eligible: false)
        precondition(ai.state == .idle)
        ai.observe(sequence: 4, kind: .jab, inRange: true, eligible: true)
        precondition(ai.state == .reacting && ai.remaining == 0.1)
        precondition(ai.advance(0.04) == nil)
        let saved = ai.remaining
        ai.observe(sequence: 4, kind: .jab, inRange: true, eligible: true)
        ai.observe(sequence: 5, kind: .cross, inRange: true, eligible: true)
        precondition(ai.remaining == saved) // duplicate/second event cannot delay earliest
        precondition(ai.advance(0) == nil && ai.remaining == saved)
        precondition(ai.advance(0.06) == .raise)
        precondition(ai.state == .guarding)
        var guardPose = GuardPlayback()
        guardPose.toggle()
        guardPose.advance(0.05) // contact at150ms, activation at100ms
        precondition(!guardPose.isEffective) // late Jab remains HIT
        ai.cancel()
        guardPose.cancel()
        precondition(ai.state == .idle)
        // Hold extensions cannot exceed1.5s from first activation.
        ai.observe(sequence: 6, kind: .cross, inRange: true, eligible: true)
        precondition(ai.advance(0.14) == .raise)
        var elapsed = 0.0
        var sequence = 7
        while elapsed < 1.4 {
            precondition(ai.advance(0.1) == nil)
            elapsed += 0.1
            ai.observe(sequence: sequence, kind: .cross, inRange: true, eligible: true)
            sequence += 1
            precondition(ai.remaining <= 1.5-elapsed+1e-8)
        }
        precondition(ai.advance(0.1) == .release)
        precondition(ai.state == .idle)
        ai.setEnabled(false)
        precondition(ai.label == "OFF" && ai.advance(2) == nil)
        // Identical seed/event sequences make identical decisions.
        var a = DefensiveAI(seed: 777)
        var b = DefensiveAI(seed: 777)
        a.setEnabled(true); b.setEnabled(true)
        var attempts = 0
        for n in 1...100 {
            a.observe(sequence:n,kind:.jab,inRange:true,eligible:true)
            b.observe(sequence:n,kind:.jab,inRange:true,eligible:true)
            precondition(a.state == b.state)
            if a.state == .reacting { attempts += 1 }
            a.cancel(); b.cancel()
        }
        precondition(attempts > 30 && attempts < 90)
        // Tunable faster response uses the SAME guard model, not forced protection.
        ai.setEnabled(true); ai.crossProfile.reactionDelay = 0.1
        ai.observe(sequence:1000,kind:.cross,inRange:true,eligible:true)
        precondition(ai.advance(0.1) == .raise)
        guardPose.toggle();guardPose.advance(0.14)
        precondition(guardPose.isEffective)
        ai.cancel(reseed:true);guardPose.cancel()
        precondition(ai.state == .idle && !guardPose.isSelected)
        // Production defaults must allow both initial punches to be blocked.
        for kind in [PunchKind.jab, .cross] {
            var cpu = DefensiveAI()
            cpu.setEnabled(true)
            cpu.jabProfile.chance = 1
            cpu.crossProfile.chance = 1
            cpu.observe(sequence: 1, kind: kind, inRange: true, eligible: true)
            let delay = cpu.remaining
            precondition(cpu.advance(delay) == .raise)
            var posture = GuardPlayback()
            posture.toggle()
            let contactTime = Double(kind.contactFrame) * kind.frameDuration
            posture.advance(contactTime - delay)
            precondition(posture.isEffective)
        }
        print("PASS: default OFF, seeded event decisions, range/eligibility gating, earliest reaction, pause, late Jab, hold cap/release, mode/reset cancellation and normal guard activation")
    }
}
