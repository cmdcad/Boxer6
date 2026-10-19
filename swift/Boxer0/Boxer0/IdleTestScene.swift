//
//  IdleTestScene.swift
//  Boxer0
//
//  Idle playback, Task 3B footwork and Task 5C profiled hit feedback.
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
    // User-approved Task 5A spacing: physical torso widths, not idle glove reach.
    static let bodyMinX: CGFloat = 220
    static let bodyMaxX: CGFloat = 308
    var minimumBodyGapFactor: CGFloat = 0.8
    static let defaultMoveSpeed: CGFloat = 100

    private var motion = FootworkMotion()
    private var orangeMotion = FootworkMotion()
    private var cpuDistance = CPUDistanceController()
    private var orangeLocomotionClip = FighterClip.idle
    private var orangeXFraction: CGFloat = 0.70
    var cpuMovementLabel: String { cpuDistance.intent.rawValue }
    var orangeVelocity: Double { orangeMotion.velocity }
    private func stopCPUFootwork() {
        orangeMotion.stop()
        cpuDistance.reset()
        setOrangeLocomotion(.idle)
    }
    private func setOrangeLocomotion(_ clip: FighterClip) {
        if orangeLocomotionClip != clip {
            orangeLocomotionClip = clip
            orangeFrame = 0
            orangeAccumulator = 0
        }
    }
    private var punch = PunchPlayback()
    private var orangePunch = PunchPlayback()
    private var blueGuard = GuardPlayback()
    private var blueBlockFeedback = BlockFeedbackPlayback()
    private var blueGuardEffectiveAtContact: Bool?
    private(set) var guardHeld = false
    private(set) var guardInputGeneration = 0
    private(set) var playerGuardAssetsAvailable = false
    var canHoldGuard: Bool {
        playerGuardAssetsAvailable && hasFocus && blueCombatState == .standing && !blueKnockdown.hasStarted
    }
    var blueGuardStatus: String {
        !blueGuard.isSelected ? "LOWERED" : (blueGuard.isEffective ? "RAISED" : "RAISING")
    }
    var blueBlockFeedbackLabel: String { blueBlockFeedback.label }
    func setGuardHeld(_ held: Bool) {
        guardHeld = held && canHoldGuard
        blueGuardEffectiveAtContact = nil
        syncBlueGuard()
        applyFrames(); onPlaybackChange?()
    }
    private func clearBlueGuardInput() {
        guardHeld = false
        guardInputGeneration += 1
        blueGuard.cancel(); blueBlockFeedback.cancel()
        blueGuardEffectiveAtContact = nil
    }
    private func syncBlueGuard() {
        let eligible = guardHeld && canHoldGuard && !punch.isActive && !blueVisualBusy
        if !eligible {
            blueGuard.cancel(); blueBlockFeedback.cancel()
        } else if !blueGuard.isSelected {
            blueGuard.toggle()
        }
    }
    private func advanceBlueDefense(_ dt: Double) {
        let wasSelected = blueGuard.isSelected
        syncBlueGuard()
        blueGuardEffectiveAtContact = nil
        if wasSelected && blueGuard.isSelected {
            if let contactTime = orangePunch.timeUntilContact, contactTime <= dt {
                blueGuard.advance(contactTime)
                blueGuardEffectiveAtContact = blueGuard.isEffective
                blueGuard.advance(max(0, dt-contactTime))
            } else { blueGuard.advance(dt) }
        }
        blueBlockFeedback.advance(dt)
    }
    private var blueReaction = HitReactionPlayback()
    private var blueKnockdown = KnockdownPlayback()
    private var cpuOffense = CPUOffense()
    private var cpuContactTracker = PunchContactTracker()
    private var simulationTime = 0.0
    private var attackSequence = 0
    private var cpuStartedThisTick = false
    private var blueVisualBusy: Bool { blueReaction.isActive || blueKnockdown.hasStarted }
    private var canCPUAttack: Bool {
        health.canExchangePunches && !reaction.isActive && !knockdown.hasStarted
            && !guardPlayback.isSelected && !blockFeedback.isActive && !orangePunch.isActive
            && defensiveAI.state == .idle
            && orangePunchAssetsAvailable && blueRecoveryAssetsAvailable
    }
    private(set) var orangePunchAssetsAvailable = false
    private(set) var blueRecoveryAssetsAvailable = false
    var cpuAttackLabel: String { cpuOffense.label }
    var cpuStats: String {
        "O J\(cpuContactTracker.jabContacts) C\(cpuContactTracker.crossContacts) H\(cpuContactTracker.hits) B\(cpuContactTracker.blocks) M\(cpuContactTracker.misses)"
    }
    var cpuLastResult: String { cpuContactTracker.latest?.result.rawValue ?? "-" }
    var blueAnimationLabel: String {
        if blueKnockdown.hasStarted { return "\(blueKnockdown.clip.rawValue) \(blueKnockdown.frameIndex+1)/\(blueKnockdown.clip == .down ? 1 : 8)" }
        if blueReaction.isActive { return "hit_react \(blueReaction.frameIndex+1)/4" }
        if blueGuard.isSelected { return "guard \(blueGuard.frameIndex+1)/3" }
        return "\(activeClip.rawValue) \(frameIndex+1)/\(activeClip.frameCount)"
    }
    var canBlueRise: Bool {
        blueRecoveryAssetsAvailable && hasFocus && blueCombatState == .defeated && blueKnockdown.clip == .down
    }
    func startBlueRise() {
        guard canBlueRise, blueKnockdown.startRise() else { return }
        cpuOffense.cancel(); defensiveAI.cancel()
        clearHeldInput(); clearBlueGuardInput(); motion.stop()
        lastTime = 0
        applyFrames(); onPlaybackChange?()
    }
    private var reaction = HitReactionPlayback()
    private var knockdown = KnockdownPlayback()
    private var guardPlayback = GuardPlayback()
    private var defensiveAI = DefensiveAI()
    private var punchStartSequence = 0
    private var guardEffectiveAtContact: Bool?
    var cpuEnabled: Bool { defensiveAI.enabled }
    var cpuStatus: String { defensiveAI.label }
    func toggleCPU() {
        defensiveAI.setEnabled(!defensiveAI.enabled)
        cpuOffense.disable()
        stopCPUFootwork()
        requestGuard(false)
        applyFrames()
        onPlaybackChange?()
    }
    private var blockFeedback = BlockFeedbackPlayback()
    var blockFeedbackLabel: String { blockFeedback.label }
    private(set) var blockRecoilAssetsAvailable = false
    // Optional development tuning, off until readability is reviewed on device.
    // Does not affect reaction timing, geometry, roots, or counters.
    var impactEmphasisEnabled = false {
        didSet { applyImpactEmphasis() }
    }
    var orangeProfileLabel: String { reaction.profile?.label ?? "" }
    private var hasFocus = true
    private(set) var jabAssetsAvailable = false
    private(set) var crossAssetsAvailable = false
    private(set) var reactionAssetsAvailable = false
    private(set) var knockdownAssetsAvailable = false
    private(set) var riseAssetsAvailable = false
    var canRise: Bool {
        riseAssetsAvailable && hasFocus && orangeCombatState == .defeated && knockdown.clip == .down
    }

    func startRise() {
        guard canRise, knockdown.startRise() else { return }
        cpuOffense.cancel()
        defensiveAI.cancel()
        blockFeedback.cancel()
        lastTime = 0
        applyFrames()
        onPlaybackChange?()
    }
    private(set) var guardAssetsAvailable = false
    var guardStatus: String { guardPlayback.status }
    var guardSelected: Bool { guardPlayback.isSelected }
    private var canRequestGuard: Bool {
        guardAssetsAvailable && hasFocus && orangeCombatState == .standing
            && !reaction.isActive && !knockdown.hasStarted && !orangePunch.isActive
    }
    var canToggleGuard: Bool { !cpuEnabled && canRequestGuard }
    func toggleGuard() {
        guard canToggleGuard else { return }
        requestGuard(!guardPlayback.isSelected)
        applyFrames()
        onPlaybackChange?()
    }
    private func requestGuard(_ selected: Bool) {
        guard !selected || canRequestGuard else { return }
        guard guardPlayback.isSelected != selected else { return }
        guardPlayback.toggle()
        if selected {
            stopCPUFootwork()
            cpuOffense.disable()
        }
        if !guardPlayback.isSelected { blockFeedback.cancel() }
        orangeFrame = 0
        orangeAccumulator = 0
    }
    var orangeClip: DefenderClip {
        if knockdown.hasStarted { return knockdown.clip }
        if reaction.isActive { return reaction.clip }
        if orangePunch.isActive { return orangePunch.kind == .jab ? .jab : .cross }
        if guardPlayback.isSelected { return .guardPose }
        if orangeLocomotionClip == .advance { return .advance }
        if orangeLocomotionClip == .retreat { return .retreat }
        return .idle
    }
    var orangeFrameCount: Int {
        switch orangeClip {
        case .idle, .hitReact: return 4
        case .advance, .retreat, .jab: return 6
        case .knockdown, .rise, .cross: return 8
        case .down: return 1
        case .guardPose: return 3
        }
    }
    var orangeFrameIndex: Int {
        if knockdown.hasStarted { return knockdown.frameIndex }
        if reaction.isActive { return reaction.frameIndex }
        if orangePunch.isActive { return orangePunch.frameIndex }
        return guardPlayback.isSelected ? guardPlayback.frameIndex : orangeFrame
    }
    private var contactTracker = PunchContactTracker()
    private var health = FighterHealthState()
    var blueHealth: FighterHealth { health.blue }
    var orangeHealth: FighterHealth { health.orange }
    var blueCombatState: FighterCombatState { health.blueCombat.state }
    var orangeCombatState: FighterCombatState { health.orangeCombat.state }
    var orangeDefeatRecorded: Bool { health.orangeCombat.defeatRecorded }

    func resetHealth() {
        health.reset()
        clearBlueGuardInput()
        orangePunch.cancel(); cpuContactTracker.finish()
        blueReaction.cancel(); blueKnockdown.cancel()
        cpuOffense.cancel(reseed: true)
        defensiveAI.cancel(reseed: true)
        stopCPUFootwork()
        // End pending ownership, not the diagnostic counters or root positions.
        punch.cancel()
        contactTracker.finish()
        reaction.cancel()
        knockdown.cancel()
        guardPlayback.cancel()
        blockFeedback.cancel()
        orangeFrame = 0
        orangeAccumulator = 0
        clearHeldInput()
        motion.stop()
        settleIdle()
        blueAccumulator = 0
        cpuStartedThisTick = false
        lastTime = 0
        applyFrames()
        onPlaybackChange?()
    }
    var contactGeometry = PunchContactGeometry() {
        didSet { updateContactGuides() }
    }
    var debugOverlaysEnabled = true {
        didSet { applyGuideVisibility() }
    }
    var jabContactCount: Int { contactTracker.jabContacts }
    var crossContactCount: Int { contactTracker.crossContacts }
    var hitCount: Int { contactTracker.hits }
    var missCount: Int { contactTracker.misses }
    var blockCount: Int { contactTracker.blocks }
    var latestContact: PunchContactEvent? { contactTracker.latest }
    private(set) var textureCanvasInfo = "Textures pending"
    var onPunchContact: ((PunchContactEvent) -> Void)?
    var canStartJab: Bool {
        health.canExchangePunches && jabAssetsAvailable && boxerA != nil && hasFocus && isPlaying && !punch.isActive && !blueVisualBusy && !blueGuard.isSelected
    }
    var canStartCross: Bool {
        health.canExchangePunches && crossAssetsAvailable && boxerA != nil && hasFocus && isPlaying && !punch.isActive && !blueVisualBusy && !blueGuard.isSelected
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

    // Only these roots own placement, scale and facing. Sprite children remain
    // on the unscaled 512-point canvas throughout texture playback.
    private let rootA = SKNode()
    private let rootB = SKNode()
    private var boxerA: SKSpriteNode!
    private var boxerB: SKSpriteNode!
    private var idleA: [SKTexture] = []
    private var idleB: [SKTexture] = []
    private var advanceA: [SKTexture] = []
    private var retreatA: [SKTexture] = []
    private var jabA: [SKTexture] = []
    private var crossA: [SKTexture] = []
    private var hitReactB: [SKTexture] = []
    private var knockdownB: [SKTexture] = []
    private var downB: [SKTexture] = []
    private var riseB: [SKTexture] = []
    private var guardB: [SKTexture] = []
    private var jabB: [SKTexture] = []
    private var crossB: [SKTexture] = []
    private var guardA: [SKTexture] = []
    private var blockJabA: [SKTexture] = []
    private var blockCrossA: [SKTexture] = []
    private var hitReactA: [SKTexture] = []
    private var knockdownA: [SKTexture] = []
    private var downA: [SKTexture] = []
    private var riseA: [SKTexture] = []
    private var advanceB: [SKTexture] = []
    private var retreatB: [SKTexture] = []
    private var blockJabB: [SKTexture] = []
    private var blockCrossB: [SKTexture] = []
    private var groundLine: SKShapeNode!
    private var targetGuide: SKShapeNode!
    private var gloveRadiusGuide: SKShapeNode!
    private var glovePointGuide: SKShapeNode!
    private var contactDistanceGuide: SKShapeNode!
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

    var bluePositionX: CGFloat { rootA.position.x }

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
        clearBlueGuardInput()
        punch.cancel()
        reaction.cancel()
        knockdown.cancel()
        orangePunch.cancel(); cpuContactTracker.finish()
        blueReaction.cancel(); blueKnockdown.cancel()
        cpuOffense.cancel()
        defensiveAI.cancel()
        guardPlayback.cancel()
        blockFeedback.cancel()
        orangeFrame = 0
        orangeAccumulator = 0
        contactTracker.finish()
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
        simulationTime += dt
        advanceBlueRecovery(dt)
        advanceBlueDefense(dt)
        advanceCPUOffense(dt)
        // Advance the previous orange state before processing this tick's HIT.
        // A newly triggered recoil must still display frame zero at applyFrames.
        advanceBlockFeedback(dt)
        guardEffectiveAtContact = nil
        if cpuEnabled, let contactTime = punch.timeUntilContact, contactTime <= dt {
            advanceOrange(contactTime)
            guardEffectiveAtContact = guardPlayback.isEffective
            advanceOrange(max(0, dt - contactTime))
        } else {
            advanceOrange(dt)
        }
        if punch.isActive {
            let event = punch.advance(dt, preserveContactPose: true)
            handlePunchEvent(event)
            guardEffectiveAtContact = nil
            advanceCPUAttack(dt)
            applyFrames()
            publishIfNeeded()
            return
        }

        if blueVisualBusy || blueCombatState == .defeated {
            advanceCPUAttack(dt)
            applyFrames(); publishIfNeeded()
            return
        }
        if blueGuard.isEffective { motion.stop() }
        let direction = blueGuard.isSelected ? 0.0 : Double(movementDirection ?? 0)
        let segments = motion.advance(duration: dt, direction: direction)
        for segment in segments {
            let oldX = rootA.position.x
            rootA.position.x += CGFloat(segment.displacement)
            let hitBoundary = clampBlue()
            let travel = Double(rootA.position.x - oldX)
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
        blueXFraction = rootA.position.x / max(size.width, 1)
        originA.position = rootA.position
        advanceCPUAttack(dt)

        applyFrames()
        publishIfNeeded()
    }

    private var lastPublishedFrame = -1
    private var lastPublishedX: CGFloat = .nan
    private var lastPublishedClip: FighterClip?
    private var lastPublishedVelocity: Double = .nan
    private var lastPublishedOrangeFrame = -1
    private var lastPublishedOrangeClip: DefenderClip?
    private var lastPublishedBlueGuard = ""
    private var lastPublishedBlueFX = ""
    private var lastPublishedCPUAttack = ""
    private var lastPublishedBlueAnimation = ""

    private func publishIfNeeded() {
        let x = rootA.position.x
        if frameIndex != lastPublishedFrame
            || activeClip != lastPublishedClip
            || lastPublishedX.isNaN
            || abs(x - lastPublishedX) >= 1
            || lastPublishedVelocity.isNaN
            || abs(motion.velocity - lastPublishedVelocity) >= 1
            || orangeFrameIndex != lastPublishedOrangeFrame
            || orangeClip != lastPublishedOrangeClip
            || blueGuardStatus != lastPublishedBlueGuard
            || blueBlockFeedbackLabel != lastPublishedBlueFX
            || cpuAttackLabel != lastPublishedCPUAttack
            || blueAnimationLabel != lastPublishedBlueAnimation {
            lastPublishedFrame = frameIndex
            lastPublishedClip = activeClip
            lastPublishedX = x
            lastPublishedVelocity = motion.velocity
            lastPublishedOrangeFrame = orangeFrameIndex
            lastPublishedOrangeClip = orangeClip
            lastPublishedBlueGuard = blueGuardStatus
            lastPublishedBlueFX = blueBlockFeedbackLabel
            lastPublishedCPUAttack = cpuAttackLabel
            lastPublishedBlueAnimation = blueAnimationLabel
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
        // As in update: step old orange state first, then a new HIT may restart
        // frame zero. Never step a reaction again in the tick it is triggered.
        // Expire only an old effect; a BLOCK created below starts at elapsed zero.
        let blueStep = punch.isActive ? punch.kind.frameDuration : Double.infinity
        let orangeStep = orangePunch.isActive ? orangePunch.kind.frameDuration : Double.infinity
        let guardStep = blueGuard.isSelected ? GuardPlayback.frameDuration : Double.infinity
        let attackStep = min(min(blueStep, orangeStep), guardStep)
        let effectStep = attackStep.isFinite ? attackStep
            : activeClip.cycleDuration / Double(activeClip.frameCount)
        simulationTime += effectStep
        advanceBlueRecovery(effectStep, stepping: true)
        advanceBlueDefense(effectStep)
        advanceCPUOffense(effectStep)
        advanceBlockFeedback(effectStep)
        stepOrange()
        if punch.isActive {
            let event = punch.step()
            handlePunchEvent(event)
        } else if !blueVisualBusy && blueCombatState == .standing {
            frameIndex = (frameIndex + 1) % activeClip.frameCount
        }
        advanceCPUAttack(effectStep)
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
        holdAdvance = held && isPlaying && hasFocus && !punch.isActive && !blueVisualBusy && blueCombatState == .standing
        onPlaybackChange?()
    }

    func setRetreatHeld(_ held: Bool) {
        holdRetreat = held && isPlaying && hasFocus && !punch.isActive && !blueVisualBusy && blueCombatState == .standing
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
        clearBlueGuardInput()
        motion.stop()
        if !punch.isActive { settleIdle() }
        applyFrames()
        onPlaybackChange?()
    }

    func startJab() { startPunch(.jab) }
    func startCross() { startPunch(.cross) }

    private func startPunch(_ kind: PunchKind) { _ = beginAttack(.blue, kind: kind) }

    @discardableResult
    private func beginAttack(_ attacker: FighterID, kind: PunchKind) -> Bool {
        if attacker == .orange {
            guard cpuEnabled, canCPUAttack, orangePunch.start(kind) else { return false }
            attackSequence += 1
            cpuContactTracker.begin(kind, attackerID: .orange, attackID: attackSequence, startTime: simulationTime)
            stopCPUFootwork()
            defensiveAI.cancel()
            cpuStartedThisTick = true
            onPlaybackChange?()
            return true
        }
        let available = kind == .jab ? canStartJab : canStartCross
        guard available, punch.start(kind) else { return false }
        clearHeldInput(); motion.stop()
        attackSequence += 1
        contactTracker.begin(kind, attackerID: .blue, attackID: attackSequence, startTime: simulationTime)
        punchStartSequence += 1
        defensiveAI.observe(sequence: punchStartSequence, kind: kind,
                            inRange: predictedContact(.blue, kind: kind), eligible: canRequestGuard)
        if defensiveAI.state == .reacting && !orangePunch.isActive { cpuOffense.disable() }
        setClip(kind == .jab ? .jab : .cross)
        lastTime = 0
        applyFrames(); onPlaybackChange?()
        return true
    }

    private func predictedContact(_ attacker: FighterID, kind: PunchKind) -> Bool {
        let a = canvasTransform(for: attacker == .blue ? boxerA : boxerB)
        let b = canvasTransform(for: attacker == .blue ? boxerB : boxerA)
        return PunchContactGeometry.intersects(center: a.scenePoint(fromImage: contactGeometry.center(for: kind)),
            radius: a.sceneRadius(fromImage: contactGeometry.radius(for: kind)),
            target: b.sceneRect(fromImage: contactGeometry.defenderTarget))
    }

    private func resolveContact(_ attacker: FighterID, kind: PunchKind) {
        guard health.canExchangePunches else { return }
        var tracker = attacker == .blue ? contactTracker : cpuContactTracker
        let contact = tracker.evaluate(kind,
            attacker: canvasTransform(for: attacker == .blue ? boxerA : boxerB),
            defender: canvasTransform(for: attacker == .blue ? boxerB : boxerA), geometry: contactGeometry,
            guardEffective: attacker == .blue
                ? (guardEffectiveAtContact ?? guardPlayback.isEffective)
                : (blueGuardEffectiveAtContact ?? blueGuard.isEffective))
        if attacker == .blue { contactTracker = tracker } else { cpuContactTracker = tracker }
        guard let event = contact else { return }
        health.receive(event)
        if event.result == .hit {
            if event.defenderID == .orange {
                defensiveAI.cancel(); stopCPUFootwork()
                guardPlayback.cancel(); blockFeedback.cancel()
                if orangePunch.isActive {
                    orangePunch.cancel(); cpuContactTracker.finish(); cpuOffense.finished()
                } else { cpuOffense.disable() }
                if reactionAssetsAvailable { reaction.receive(.hit, from: event.kind) }
                orangeFrame = 0; orangeAccumulator = 0
                startKnockdownIfReady()
            } else {
                punch.cancel(); contactTracker.finish()
                blueGuard.cancel(); blueBlockFeedback.cancel()
                clearHeldInput(); motion.stop(); settleIdle()
                if blueCombatState == .defeated { clearBlueGuardInput() }
                if blueRecoveryAssetsAvailable { blueReaction.receive(.hit, from: event.kind) }
            }
        } else if event.result == .block {
            if event.defenderID == .orange && blockRecoilAssetsAvailable { blockFeedback.receive(event) }
            else if event.defenderID == .blue && playerGuardAssetsAvailable { blueBlockFeedback.receive(event) }
        }
        if !health.canExchangePunches {
            defensiveAI.cancel(); cpuOffense.disable(); stopCPUFootwork()
            clearHeldInput(); motion.stop()
        }
        onPunchContact?(event); onPlaybackChange?()
    }

    private func handlePunchEvent(_ event: (contact: Bool, completed: Bool)) {
        if event.contact { resolveContact(.blue, kind: punch.kind) }
        if event.completed {
            contactTracker.finish(); clearHeldInput(); motion.stop(); settleIdle()
            syncBlueGuard()
        } else if punch.isActive { frameIndex = punch.frameIndex }
    }

    private func advanceCPUOffense(_ dt: Double) {
        if !health.canExchangePunches { cpuOffense.disable(); return }
        if let kind = cpuOffense.advance(dt, enabled: cpuEnabled, eligible: canCPUAttack,
            jabInRange: predictedContact(.orange, kind: .jab), crossInRange: predictedContact(.orange, kind: .cross)) {
            if !beginAttack(.orange, kind: kind) { cpuOffense.cancel() }
        }
    }
    private func advanceCPUAttack(_ dt: Double) {
        if cpuStartedThisTick { cpuStartedThisTick = false; return }
        guard orangePunch.isActive else { return }
        let kind = orangePunch.kind
        let event = orangePunch.advance(dt, preserveContactPose: true)
        if event.contact { resolveContact(.orange, kind: kind) }
        if event.completed {
            cpuContactTracker.finish(); cpuOffense.finished()
            orangeFrame = 0; orangeAccumulator = 0
        }
    }
    private func advanceBlueRecovery(_ dt: Double, stepping: Bool = false) {
        if blueKnockdown.hasStarted {
            let completed = stepping ? blueKnockdown.step() : blueKnockdown.advance(dt)
            if completed {
                health.recoverBlue(); clearHeldInput(); clearBlueGuardInput(); motion.stop(); settleIdle()
                frameIndex = 0; blueAccumulator = 0
                cpuOffense.cancel(); defensiveAI.cancel()
                onPlaybackChange?()
            }
        } else if blueReaction.isActive {
            let completed = stepping ? blueReaction.step() : blueReaction.advance(dt)
            if completed {
                if blueCombatState == .defeated && blueRecoveryAssetsAvailable { blueKnockdown.start() }
                else { settleIdle(); frameIndex = 0; blueAccumulator = 0 }
            }
        } else if blueCombatState == .defeated && blueRecoveryAssetsAvailable {
            blueKnockdown.start()
        }
    }

    private func advanceBlockFeedback(_ dt: TimeInterval) {
        let oldLabel = blockFeedback.label
        blockFeedback.advance(dt)
        if oldLabel != blockFeedback.label { onPlaybackChange?() }
    }

    private func completeOrangeRecovery() {
        guard health.recoverOrange() else { return }
        cpuOffense.cancel()
        defensiveAI.cancel()
        guardPlayback.cancel()
        blockFeedback.cancel()
        orangeFrame = 0
        orangeAccumulator = 0
        onPlaybackChange?()
    }

    private func startKnockdownIfReady() {
        guard orangeCombatState == .defeated, !reaction.isActive,
              knockdownAssetsAvailable else { return }
        knockdown.start()
    }

    private func advanceOrange(_ dt: TimeInterval) {
        // Split at AI decisions so a late activation receives only the remaining
        // scene time, rather than a full tick of free guard-entry progression.
        var remaining = dt
        var transitions = 0
        repeat {
            let slice = min(remaining, defensiveAI.timeToTransition)
            if slice > 0 { animateOrange(slice) }
            let request = defensiveAI.advance(slice)
            remaining = max(0, remaining - slice)
            if let request = request {
                switch request {
                case .raise:
                    if canRequestGuard { requestGuard(true) }
                    else { defensiveAI.cancel() }
                case .release: requestGuard(false)
                }
                onPlaybackChange?()
            }
            transitions += 1
        } while remaining > 1e-10 && transitions < 4
    }

    private func animateOrange(_ dt: TimeInterval) {
        if orangePunch.isActive { return }
        if knockdown.hasStarted {
            if knockdown.advance(dt) { completeOrangeRecovery() }
        } else if reaction.isActive {
            if reaction.advance(dt) {
                orangeFrame = 0
                orangeAccumulator = 0
                // Display fall frame zero now; never consume this tick twice.
                startKnockdownIfReady()
            }
        } else if guardPlayback.isSelected {
            let wasEffective = guardPlayback.isEffective
            guardPlayback.advance(dt)
            if wasEffective != guardPlayback.isEffective { onPlaybackChange?() }
        } else if orangeCombatState == .standing {
            advanceCPUFootwork(dt)
        }
    }

    private func advanceCPUFootwork(_ dt: Double) {
        guard cpuEnabled, health.canExchangePunches, advanceB.count == 6, retreatB.count == 6 else {
            stopCPUFootwork()
            animateBoxer(&orangeAccumulator, frame: &orangeFrame, clip: .idle,
                         speed: playbackSpeed.rawValue, dt: dt)
            return
        }
        let limits = orangeMovementLimits()
        let minimum = Double(limits.lowerBound - rootA.position.x)
        let a = canvasTransform(for: boxerA)
        let b = canvasTransform(for: boxerB)
        let reach = Double(a.scenePoint(fromImage: contactGeometry.crossCenter).x - a.rootPosition.x
            + a.sceneRadius(fromImage: contactGeometry.crossRadius)
            + b.rootPosition.x - b.sceneRect(fromImage: contactGeometry.defenderTarget).minX)
        cpuDistance.maximumRangeFactor = 0.99
        cpuDistance.advance(dt, separation: Double(abs(rootB.position.x-rootA.position.x)),
                            reach: max(1, reach), minimum: max(0, minimum))
        orangeMotion.maximumSpeed = cpuDistance.speed
        let direction = cpuOffense.state == .preparing ? 0.0
            : (cpuDistance.intent == .advance ? -1.0 : (cpuDistance.intent == .retreat ? 1.0 : 0))
        for segment in orangeMotion.advance(duration: dt, direction: direction) {
            let old = rootB.position.x
            rootB.position.x = min(limits.upperBound, max(limits.lowerBound, old + CGFloat(segment.displacement)))
            let travel = Double(rootB.position.x-old)
            if abs(travel) > 1e-8 {
                setOrangeLocomotion(travel < 0 ? .advance : .retreat)
                animateBoxer(&orangeAccumulator, frame: &orangeFrame, clip: orangeLocomotionClip,
                    speed: 1, dt: abs(travel) / max(1, cpuDistance.speed))
            } else {
                setOrangeLocomotion(.idle)
                animateBoxer(&orangeAccumulator, frame: &orangeFrame, clip: .idle, speed: 1, dt: segment.duration)
            }
            if rootB.position.x == limits.lowerBound || rootB.position.x == limits.upperBound {
                orangeMotion.stop()
                setOrangeLocomotion(.idle)
                break
            }
        }
        if orangeMotion.velocity == 0 { setOrangeLocomotion(.idle) }
        orangeXFraction = rootB.position.x / max(1, size.width)
        originB.position = rootB.position
    }

    private func orangeMovementLimits() -> ClosedRange<CGFloat> {
        let a = canvasTransform(for: boxerA)
        let b = canvasTransform(for: boxerB)
        let body = CGRect(x: Self.bodyMinX, y: 183, width: Self.bodyMaxX-Self.bodyMinX, height: 117)
        let aBody = a.sceneRect(fromImage: body)
        let bBody = b.sceneRect(fromImage: body)
        let visible = b.sceneRect(fromImage: CGRect(x: Self.contentMinX,y: 0,
            width: Self.contentMaxX-Self.contentMinX,height: Self.spriteCanvas))
        let gap = max(aBody.width,bBody.width) * max(0, minimumBodyGapFactor)
        let lower = aBody.maxX + gap - (bBody.minX-b.rootPosition.x)
        let upper = size.width-Self.edgePaddingPoints-(visible.maxX-b.rootPosition.x)
        return min(lower,upper)...upper
    }

    private func stepOrange() {
        if orangePunch.isActive { return }
        if cpuEnabled && canRequestGuard {
            let interval = punch.isActive ? punch.kind.frameDuration
                : activeClip.cycleDuration / Double(activeClip.frameCount)
            advanceOrange(interval)
            return
        }
        if knockdown.hasStarted {
            if knockdown.step() { completeOrangeRecovery() }
        } else if reaction.isActive {
            if reaction.step() {
                orangeFrame = 0
                orangeAccumulator = 0
                // Display fall frame zero now; never consume this tick twice.
                startKnockdownIfReady()
            }
        } else if guardPlayback.isSelected {
            guardPlayback.step()
        } else if orangeCombatState == .standing {
            orangeAccumulator = 0
            orangeFrame = (orangeFrame + 1) % FighterClip.idle.frameCount
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
        hitReactB = loadPunchTextures(prefix: "hit_react_b", count: HitReactionPlayback.frameCount)
        reactionAssetsAvailable = hitReactB.count == HitReactionPlayback.frameCount
        knockdownB = loadPunchTextures(prefix: "knockdown_b", count: KnockdownPlayback.frameCount)
        downB = loadPunchTextures(prefix: "down_b", count: 1)
        knockdownAssetsAvailable = knockdownB.count == KnockdownPlayback.frameCount && downB.count == 1
        riseB = loadPunchTextures(prefix: "rise_b", count: 8)
        riseAssetsAvailable = riseB.count == 8
        jabB = loadPunchTextures(prefix: "jab_b", count: 6)
        crossB = loadPunchTextures(prefix: "cross_b", count: 8)
        orangePunchAssetsAvailable = jabB.count == 6 && crossB.count == 8
        hitReactA = loadPunchTextures(prefix: "hit_react_a", count: 4)
        knockdownA = loadPunchTextures(prefix: "knockdown_a", count: 8)
        downA = loadPunchTextures(prefix: "down_a", count: 1)
        riseA = loadPunchTextures(prefix: "rise_a", count: 8)
        blueRecoveryAssetsAvailable = hitReactA.count == 4 && knockdownA.count == 8 && downA.count == 1 && riseA.count == 8
        guardA = loadPunchTextures(prefix: "guard_a", count: 3)
        blockJabA = loadPunchTextures(prefix: "block_jab_a", count: 3)
        blockCrossA = loadPunchTextures(prefix: "block_cross_a", count: 3)
        playerGuardAssetsAvailable = guardA.count == 3 && blockJabA.count == 3 && blockCrossA.count == 3
        guardB = loadPunchTextures(prefix: "guard_b", count: GuardPlayback.frameCount)
        guardAssetsAvailable = guardB.count == GuardPlayback.frameCount
        advanceB = loadPunchTextures(prefix: "advance_b", count: 6)
        retreatB = loadPunchTextures(prefix: "retreat_b", count: 6)
        blockJabB = loadPunchTextures(prefix: "block_jab_b", count: BlockFeedbackPlayback.frameCount)
        blockCrossB = loadPunchTextures(prefix: "block_cross_b", count: BlockFeedbackPlayback.frameCount)
        blockRecoilAssetsAvailable = blockJabB.count == BlockFeedbackPlayback.frameCount
            && blockCrossB.count == BlockFeedbackPlayback.frameCount
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

        boxerA = makeBoxer(texture: idleA[0])
        boxerB = makeBoxer(texture: idleB[0])
        rootA.addChild(boxerA)
        rootB.addChild(boxerB)
        addChild(rootA)
        addChild(rootB)

        targetGuide = SKShapeNode()
        targetGuide.lineWidth = 1.5
        targetGuide.strokeColor = .orange
        targetGuide.fillColor = SKColor.orange.withAlphaComponent(0.08)
        targetGuide.zPosition = 4
        addChild(targetGuide)
        gloveRadiusGuide = SKShapeNode()
        gloveRadiusGuide.lineWidth = 1.5
        gloveRadiusGuide.zPosition = 5
        addChild(gloveRadiusGuide)
        glovePointGuide = SKShapeNode(circleOfRadius: 2)
        glovePointGuide.zPosition = 6
        addChild(glovePointGuide)
        contactDistanceGuide = SKShapeNode()
        contactDistanceGuide.lineWidth = 1
        contactDistanceGuide.zPosition = 5
        addChild(contactDistanceGuide)
    }

    private func makeBoxer(texture: SKTexture) -> SKSpriteNode {
        let node = SKSpriteNode(texture: texture)
        // Set child geometry once, before its parent is scaled. Never resize
        // a scaled fighter during playback.
        node.size = CGSize(width: Self.spriteCanvas, height: Self.spriteCanvas)
        node.anchorPoint = Self.originAnchor
        node.xScale = 1
        node.yScale = 1
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
        let right = CGPoint(x: size.width * orangeXFraction, y: groundY)

        rootB.position = right
        rootA.yScale = fighterScale
        rootB.yScale = fighterScale
        rootA.xScale = fighterScale
        rootB.xScale = -fighterScale

        if !didInitialLayout {
            rootA.position = CGPoint(x: size.width * 0.30, y: groundY)
            didInitialLayout = true
        } else {
            rootA.position = CGPoint(x: size.width * blueXFraction, y: groundY)
        }

        let orangeLimits = orangeMovementLimits()
        rootB.position.x = min(orangeLimits.upperBound, max(orangeLimits.lowerBound, rootB.position.x))
        orangeXFraction = rootB.position.x / size.width
        clampBlue()
        blueXFraction = rootA.position.x / size.width

        let path = CGMutablePath()
        path.move(to: CGPoint(x: Self.edgePaddingPoints, y: groundY))
        path.addLine(to: CGPoint(x: size.width - Self.edgePaddingPoints, y: groundY))
        groundLine.path = path
        originA.position = rootA.position
        originB.position = rootB.position
        updateContactGuides()
    }

    private func movementLimits() -> ClosedRange<CGFloat> {
        let spacing = FighterSpacing(
            bodyBounds: CGRect(x: Self.bodyMinX, y: 183, width: Self.bodyMaxX - Self.bodyMinX, height: 117),
            visibleBounds: CGRect(x: Self.contentMinX, y: 0, width: Self.contentMaxX - Self.contentMinX, height: Self.spriteCanvas),
            minimumBodyGapFactor: minimumBodyGapFactor)
        return spacing.horizontalLimits(attacker: canvasTransform(for: boxerA),
            defender: canvasTransform(for: boxerB), sceneWidth: size.width,
            edgePadding: Self.edgePaddingPoints)
    }

    @discardableResult
    private func clampBlue() -> Bool {
        let limits = movementLimits()
        let proposedX = rootA.position.x
        rootA.position.x = min(max(proposedX, limits.lowerBound), limits.upperBound)
        rootA.position.y = groundY
        let blocked = proposedX != rootA.position.x
            || (proposedX <= limits.lowerBound && motion.velocity < 0)
            || (proposedX >= limits.upperBound && motion.velocity > 0)
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
        if blueKnockdown.clip == .knockdown && blueRecoveryAssetsAvailable {
            boxerA.texture = knockdownA[blueKnockdown.frameIndex]
        } else if blueKnockdown.clip == .down && blueRecoveryAssetsAvailable {
            boxerA.texture = downA[0]
        } else if blueKnockdown.clip == .rise && blueRecoveryAssetsAvailable {
            boxerA.texture = riseA[blueKnockdown.frameIndex]
        } else if blueReaction.isActive && blueRecoveryAssetsAvailable {
            boxerA.texture = hitReactA[blueReaction.frameIndex]
        } else if blueBlockFeedback.isActive && blueGuard.isEffective && playerGuardAssetsAvailable {
            let textures = blueBlockFeedback.kind == .cross ? blockCrossA : blockJabA
            boxerA.texture = textures[blueBlockFeedback.frameIndex]
        } else if blueGuard.isSelected && playerGuardAssetsAvailable {
            boxerA.texture = guardA[blueGuard.frameIndex]
        } else { boxerA.texture = blueTextures[frameIndex % blueTextures.count] }
        if knockdown.clip == .knockdown && knockdownAssetsAvailable {
            boxerB.texture = knockdownB[knockdown.frameIndex]
        } else if knockdown.clip == .rise && riseAssetsAvailable {
            boxerB.texture = riseB[knockdown.frameIndex]
        } else if knockdown.clip == .down && knockdownAssetsAvailable {
            boxerB.texture = downB[0]
        } else if reaction.isActive && reactionAssetsAvailable {
            boxerB.texture = hitReactB[reaction.frameIndex]
        } else if orangePunch.isActive && orangePunchAssetsAvailable {
            let textures = orangePunch.kind == .jab ? jabB : crossB
            boxerB.texture = textures[orangePunch.frameIndex]
        } else if blockFeedback.isActive && blockRecoilAssetsAvailable && guardPlayback.isEffective {
            let textures = blockFeedback.kind == .cross ? blockCrossB : blockJabB
            boxerB.texture = textures[blockFeedback.frameIndex]
        } else if guardPlayback.isSelected && guardAssetsAvailable {
            boxerB.texture = guardB[guardPlayback.frameIndex]
        } else if orangeLocomotionClip == .advance && !advanceB.isEmpty {
            boxerB.texture = advanceB[orangeFrame % advanceB.count]
        } else if orangeLocomotionClip == .retreat && !retreatB.isEmpty {
            boxerB.texture = retreatB[orangeFrame % retreatB.count]
        } else {
            boxerB.texture = idleB[orangeFrame % idleB.count]
        }
        applyImpactEmphasis()
        textureCanvasInfo = "child A\(Int(boxerA.size.width)) B\(Int(boxerB.size.width)) · tex A\(Int(boxerA.texture?.size().width ?? 0)) B\(Int(boxerB.texture?.size().width ?? 0))"
        updateContactGuides()
    }

    private func applyImpactEmphasis() {
        guard boxerB != nil else { return }
        // Texture-only white blend. It is independent of Guides and diagnostics,
        // and uses the same paused/stepped reaction clock, not a wall-clock action.
        boxerB.color = .white
        boxerB.colorBlendFactor = impactEmphasisEnabled && reactionAssetsAvailable
            ? CGFloat(reaction.emphasisAmount) : 0
    }

    private func canvasTransform(for node: SKSpriteNode) -> SpriteCanvasTransform {
        // Child-local units ARE canvas pixels. Convert a single unit, not an
        // already-scaled size, through the parent root exactly once.
        let root = node.convert(.zero, to: self)
        let xBasis = node.convert(CGPoint(x: 1, y: 0), to: self)
        let yBasis = node.convert(CGPoint(x: 0, y: 1), to: self)
        return SpriteCanvasTransform(rootPosition: root,
            scaleX: xBasis.x - root.x, scaleY: yBasis.y - root.y,
            rootInImage: CGPoint(x: node.anchorPoint.x * Self.spriteCanvas,
                                 y: (1 - node.anchorPoint.y) * Self.spriteCanvas))
    }

    private func updateContactGuides() {
        guard boxerA != nil, boxerB != nil, targetGuide != nil else { return }
        let visible = showsGuides && debugOverlaysEnabled
        let target = canvasTransform(for: boxerB).sceneRect(fromImage: contactGeometry.defenderTarget)
        targetGuide.path = CGPath(rect: target, transform: nil)
        targetGuide.isHidden = !visible
        // Show the attacking point only while its actual contact pose is visible.
        let contactVisible = visible && punch.isActive && punch.frameIndex == punch.kind.contactFrame
        gloveRadiusGuide.isHidden = !contactVisible
        glovePointGuide.isHidden = !contactVisible
        contactDistanceGuide.isHidden = !contactVisible
        guard contactVisible else { return }
        let attacker = canvasTransform(for: boxerA)
        let center = attacker.scenePoint(fromImage: contactGeometry.center(for: punch.kind))
        let radius = attacker.sceneRadius(fromImage: contactGeometry.radius(for: punch.kind))
        let color: SKColor
        switch contactTracker.latest?.result {
        case .hit?: color = .systemGreen
        case .block?: color = .systemBlue
        default: color = .systemRed
        }
        gloveRadiusGuide.path = CGPath(ellipseIn: CGRect(x: center.x - radius, y: center.y - radius,
            width: radius * 2, height: radius * 2), transform: nil)
        gloveRadiusGuide.strokeColor = color
        gloveRadiusGuide.fillColor = color.withAlphaComponent(0.16)
        glovePointGuide.position = center
        glovePointGuide.strokeColor = color
        glovePointGuide.fillColor = color
        let nearest = PunchContactGeometry.nearestPoint(to: center, on: target)
        let line = CGMutablePath()
        line.move(to: center)
        line.addLine(to: nearest)
        contactDistanceGuide.path = line
        contactDistanceGuide.strokeColor = color
    }

    private func applyGuideVisibility() {
        let visible = showsGuides && debugOverlaysEnabled
        groundLine?.isHidden = !visible
        originA?.isHidden = !visible
        originB?.isHidden = !visible
        updateContactGuides()
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
