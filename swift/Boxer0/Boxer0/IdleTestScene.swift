//
//  IdleTestScene.swift
//  Boxer0
//
//  Idle playback, Task 3B footwork and Task 4B shared punch playback.
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
    case jab
    case cross

    var frameCount: Int {
        switch self {
        case .idle: return 4
        case .advance, .retreat, .jab: return 6
        case .cross: return 8
        }
    }

    var cycleDuration: TimeInterval {
        switch self {
        case .idle: return 0.8
        case .advance, .retreat: return 0.48
        case .jab: return PunchKind.jab.duration
        case .cross: return PunchKind.cross.duration
        }
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

    private var motion = FootworkMotion()
    private var punch = PunchPlayback()
    private var hasFocus = true
    private(set) var jabAssetsAvailable = false
    private(set) var crossAssetsAvailable = false
    private(set) var jabContactCount = 0
    private(set) var crossContactCount = 0
    var canStartJab: Bool {
        jabAssetsAvailable && boxerA != nil && hasFocus && isPlaying && !punch.isActive
    }
    var canStartCross: Bool {
        crossAssetsAvailable && boxerA != nil && hasFocus && isPlaying && !punch.isActive
    }
    var showsJabContact: Bool {
        punch.isActive && punch.kind == .jab && punch.frameIndex == punch.kind.contactFrame
    }
    var showsCrossContact: Bool {
        punch.isActive && punch.kind == .cross && punch.frameIndex == punch.kind.contactFrame
    }
    var movementSpeed: CGFloat {
        get { CGFloat(motion.maximumSpeed) }
        set { motion.maximumSpeed = max(0, Double(newValue)) }
    }
    var acceleration: Double {
        get { motion.acceleration }
        set { motion.acceleration = max(1, newValue) }
    }
    var deceleration: Double {
        get { motion.deceleration }
        set { motion.deceleration = max(1, newValue) }
    }
    var velocityDeadZone: Double {
        get { motion.deadZone }
        set { motion.deadZone = max(0, newValue) }
    }
    private(set) var inputGeneration = 0
    var advanceHeld: Bool { holdAdvance }
    var retreatHeld: Bool { holdRetreat }
    var horizontalVelocity: Double { motion.velocity }
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
    private var jabA: [SKTexture] = []
    private var crossA: [SKTexture] = []
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
    private var activeObserver: NSObjectProtocol?

    var bluePositionX: CGFloat { boxerA?.position.x ?? 0 }

    override func didMove(to view: SKView) {
        lastTime = 0
        hasFocus = UIApplication.shared.applicationState == .active
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
        onPlaybackChange?()
    }

    override func willMove(from view: SKView) {
        cancelMovement()
        punch.cancel()
        settleIdle()
        applyFrames()
        if let activeObserver = activeObserver {
            NotificationCenter.default.removeObserver(activeObserver)
            self.activeObserver = nil
        }
        if let resignObserver = resignObserver { 
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
        guard isPlaying, hasFocus else { return }
        if punch.isActive {
            let event = punch.advance(dt)
            handlePunchEvent(event)
            animateBoxer(&orangeAccumulator, frame: &orangeFrame, clip: .idle,
                         speed: playbackSpeed.rawValue, dt: dt)
            applyFrames()
            publishIfNeeded()
            return
        }

        let segments = motion.advance(duration: dt, direction: Double(movementDirection ?? 0))
        for segment in segments {
            let oldX = boxerA.position.x
            boxerA.position.x += CGFloat(segment.displacement)
            let hitBoundary = clampBlue()
            let travel = Double(boxerA.position.x - oldX)
            if abs(travel) > 1e-8 {
                // Follow travel, not input: a reversal still plays the old clip
                // throughout braking. At full speed a cycle remains 480 ms.
                setClip(travel > 0 ? .advance : .retreat)
                let animationTime = abs(travel) / max(motion.maximumSpeed, 1)
                animateBoxer(&blueAccumulator, frame: &frameIndex, clip: activeClip,
                             speed: playbackSpeed.rawValue, dt: animationTime)
            } else {
                settleIdle()
                animateBoxer(&blueAccumulator, frame: &frameIndex, clip: .idle,
                             speed: playbackSpeed.rawValue, dt: segment.duration)
            }
            if hitBoundary {
                motion.stop()
                settleIdle()
                break
            }
        }
        if motion.velocity == 0 { settleIdle() }
        animateBoxer(&orangeAccumulator, frame: &orangeFrame, clip: .idle,
                     speed: playbackSpeed.rawValue, dt: dt)
        blueXFraction = boxerA.position.x / max(size.width, 1)
        originA.position = boxerA.position

        applyFrames()
        publishIfNeeded()
    }

    private var lastPublishedFrame = -1
    private var lastPublishedX: CGFloat = .nan
    private var lastPublishedClip: FighterClip?
    private var lastPublishedVelocity: Double = .nan

    private func publishIfNeeded() {
        let x = boxerA.position.x
        if frameIndex != lastPublishedFrame
            || activeClip != lastPublishedClip
            || lastPublishedX.isNaN
            || abs(x - lastPublishedX) >= 1
            || lastPublishedVelocity.isNaN
            || abs(motion.velocity - lastPublishedVelocity) >= 1 {
            lastPublishedFrame = frameIndex
            lastPublishedClip = activeClip
            lastPublishedX = x
            lastPublishedVelocity = motion.velocity
            onPlaybackChange?()
        }
    }

    func togglePlayback() {
        isPlaying.toggle()
        clearHeldInput()
        motion.stop()
        lastTime = 0
        if isPlaying {
            if !punch.isActive { settleIdle() }
            applyFrames()
        }
        onPlaybackChange?()
    }

    func stepFrame() {
        isPlaying = false
        clearHeldInput()
        motion.stop()
        lastTime = 0
        blueAccumulator = 0
        if punch.isActive {
            let event = punch.step()
            handlePunchEvent(event)
        } else {
            frameIndex = (frameIndex + 1) % activeClip.frameCount
        }
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
        holdAdvance = held && isPlaying && hasFocus && !punch.isActive
        onPlaybackChange?()
    }

    func setRetreatHeld(_ held: Bool) {
        holdRetreat = held && isPlaying && hasFocus && !punch.isActive
        onPlaybackChange?()
    }

    private func clearHeldInput() {
        holdAdvance = false
        holdRetreat = false
        inputGeneration += 1
    }

    func cancelMovement() {
        lastTime = 0
        clearHeldInput()
        motion.stop()
        if !punch.isActive { settleIdle() }
        applyFrames()
        onPlaybackChange?()
    }

    func startJab() { startPunch(.jab) }
    func startCross() { startPunch(.cross) }

    private func startPunch(_ kind: PunchKind) {
        let available = kind == .jab ? canStartJab : canStartCross
        guard available, punch.start(kind) else { return }
        clearHeldInput()
        motion.stop()
        setClip(kind == .jab ? .jab : .cross)
        // Present ready before consuming any of the punch frame intervals.
        lastTime = 0
        applyFrames()
        onPlaybackChange?()
    }

    private func handlePunchEvent(_ event: (contact: Bool, completed: Bool)) {
        if event.contact {
            if punch.kind == .jab { jabContactCount += 1 }
            else { crossContactCount += 1 }
        }
        if event.completed {
            clearHeldInput()
            motion.stop()
            settleIdle()
        } else {
            frameIndex = punch.frameIndex
        }
    }

    private var movementDirection: CGFloat? {
        if holdAdvance && !holdRetreat { return 1 }
        if holdRetreat && !holdAdvance { return -1 }
        return nil
    }

    private func settleIdle() { setClip(.idle) }

    private func setClip(_ next: FighterClip) {
        guard next != activeClip else { return }
        // Frame zero is the shared rest/guard pose in every clip.
        // Keep phase untouched while staying in a clip; only reset on a real
        // state change. Direction changes occur after braking through zero.
        activeClip = next
        frameIndex = 0
        blueAccumulator = 0
    }

    private func animateBoxer(
        _ accumulator: inout TimeInterval,
        frame: inout Int,
        clip: FighterClip,
        speed: Double,
        dt: TimeInterval
    ) {
        // Shorten the double-planted holds, lengthen the lifted-foot poses.
        // Total footwork timing remains 480 ms. Idle timing is unchanged.
        let durations: [TimeInterval] = clip == .idle
            ? [0.2, 0.2, 0.2, 0.2]
            : [0.04, 0.14, 0.04, 0.14, 0.06, 0.06]
        accumulator += dt * speed
        while accumulator >= durations[frame] {
            accumulator -= durations[frame]
            frame = (frame + 1) % clip.frameCount
        }
    }

    private func loadTextures() {
        idleA = (0..<4).map { makeTexture(named: "idle_a_\($0)") }
        idleB = (0..<4).map { makeTexture(named: "idle_b_\($0)") }
        advanceA = (0..<6).map { makeTexture(named: "advance_a_\($0)") }
        retreatA = (0..<6).map { makeTexture(named: "retreat_a_\($0)") }
        // Never substitute another clip or a missing-image placeholder.
        jabA = loadPunchTextures(prefix: "jab_a", count: PunchKind.jab.frameCount)
        crossA = loadPunchTextures(prefix: "cross_a", count: PunchKind.cross.frameCount)
        jabAssetsAvailable = jabA.count == PunchKind.jab.frameCount
        crossAssetsAvailable = crossA.count == PunchKind.cross.frameCount
    }

    private func loadPunchTextures(prefix: String, count: Int) -> [SKTexture] {
        let images = (0..<count).compactMap { UIImage(named: "\(prefix)_\($0)") }
        guard images.count == count, images.allSatisfy({
            $0.cgImage?.width == 512 && $0.cgImage?.height == 512
        }) else { return [] }
        return images.map {
            let texture = SKTexture(image: $0)
            texture.filteringMode = .linear
            return texture
        }
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

    @discardableResult
    private func clampBlue() -> Bool {
        let box = extents()
        // Mirrored orange: visual left edge uses the unmirrored right extent.
        let minX = Self.edgePaddingPoints + box.left
        let orangeLeft = boxerB.position.x - box.right
        let maxX = orangeLeft - box.separation - box.right
        let upper = max(minX, maxX)
        let proposedX = boxerA.position.x
        boxerA.position.x = min(max(proposedX, minX), upper)
        boxerA.position.y = groundY
        let blocked = proposedX != boxerA.position.x
            || (proposedX <= minX && motion.velocity < 0)
            || (proposedX >= upper && motion.velocity > 0)
        if blocked { motion.stop() }
        return blocked
    }

    private func applyFrames() {
        guard boxerA != nil else { return }
        let blueTextures: [SKTexture]
        switch activeClip {
        case .idle: blueTextures = idleA
        case .advance: blueTextures = advanceA
        case .retreat: blueTextures = retreatA
        case .jab: blueTextures = jabA
        case .cross: blueTextures = crossA
        }
        guard !blueTextures.isEmpty, !idleB.isEmpty else { return }
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
            self?.hasFocus = false
            self?.cancelMovement()
        }
        activeObserver = NotificationCenter.default.addObserver(
            forName: UIApplication.didBecomeActiveNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.hasFocus = true
            self?.lastTime = 0
            self?.onPlaybackChange?()
        }
    }
}
