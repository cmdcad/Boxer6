import Foundation

@main
struct PunchContactChecks {
    static func near(_ actual: CGFloat, _ expected: CGFloat) {
        precondition(abs(actual - expected) < 1e-8)
    }

    static func main() {
        let geometry = PunchContactGeometry()
        let attacker = SpriteCanvasTransform(rootPosition: .zero, scaleX: 1, scaleY: 1)
        let root = attacker.scenePoint(fromImage: CGPoint(x: 256, y: 448))
        near(root.x, 0); near(root.y, 0)
        let glove = attacker.scenePoint(fromImage: geometry.jabCenter)
        near(glove.x, 128.5); near(glove.y, 259)
        let mirrored = SpriteCanvasTransform(rootPosition: CGPoint(x: 50, y: 10), scaleX: -0.5, scaleY: 0.5)
        let mirroredGlove = mirrored.scenePoint(fromImage: geometry.jabCenter)
        near(mirroredGlove.x, -14.25); near(mirroredGlove.y, 139.5)
        near(mirrored.sceneRadius(fromImage: 20), 10)
        let custom = SpriteCanvasTransform(rootPosition: CGPoint(x: 10, y: 20), scaleX: 0.5, scaleY: 0.5,
                                          rootInImage: CGPoint(x: 0, y: 512))
        let corner = custom.scenePoint(fromImage: CGPoint(x: 512, y: 0))
        near(corner.x, 266); near(corner.y, 276)

        let target = CGRect(x: 0, y: 0, width: 10, height: 10)
        precondition(PunchContactGeometry.intersects(center: CGPoint(x: 11, y: 10), radius: 1, target: target))
        precondition(!PunchContactGeometry.intersects(center: CGPoint(x: 11, y: 11), radius: 1, target: target))
        precondition(PunchContactGeometry.intersects(center: CGPoint(x: 5, y: 5), radius: 0, target: target))
        precondition(!PunchContactGeometry.intersects(center: .zero, radius: -1, target: target))

        var tracker = PunchContactTracker()
        let scales: [CGFloat] = [0.3, 0.5, 0.8, 1]
        for scale in scales {
            let a = SpriteCanvasTransform(rootPosition: CGPoint(x: 31, y: 17), scaleX: scale, scaleY: scale)
            for kind in [PunchKind.jab, .cross] {
                // Approved body spacing: 2*52 + 0.8*88 = 174.4 canvas units.
                let d = SpriteCanvasTransform(rootPosition: CGPoint(x: 31 + 174.4 * scale, y: 17), scaleX: -scale, scaleY: scale)
                tracker.begin(kind)
                let hit = tracker.evaluate(kind, attacker: a, defender: d, geometry: geometry)
                precondition(hit?.result == .hit && hit?.kind == kind)
                precondition(tracker.evaluate(kind, attacker: a, defender: d, geometry: geometry) == nil)
                tracker.finish()

                let far = SpriteCanvasTransform(rootPosition: CGPoint(x: 31 + 400 * scale, y: 17), scaleX: -scale, scaleY: scale)
                tracker.begin(kind)
                precondition(tracker.evaluate(kind, attacker: a, defender: far, geometry: geometry)?.result == .miss)
                tracker.finish()
                precondition(tracker.jabContacts + tracker.crossContacts == tracker.hits + tracker.misses)
            }
        }
        precondition(tracker.hits == 8 && tracker.misses == 8)
        let before = tracker.hits + tracker.misses
        tracker.begin(.jab)
        tracker.finish() // Scene canceled before contact.
        precondition(tracker.evaluate(.jab, attacker: attacker, defender: attacker, geometry: geometry) == nil)
        precondition(tracker.hits + tracker.misses == before)

        // Exact reach edge and mirrored attacking direction.
        let tangentDefender = SpriteCanvasTransform(rootPosition: CGPoint(x: 200.5, y: 0), scaleX: -1, scaleY: 1)
        tracker.begin(.jab)
        precondition(tracker.evaluate(.jab, attacker: attacker, defender: tangentDefender, geometry: geometry)?.result == .hit)
        let outside = SpriteCanvasTransform(rootPosition: CGPoint(x: 200.51, y: 0), scaleX: -1, scaleY: 1)
        tracker.begin(.jab)
        precondition(tracker.evaluate(.jab, attacker: attacker, defender: outside, geometry: geometry)?.result == .miss)
        let leftAttacker = SpriteCanvasTransform(rootPosition: .zero, scaleX: -1, scaleY: 1)
        let leftDefender = SpriteCanvasTransform(rootPosition: CGPoint(x: -180, y: 0), scaleX: 1, scaleY: 1)
        tracker.begin(.cross)
        precondition(tracker.evaluate(.cross, attacker: leftAttacker, defender: leftDefender, geometry: geometry)?.result == .hit)

        // Real rendered-canvas scaling, including a texture logical-size mismatch.
        // Old spacing assumed 512 pixels while contact used 256/512 of that scale.
        let spacing = FighterSpacing()
        let textureFactors: [CGFloat] = [0.5, 1, 2]
        for textureFactor in textureFactors {
            let actualScale: CGFloat = 0.32 * textureFactor
            let initialA = SpriteCanvasTransform(rootPosition: CGPoint(x: 170, y: 41), scaleX: actualScale, scaleY: actualScale)
            let actualB = SpriteCanvasTransform(rootPosition: CGPoint(x: 397, y: 41), scaleX: -actualScale, scaleY: actualScale)
            let limits = spacing.horizontalLimits(attacker: initialA, defender: actualB, sceneWidth: 568, edgePadding: 20)
            let closeA = SpriteCanvasTransform(rootPosition: CGPoint(x: limits.upperBound, y: 41), scaleX: actualScale, scaleY: actualScale)
            for kind in [PunchKind.jab, .cross] {
                tracker.begin(kind)
                let contact = tracker.evaluate(kind, attacker: closeA, defender: actualB, geometry: geometry)!
                precondition(contact.result == .hit && contact.signedGap <= 0)
                let maximumReach = kind == .jab ? CGFloat(200.5) : CGFloat(192)
                for (offset,expected) in [(CGFloat(50),PunchContactResult.miss), (CGFloat(0.1),.miss),
                                         (CGFloat(0),.hit), (CGFloat(-0.1),.hit), (CGFloat(-5),.hit)] {
                    let a = SpriteCanvasTransform(rootPosition: CGPoint(x: 397 - (maximumReach + offset) * actualScale, y: 41),
                                                  scaleX: actualScale, scaleY: actualScale)
                    tracker.begin(kind)
                    precondition(tracker.evaluate(kind, attacker: a, defender: actualB, geometry: geometry)?.result == expected)
                }
            }
        }
        // Reproduce the prior mixed-scale failure without changing hitboxes.
        let halfA = SpriteCanvasTransform(rootPosition: CGPoint(x: 397 - 174.4 * 0.32, y: 41), scaleX: 0.16, scaleY: 0.16)
        let halfB = SpriteCanvasTransform(rootPosition: CGPoint(x: 397, y: 41), scaleX: -0.16, scaleY: 0.16)
        for kind in [PunchKind.jab, .cross] {
            tracker.begin(kind)
            precondition(tracker.evaluate(kind, attacker: halfA, defender: halfB, geometry: geometry)?.result == .miss)
        }

        // Playback integration: marker entry, pause, step and repeated evaluation.
        for kind in [PunchKind.jab, .cross] {
            var punch = PunchPlayback()
            _ = punch.start(kind)
            tracker.begin(kind)
            let countBefore = tracker.hits + tracker.misses
            for _ in 1..<kind.frameCount {
                let event = punch.step()
                if event.contact {
                    _ = tracker.evaluate(kind, attacker: attacker, defender: tangentDefender, geometry: geometry)
                    _ = tracker.evaluate(kind, attacker: attacker, defender: tangentDefender, geometry: geometry)
                }
                precondition(tracker.hits + tracker.misses <= countBefore + 1)
            }
            precondition(tracker.hits + tracker.misses == countBefore + 1)
            _ = punch.step()
            tracker.finish()
        }
        precondition(tracker.jabContacts + tracker.crossContacts == tracker.hits + tracker.misses)
        print("PASS: coordinate flip/anchor/scale/mirroring, exact circle/rect contact, range edges, once-only results, cancellation, stepping and counter invariant")
    }
}
