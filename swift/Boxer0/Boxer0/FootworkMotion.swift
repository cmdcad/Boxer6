import Foundation

/// Pure horizontal locomotion; SpriteKit owns rendering and visible bounds.
struct FootworkMotion {
    struct Segment {
        let duration: Double
        let displacement: Double
    }

    var maximumSpeed: Double = 100
    var acceleration: Double = 600
    var deceleration: Double = 900
    var deadZone: Double = 2
    private(set) var velocity: Double = 0

    mutating func stop() { velocity = 0 }

    /// Integrate constant-acceleration legs exactly, splitting at target speed
    /// and zero crossings so reversals do not depend on the display frame rate.
    mutating func advance(duration: Double, direction: Double) -> [Segment] {
        guard duration > 0, duration.isFinite else { return [] }
        let input = direction > 0 ? 1.0 : (direction < 0 ? -1.0 : 0.0)
        let speed = max(0, maximumSpeed)
        var remaining = duration
        var result: [Segment] = []
        while remaining > 1e-10 {
            let braking = velocity != 0 && (input == 0 || velocity * input < 0)
            let target = braking ? 0 : input * speed
            let rate = max(1, braking ? deceleration : acceleration)
            let difference = target - velocity
            if abs(difference) < 1e-10 {
                result.append(Segment(duration: remaining, displacement: velocity * remaining))
                break
            }
            // Snap only the final <=2 points/s braking tail, never acceleration.
            if braking && abs(velocity) <= max(0, deadZone) {
                velocity = 0
                continue
            }
            let endpoint = braking ? (velocity > 0 ? max(0, deadZone) : -max(0, deadZone)) : target
            let timeToEndpoint = abs(endpoint - velocity) / rate
            let dt = min(remaining, timeToEndpoint)
            let signedRate = difference > 0 ? rate : -rate
            let nextVelocity = velocity + signedRate * dt
            result.append(Segment(duration: dt, displacement: (velocity + nextVelocity) * 0.5 * dt))
            velocity = nextVelocity
            remaining -= dt
            if dt >= timeToEndpoint {
                velocity = braking ? 0 : target
            }
        }
        return result
    }
}
