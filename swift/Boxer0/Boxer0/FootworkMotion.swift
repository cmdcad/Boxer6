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

enum CPUMovementIntent: String { case advance, retreat, hold }

/// Distance policy only; FootworkMotion still owns all velocity integration.
struct CPUDistanceController {
    var speed = 65.0
    var decisionInterval = 0.20
    var preferredReachFactor = 0.90
    var tooFarFactor = 1.15
    var tooCloseFactor = 0.75
    var maximumRangeFactor: Double?
    private(set) var intent: CPUMovementIntent = .hold
    private var remaining = 0.0
    mutating func reset() { intent = .hold; remaining = 0 }
    func thresholds(reach: Double, minimum: Double) -> (close: Double, preferred: Double, far: Double) {
        // Keep retreat reachable above the physical body-spacing floor.
        let closeFloor = minimum + reach * 0.04
        let preferred = max(reach * preferredReachFactor, closeFloor + reach * 0.06)
        let close = max(preferred * tooCloseFactor, closeFloor)
        let far = maximumRangeFactor.map { max(close + reach * 0.02, min(preferred * tooFarFactor, reach * $0)) }
            ?? preferred * tooFarFactor
        return (close, min(preferred, far), far)
    }
    mutating func advance(_ dt: Double, separation: Double, reach: Double, minimum: Double) {
        guard dt.isFinite, dt >= 0 else { return }
        remaining -= dt
        guard remaining <= 1e-10 else { return }
        remaining += max(0.001, decisionInterval) * max(1, ceil(-remaining / max(0.001, decisionInterval)))
        let band = thresholds(reach: reach, minimum: minimum)
        if separation > band.far { intent = .advance }
        else if separation < band.close { intent = .retreat }
        else { intent = .hold }
    }
}
