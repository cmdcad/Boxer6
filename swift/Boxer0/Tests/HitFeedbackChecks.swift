import Foundation

@main
struct HitFeedbackChecks {
    static func near(_ actual: Double, _ expected: Double) {
        precondition(abs(actual - expected) < 1e-9)
    }

    static func main() {
        for kind in [PunchKind.jab, .cross] {
            var feedback = HitReactionPlayback()
            precondition(!feedback.receive(.miss, from: kind) && feedback.profile == nil)
            precondition(feedback.receive(.hit, from: kind))
            precondition(feedback.frameIndex == 0 && feedback.profile?.punch == kind)
            let profile = feedback.profile!
            near(feedback.emphasisAmount, profile.emphasisStrength)
            _ = feedback.advance(0.03)
            near(feedback.emphasisAmount, profile.emphasisStrength / 2)
            precondition(feedback.frameIndex == 0)
            let frozenAmount = feedback.emphasisAmount
            // No elapsed-time advancement is performed while paused.
            near(feedback.emphasisAmount, frozenAmount)
            precondition(!feedback.receive(.miss, from: kind == .jab ? .cross : .jab))
            near(feedback.emphasisAmount, frozenAmount)
            precondition(feedback.profile?.punch == kind)
            _ = feedback.advance(0.03)
            near(feedback.emphasisAmount, 0)
            precondition(feedback.frameIndex == 1)
            _ = feedback.advance(0.06)
            precondition(feedback.frameIndex == 2)
            _ = feedback.advance(0.06)
            precondition(feedback.frameIndex == 3 && feedback.isActive)
            precondition(feedback.advance(0.06) && feedback.clip == .idle)
            precondition(feedback.profile == nil)
            near(feedback.emphasisAmount, 0)
        }
        precondition(HitFeedbackProfile(punch: .cross).emphasisStrength > HitFeedbackProfile(punch: .jab).emphasisStrength)
        near(HitFeedbackProfile(punch: .cross).emphasisDuration, 0.06)
        near(HitFeedbackProfile(punch: .jab).emphasisDuration, 0.06)
        var restarted = HitReactionPlayback()
        _ = restarted.receive(.hit, from: .cross)
        _ = restarted.advance(0.035)
        _ = restarted.receive(.hit, from: .jab)
        precondition(restarted.frameIndex == 0 && restarted.profile?.punch == .jab)
        near(restarted.emphasisAmount, HitFeedbackProfile(punch: .jab).emphasisStrength)
        _ = restarted.step()
        near(restarted.emphasisAmount, 0)
        _ = restarted.receive(.hit, from: .cross)
        restarted.cancel()
        near(restarted.emphasisAmount, 0)
        precondition(restarted.profile == nil && restarted.clip == .idle)
        print("PASS: jab/cross profiles, immediate emphasis, 60 ms decay, unchanged 240 ms four-pose recovery, MISS immunity, restart/step/cancel and tint cleanup state")
    }
}
