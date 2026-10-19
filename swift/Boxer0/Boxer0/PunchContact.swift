import Foundation

/// Top-left image coordinates to axis-aligned SpriteKit scene coordinates.
/// Signed scaleX handles mirroring. rootInImage comes from the sprite anchor.
struct SpriteCanvasTransform {
    var rootPosition: CGPoint
    var scaleX: CGFloat
    var scaleY: CGFloat
    var rootInImage = CGPoint(x: 256, y: 448)

    func scenePoint(fromImage point: CGPoint) -> CGPoint {
        CGPoint(x: rootPosition.x + (point.x - rootInImage.x) * scaleX,
                y: rootPosition.y + (rootInImage.y - point.y) * scaleY)
    }

    func sceneRect(fromImage rect: CGRect) -> CGRect {
        let a = scenePoint(fromImage: CGPoint(x: rect.minX, y: rect.minY))
        let b = scenePoint(fromImage: CGPoint(x: rect.maxX, y: rect.maxY))
        return CGRect(x: min(a.x, b.x), y: min(a.y, b.y),
                      width: abs(b.x - a.x), height: abs(b.y - a.y))
    }

    func sceneRadius(fromImage radius: CGFloat) -> CGFloat {
        // Current fighters use uniform scaling. Under non-uniform scaling use
        // the smaller axis, keeping the provisional circle inside the glove.
        max(0, radius) * min(abs(scaleX), abs(scaleY))
    }
}

enum PunchContactResult: String {
    case hit = "HIT"
    case miss = "MISS"
}

struct PunchContactGeometry {
    // Provisional config derived from generated SVG ellipse centers + transforms.
    // These are not artist-authored sprite-contract metadata.
    var jabCenter = CGPoint(x: 384.5, y: 189)
    var crossCenter = CGPoint(x: 378, y: 186)
    var jabRadius: CGFloat = 20
    var crossRadius: CGFloat = 18
    // One upper-body rectangle spanning head/torso; excludes gloves and padding.
    var defenderTarget = CGRect(x: 220, y: 127, width: 88, height: 173)

    func center(for kind: PunchKind) -> CGPoint { kind == .jab ? jabCenter : crossCenter }
    func radius(for kind: PunchKind) -> CGFloat { kind == .jab ? jabRadius : crossRadius }

    static func intersects(center: CGPoint, radius: CGFloat, target: CGRect) -> Bool {
        guard !target.isEmpty, radius >= 0 else { return false }
        let x = min(max(center.x, target.minX), target.maxX)
        let y = min(max(center.y, target.minY), target.maxY)
        let dx = center.x - x
        let dy = center.y - y
        return dx * dx + dy * dy <= radius * radius + 1e-10
    }
}

struct PunchContactEvent {
    let sequence: Int
    let kind: PunchKind
    let result: PunchContactResult
    let center: CGPoint
    let radius: CGFloat
    let target: CGRect
}

/// Receives contact markers, never render-frame polling. One evaluation per
/// accepted punch, independent of pause, repeated markers or frame stepping.
struct PunchContactTracker {
    private(set) var jabContacts = 0
    private(set) var crossContacts = 0
    private(set) var hits = 0
    private(set) var misses = 0
    private(set) var latest: PunchContactEvent?
    private var sequence = 0
    private var activeKind: PunchKind?
    private var evaluated = false

    mutating func begin(_ kind: PunchKind) {
        sequence += 1
        activeKind = kind
        evaluated = false
    }

    mutating func finish() { activeKind = nil }

    @discardableResult
    mutating func evaluate(_ kind: PunchKind, attacker: SpriteCanvasTransform,
                           defender: SpriteCanvasTransform, geometry: PunchContactGeometry) -> PunchContactEvent? {
        guard let activeKind = activeKind, activeKind == kind, !evaluated else { return nil }
        evaluated = true
        let center = attacker.scenePoint(fromImage: geometry.center(for: kind))
        let radius = attacker.sceneRadius(fromImage: geometry.radius(for: kind))
        let target = defender.sceneRect(fromImage: geometry.defenderTarget)
        let result: PunchContactResult = PunchContactGeometry.intersects(center: center, radius: radius, target: target) ? .hit : .miss
        let event = PunchContactEvent(sequence: sequence, kind: kind, result: result,
                                      center: center, radius: radius, target: target)
        if kind == .jab { jabContacts += 1 } else { crossContacts += 1 }
        if result == .hit { hits += 1 } else { misses += 1 }
        latest = event
        return event
    }
}
