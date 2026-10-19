import Foundation

@main
struct FootworkMotionChecks {
    static func near(_ actual: Double, _ expected: Double, _ label: String) {
        precondition(abs(actual - expected) < 1e-7, "\(label): \(actual) != \(expected)")
    }

    static func main() {
        var motion = FootworkMotion()
        let ramp = motion.advance(duration: 1.0 / 6.0, direction: 1)
        near(motion.velocity, 100, "maximum speed after acceleration")
        near(ramp.reduce(0) { $0 + $1.displacement }, 100.0 / 12.0, "acceleration distance")
        let braking = motion.advance(duration: 0.5, direction: 0)
        near(motion.velocity, 0, "neutral stops")
        near(braking.reduce(0) { $0 + $1.displacement }, (10000.0 - 4.0) / 1800.0, "stopping distance")

        _ = motion.advance(duration: 1, direction: 1)
        let firstReversal = motion.advance(duration: 0.05, direction: -1)
        near(motion.velocity, 55, "reversal brakes before changing sign")
        precondition(firstReversal.allSatisfy { $0.displacement > 0 })
        let crossing = motion.advance(duration: 0.2, direction: -1)
        precondition(crossing.first!.displacement > 0 && crossing.last!.displacement < 0)
        precondition(motion.velocity < 0)
        motion.stop()
        near(motion.velocity, 0, "boundary/focus/pause reset")
        _ = motion.advance(duration: 0.2, direction: 0)
        near(motion.velocity, 0, "stop remains stopped without fresh input")

        var reference: (Double, Double)?
        for fps in [30, 60, 120] {
            var sample = FootworkMotion()
            var position = 0.0
            // Neutral is used both for release and simultaneous direction holds.
            for (seconds, direction) in [(0.6, 1.0), (0.3, 0.0), (0.7, -1.0), (0.4, 1.0), (0.2, 0.0)] {
                for _ in 0..<Int((seconds * Double(fps)).rounded()) {
                    position += sample.advance(duration: 1 / Double(fps), direction: direction)
                        .reduce(0) { $0 + $1.displacement }
                    precondition(abs(sample.velocity) <= 100.000001)
                }
            }
            if let baseline = reference {
                near(position, baseline.0, "frame-rate independent position at \(fps) fps")
                near(sample.velocity, baseline.1, "frame-rate independent velocity at \(fps) fps")
            } else {
                reference = (position, sample.velocity)
            }
        }
        print("PASS: acceleration, braking distance, dead zone, reversal, stop reset, neutral, 30/60/120 fps")
    }
}
