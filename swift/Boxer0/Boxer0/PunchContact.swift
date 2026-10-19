import Foundation
import CoreGraphics
import UIKit

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
    case block = "BLOCK"
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

    static func nearestPoint(to center: CGPoint, on target: CGRect) -> CGPoint {
        CGPoint(x: min(max(center.x, target.minX), target.maxX),
                y: min(max(center.y, target.minY), target.maxY))
    }

    static func distance(center: CGPoint, target: CGRect) -> CGFloat {
        let nearest = nearestPoint(to: center, on: target)
        return hypot(center.x - nearest.x, center.y - nearest.y)
    }

    static func intersects(center: CGPoint, radius: CGFloat, target: CGRect) -> Bool {
        guard !target.isEmpty, radius >= 0 else { return false }
        return distance(center: center, target: target) <= radius + 1e-10
    }

}

struct PunchContactEvent {
    let sequence: Int
    let kind: PunchKind
    let result: PunchContactResult
    let center: CGPoint
    let radius: CGFloat
    let target: CGRect
    let attacker: SpriteCanvasTransform
    let defender: SpriteCanvasTransform
    var centerDistance: CGFloat { PunchContactGeometry.distance(center: center, target: target) }
    // <=0 means intersection; >0 means actual separation between circle and target.
    var signedGap: CGFloat { centerDistance - radius }
}

/// Uses the SAME rendered transforms as contact evaluation, not a parallel
/// layout-scale estimate. Texture logical size cannot make reach impossible.
struct FighterSpacing {
    var bodyBounds = CGRect(x: 220, y: 183, width: 88, height: 117)
    var visibleBounds = CGRect(x: 149, y: 0, width: 249, height: 512)
    var minimumBodyGapFactor: CGFloat = 0.8

    func horizontalLimits(attacker: SpriteCanvasTransform, defender: SpriteCanvasTransform,
                          sceneWidth: CGFloat, edgePadding: CGFloat) -> ClosedRange<CGFloat> {
        let aBody = attacker.sceneRect(fromImage: bodyBounds)
        let bBody = defender.sceneRect(fromImage: bodyBounds)
        let aVisible = attacker.sceneRect(fromImage: visibleBounds)
        let rightOffset = aBody.maxX - attacker.rootPosition.x
        let visibleLeft = aVisible.minX - attacker.rootPosition.x
        let visibleRight = aVisible.maxX - attacker.rootPosition.x
        let gap = max(aBody.width, bBody.width) * max(0, minimumBodyGapFactor)
        let lower = edgePadding - visibleLeft
        let upper = min(bBody.minX - gap - rightOffset,
                        sceneWidth - edgePadding - visibleRight)
        return lower...max(lower, upper)
    }
}

/// Receives contact markers, never render-frame polling. One evaluation per
/// accepted punch, independent of pause, repeated markers or frame stepping.
struct PunchContactTracker {
    private(set) var jabContacts = 0
    private(set) var crossContacts = 0
    private(set) var hits = 0
    private(set) var misses = 0
    private(set) var blocks = 0
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
                           defender: SpriteCanvasTransform, geometry: PunchContactGeometry, guardEffective: Bool = false) -> PunchContactEvent? {
        guard let activeKind = activeKind, activeKind == kind, !evaluated else { return nil }
        evaluated = true
        let center = attacker.scenePoint(fromImage: geometry.center(for: kind))
        let radius = attacker.sceneRadius(fromImage: geometry.radius(for: kind))
        let target = defender.sceneRect(fromImage: geometry.defenderTarget)
        let overlaps = PunchContactGeometry.intersects(center: center, radius: radius, target: target)
        let result: PunchContactResult = !overlaps ? .miss : (guardEffective ? .block : .hit)
        let event = PunchContactEvent(sequence: sequence, kind: kind, result: result,
                                      center: center, radius: radius, target: target,
                                      attacker: attacker, defender: defender)
        if kind == .jab { jabContacts += 1 } else { crossContacts += 1 }
        switch result {
        case .hit: hits += 1
        case .block: blocks += 1
        case .miss: misses += 1
        }
        latest = event
        return event
    }
}

// Task 6A gameplay state. Kept with contact types to preserve target membership.
struct FighterHealth {
    let maximum = 100
    private(set) var current = 100
    mutating func applyDamage(_ amount: Int) {
        current -= min(current, max(0, amount))
    }
    mutating func reset() { current = maximum }
}

enum PunchDamage {
    static let jab = 5
    static let cross = 10
    static func amount(for kind: PunchKind) -> Int {
        return kind == .jab ? jab : cross
    }
}

enum FighterCombatState: String {
    case standing
    case defeated
}

/// Combat eligibility is independent of animation frame/clip selection.
struct FighterCombatStatus {
    private(set) var state: FighterCombatState = .standing
    private(set) var defeatRecorded = false

    @discardableResult
    mutating func receiveHealth(_ health: FighterHealth) -> Bool {
        guard state == .standing, health.current == 0 else { return false }
        state = .defeated
        defeatRecorded = true
        return true
    }

    mutating func reset() {
        state = .standing
        defeatRecorded = false
    }
}

struct FighterHealthState {
    private(set) var blue = FighterHealth()
    private(set) var orange = FighterHealth()
    private(set) var blueCombat = FighterCombatStatus()
    private(set) var orangeCombat = FighterCombatStatus()
    var canExchangePunches: Bool {
        blueCombat.state == .standing && orangeCombat.state == .standing
    }
    private var lastContactSequence = 0

    // Tracker sequences are monotonic for this scene. Resetting health must
    // retain this watermark so replaying an old event cannot damage again.
    @discardableResult
    mutating func receive(_ event: PunchContactEvent) -> Bool {
        guard canExchangePunches else { return false }
        guard event.sequence > lastContactSequence else { return false }
        lastContactSequence = event.sequence
        guard event.result == .hit else { return false }
        orange.applyDamage(PunchDamage.amount(for: event.kind))
        orangeCombat.receiveHealth(orange)
        return true
    }

    /// Debug recovery policy: only orange is restored, only after visual completion.
    /// Retains accepted-contact watermark and all scene diagnostics.
    @discardableResult
    mutating func recoverOrange() -> Bool {
        guard orangeCombat.state == .defeated else { return false }
        orange.reset()
        orangeCombat.reset()
        return true
    }

    mutating func reset() {
        blue.reset()
        orange.reset()
        blueCombat.reset()
        orangeCombat.reset()
    }
}
