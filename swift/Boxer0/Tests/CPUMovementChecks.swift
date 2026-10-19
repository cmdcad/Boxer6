import Foundation

@main
struct CPUMovementChecks {
    static func main() {
        var policy = CPUDistanceController()
        let reach = 192.0
        let minimum = 174.4
        let band = policy.thresholds(reach: reach, minimum: minimum)
        precondition(band.close > minimum && band.preferred > band.close && band.far > band.preferred)
        policy.advance(0, separation: band.far+1, reach: reach, minimum: minimum)
        precondition(policy.intent == .advance)
        policy.advance(0.1, separation: minimum, reach: reach, minimum: minimum)
        precondition(policy.intent == .advance) //200ms sample interval
        policy.advance(0.1, separation: minimum, reach: reach, minimum: minimum)
        precondition(policy.intent == .retreat)
        policy.advance(0.2, separation: band.preferred, reach: reach, minimum: minimum)
        precondition(policy.intent == .hold)
        policy.reset()
        precondition(policy.intent == .hold)
        var motion = FootworkMotion()
        motion.maximumSpeed = policy.speed
        var x = 500.0
        for _ in 0..<120 {
            for segment in motion.advance(duration: 1.0/60, direction: -1) { x += segment.displacement }
            precondition(abs(motion.velocity) <= 65+1e-8)
        }
        precondition(x < 400 && motion.velocity == -65)
        for _ in 0..<60 { _ = motion.advance(duration:1.0/60,direction:0) }
        precondition(motion.velocity == 0)
        motion.stop();policy.reset()
        precondition(motion.velocity == 0 && policy.intent == .hold)
        print("PASS: reachable distance band,200ms decisions, hold, reused65pt/s analytic movement and stop/reset")
    }
}
