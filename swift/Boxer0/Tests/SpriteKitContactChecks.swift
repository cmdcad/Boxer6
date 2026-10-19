import Foundation
import SpriteKit

/// Run on macOS with SpriteKit; exercises the real scene-graph conversion,
/// not only the pure geometry equations.
@main
struct SpriteKitContactChecks {
    static func near(_ a: CGFloat, _ b: CGFloat) { precondition(abs(a-b) < 1e-7) }

    static func main() {
        let scene = SKScene(size: CGSize(width: 568, height: 186))
        let rootA = SKNode()
        let rootB = SKNode()
        scene.addChild(rootA); scene.addChild(rootB)
        let a = SKSpriteNode(color: .white, size: CGSize(width: 512, height: 512))
        let b = SKSpriteNode(color: .white, size: CGSize(width: 512, height: 512))
        a.anchorPoint = CGPoint(x: 0.5, y: 0.125)
        b.anchorPoint = a.anchorPoint
        rootA.addChild(a); rootB.addChild(b)
        rootA.position = CGPoint(x: 170, y: 41)
        rootB.position = CGPoint(x: 397, y: 41)
        let scales: [CGFloat] = [0.2, 0.32, 0.8]
        for scale in scales {
            rootA.xScale = scale; rootA.yScale = scale
            rootB.xScale = -scale; rootB.yScale = scale
            near(a.size.width, 512); near(b.size.width, 512)
            near(a.frame.width, b.frame.width)
            near(a.frame.height, b.frame.height)
            let aOrigin = a.convert(.zero, to: scene)
            let bOrigin = b.convert(.zero, to: scene)
            let aUnit = a.convert(CGPoint(x: 1, y: 0), to: scene)
            let bUnit = b.convert(CGPoint(x: 1, y: 0), to: scene)
            near(aUnit.x - aOrigin.x, scale)
            near(bUnit.x - bOrigin.x, -scale)
            let at = SpriteCanvasTransform(rootPosition: aOrigin, scaleX: scale, scaleY: scale)
            let bt = SpriteCanvasTransform(rootPosition: bOrigin, scaleX: -scale, scaleY: scale)
            let geometry = PunchContactGeometry()
            let limits = FighterSpacing().horizontalLimits(attacker: at, defender: bt, sceneWidth: 568, edgePadding: 20)
            rootA.position.x = limits.upperBound
            for kind in [PunchKind.jab, .cross] {
                let imagePoint = geometry.center(for: kind)
                let actualPoint = a.convert(CGPoint(x: imagePoint.x - 256, y: 448 - imagePoint.y), to: scene)
                let current = SpriteCanvasTransform(rootPosition: rootA.position, scaleX: scale, scaleY: scale)
                let expectedPoint = current.scenePoint(fromImage: imagePoint)
                near(actualPoint.x, expectedPoint.x); near(actualPoint.y, expectedPoint.y)
                let rect = bt.sceneRect(fromImage: geometry.defenderTarget)
                precondition(PunchContactGeometry.intersects(center: actualPoint,
                    radius: geometry.radius(for: kind) * scale, target: rect))
            }
        }
        print("PASS: real SpriteKit root/child sizes, uniform mirrored scale, canvas coordinates and close-range jab/cross contact")
    }
}
