//
//  IdleTestScene.swift
//  Boxer0
//
//  Task 2 idle playback plus Task 3A horizontal footwork for the blue boxer.
//

import SpriteKit
import UIKit

enum IdlePlaybackSpeed: Double, CaseIterable {
    case quarter = 0.25
    case normal = 1.0

    var label: String {
        switch self {
        case .quarter: return "1/4 speed"
        case .normal: return "1× speed"
        }
    }
}

enum FighterClip: String {
    case idle
    case advance
    case retreat

    var frameCount: Int { self == .idle ? 4 : 6 }

    var cycleDuration: TimeInterval {
        self == .idle ? 0.8 : 0.48
    }
}

final class IdleTestScene: SKScene {

    static let originAnchor = CGPoint(x: 0.5, y: 1.0 - 448.0 / 512.0)
    static let spriteCanvas: CGFloat = 512
    static let figureOriginX: CGFloat = 256
    // Conservative alpha bounds across all idle and footwork frames (including antialiasing).
    static let contentMinX: CGFloat = 149
    static let contentMaxX: CGFloat = 398
    static let edgePaddingPoints: CGFloat = 20
    static let minSeparationFactor: CGFloat = 0.22
    static let defaultMoveSpeed: CGFloat = 100

    var movementSpeed: CGFloat = IdleTestScene.defaultMoveSpeed
    var isPlaying = true
    var playbackSpeed: IdlePlaybackSpeed = .normal
    var showsGuides = true {
        didSet { applyGuideVisibility() }
    }
    var frameIndex = 0
    var activeClip: FighterClip = .idle
    var onPlaybackChange: (() -> Void)?

    private var boxerA: SKSpriteNode!
    private var boxerB: SKSpriteNode!
    private var idleA: [SKTexture] = []
    private var idleB: [SKTexture] = []
    private var advanceA: [SKTexture] = []
    private var retreatA: [SKTexture] = []
    private var groundLine: SKShapeNode!
    private var originA: SKShapeNode!
    private var originB: SKShapeNode!
    private var lastTime: TimeInterval = 0
    private var blueAccumulator: TimeInterval = 0
    private var orangeAccumulator: TimeInterval = 0
    private var orangeFrame = 0
    private var groundY: CGFloat = 0
    private var fighterScale: CGFloat = 1
    private var didInitialLayout = false
    private var blueXFraction: CGFloat = 0.30
    private var holdAdvance = false
    private var holdRetreat = false
    private var resignObserver: NSObjectProtocol?

    var bluePositionX: CGFloat { boxerA?.position.x ?? 0 }

    override func didMove(to view: SKView) {
        lastTime = 0
        backgroundColor = SKColor(red: 0.91, green: 0.933, blue: 0.957, alpha: 1)
        scaleMode = .resizeFill
        loadTextures()
        if boxerA == nil {
            buildNodes()
        }
        layoutFighters()
        applyFrames()
        applyGuideVisibility()
        observeAppFocus()
    }

    override func willMove(from view: SKView) {
        cancelMovement()
        if let resignObserver {
            NotificationCenter.default.removeObserver(resignObserver)
            self.resignObserver = nil
        }
    }

    override func didChangeSize(_ oldSize: CGSize) {
        super.didChangeSize(oldSize)
        guard boxerA != nil else { return }
        layoutFighters()
    }

    override func update(_ currentTime: TimeInterval) {
        guard boxerA != nil, boxerB != nil else {
            lastTime = 0
            return
        }
        if lastTime == 0 {
            lastTime = currentTime
            return
        }
        let dt = currentTime - lastTime
        lastTime = currentTime
        // Resume safely after a suspended render loop without changing nodes
        // from inside SpriteKit's inherited pause-property setter.
        guard dt >= 0, dt <= 0.25 else {
            cancelMovement()
            return
        }
        guard isPlaying else { return }

        resolveClip()
        animateBoxer(&blueAccumulator, frame: &frameIndex, clip: activeClip, speed: playbackSpeed.rawValue, dt: dt)
        animateBoxer(&orangeAccumulator, frame: &orangeFrame, clip: .idle, speed: playbackSpeed.rawValue, dt: dt)

        if let direction = movementDirection {
            boxerA.position.x += direction * movementSpeed * CGFloat(dt)
            clampBlue()
            blueXFraction = boxerA.position.x / max(size.width, 1)
            originA.position = boxerA.position
        }

        applyFrames()
        publishIfNeeded()
    }

    private var lastPublishedFrame = -1
    private var lastPublishedX: CGFloat = .nan
    private var lastPublishedClip: FighterClip?

    private func publishIfNeeded() {
        let x = boxerA.position.x
        if frameIndex != lastPublishedFrame
            || activeClip != lastPublishedClip
            || lastPublishedX.isNaN
            || abs(x - lastPublishedX) >= 1 {
            lastPublishedFrame = frameIndex
            lastPublishedClip = activeClip
            lastPublishedX = x
            onPlaybackChange?()
        }
    }

    func togglePlayback() {
        isPlaying.toggle()
        if isPlaying {
            lastTime = 0
        }
        onPlaybackChange?()
    }

    func stepFrame() {
        isPlaying = false
        blueAccumulator = 0
        frameIndex = (frameIndex + 1) % activeClip.frameCount
        orangeAccumulator = 0
        orangeFrame = (orangeFrame + 1) % FighterClip.idle.frameCount
        applyFrames()
        onPlaybackChange?()
    }

    func setSpeed(_ speed: IdlePlaybackSpeed) {
        playbackSpeed = speed
        onPlaybackChange?()
    }

    func toggleGuides() {
        showsGuides.toggle()
        onPlaybackChange?()
    }

    func setAdvanceHeld(_ held: Bool) {
        holdAdvance = held
        if !held && !holdRetreat {
            settleIdle()
        }
        resolveClip()
        applyFrames()
        onPlaybackChange?()
    }

    func setRetreatHeld(_ held: Bool) {
        holdRetreat = held
        if !held && !holdAdvance {
            settleIdle()
        }
        resolveClip()
        applyFrames()
        onPlaybackChange?()
    }

    func cancelMovement() {
        lastTime = 0
        holdAdvance = false
        holdRetreat = false
        settleIdle()
        applyFrames()
        onPlaybackChange?()
    }

    private var movementDirection: CGFloat? {
        if holdAdvance && !holdRetreat { return 1 }
        if holdRetreat && !holdAdvance { return -1 }
        return nil
    }

    private func settleIdle() {
        if activeClip != .idle {
            activeClip = .idle
            frameIndex = 0
            blueAccumulator = 0
        }
    }

    private func resolveClip() {
        let next: FighterClip
        if holdAdvance && !holdRetreat {
            next = .advance
        } else if holdRetreat && !holdAdvance {
            next = .retreat
        } else {
            next = .idle
        }
        if next != activeClip {
            activeClip = next
            frameIndex = 0
            blueAccumulator = 0
        }
    }

    private func animateBoxer(
        _ accumulator: inout TimeInterval,
        frame: inout Int,
        clip: FighterClip,
        speed: Double,
        dt: TimeInterval
    ) {
        let frameDuration = clip.cycleDuration / TimeInterval(clip.frameCount)
        accumulator += dt * speed
        while accumulator >= frameDuration {
            accumulator -= frameDuration
            frame = (frame + 1) % clip.frameCount
        }
    }

    private func loadTextures() {
        idleA = (0..<4).map { makeTexture(named: "idle_a_\($0)") }
        idleB = (0..<4).map { makeTexture(named: "idle_b_\($0)") }
        advanceA = (0..<6).map { makeTexture(named: "advance_a_\($0)") }
        retreatA = (0..<6).map { makeTexture(named: "retreat_a_\($0)") }
    }

    private func makeTexture(named name: String) -> SKTexture {
        let texture = SKTexture(imageNamed: name)
        texture.filteringMode = .linear
        return texture
    }

    private func buildNodes() {
        groundLine = SKShapeNode()
        groundLine.strokeColor = SKColor(red: 0.47, green: 0.55, blue: 0.63, alpha: 1)
        groundLine.lineWidth = 2
        groundLine.zPosition = 1
        addChild(groundLine)

        originA = makeOriginMarker(color: SKColor(red: 0.16, green: 0.46, blue: 0.82, alpha: 1))
        originB = makeOriginMarker(color: SKColor(red: 0.91, green: 0.47, blue: 0.16, alpha: 1))
        addChild(originA)
        addChild(originB)

        boxerA = makeBoxer(texture: idleA[0], mirrored: false)
        boxerB = makeBoxer(texture: idleB[0], mirrored: true)
        addChild(boxerA)
        addChild(boxerB)
    }

    private func makeBoxer(texture: SKTexture, mirrored: Bool) -> SKSpriteNode {
        let node = SKSpriteNode(texture: texture)
        node.anchorPoint = Self.originAnchor
        node.xScale = mirrored ? -1 : 1
        node.zPosition = 2
        return node
    }

    private func makeOriginMarker(color: SKColor) -> SKShapeNode {
        let node = SKShapeNode(circleOfRadius: 5)
        node.strokeColor = color
        node.fillColor = .clear
        node.lineWidth = 2
        node.zPosition = 3
        let cross = SKShapeNode()
        let path = CGMutablePath()
        path.move(to: CGPoint(x: -8, y: 0))
        path.addLine(to: CGPoint(x: 8, y: 0))
        path.move(to: CGPoint(x: 0, y: -8))
        path.addLine(to: CGPoint(x: 0, y: 8))
        cross.path = path
        cross.strokeColor = color
        cross.lineWidth = 1
        node.addChild(cross)
        return node
    }

    private func layoutFighters() {
        guard size.width > 1, size.height > 1 else { return }

        groundY = size.height * 0.22
        let spriteSide = min(size.height * 0.88, size.width * 0.46, 420)
        fighterScale = spriteSide / Self.spriteCanvas
        let right = CGPoint(x: size.width * 0.70, y: groundY)

        boxerB.position = right
        boxerA.yScale = fighterScale
        boxerB.yScale = fighterScale
        boxerA.xScale = fighterScale
        boxerB.xScale = -fighterScale

        if !didInitialLayout {
            boxerA.position = CGPoint(x: size.width * 0.30, y: groundY)
            didInitialLayout = true
        } else {
            boxerA.position = CGPoint(x: size.width * blueXFraction, y: groundY)
        }

        clampBlue()
        blueXFraction = boxerA.position.x / size.width

        let path = CGMutablePath()
        path.move(to: CGPoint(x: Self.edgePaddingPoints, y: groundY))
        path.addLine(to: CGPoint(x: size.width - Self.edgePaddingPoints, y: groundY))
        groundLine.path = path
        originA.position = boxerA.position
        originB.position = boxerB.position
    }

    private func extents() -> (left: CGFloat, right: CGFloat, separation: CGFloat) {
        let left = (Self.figureOriginX - Self.contentMinX) * fighterScale
        let right = (Self.contentMaxX - Self.figureOriginX) * fighterScale
        let stance = (Self.contentMaxX - Self.contentMinX) * fighterScale
        return (left, right, stance * Self.minSeparationFactor)
    }

    private func clampBlue() {
        let box = extents()
        // Mirrored orange: visual left edge uses the unmirrored right extent.
        let minX = Self.edgePaddingPoints + box.left
        let orangeLeft = boxerB.position.x - box.right
        let maxX = orangeLeft - box.separation - box.right
        boxerA.position.x = min(max(boxerA.position.x, minX), max(minX, maxX))
        boxerA.position.y = groundY
    }

    private func applyFrames() {
        guard boxerA != nil else { return }
        let blueTextures: [SKTexture]
        switch activeClip {
        case .idle: blueTextures = idleA
        case .advance: blueTextures = advanceA
        case .retreat: blueTextures = retreatA
        }
        boxerA.texture = blueTextures[frameIndex % blueTextures.count]
        boxerB.texture = idleB[orangeFrame % idleB.count]
    }

    private func applyGuideVisibility() {
        groundLine?.isHidden = !showsGuides
        originA?.isHidden = !showsGuides
        originB?.isHidden = !showsGuides
    }

    private func observeAppFocus() {
        guard resignObserver == nil else { return }
        resignObserver = NotificationCenter.default.addObserver(
            forName: UIApplication.willResignActiveNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.cancelMovement()
        }
    }
}
