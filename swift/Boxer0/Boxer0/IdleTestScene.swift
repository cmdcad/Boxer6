//
//  IdleTestScene.swift
//  Boxer0
//
//  Minimal SpriteKit scene that plays the four-frame idle cycle for both
//  placeholder boxers. Boxer B is mirrored at runtime. No combat systems.
//

import SpriteKit

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

final class IdleTestScene: SKScene {

    static let frameCount = 4
    static let cycleDuration: TimeInterval = 0.8
    static let originAnchor = CGPoint(x: 0.5, y: 1.0 - 448.0 / 512.0)

    var isPlaying = true
    var playbackSpeed: IdlePlaybackSpeed = .normal
    var showsGuides = true {
        didSet { applyGuideVisibility() }
    }
    var frameIndex = 0 {
        didSet { applyFrame() }
    }
    var onFrameChange: ((Int) -> Void)?

    private var boxerA: SKSpriteNode!
    private var boxerB: SKSpriteNode!
    private var texturesA: [SKTexture] = []
    private var texturesB: [SKTexture] = []
    private var groundLine: SKShapeNode!
    private var originA: SKShapeNode!
    private var originB: SKShapeNode!
    private var lastTime: TimeInterval = 0
    private var accumulator: TimeInterval = 0
    private var groundY: CGFloat = 0

    override func didMove(to view: SKView) {
        backgroundColor = SKColor(red: 0.91, green: 0.933, blue: 0.957, alpha: 1)
        scaleMode = .resizeFill
        loadTextures()
        if boxerA == nil {
            buildNodes()
        }
        layoutFighters()
        applyFrame()
        applyGuideVisibility()
    }

    override func didChangeSize(_ oldSize: CGSize) {
        super.didChangeSize(oldSize)
        guard boxerA != nil else { return }
        layoutFighters()
    }

    override func update(_ currentTime: TimeInterval) {
        if lastTime == 0 {
            lastTime = currentTime
            return
        }
        let dt = currentTime - lastTime
        lastTime = currentTime
        guard isPlaying else { return }

        let frameDuration = Self.cycleDuration / TimeInterval(Self.frameCount)
        accumulator += dt * playbackSpeed.rawValue
        var advanced = false
        while accumulator >= frameDuration {
            accumulator -= frameDuration
            frameIndex = (frameIndex + 1) % Self.frameCount
            advanced = true
        }
        if advanced {
            onFrameChange?(frameIndex)
        }
    }

    func togglePlayback() {
        isPlaying.toggle()
        if isPlaying {
            accumulator = 0
        }
    }

    func stepFrame() {
        isPlaying = false
        accumulator = 0
        frameIndex = (frameIndex + 1) % Self.frameCount
        onFrameChange?(frameIndex)
    }

    func setSpeed(_ speed: IdlePlaybackSpeed) {
        playbackSpeed = speed
    }

    func toggleGuides() {
        showsGuides.toggle()
    }

    private func loadTextures() {
        texturesA = (0..<Self.frameCount).map { makeTexture(named: "idle_a_\($0)") }
        texturesB = (0..<Self.frameCount).map { makeTexture(named: "idle_b_\($0)") }
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

        boxerA = makeBoxer(texture: texturesA[0], mirrored: false)
        boxerB = makeBoxer(texture: texturesB[0], mirrored: true)
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
        let scale = spriteSide / 512.0
        let left = CGPoint(x: size.width * 0.30, y: groundY)
        let right = CGPoint(x: size.width * 0.70, y: groundY)

        boxerA.position = left
        boxerB.position = right
        boxerA.xScale = scale
        boxerA.yScale = scale
        boxerB.xScale = -scale
        boxerB.yScale = scale

        let path = CGMutablePath()
        path.move(to: CGPoint(x: 20, y: groundY))
        path.addLine(to: CGPoint(x: size.width - 20, y: groundY))
        groundLine.path = path
        originA.position = left
        originB.position = right
    }

    private func applyFrame() {
        guard boxerA != nil, !texturesA.isEmpty else { return }
        let index = frameIndex % Self.frameCount
        boxerA.texture = texturesA[index]
        boxerB.texture = texturesB[index]
    }

    private func applyGuideVisibility() {
        groundLine?.isHidden = !showsGuides
        originA?.isHidden = !showsGuides
        originB?.isHidden = !showsGuides
    }
}
