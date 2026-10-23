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
    var guardedMovementMultiplier = 0.55
    var blueMovementLabel: String {
        movementLabel(guarded: blueGuard.isEffective, velocity: motion.velocity, mirrored: false)
    }
    var orangeMovementLabel: String {
        movementLabel(guarded: guardPlayback.isEffective, velocity: orangeMotion.velocity, mirrored: true)
    }
    private func movementLabel(guarded: Bool, velocity: Double, mirrored: Bool) -> String {
        let direction = abs(velocity) < 1e-8 ? "HOLD" : ((velocity > 0) != mirrored ? "ADVANCE" : "RETREAT")
        return (guarded ? "GUARDED " : "") + direction
    }

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
    // Restart the approved bounce from its shared stance when a non-reaction
    // action returns to idle. Keep root position and contact geometry untouched.
    private func restartOrangeBounceAtStance() {
        orangeBounceFrame = 0
        orangeBounceAccumulator = 0
    }
    private func setOrangeLocomotion(_ clip: FighterClip) {
        if orangeLocomotionClip != clip {
            orangeLocomotionClip = clip
            orangeFrame = 0
            orangeAccumulator = 0
            if clip == .idle { restartOrangeBounceAtStance() }
        }
    }
    func isAttackVulnerable(_ fighter: FighterID) -> Bool {
        if fighter == .blue {
            return blueCombatState == .standing && !blueVisualBusy && (punch.isActive || blueRecovery.isRecovering)
        }
        return orangeCombatState == .standing && !reaction.isActive && !knockdown.hasStarted
            && (orangePunch.isActive || orangeRecovery.isRecovering)
    }
    var counterSummary: String {
        "Counters Blue \(contactTracker.successfulCounters)/\(contactTracker.counterAttempts) · Orange \(cpuContactTracker.successfulCounters)/\(cpuContactTracker.counterAttempts)"
    }
    private(set) var lastCounterText = "Last Counter: -"
    private var blueRecovery = PunchRecovery()
    private var orangeRecovery = PunchRecovery()
    var blueActionLabel: String {
        if blueVisualBusy { return blueKnockdown.hasStarted ? blueKnockdown.clip.rawValue.uppercased() : "HIT REACTION" }
        if blueBlockFeedback.isActive { return "BLOCK REACTION" }
        if blueRecovery.phase != .ready { return blueRecovery.diagnosticLabel }
        if blueGuard.isSelected { return "GUARD \(blueGuardStatus)" }
        if !hasFocus { return "INACTIVE" }
        if !isPlaying { return "PAUSED" }
        if !health.canExchangePunches { return "OPPONENT DOWN" }
        if guardHeld { return "GUARD PENDING" }
        return canStartJab || canStartCross ? "READY" : "UNAVAILABLE"
    }
    var orangeActionLabel: String {
        if knockdown.hasStarted { return knockdown.clip.rawValue.uppercased() }
        if reaction.isActive { return "HIT REACTION" }
        if blockFeedback.isActive { return "BLOCK REACTION" }
        if orangeRecovery.phase != .ready { return orangeRecovery.diagnosticLabel }
        if guardPlayback.isSelected { return "GUARD \(guardPlayback.status)" }
        if !hasFocus { return "INACTIVE" }
        if !isPlaying { return "PAUSED" }
        if !health.canExchangePunches { return "OPPONENT DOWN" }
        if cpuEnabled && cpuOffense.state != .ready { return cpuOffense.label }
        if cpuEnabled && defensiveAI.state != .idle { return defensiveAI.label }
        if cpuEnabled && !canCPUAttack { return "UNAVAILABLE" }
        return cpuEnabled ? "READY" : "CPU OFF"
    }
    private func advancePhysicalRecovery(_ dt: Double) {
        let blueReady = blueRecovery.advance(dt)
        let orangeReady = orangeRecovery.advance(dt)
        if orangeReady { restartOrangeBounceAtStance() }
        if blueReady || orangeReady { onPlaybackChange?() }
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
        let eligible = guardHeld && canHoldGuard && !punch.isActive && !blueVisualBusy && !blueRecovery.isRecovering
        if !eligible {
            blueGuard.cancel()
            if blueVisualBusy || punch.isActive || blueCombatState == .defeated { blueBlockFeedback.cancel() }
        } else if !blueGuard.isSelected && !blueBlockFeedback.isActive {
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
    private(set) var simulationTime = 0.0
    var combatLog = CombatEventLog()
    private var diagnosticContactTime: Double?
    private var loggedTransitions: [String: String] = [:]
    func setCombatLogging(_ enabled: Bool) {
        combatLog.enabled = enabled
        loggedTransitions.removeAll()
        onPlaybackChange?()
    }
    private func logCombat(_ name: String, fighter: FighterID, context: AttackContext? = nil, detail: String = "") {
        combatLog.record(time: diagnosticContactTime ?? simulationTime, name: name, fighter: fighter,
                         attackID: context?.id, kind: context?.kind, detail: detail)
    }
    var combatInvariantViolations: [String] {
        var failures: [String] = []
        for actor in [FighterID.blue, .orange] {
            let blue = actor == .blue
            let activePunch = blue ? punch.isActive : orangePunch.isActive
            let recovery = blue ? blueRecovery : orangeRecovery
            let guardPose = blue ? blueGuard : guardPlayback
            let fall = blue ? blueKnockdown : knockdown
            let reacting = blue ? blueReaction.isActive : reaction.isActive
            let tracker = blue ? contactTracker : cpuContactTracker
            let hp = blue ? blueHealth.current : orangeHealth.current
            if activePunch && (recovery.isRecovering || guardPose.isSelected || reacting || fall.hasStarted) {
                failures.append("\(actor): incompatible attack state")
            }
            if guardPose.isEffective && (reacting || fall.hasStarted || hp == 0) {
                failures.append("\(actor): incompatible effective guard")
            }
            if tracker.jabContacts + tracker.crossContacts != tracker.hits + tracker.blocks + tracker.misses {
                failures.append("\(actor): contact totals disagree")
            }
            if tracker.successfulCounters > tracker.counterAttempts || tracker.successfulCounters > tracker.hits {
                failures.append("\(actor): counter subset invalid")
            }
        }
        return failures
    }
    private func observeCombatTransitions() {
        guard combatLog.enabled else { return }
        let failures = combatInvariantViolations.joined(separator: "; ")
        if !failures.isEmpty && loggedTransitions["INVARIANT"] != failures {
            logCombat("INVARIANT_FAILURE", fighter: .blue, detail: failures)
        }
        loggedTransitions["INVARIANT"] = failures
        for actor in [FighterID.blue, .orange] {
            let blue = actor == .blue
            let recovery = blue ? blueRecovery : orangeRecovery
            let guardPose = blue ? blueGuard : guardPlayback
            let fall = blue ? blueKnockdown : knockdown
            let context = blue ? contactTracker.context : cpuContactTracker.context
            let values = [("RECOVERY", recovery.isRecovering ? "START" : "END"),
                          ("GUARD", !guardPose.isSelected ? "RELEASE" : (guardPose.isEffective ? "EFFECTIVE" : "START")),
                          ("POSE", fall.hasStarted ? fall.clip.rawValue : "standing")]
            for (category, value) in values {
                let key = "\(actor)-\(category)"
                let old = loggedTransitions[key]
                if old != value {
                    if category == "POSE" {
                        if value == "knockdown" { logCombat("KNOCKDOWN", fighter: actor) }
                        if value == "rise" { logCombat("RISE_START", fighter: actor) }
                        if old == "rise" && value == "standing" { logCombat("RISE_END", fighter: actor) }
                    } else if old != nil || value == "START" || value == "EFFECTIVE" {
                        logCombat(category + "_" + value, fighter: actor, context: context)
                    }
                    loggedTransitions[key] = value
                }
            }
        }
    }
#if DEBUG
    /// Initializes the actual scene without an SKView/display clock.
    func prepareForCombatTests(separation: CGFloat = 170) {
        size = CGSize(width: 900, height: 500)
        hasFocus = true; isPlaying = true
        loadTextures(); if boxerA == nil { buildNodes() }
        layoutFighters()
        rootA.position.x = 300; rootB.position.x = 300 + separation
        rootA.setScale(1); rootB.xScale = -1; rootB.yScale = 1
        applyFrames()
    }
    @discardableResult
    func testBeginAttack(_ fighter: FighterID, _ kind: PunchKind) -> Bool {
        if fighter == .orange { defensiveAI.setEnabled(true) }
        let accepted = beginAttack(fighter, kind: kind)
        cpuStartedThisTick = false
        return accepted
    }
    func testSetSeparation(_ value: CGFloat) { rootB.position.x = rootA.position.x + value }
    func testSetOrangeGuard(_ selected: Bool) { requestGuard(selected) }
    func testConfigureCPU(attackDraw: Double, defenseDraw: Double) {
        cpuOffense.randomDraw = { attackDraw }
        defensiveAI.randomDraw = { defenseDraw }
    }
    var testBluePosition: CGFloat { rootA.position.x }
    var testOrangePosition: CGFloat { rootB.position.x }
    var testBlueVelocity: Double { motion.velocity }
    var testOrangeVelocity: Double { orangeMotion.velocity }
    var testBlueLimits: ClosedRange<CGFloat> { movementLimits() }
    var testOrangeLimits: ClosedRange<CGFloat> { orangeMovementLimits() }
    var testCanCPUAttack: Bool { canCPUAttack }
    var testBlueRecovery: PunchRecovery { blueRecovery }
    var testOrangeRecovery: PunchRecovery { orangeRecovery }
    var testBlueGuardEffective: Bool { blueGuard.isEffective }
    var testOrangeGuardEffective: Bool { guardPlayback.isEffective }
    var testBlueTexture: SKTexture? { boxerA.texture }
    var testOrangeTexture: SKTexture? { boxerB.texture }
    var testBlueTracker: PunchContactTracker { contactTracker }
    var testOrangeTracker: PunchContactTracker { cpuContactTracker }
#endif
    private var attackSequence = 0
    private var cpuStartedThisTick = false
    private var blueVisualBusy: Bool { blueReaction.isActive || blueKnockdown.hasStarted }
    private var canCPUAttack: Bool {
        health.canExchangePunches && !reaction.isActive && !knockdown.hasStarted
            && !guardPlayback.isSelected && !blockFeedback.isActive && !orangePunch.isActive
            && defensiveAI.state == .idle
            && orangePunchAssetsAvailable && blueRecoveryAssetsAvailable && !orangeRecovery.isRecovering
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
        if blueRecovery.isRecovering { return "\(blueRecovery.kind == .jab ? "jab" : "cross") recovery" }
        if blueGuard.isSelected { return "guard \(blueGuard.frameIndex+1)/3" }
        return "\(activeClip.rawValue) \(frameIndex+1)/\(activeClip.frameCount)"
    }
    var canBlueRise: Bool {
        blueRecoveryAssetsAvailable && hasFocus && blueCombatState == .defeated && blueKnockdown.clip == .down
    }
    func startBlueRise() {
        guard canBlueRise, blueKnockdown.startRise() else { return }
        blueRecovery.cancel()
        cpuOffense.cancel(); defensiveAI.cancel()
        clearHeldInput(); clearBlueGuardInput(); motion.stop()
        lastTime = 0
        applyFrames(); onPlaybackChange?()
    }
    private var reaction = HitReactionPlayback()
    private var orangeBounceV3: [SKTexture] = []
    private var orangeNormalV1: [SKTexture] = []
    private var orangeHeavyV1: [SKTexture] = []
    private var orangeBounceFrame = 0
    private var orangeBounceAccumulator = 0.0
    private var orangeBounceAvailable: Bool { orangeBounceV3.count == 17 }
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
        orangeRecovery.cancel()
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
            && !orangeRecovery.isRecovering && !blockFeedback.isActive
    }
    var canToggleGuard: Bool { !cpuEnabled && (canRequestGuard || guardPlayback.isSelected) }
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
            cpuDistance.reset()
            setOrangeLocomotion(.idle)
            cpuOffense.cancelPreparation()
        }
        // Releasing guard ends protection immediately; an existing block recoil
        // finishes before idle/movement/another attack resumes.
        // Don't resume a frozen mid-bounce pose after guard release.
        if !selected { restartOrangeBounceAtStance() }
        orangeFrame = 0
        orangeAccumulator = 0
    }
    var orangeClip: DefenderClip {
        if knockdown.hasStarted { return knockdown.clip }
        if reaction.isActive { return reaction.clip }
        if orangePunch.isActive { return orangePunch.kind == .jab ? .jab : .cross }
        if orangeRecovery.isRecovering { return orangeRecovery.kind == .jab ? .jab : .cross }
        if guardPlayback.isSelected { return .guardPose }
        if orangeLocomotionClip == .advance { return .advance }
        if orangeLocomotionClip == .retreat { return .retreat }
        return .idle
    }
    private var orangeHasDedicatedRecoveryPose: Bool {
        orangeRecovery.isRecovering && usesDedicatedRecoveryPoses
            && !(orangeRecovery.kind == .jab ? jabRecoveryB : crossRecoveryB).isEmpty
    }
    // Report the actual texture family and index selected by applyFrames(),
    // not merely the high-level action state. This distinguishes approved
    // bounce/jab/reaction art from provisional cross, guard and movement art.
    // Diagnostic-only: does not alter playback, rendering or hit detection.
    private var orangePresentedAnimation: (name: String, index: Int, count: Int) {
        if knockdown.clip == .knockdown && knockdownAssetsAvailable {
            return ("knockdown_b", knockdown.frameIndex, knockdownB.count)
        }
        if knockdown.clip == .rise && riseAssetsAvailable {
            return ("rise_b", knockdown.frameIndex, riseB.count)
        }
        if knockdown.clip == .down && knockdownAssetsAvailable {
            return ("down_b", 0, downB.count)
        }
        if reaction.isActive && reactionAssetsAvailable {
            let approved = reaction.profile?.punch == .cross ? orangeHeavyV1 : orangeNormalV1
            if reaction.approvedOrangeArt && reaction.frameIndex < approved.count {
                return (reaction.profile?.punch == .cross ? "orange_heavy" : "orange_normal",
                        reaction.frameIndex, approved.count)
            }
            if reaction.frameIndex < hitReactB.count {
                return ("hit_react_b", reaction.frameIndex, hitReactB.count)
            }
        }
        if orangePunch.isActive && orangePunchAssetsAvailable {
            return (orangePunch.kind == .jab ? "jab_b" : "cross_b",
                    orangePunch.frameIndex, orangePunch.kind == .jab ? jabB.count : crossB.count)
        }
        if blockFeedback.isActive && blockRecoilAssetsAvailable {
            return (blockFeedback.kind == .cross ? "block_cross_b" : "block_jab_b",
                    blockFeedback.frameIndex, blockFeedback.kind == .cross ? blockCrossB.count : blockJabB.count)
        }
        if orangeRecovery.isRecovering {
            let jab = orangeRecovery.kind == .jab
            let dedicated = jab ? jabRecoveryB : crossRecoveryB
            if usesDedicatedRecoveryPoses && !dedicated.isEmpty {
                return (jab ? "jab_recovery_b" : "cross_recovery_b", 0, dedicated.count)
            }
            return (jab ? "jab_b" : "cross_b", orangeRecovery.kind.recoveryPoseFrame,
                    jab ? jabB.count : crossB.count)
        }
        if guardPlayback.isSelected && guardAssetsAvailable {
            if guardPlayback.isEffective && orangeLocomotionClip == .advance && !guardedAdvanceB.isEmpty {
                return ("guarded_advance_b", orangeFrame % guardedAdvanceB.count, guardedAdvanceB.count)
            }
            if guardPlayback.isEffective && orangeLocomotionClip == .retreat && !guardedRetreatB.isEmpty {
                return ("guarded_retreat_b", orangeFrame % guardedRetreatB.count, guardedRetreatB.count)
            }
            return ("guard_b", guardPlayback.frameIndex, guardB.count)
        }
        if orangeLocomotionClip == .advance && !advanceB.isEmpty {
            return ("advance_b", orangeFrame % advanceB.count, advanceB.count)
        }
        if orangeLocomotionClip == .retreat && !retreatB.isEmpty {
            return ("retreat_b", orangeFrame % retreatB.count, retreatB.count)
        }
        if orangeBounceAvailable { return ("orange_bounce", orangeBounceFrame, orangeBounceV3.count) }
        return ("idle_b", orangeFrame % max(1, idleB.count), idleB.count)
    }
    var orangeAnimationName: String { orangePresentedAnimation.name }
    var orangeFrameCount: Int { orangePresentedAnimation.count }
    var orangeFrameIndex: Int { orangePresentedAnimation.index }
    private var contactTracker = PunchContactTracker()
    private var health = FighterHealthState()
    var blueHealth: FighterHealth { health.blue }
    var orangeHealth: FighterHealth { health.orange }
    var blueCombatState: FighterCombatState { health.blueCombat.state }
    var orangeCombatState: FighterCombatState { health.orangeCombat.state }
    var orangeDefeatRecorded: Bool { health.orangeCombat.defeatRecorded }

    func resetHealth() {
        for actor in [FighterID.blue, .orange] {
            if actor == .blue ? punch.isActive : orangePunch.isActive {
                logCombat("ATTACK_INTERRUPTED", fighter: actor,
                    context: actor == .blue ? contactTracker.context : cpuContactTracker.context, detail: "RESET")
            }
        }
        logCombat("RESET", fighter: .blue)
        health.reset()
        blueRecovery.cancel(); orangeRecovery.cancel()
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
        orangeBounceFrame = 0; orangeBounceAccumulator = 0
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
        health.canExchangePunches && jabAssetsAvailable && boxerA != nil && hasFocus && isPlaying && !punch.isActive && !blueVisualBusy && !blueGuard.isSelected && !blueRecovery.isRecovering && !blueBlockFeedback.isActive && !guardHeld
    }
    var canStartCross: Bool {
        health.canExchangePunches && crossAssetsAvailable && boxerA != nil && hasFocus && isPlaying && !punch.isActive && !blueVisualBusy && !blueGuard.isSelected && !blueRecovery.isRecovering && !blueBlockFeedback.isActive && !guardHeld
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
    // Reversible presentation switch: false restores the Task 9B.1 withdrawal frames.
    var usesDedicatedRecoveryPoses = true
    private var jabRecoveryA: [SKTexture] = []
    private var crossRecoveryA: [SKTexture] = []
    private var jabRecoveryB: [SKTexture] = []
    private var crossRecoveryB: [SKTexture] = []
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
    private var guardedAdvanceA: [SKTexture] = []
    private var guardedRetreatA: [SKTexture] = []
    private var guardedAdvanceB: [SKTexture] = []
    private var guardedRetreatB: [SKTexture] = []
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
        blueRecovery.cancel(); orangeRecovery.cancel()
        clearBlueGuardInput()
        punch.cancel()
        reaction.cancel()
        orangeBounceFrame = 0; orangeBounceAccumulator = 0
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
        advanceSimulation(by: dt)
    }

    /// Production update entry point shared with deterministic XCTest drivers.
    /// Large intervals are rejected just as they are by the render-loop adapter.
    func advanceSimulation(by dt: Double, stepping: Bool = false) {
        guard boxerA != nil, boxerB != nil, dt.isFinite, dt >= 0, dt <= 0.25 else { return }
        guard (isPlaying || stepping), hasFocus else { return }
        // Resolve geometry at the marker, before movement in the rest of a tick.
        let marker = min(punch.timeUntilContact ?? .infinity, orangePunch.timeUntilContact ?? .infinity)
        if marker > 1e-9 && marker < dt - 1e-9 {
            advanceSimulation(by: marker, stepping: stepping)
            advanceSimulation(by: dt - marker, stepping: stepping)
            return
        }
        let blueGuardWasRaising = blueGuard.isSelected && !blueGuard.isEffective
        simulationTime += dt
        advancePhysicalRecovery(dt)
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
            advanceActiveAttacks(dt)
            guardEffectiveAtContact = nil
            applyFrames()
            publishIfNeeded()
            return
        }

        if blueVisualBusy || blueCombatState == .defeated || blueRecovery.isRecovering || blueBlockFeedback.isActive {
            motion.stop()
            advanceActiveAttacks(dt)
            applyFrames(); publishIfNeeded()
            return
        }
        advanceBlueFootwork(dt, guardEntry: blueGuardWasRaising)
        advanceActiveAttacks(dt)

        applyFrames()
        publishIfNeeded()
    }

    private func advanceBlueFootwork(_ dt: Double, guardEntry: Bool) {
        let enteringGuard = guardEntry || (blueGuard.isSelected && !blueGuard.isEffective)
        let direction = enteringGuard ? 0.0 : Double(movementDirection ?? 0)
        let segments = motion.advance(duration: dt, direction: direction,
            speedMultiplier: blueGuard.isEffective ? guardedMovementMultiplier : 1)
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
    }

    private var lastPublishedFrame = -1
    private var lastPublishedX: CGFloat = .nan
    private var lastPublishedClip: FighterClip?
    private var lastPublishedVelocity: Double = .nan
    private var lastPublishedOrangeFrame = -1
    private var lastPublishedOrangeClip: DefenderClip?
    private var lastPublishedMovement = ""
    private var lastPublishedActions = ""
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
            || blueMovementLabel + orangeMovementLabel != lastPublishedMovement
            || blueActionLabel + orangeActionLabel != lastPublishedActions
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
            lastPublishedMovement = blueMovementLabel + orangeMovementLabel
            lastPublishedActions = blueActionLabel + orangeActionLabel
            lastPublishedBlueGuard = blueGuardStatus
            lastPublishedBlueFX = blueBlockFeedbackLabel
            lastPublishedCPUAttack = cpuAttackLabel
            lastPublishedBlueAnimation = blueAnimationLabel
            onPlaybackChange?()
        }
    }

    func togglePlayback() {
        isPlaying.toggle()
        lastTime = 0
        if isPlaying {
            if !punch.isActive { settleIdle() }
            applyFrames()
        }
        onPlaybackChange?()
    }

    private var simulationStepDuration: Double {
        var duration = activeClip.cycleDuration / Double(activeClip.frameCount)
        if punch.isActive { duration = min(duration, punch.kind.frameDuration) }
        if orangePunch.isActive { duration = min(duration, orangePunch.kind.frameDuration) }
        if blueReaction.isActive { duration = min(duration, HitReactionPlayback.frameDuration) }
        if reaction.isActive { duration = min(duration, reaction.activeFrameDuration / (reaction.approvedOrangeArt ? playbackSpeed.rawValue : 1)) }
        if blueKnockdown.clip == .knockdown || knockdown.clip == .knockdown { duration = min(duration, KnockdownPlayback.frameDuration) }
        if blueKnockdown.clip == .rise || knockdown.clip == .rise { duration = min(duration, KnockdownPlayback.riseFrameDuration) }
        if blueGuard.isSelected || guardPlayback.isSelected { duration = min(duration, GuardPlayback.frameDuration) }
        if blueBlockFeedback.isActive { duration = min(duration, blueBlockFeedback.frameDuration) }
        if blockFeedback.isActive { duration = min(duration, blockFeedback.frameDuration) }
        if blueRecovery.isRecovering { duration = min(min(duration, 0.04), blueRecovery.remaining) }
        if orangeRecovery.isRecovering { duration = min(min(duration, 0.04), orangeRecovery.remaining) }
        return max(1e-6, duration)
    }

    func stepFrame() {
        isPlaying = false
        lastTime = 0
        advanceSimulation(by: simulationStepDuration, stepping: true)
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
        holdAdvance = held && isPlaying && hasFocus && !blueVisualBusy && blueCombatState == .standing
        onPlaybackChange?()
    }

    func setRetreatHeld(_ held: Bool) {
        holdRetreat = held && isPlaying && hasFocus && !blueVisualBusy && blueCombatState == .standing
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
            orangeRecovery.begin(kind)
            attackSequence += 1
            cpuContactTracker.begin(kind, attackerID: .orange, attackID: attackSequence, startTime: simulationTime,
                                    counterAttempt: isAttackVulnerable(.blue))
            logAttackStart(.orange, context: cpuContactTracker.context)
            stopCPUFootwork()
            defensiveAI.cancel()
            cpuStartedThisTick = true
            onPlaybackChange?()
            return true
        }
        let available = kind == .jab ? canStartJab : canStartCross
        guard available, punch.start(kind) else { return false }
        blueRecovery.begin(kind)
        motion.stop()
        attackSequence += 1
        contactTracker.begin(kind, attackerID: .blue, attackID: attackSequence, startTime: simulationTime,
                             counterAttempt: isAttackVulnerable(.orange))
        logAttackStart(.blue, context: contactTracker.context)
        punchStartSequence += 1
        defensiveAI.observe(sequence: punchStartSequence, kind: kind,
                            inRange: predictedContact(.blue, kind: kind), eligible: canRequestGuard)
        if defensiveAI.state == .reacting && !orangePunch.isActive { cpuOffense.cancelPreparation() }
        setClip(kind == .jab ? .jab : .cross)
        lastTime = 0
        applyFrames(); onPlaybackChange?()
        return true
    }

    private func logAttackStart(_ fighter: FighterID, context: AttackContext?) {
        logCombat("ATTACK_START", fighter: fighter, context: context)
        if context?.isCounterAttempt == true { logCombat("COUNTER_ATTEMPT", fighter: fighter, context: context) }
    }

    private func predictedContact(_ attacker: FighterID, kind: PunchKind) -> Bool {
        let a = canvasTransform(for: attacker == .blue ? boxerA : boxerB)
        let b = canvasTransform(for: attacker == .blue ? boxerB : boxerA)
        return PunchContactGeometry.intersects(center: a.scenePoint(fromImage: contactGeometry.center(for: kind)),
            radius: a.sceneRadius(fromImage: contactGeometry.radius(for: kind)),
            target: b.sceneRect(fromImage: contactGeometry.defenderTarget))
    }

    @discardableResult
    private func resolveContact(_ attacker: FighterID, kind: PunchKind, deferImpact: Bool = false) -> PunchContactEvent? {
        guard health.canExchangePunches else { return nil }
        var tracker = attacker == .blue ? contactTracker : cpuContactTracker
        let contact = tracker.evaluate(kind,
            attacker: canvasTransform(for: attacker == .blue ? boxerA : boxerB),
            defender: canvasTransform(for: attacker == .blue ? boxerB : boxerA), geometry: contactGeometry,
            guardEffective: attacker == .blue
                ? (guardEffectiveAtContact ?? guardPlayback.isEffective)
                : (blueGuardEffectiveAtContact ?? blueGuard.isEffective))
        if attacker == .blue { contactTracker = tracker } else { cpuContactTracker = tracker }
        guard let event = contact else { return nil }
        if !deferImpact { applyContact(event) }
        return event
    }

    private func applyContact(_ event: PunchContactEvent, simultaneous: Bool = false) {
        let previousHealth = event.defenderID == .blue ? blueHealth.current : orangeHealth.current
        logCombat("CONTACT_" + event.result.rawValue.uppercased(), fighter: event.attackerID,
                  context: event.attackerID == .blue ? contactTracker.context : cpuContactTracker.context,
                  detail: "defender=\(event.defenderID)")
        if event.isSuccessfulCounter { logCombat("COUNTER_SUCCESS", fighter: event.attackerID,
            context: event.attackerID == .blue ? contactTracker.context : cpuContactTracker.context) }
        if event.result == .hit {
            let interrupted = event.defenderID == .blue ? punch.isActive : orangePunch.isActive
            if interrupted { logCombat("ATTACK_INTERRUPTED", fighter: event.defenderID,
                context: event.defenderID == .blue ? contactTracker.context : cpuContactTracker.context) }
        }
        health.receive(event, simultaneous: simultaneous)
        let nextHealth = event.defenderID == .blue ? blueHealth.current : orangeHealth.current
        if previousHealth != nextHealth { logCombat("HEALTH_CHANGED", fighter: event.defenderID,
            context: event.attackerID == .blue ? contactTracker.context : cpuContactTracker.context, detail: "\(previousHealth)->\(nextHealth)") }
        if event.isCounterAttempt {
            let actor = event.attackerID == .blue ? "BLUE" : "ORANGE"
            let kind = event.kind == .jab ? "JAB" : "CROSS"
            lastCounterText = "Last Counter: \(actor) \(kind) \(event.result.rawValue)"
        }
        if event.result == .hit {
            if event.defenderID == .orange {
                orangeRecovery.cancel()
                defensiveAI.cancel(); stopCPUFootwork()
                guardPlayback.cancel(); blockFeedback.cancel()
                if orangePunch.isActive {
                    orangePunch.cancel(); cpuContactTracker.finish(); cpuOffense.finished()
                } else { cpuOffense.cancelPreparation() }
                if reactionAssetsAvailable { reaction.receive(.hit, from: event.kind) }
                orangeBounceFrame = 0; orangeBounceAccumulator = 0
                orangeFrame = 0; orangeAccumulator = 0
                startKnockdownIfReady()
            } else {
                blueRecovery.cancel()
                punch.cancel(); contactTracker.finish()
                blueGuard.cancel(); blueBlockFeedback.cancel()
                clearHeldInput(); motion.stop(); settleIdle()
                if blueCombatState == .defeated { clearBlueGuardInput() }
                if blueRecoveryAssetsAvailable { blueReaction.receive(.hit, from: event.kind) }
            }
        } else if event.result == .block {
            if event.defenderID == .blue { motion.stop() } else { stopCPUFootwork() }
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
        if event.completed {
            logCombat("ATTACK_END", fighter: .blue, context: contactTracker.context)
            contactTracker.finish(); motion.stop(); settleIdle()
            blueRecovery.completeAttack()
            syncBlueGuard()
        } else if punch.isActive { frameIndex = punch.frameIndex }
    }

    private func advanceCPUOffense(_ dt: Double) {
        if !health.canExchangePunches { cpuOffense.disable(); return }
        if let kind = cpuOffense.advance(dt, enabled: cpuEnabled, eligible: canCPUAttack,
            jabInRange: predictedContact(.orange, kind: .jab), crossInRange: predictedContact(.orange, kind: .cross),
            opponentVulnerable: isAttackVulnerable(.blue)) {
            if !beginAttack(.orange, kind: kind) { cpuOffense.cancel() }
        }
    }
    private func advanceActiveAttacks(_ dt: Double) {
        let blueKind = punch.kind
        let orangeKind = orangePunch.kind
        let blueTime = punch.timeUntilContact ?? .infinity
        let orangeTime = orangePunch.timeUntilContact ?? .infinity
        let blueEvent = punch.advance(dt, preserveContactPose: true)
        let orangeEvent: (contact: Bool, completed: Bool)
        if cpuStartedThisTick {
            cpuStartedThisTick = false
            orangeEvent = (false, false)
        } else { orangeEvent = orangePunch.advance(dt, preserveContactPose: true) }
        defer { diagnosticContactTime = nil }
        if blueEvent.contact && orangeEvent.contact && abs(blueTime-orangeTime) < 1e-9 {
            diagnosticContactTime = simulationTime - dt + blueTime
            // Snapshot both legal contacts BEFORE reactions cancel either clock.
            let blueContact = resolveContact(.blue, kind: blueKind, deferImpact: true)
            let orangeContact = resolveContact(.orange, kind: orangeKind, deferImpact: true)
            if let event = blueContact { applyContact(event, simultaneous: true) }
            if let event = orangeContact { applyContact(event, simultaneous: true) }
        } else if blueTime <= orangeTime {
            if blueEvent.contact { diagnosticContactTime = simulationTime - dt + blueTime; resolveContact(.blue, kind: blueKind) }
            if orangeEvent.contact && orangePunch.isActive { diagnosticContactTime = simulationTime - dt + orangeTime; resolveContact(.orange, kind: orangeKind) }
        } else {
            if orangeEvent.contact { diagnosticContactTime = simulationTime - dt + orangeTime; resolveContact(.orange, kind: orangeKind) }
            if blueEvent.contact && punch.isActive { diagnosticContactTime = simulationTime - dt + blueTime; resolveContact(.blue, kind: blueKind) }
        }
        diagnosticContactTime = nil
        if blueEvent.completed && blueRecovery.phase == .attacking {
            handlePunchEvent(blueEvent)
        } else if punch.isActive { frameIndex = punch.frameIndex }
        if orangeEvent.completed && orangeRecovery.phase == .attacking {
            logCombat("ATTACK_END", fighter: .orange, context: cpuContactTracker.context)
            cpuContactTracker.finish(); cpuOffense.finished()
            orangeRecovery.completeAttack()
            orangeFrame = 0; orangeAccumulator = 0
        }
    }
    private func advanceBlueRecovery(_ dt: Double) {
        if blueKnockdown.hasStarted {
            let completed = blueKnockdown.advance(dt)
            if completed {
                blueRecovery.cancel()
                health.recoverBlue(); clearHeldInput(); clearBlueGuardInput(); motion.stop(); settleIdle()
                frameIndex = 0; blueAccumulator = 0
                cpuOffense.cancel(); defensiveAI.cancel()
                onPlaybackChange?()
            }
        } else if blueReaction.isActive {
            let completed = blueReaction.advance(dt)
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
        orangeRecovery.cancel()
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
        if orangeRecovery.isRecovering || blockFeedback.isActive {
            stopCPUFootwork()
            return
        }
        if knockdown.hasStarted {
            if knockdown.advance(dt) { completeOrangeRecovery() }
        } else if reaction.isActive {
            if reaction.advance(dt * (reaction.approvedOrangeArt ? playbackSpeed.rawValue : 1)) {
                orangeFrame = 0
                orangeAccumulator = 0
                // Last approved pose matches guard 00; resume bounce at 01.
                if orangeBounceAvailable { orangeBounceFrame = 1; orangeBounceAccumulator = 0 }
                // Display fall frame zero now; never consume this tick twice.
                startKnockdownIfReady()
            }
        } else if guardPlayback.isSelected {
            let wasEffective = guardPlayback.isEffective
            guardPlayback.advance(dt)
            if wasEffective != guardPlayback.isEffective { onPlaybackChange?() }
            advanceCPUFootwork(dt, guardEntry: !wasEffective)
        } else if orangeCombatState == .standing {
            advanceCPUFootwork(dt)
        }
        // Independent approved bounce clock. Root movement stays in CPU footwork.
        if orangeCombatState == .standing && !reaction.isActive && !knockdown.hasStarted
            && !guardPlayback.isSelected && !orangePunch.isActive && !orangeRecovery.isRecovering
            && !blockFeedback.isActive && orangeLocomotionClip == .idle && orangeBounceAvailable {
            orangeBounceAccumulator += dt * playbackSpeed.rawValue
            let interval = 1.105 / Double(orangeBounceV3.count)
            while orangeBounceAccumulator >= interval {
                orangeBounceAccumulator -= interval
                orangeBounceFrame = (orangeBounceFrame + 1) % orangeBounceV3.count
            }
        }
    }

    private func advanceCPUFootwork(_ dt: Double, guardEntry: Bool = false) {
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
        let direction = guardEntry || cpuOffense.state == .preparing ? 0.0
            : (cpuDistance.intent == .advance ? -1.0 : (cpuDistance.intent == .retreat ? 1.0 : 0))
        for segment in orangeMotion.advance(duration: dt, direction: direction,
            speedMultiplier: guardPlayback.isEffective ? guardedMovementMultiplier : 1) {
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
        jabRecoveryA = loadPunchTextures(prefix: "jab_recovery_a", count: 1)
        crossRecoveryA = loadPunchTextures(prefix: "cross_recovery_a", count: 1)
        jabRecoveryB = loadPunchTextures(prefix: "jab_recovery_b", count: 1)
        crossRecoveryB = loadPunchTextures(prefix: "cross_recovery_b", count: 1)
        jabAssetsAvailable = jabA.count == PunchKind.jab.frameCount
        crossAssetsAvailable = crossA.count == PunchKind.cross.frameCount
        orangeBounceV3 = loadNumberedTextures(prefix: "orange_bounce", count: 17)
        orangeNormalV1 = loadNumberedTextures(prefix: "orange_normal", count: 18)
        orangeHeavyV1 = loadNumberedTextures(prefix: "orange_heavy", count: 14)
        reaction.setApprovedOrangeArt(orangeNormalV1.count == 18 && orangeHeavyV1.count == 14)
        hitReactB = loadPunchTextures(prefix: "hit_react_b", count: HitReactionPlayback.frameCount)
        reactionAssetsAvailable = hitReactB.count == HitReactionPlayback.frameCount
            || (orangeNormalV1.count == 18 && orangeHeavyV1.count == 14)
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
        guardedAdvanceA = loadPunchTextures(prefix: "guarded_advance_a", count: 6)
        guardedRetreatA = loadPunchTextures(prefix: "guarded_retreat_a", count: 6)
        guardedAdvanceB = loadPunchTextures(prefix: "guarded_advance_b", count: 6)
        guardedRetreatB = loadPunchTextures(prefix: "guarded_retreat_b", count: 6)
        blockJabB = loadPunchTextures(prefix: "block_jab_b", count: BlockFeedbackPlayback.frameCount)
        blockCrossB = loadPunchTextures(prefix: "block_cross_b", count: BlockFeedbackPlayback.frameCount)
        blockRecoilAssetsAvailable = blockJabB.count == BlockFeedbackPlayback.frameCount
            && blockCrossB.count == BlockFeedbackPlayback.frameCount
    }

    private func loadNumberedTextures(prefix: String, count: Int) -> [SKTexture] {
        let images = (0..<count).compactMap { UIImage(named: String(format: "%@_%02d", prefix, $0)) }
        guard images.count == count, images.allSatisfy({ $0.cgImage?.width == 512 && $0.cgImage?.height == 512 }) else { return [] }
        return images.map { image in
            // Approved Orange art faces left already. Pre-flip its pixels so
            // rootB's existing mirror restores left-facing art without changing
            // the SpriteKit child transform used by contact geometry.
            let renderer = UIGraphicsImageRenderer(size: image.size)
            let corrected = renderer.image { context in
                context.cgContext.translateBy(x: image.size.width, y: 0)
                context.cgContext.scaleBy(x: -1, y: 1)
                image.draw(at: .zero)
            }
            let texture = SKTexture(image: corrected)
            texture.filteringMode = .linear
            return texture
        }
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
        observeCombatTransitions()
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
        } else if blueBlockFeedback.isActive && playerGuardAssetsAvailable {
            let textures = blueBlockFeedback.kind == .cross ? blockCrossA : blockJabA
            boxerA.texture = textures[blueBlockFeedback.frameIndex]
        } else if blueRecovery.isRecovering {
            let textures = blueRecovery.kind == .jab ? jabA : crossA
            let dedicated = blueRecovery.kind == .jab ? jabRecoveryA : crossRecoveryA
            boxerA.texture = usesDedicatedRecoveryPoses && !dedicated.isEmpty
                ? dedicated[0] : textures[blueRecovery.kind.recoveryPoseFrame]
        } else if blueGuard.isSelected && playerGuardAssetsAvailable {
            // Entry and stationary guard retain their authoritative guard clock.
            // Once raised, walking uses the existing travel-driven footwork phase.
            if blueGuard.isEffective && activeClip == .advance && !guardedAdvanceA.isEmpty {
                boxerA.texture = guardedAdvanceA[frameIndex % guardedAdvanceA.count]
            } else if blueGuard.isEffective && activeClip == .retreat && !guardedRetreatA.isEmpty {
                boxerA.texture = guardedRetreatA[frameIndex % guardedRetreatA.count]
            } else {
                boxerA.texture = guardA[blueGuard.frameIndex]
            }
        } else { boxerA.texture = blueTextures[frameIndex % blueTextures.count] }
        if knockdown.clip == .knockdown && knockdownAssetsAvailable {
            boxerB.texture = knockdownB[knockdown.frameIndex]
        } else if knockdown.clip == .rise && riseAssetsAvailable {
            boxerB.texture = riseB[knockdown.frameIndex]
        } else if knockdown.clip == .down && knockdownAssetsAvailable {
            boxerB.texture = downB[0]
        } else if reaction.isActive && reactionAssetsAvailable {
            let approved = reaction.profile?.punch == .cross ? orangeHeavyV1 : orangeNormalV1
            if reaction.approvedOrangeArt && reaction.frameIndex < approved.count {
                boxerB.texture = approved[reaction.frameIndex]
            } else if reaction.frameIndex < hitReactB.count {
                boxerB.texture = hitReactB[reaction.frameIndex]
            }
        } else if orangePunch.isActive && orangePunchAssetsAvailable {
            let textures = orangePunch.kind == .jab ? jabB : crossB
            boxerB.texture = textures[orangePunch.frameIndex]
        } else if blockFeedback.isActive && blockRecoilAssetsAvailable {
            let textures = blockFeedback.kind == .cross ? blockCrossB : blockJabB
            boxerB.texture = textures[blockFeedback.frameIndex]
        } else if orangeRecovery.isRecovering {
            let textures = orangeRecovery.kind == .jab ? jabB : crossB
            let dedicated = orangeRecovery.kind == .jab ? jabRecoveryB : crossRecoveryB
            boxerB.texture = usesDedicatedRecoveryPoses && !dedicated.isEmpty
                ? dedicated[0] : textures[orangeRecovery.kind.recoveryPoseFrame]
        } else if guardPlayback.isSelected && guardAssetsAvailable {
            if guardPlayback.isEffective && orangeLocomotionClip == .advance && !guardedAdvanceB.isEmpty {
                boxerB.texture = guardedAdvanceB[orangeFrame % guardedAdvanceB.count]
            } else if guardPlayback.isEffective && orangeLocomotionClip == .retreat && !guardedRetreatB.isEmpty {
                boxerB.texture = guardedRetreatB[orangeFrame % guardedRetreatB.count]
            } else {
                boxerB.texture = guardB[guardPlayback.frameIndex]
            }
        } else if orangeLocomotionClip == .advance && !advanceB.isEmpty {
            boxerB.texture = advanceB[orangeFrame % advanceB.count]
        } else if orangeLocomotionClip == .retreat && !retreatB.isEmpty {
            boxerB.texture = retreatB[orangeFrame % retreatB.count]
        } else {
            boxerB.texture = orangeBounceAvailable ? orangeBounceV3[orangeBounceFrame] : idleB[orangeFrame % idleB.count]
        }
        applyOrangeVisualPose()
        applyImpactEmphasis()
        textureCanvasInfo = "child A\(Int(boxerA.size.width)) B\(Int(boxerB.size.width)) · tex A\(Int(boxerA.texture?.size().width ?? 0)) B\(Int(boxerB.texture?.size().width ?? 0))"
        updateContactGuides()
    }

    /// Approved Orange art is corrected when textures load. Keep the SpriteKit
    /// child unmirrored so the established contact geometry is unchanged.
    /// Normal and heavy reactions have distinct recoil envelopes.
    private func applyOrangeVisualPose() {
        let approvedReaction = reaction.isActive && reaction.approvedOrangeArt
        // Keep child geometry at +1: contact and spacing transforms rely on it.
        boxerB.xScale = 1
        boxerB.yScale = 1
        boxerB.zRotation = 0

        guard approvedReaction else { return }
        let progress = Double(reaction.frameIndex) / Double(max(1, reaction.activeFrameCount - 1))
        let isHeavy = reaction.profile?.punch == .cross
        // The cross recoils farther and holds a visible off-balance pose.
        // The final pose settles at zero so bounce resumes without a jump.
        let envelope = pow(sin(.pi * progress), isHeavy ? 0.65 : 1.4)
        boxerB.zRotation = CGFloat((isHeavy ? -9.0 : -2.0) * .pi / 180 * envelope)
        boxerB.yScale = CGFloat(1 - (isHeavy ? 0.035 : 0.008) * envelope)
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
