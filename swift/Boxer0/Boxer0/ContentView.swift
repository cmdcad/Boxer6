//
//  ContentView.swift
//  Boxer0
//

import SpriteKit
import SwiftUI
import UIKit

final class IdlePlayback: ObservableObject {
    let scene: IdleTestScene

    @Published var blueCombatState = FighterCombatState.standing
    @Published var orangeCombatState = FighterCombatState.standing
    @Published var blueHealth = 100
    @Published var orangeHealth = 100
    @Published var matchRound = 1
    @Published var matchSecondsRemaining = 120.0
    @Published var bluePoints = 0
    @Published var orangePoints = 0
    @Published var matchResult: MatchResult?
    @Published var blueStamina = 100.0
    @Published var orangeStamina = 100.0
    @Published var blueAwareness = 100.0
    @Published var orangeAwareness = 100.0
    @Published var blueMaximumHealth = 100
    @Published var orangeMaximumHealth = 100
    @Published var isPlaying = true
    @Published var frameIndex = 0
    @Published var frameCount = 4
    @Published var showsGuides = true
    @Published var clipName = FighterClip.idle.rawValue
    @Published var positionX = 0
    @Published var velocityX = 0
    @Published var inputGeneration = 0
    @Published var vulnerabilityText = ""
    @Published var counterSummary = ""
    @Published var lastCounterText = ""
    @Published var movementReadout = ""
    @Published var combatLogEnabled = false
    @Published var recentCombatEvents = ""
    func toggleCombatLog() { scene.setCombatLogging(!scene.combatLog.enabled); syncFromScene() }
    func copyCombatLog() { UIPasteboard.general.string = scene.combatLog.text }
    @Published var blueAction = "READY"
    @Published var orangeAction = "READY"
    @Published var guardHeld = false
    @Published var guardInputGeneration = 0
    @Published var canHoldGuard = false
    @Published var playerGuardAssetsAvailable = false
    @Published var blueGuardStatus = "LOWERED"
    @Published var blueBlockFX = "OFF"
    @Published var cpuAttack = "READY"
    @Published var cpuStats = ""
    @Published var cpuLastResult = "-"
    @Published var blueAnimation = "idle"
    @Published var canBlueRise = false
    @Published var bidirectionalAssetsAvailable = false
    @Published var cpuMovement = "hold"
    @Published var cpuEnabled = false
    @Published var cpuStatus = "OFF"
    @Published var blockCount = 0
    @Published var latestWasBlock = false
    @Published var blockFeedbackLabel = "OFF"
    @Published var blockRecoilAssetsAvailable = false
    @Published var guardStatus = "OFF"
    @Published var guardSelected = false
    @Published var canToggleGuard = false
    @Published var guardAssetsAvailable = false
    @Published var hitCount = 0
    @Published var missCount = 0
    @Published var latestResultText = "No contact yet"
    @Published var latestDistanceText = ""
    @Published var latestTransformText = ""
    @Published var canvasInfo = ""
    @Published var latestWasHit = false
    @Published var hasContactResult = false
    @Published var orangeState = DefenderClip.idle.rawValue
    @Published var orangeProfile = ""
    @Published var orangeFrameIndex = 0
    @Published var orangeFrameCount = 4
    @Published var knockdownAssetsAvailable = false
    @Published var riseAssetsAvailable = false
    @Published var canRise = false
    @Published var reactionAssetsAvailable = false
    @Published var canJab = false
    @Published var canCross = false
    @Published var crossAssetsAvailable = false
    @Published var crossContact = false
    @Published var crossContactCount = 0
    @Published var jabAssetsAvailable = false
    @Published var jabContact = false
    @Published var jabContactCount = 0
    @Published var holdAdvance = false
    @Published var holdRetreat = false

    init() {
        let scene = IdleTestScene(size: CGSize(width: 844, height: 390))
        scene.scaleMode = .resizeFill
        self.scene = scene
        scene.onPlaybackChange = { [weak self] in
            DispatchQueue.main.async {
                self?.syncFromScene()
            }
        }
    }

    func syncFromScene() {
        matchRound = scene.match.round
        matchSecondsRemaining = scene.match.remaining
        bluePoints = scene.match.bluePoints
        orangePoints = scene.match.orangePoints
        matchResult = scene.match.result
        blueCombatState = scene.blueCombatState
        orangeCombatState = scene.orangeCombatState
        blueHealth = scene.blueHealth.current
        orangeHealth = scene.orangeHealth.current
        blueStamina = scene.blueMeters.stamina
        orangeStamina = scene.orangeMeters.stamina
        blueAwareness = scene.blueMeters.awareness
        orangeAwareness = scene.orangeMeters.awareness
        blueMaximumHealth = scene.blueHealth.maximum
        orangeMaximumHealth = scene.orangeHealth.maximum
        isPlaying = scene.isPlaying
        frameIndex = scene.frameIndex
        frameCount = scene.activeClip.frameCount
        showsGuides = scene.showsGuides
        clipName = scene.activeClip.rawValue
        positionX = Int(scene.bluePositionX.rounded())
        velocityX = Int(scene.horizontalVelocity.rounded())
        holdAdvance = scene.advanceHeld
        holdRetreat = scene.retreatHeld
        inputGeneration = scene.inputGeneration
        canJab = scene.canStartJab
        canCross = scene.canStartCross
        crossAssetsAvailable = scene.crossAssetsAvailable
        crossContact = scene.showsCrossContact
        crossContactCount = scene.crossContactCount
        jabAssetsAvailable = scene.jabAssetsAvailable
        jabContact = scene.showsJabContact
        jabContactCount = scene.jabContactCount
        vulnerabilityText = "Vulnerable Blue: \(scene.isAttackVulnerable(.blue) ? "YES" : "NO") · Orange: \(scene.isAttackVulnerable(.orange) ? "YES" : "NO")"
        counterSummary = scene.counterSummary
        lastCounterText = scene.lastCounterText
        movementReadout = "Blue Move: \(scene.blueMovementLabel) | Orange Move: \(scene.orangeMovementLabel)"
        combatLogEnabled = scene.combatLog.enabled
        recentCombatEvents = scene.combatLog.recent
        blueAction = scene.blueActionLabel
        orangeAction = scene.orangeActionLabel
        guardHeld = scene.guardHeld
        guardInputGeneration = scene.guardInputGeneration
        canHoldGuard = scene.canHoldGuard
        playerGuardAssetsAvailable = scene.playerGuardAssetsAvailable
        blueGuardStatus = scene.blueGuardStatus
        blueBlockFX = scene.blueBlockFeedbackLabel
        cpuAttack = scene.cpuAttackLabel
        cpuStats = scene.cpuStats
        cpuLastResult = scene.cpuLastResult
        blueAnimation = scene.blueAnimationLabel
        canBlueRise = scene.canBlueRise
        bidirectionalAssetsAvailable = scene.orangePunchAssetsAvailable && scene.blueRecoveryAssetsAvailable
        cpuMovement = scene.cpuMovementLabel
        cpuEnabled = scene.cpuEnabled
        cpuStatus = scene.cpuStatus
        blockCount = scene.blockCount
        blockFeedbackLabel = scene.blockFeedbackLabel
        blockRecoilAssetsAvailable = scene.blockRecoilAssetsAvailable
        guardStatus = scene.guardStatus
        guardSelected = scene.guardSelected
        canToggleGuard = scene.canToggleGuard
        guardAssetsAvailable = scene.guardAssetsAvailable
        hitCount = scene.hitCount
        missCount = scene.missCount
        canvasInfo = scene.textureCanvasInfo
        orangeState = scene.orangeAnimationName
        orangeProfile = scene.orangeProfileLabel
        orangeFrameIndex = scene.orangeFrameIndex
        orangeFrameCount = scene.orangeFrameCount
        knockdownAssetsAvailable = scene.knockdownAssetsAvailable
        riseAssetsAvailable = scene.riseAssetsAvailable
        canRise = scene.canRise || scene.canBlueRise
        reactionAssetsAvailable = scene.reactionAssetsAvailable
        if let event = scene.latestContact {
            latestResultText = "\(event.kind == .jab ? "JAB" : "CROSS") · \(event.result.rawValue)"
            latestWasHit = event.result == .hit
            latestWasBlock = event.result == .block
            hasContactResult = true
            latestDistanceText = String(format: "d %.2f r %.2f gap %+.2f pt",
                Double(event.centerDistance), Double(event.radius), Double(event.signedGap))
            latestTransformText = String(format: "roots %.2f · Ax %.3f Bx %.3f",
                Double(abs(event.attacker.rootPosition.x - event.defender.rootPosition.x)),
                Double(event.attacker.scaleX), Double(event.defender.scaleX))
        }
    }

    func setGuardHeld(_ held: Bool) {
        playerDidInteract()
        scene.setGuardHeld(held)
        syncFromScene()
    }

    // Future Settings switch. The current default starts a countdown only if
    // the player has not interacted during the first five seconds.
    var autoStartCountdownEnabled = true
    @Published private(set) var cpuStarting = false
    private var cpuStartGeneration = 0
    private var idleStartGeneration = 0
    private var sessionActive = false
    private var playerResponded = false
    private var didPlayLaunchHaptic = false

    func beginSession() {
        guard !sessionActive else { return }
        sessionActive = true
        playerResponded = false
        if !didPlayLaunchHaptic {
            didPlayLaunchHaptic = true
            let feedback = UIImpactFeedbackGenerator(style: .medium)
            feedback.prepare()
            feedback.impactOccurred()
        }
        guard autoStartCountdownEnabled, !scene.cpuEnabled else { return }
        idleStartGeneration += 1
        let generation = idleStartGeneration
        DispatchQueue.main.asyncAfter(deadline: .now() + 5) { [weak self] in
            guard let self = self, self.sessionActive, !self.playerResponded,
                  self.idleStartGeneration == generation,
                  !self.cpuStarting, !self.scene.cpuEnabled else { return }
            self.startCPUCountdown()
        }
    }

    /// Any deliberate player input prevents unattended auto-start this session.
    func playerDidInteract() {
        guard sessionActive else { return }
        playerResponded = true
        idleStartGeneration += 1
    }

    func toggleCPU() {
        playerDidInteract()
        if cpuStarting {
            cancelCPUStart()
            return
        }
        if scene.cpuEnabled {
            scene.toggleCPU()
            syncFromScene()
            return
        }
        startCPUCountdown()
    }

    private func startCPUCountdown() {
        guard sessionActive, !cpuStarting, !scene.cpuEnabled else { return }
        cpuStarting = true
        cpuStartGeneration += 1
        let generation = cpuStartGeneration
        for second in 0...5 {
            DispatchQueue.main.asyncAfter(deadline: .now() + Double(second)) { [weak self] in
                guard let self = self, self.sessionActive, self.cpuStarting,
                      self.cpuStartGeneration == generation else { return }
                if second < 5 {
                    let feedback = UIImpactFeedbackGenerator(style: .medium)
                    feedback.prepare()
                    feedback.impactOccurred()
                } else {
                    let feedback = UINotificationFeedbackGenerator()
                    feedback.prepare()
                    feedback.notificationOccurred(.success)
                    self.cpuStarting = false
                    if !self.scene.cpuEnabled { self.scene.toggleCPU() }
                    self.syncFromScene()
                }
            }
        }
    }

    func cancelCPUStart() {
        cpuStartGeneration += 1
        cpuStarting = false
    }

    func endSession() {
        sessionActive = false
        idleStartGeneration += 1
        cancelCPUStart()
    }

    func toggleGuard() {
        playerDidInteract()
        scene.toggleGuard()
        syncFromScene()
    }

    func rise() {
        playerDidInteract()
        if scene.canBlueRise { scene.startBlueRise() }
        else { scene.startRise() }
        syncFromScene()
    }

    func resetHealth() {
        playerDidInteract()
        scene.resetHealth()
        syncFromScene()
    }

    func cross() {
        playerDidInteract()
        scene.startCross()
        syncFromScene()
    }

    func jab() {
        playerDidInteract()
        scene.startJab()
        syncFromScene()
    }

    func togglePlayback() {
        playerDidInteract()
        scene.togglePlayback()
        syncFromScene()
    }

    func step() {
        playerDidInteract()
        scene.stepFrame()
        syncFromScene()
    }

    func toggleGuides() {
        playerDidInteract()
        scene.toggleGuides()
        syncFromScene()
    }

    func setAdvance(_ held: Bool) {
        playerDidInteract()
        scene.setAdvanceHeld(held)
        syncFromScene()
    }

    func setRetreat(_ held: Bool) {
        playerDidInteract()
        scene.setRetreatHeld(held)
        syncFromScene()
    }

    /// Single source of movement-pad input; vertical entry requests a slip.
    /// Only a correctly timed incoming CPU punch can be avoided.
    private var previousPadVertical = 0
    func setPadDirection(horizontal: Int, vertical: Int) {
        playerDidInteract()
        if vertical != 0 && previousPadVertical == 0 {
            scene.requestBlueSlip()
        }
        previousPadVertical = vertical
        scene.setRetreatHeld(horizontal < 0)
        scene.setAdvanceHeld(horizontal > 0)
        syncFromScene()
    }

    func cancelMovement() {
        previousPadVertical = 0
        holdAdvance = false
        holdRetreat = false
        scene.cancelMovement()
        syncFromScene()
    }
}

struct ContentView: View {
    @StateObject internal var playback = IdlePlayback()
    // Development presentation only; hiding it does not change locomotion.
    @State private var showsDevelopmentDiagnostics = false

    var body: some View {
        VStack(spacing: 0) {
            healthHUD
            matchHUD
            SpriteView(scene: playback.scene)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .layoutPriority(0)
                .overlay(alignment: .topLeading) {
                    if showsDevelopmentDiagnostics && playback.showsGuides {
                        diagnosticsPanel
                    }
                    
                }

            VStack(spacing: 4) {
                HStack(alignment: .center, spacing: 12) {
                    movementPad
                    Button(showsDevelopmentDiagnostics ? "Hide Dev" : "Dev") {
                        showsDevelopmentDiagnostics.toggle()
                    }
                    .font(.system(size: 12, weight: .semibold))
                    .buttonStyle(.bordered)
                    .fixedSize(horizontal: true, vertical: false)
                    Spacer(minLength: 4)
                    HStack(spacing: 8) {
                        punchButton("Jab", enabled: playback.canJab, action: playback.jab)
                        punchButton("Cross", enabled: playback.canCross, action: playback.cross)
                        playerGuardControl
                    }
                    .frame(maxWidth: .infinity, alignment: .trailing)
                }
                .padding(.horizontal, 12)
                .padding(.top, 8)
                if showsDevelopmentDiagnostics {
                    HStack(spacing: 8) {
                        statusLabel
                        Spacer(minLength: 0)
                        debugControls
                    }
                    .padding(.horizontal, 12)
                    .padding(.bottom, 6)
                }

            }
            .fixedSize(horizontal: false, vertical: true)
            .frame(maxWidth: .infinity)
            .background(Color(red: 0.85, green: 0.89, blue: 0.93))
            .layoutPriority(1)
        }
        .background(Color(red: 0.91, green: 0.933, blue: 0.957).ignoresSafeArea())
        .preferredColorScheme(ColorScheme.light)
        .onAppear {
            playback.scene.debugOverlaysEnabled = showsDevelopmentDiagnostics
            playback.syncFromScene()
            playback.beginSession()
        }
        .simultaneousGesture(TapGesture().onEnded {
            playback.playerDidInteract()
        })
        .onChange(of: showsDevelopmentDiagnostics) { enabled in
            playback.scene.debugOverlaysEnabled = enabled
        }
        .onReceive(NotificationCenter.default.publisher(for: UIApplication.willResignActiveNotification)) { _ in
            playback.cancelMovement()
            playback.endSession()
        }
        .onDisappear {
            playback.cancelMovement()
            playback.endSession()
        }
    }

    private var diagnosticColor: Color {
        guard playback.hasContactResult else { return Color.secondary }
        if playback.latestWasBlock { return Color.blue }
        return playback.latestWasHit ? Color.green : Color.red
    }

    private var diagnosticsPanel: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(playback.latestResultText)
            orangeAnimationReadout
            combatReadout
            counterReadout
            if playback.combatLogEnabled { Text(playback.recentCombatEvents).font(.system(size: 9, design: .monospaced)) }
            assetWarnings
            contactGeometryReadout
        }
        .font(Font.system(size: 13, weight: .bold, design: .monospaced))
        .foregroundColor(diagnosticColor)
        .padding(6)
        .background(Color.white.opacity(0.85), in: RoundedRectangle(cornerRadius: 8))
        .padding(8)
        .allowsHitTesting(false)
    }

    @ViewBuilder
    private var orangeAnimationReadout: some View {
        if playback.reactionAssetsAvailable {
            if playback.orangeState == DefenderClip.down.rawValue {
                Text("Orange: down")
            } else if playback.orangeProfile.isEmpty {
                Text("Orange: \(playback.orangeState) \(playback.orangeFrameIndex + 1)/\(playback.orangeFrameCount)")
            } else {
                Text("Orange: \(playback.orangeState) (\(playback.orangeProfile)) \(playback.orangeFrameIndex + 1)/\(playback.orangeFrameCount)")
            }
        } else {
            Text("Orange: reaction assets missing")
        }
    }

    private var combatReadout: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text("Orange: \(playback.orangeCombatState.rawValue)")
            Text("CPU: \(playback.cpuStatus) · \(playback.cpuMovement) | Guard: \(playback.guardStatus)")
            Text("Block FX: \(playback.blockFeedbackLabel)")
            Text("CPU Attack: \(playback.cpuAttack) | \(playback.cpuLastResult)")
            Text(playback.cpuStats)
            Text("Blue: \(playback.blueAnimation)")
            Text("Blue Guard: \(playback.blueGuardStatus) | FX: \(playback.blueBlockFX)")
            Text("Blue Action: \(playback.blueAction)").font(.system(size: 11, design: .monospaced))
            Text("Orange Action: \(playback.orangeAction)").font(.system(size: 11, design: .monospaced))
        }
    }

    private var counterReadout: some View {
        VStack(alignment: .leading, spacing: 1) {
            Text(playback.movementReadout)
            Text(playback.vulnerabilityText)
            Text(playback.counterSummary)
            Text(playback.lastCounterText)
        }
        .font(Font.system(size: 11, weight: .semibold, design: .monospaced))
    }

    @ViewBuilder
    private var assetWarnings: some View {
        if !playback.playerGuardAssetsAvailable {
            Text("Player guard assets missing").foregroundColor(Color.red)
        }
        if !playback.bidirectionalAssetsAvailable {
            Text("8C punch/recovery assets missing").foregroundColor(Color.red)
        }
        if !playback.blockRecoilAssetsAvailable {
            Text("Block recoil assets missing").foregroundColor(Color.red)
        }
        if !playback.guardAssetsAvailable {
            Text("Guard assets missing").foregroundColor(Color.red)
        }
        if !playback.riseAssetsAvailable {
            Text("Rise assets missing").foregroundColor(Color.red)
        }
        if !playback.knockdownAssetsAvailable {
            Text("Knockdown/down assets missing").foregroundColor(Color.red)
        }
    }

    @ViewBuilder
    private var contactGeometryReadout: some View {
        if playback.hasContactResult {
            VStack(alignment: .leading, spacing: 2) {
                Text(playback.latestDistanceText)
                Text(playback.latestTransformText)
                Text(playback.canvasInfo)
            }
        }
    }

    private var matchHUD: some View {
        HStack(spacing: 12) {
            Text("BLUE \(playback.bluePoints)")
                .foregroundColor(.blue)
            Spacer(minLength: 0)
            Text("ROUND \(playback.matchRound)/8")
            Text(String(format: "%02d:%02d",
                        Int(max(0, playback.matchSecondsRemaining).rounded(.up)) / 60,
                        Int(max(0, playback.matchSecondsRemaining).rounded(.up)) % 60))
                .monospacedDigit()
            if let result = playback.matchResult {
                Text(matchResultLabel(result))
                    .foregroundColor(.red)
            }
            Spacer(minLength: 0)
            Text("\(playback.orangePoints) ORANGE")
                .foregroundColor(.orange)
        }
        .font(.system(size: 12, weight: .bold, design: .monospaced))
        .lineLimit(1)
        .minimumScaleFactor(0.7)
        .padding(.horizontal, 12)
        .padding(.vertical, 3)
        .background(Color.white.opacity(0.85))
    }

    private func matchResultLabel(_ result: MatchResult) -> String {
        switch result {
        case .bluePoints: return "BLUE WINS"
        case .orangePoints: return "ORANGE WINS"
        case .draw: return "DRAW"
        case .blueKO: return "BLUE KO"
        case .orangeKO: return "ORANGE KO"
        }
    }

    // Reserved top strip keeps health separate from fighter art and Guides.
    var healthHUD: some View {
        HStack(spacing: 12) {
            fighterMeterHUD("BLUE", state: playback.blueCombatState,
                            health: playback.blueHealth, maximum: playback.blueMaximumHealth,
                            stamina: playback.blueStamina, awareness: playback.blueAwareness,
                            color: .blue)
            Button(playback.cpuStarting ? "Cancel Start" :
                   (playback.cpuEnabled ? "CPU: ON" : "Start CPU"), action: playback.toggleCPU)
                    .font(.system(size: 12, weight: .semibold))
                    .frame(minWidth: 60, minHeight: 44)
                    .buttonStyle(.plain)
            if showsDevelopmentDiagnostics {
                Button(playback.guardSelected ? "Guard on" : "Guard", action: playback.toggleGuard)
                    .font(.system(size: 12, weight: .semibold))
                    .frame(minWidth: 54, minHeight: 44)
                    .background(playback.guardSelected ? Color.blue.opacity(0.2) : Color.clear,
                                in: RoundedRectangle(cornerRadius: 6))
                    .buttonStyle(.plain)
                    .disabled(!playback.canToggleGuard)
                    .accessibilityValue(playback.guardStatus)
                Button(playback.canBlueRise ? "Blue Rise" : "Rise", action: playback.rise)
                    .font(.system(size: 12, weight: .semibold))
                    .frame(minWidth: 44, minHeight: 44)
                    .buttonStyle(.plain)
                    .disabled(!playback.canRise)
                Button("Reset Health") {
                    playback.resetHealth()
                    showsDevelopmentDiagnostics = false
                }
                    .font(.system(size: 12, weight: .semibold))
                    .frame(minWidth: 84, minHeight: 44)
                    .buttonStyle(.plain)
            }
            fighterMeterHUD("ORANGE", state: playback.orangeCombatState,
                            health: playback.orangeHealth, maximum: playback.orangeMaximumHealth,
                            stamina: playback.orangeStamina, awareness: playback.orangeAwareness,
                            color: .orange)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 5)
        .background(Color(red: 0.91, green: 0.933, blue: 0.957))
    }

    /// Read-only Phase 2 HUD. Three independently scaled values per fighter.
    /// Keep the numeric values visible while tuning combat on a device.
    private func fighterMeterHUD(_ name: String, state: FighterCombatState,
                                 health: Int, maximum: Int, stamina: Double,
                                 awareness: Double, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 3) {
            HStack(spacing: 4) {
                Text(name).foregroundColor(color)
                if state == .defeated {
                    Text("DEFEATED").foregroundColor(.red)
                }
                Spacer(minLength: 0)
            }
            .font(.system(size: 11, weight: .bold, design: .monospaced))
            .lineLimit(1)
            meterRow("HP", value: Double(health), maximum: Double(maximum), tint: color)
            meterRow("STA", value: stamina, maximum: 100, tint: .green)
            meterRow("AWA", value: awareness, maximum: 100, tint: .purple)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .accessibilityElement(children: .contain)
    }

    private func meterRow(_ title: String, value: Double, maximum: Double,
                          tint: Color) -> some View {
        let safeValue = value.isFinite ? min(max(value, 0), maximum) : 0
        return HStack(spacing: 5) {
            Text(title)
                .frame(width: 27, alignment: .leading)
            ProgressView(value: safeValue, total: maximum)
                .tint(tint)
            Text("\(Int(safeValue.rounded()))")
                .frame(width: 26, alignment: .trailing)
                .monospacedDigit()
        }
        .font(.system(size: 10, weight: .semibold, design: .monospaced))
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(title) \(Int(safeValue.rounded())) of \(Int(maximum))")
    }

    var statusLabel: some View {
        VStack(spacing: 2) {
            Text("10A · \(playback.clipName) \(playback.frameIndex + 1)/\(playback.frameCount)")
            Text("x \(playback.positionX) · v \(playback.velocityX)")
            if !playback.jabAssetsAvailable {
                Text("Jab assets missing").foregroundColor(.red)
            } else if !playback.crossAssetsAvailable {
                Text("Cross assets missing").foregroundColor(.red)
            } else {
                Text("J\(playback.jabContactCount) C\(playback.crossContactCount) H\(playback.hitCount) B\(playback.blockCount) M\(playback.missCount)")
                    .foregroundColor(playback.jabContact || playback.crossContact ? .orange : .secondary)
            }
        }
            .lineLimit(1)
            .minimumScaleFactor(0.8)
            .font(.system(size: 13, weight: .semibold, design: .monospaced))
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 8, style: .continuous))
    }

    private var playerGuardControl: some View {
        Text("Guard")
            .font(.system(size: 15, weight: .bold, design: .rounded))
            .foregroundColor(playback.canHoldGuard ? Color.accentColor : Color.secondary)
            .frame(width: 76, height: 46)
            .background(playback.guardHeld ? Color.blue.opacity(0.28) : Color.white.opacity(0.8),
                        in: RoundedRectangle(cornerRadius: 10))
            .overlay(
                HoldTouchSurface(title: "Guard", inputGeneration: playback.guardInputGeneration,
                                 hint: "Hold to defend; protection starts after gloves are raised") { held in
                    playback.setGuardHeld(held)
                }
            )
            .allowsHitTesting(playback.canHoldGuard)
            .opacity(playback.canHoldGuard ? 1 : 0.55)
    }

    func punchButton(_ title: String, enabled: Bool, action: @escaping () -> Void) -> some View {
        Text(title)
            .font(.system(size: 15, weight: .bold, design: .rounded))
            .foregroundColor(enabled ? Color.accentColor : Color.secondary)
            .frame(width: 64, height: 46)
            .background(Color.white.opacity(0.8), in: RoundedRectangle(cornerRadius: 10))
            .overlay(
                HoldTouchSurface(title: title, inputGeneration: playback.inputGeneration,
                                 hint: "Press once for one punch") { held in
                    if held { action() }
                }
            )
            .allowsHitTesting(enabled)
            .opacity(enabled ? 1 : 0.55)
    }

    /// Eight directional sectors. Vertical/diagonal entry requests a timed
    /// slip; horizontal components retain ordinary advance/retreat. Earned
    /// pivot and duck-and-switch remain future Phase 5B actions.
    private var movementPad: some View {
        ZStack {
            Circle().fill(Color.white.opacity(0.8))
            Circle().stroke(Color(red: 0.25, green: 0.37, blue: 0.49), lineWidth: 2)
            Image(systemName: "arrow.up")
                .offset(y: -34)
            Image(systemName: "arrow.down")
                .offset(y: 34)
            Image(systemName: "arrow.left")
                .offset(x: -35)
            Image(systemName: "arrow.right")
                .offset(x: 35)
            Circle().fill(Color.blue.opacity(0.12)).frame(width: 27, height: 27)
            CircularPadTouchSurface(inputGeneration: playback.inputGeneration) { horizontal, vertical in
                playback.setPadDirection(horizontal: horizontal, vertical: vertical)
            }
        }
        .font(.system(size: 16, weight: .bold))
        .foregroundColor(Color(red: 0.08, green: 0.20, blue: 0.36))
        .frame(width: 112, height: 112)
        .accessibilityLabel("Eight-direction movement pad")
    }

    var debugControls: some View {
        HStack(spacing: 8) {
            controlButton(playback.isPlaying ? "Pause" : "Resume", action: playback.togglePlayback)
            controlButton("Step \(playback.frameIndex + 1)/\(playback.frameCount)", action: playback.step)
        }
        .padding(.horizontal, 8)
        .frame(height: 54)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    func controlButton(_ title: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 13, weight: .semibold, design: .rounded))
                .padding(.horizontal, 10)
                .padding(.vertical, 8)
                .lineLimit(1)
                .minimumScaleFactor(0.75)
                .frame(maxWidth: .infinity, minHeight: 36)
        }
        .buttonStyle(.bordered)
    }

}

struct PressHoldButton: View {
    let title: String
    let pressed: Bool
    let inputGeneration: Int
    let action: (Bool) -> Void

    var body: some View {
        Text(title)
            .font(.system(size: 16, weight: .bold, design: .rounded))
            .foregroundColor(Color(red: 0.08, green: 0.20, blue: 0.36))
            .lineLimit(1)
            .minimumScaleFactor(0.8)
            .padding(.horizontal, 18)
            .padding(.vertical, 12)
            .frame(minWidth: 132, minHeight: 52)
            .background(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .fill(pressed ? Color.accentColor.opacity(0.28) : Color.white.opacity(0.72))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .stroke(Color.accentColor, lineWidth: 1.5)
            )
            .overlay(HoldTouchSurface(title: title, inputGeneration: inputGeneration, action: action))
    }
}


// Each surface owns its touches, so lifting one finger cannot release another
// control. UIKit also delivers cancellation when system gestures interrupt input.
private struct HoldTouchSurface: UIViewRepresentable {
    let title: String
    let inputGeneration: Int
    var hint = "Touch and hold to move"
    let action: (Bool) -> Void

    func makeUIView(context: Context) -> HoldTouchView {
        let view = HoldTouchView()
        view.isMultipleTouchEnabled = true
        view.isAccessibilityElement = true
        view.accessibilityTraits = .button
        view.action = action
        view.inputGeneration = inputGeneration
        view.accessibilityLabel = title
        view.accessibilityHint = hint
        return view
    }

    func updateUIView(_ view: HoldTouchView, context: Context) {
        view.action = action
        view.inputGeneration = inputGeneration
        view.accessibilityLabel = title
        view.accessibilityHint = hint
    }

    static func dismantleUIView(_ view: HoldTouchView, coordinator: ()) {
        view.releaseTouches()
        view.action = nil
    }
}

private final class HoldTouchView: UIView {
    var action: ((Bool) -> Void)?
    var inputGeneration = 0 {
        didSet {
            // Pause/focus cancellation invalidates existing fingers. A fresh
            // touchesBegan is required; continuing to hold cannot restart motion.
            if inputGeneration != oldValue { heldTouches.removeAll() }
        }
    }
    internal var heldTouches = Set<UITouch>()

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        let wasEmpty = heldTouches.isEmpty
        heldTouches.formUnion(touches)
        if wasEmpty { action?(true) }
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        heldTouches.subtract(touches)
        if heldTouches.isEmpty { action?(false) }
    }

    override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
        touchesEnded(touches, with: event)
    }

    override func didMoveToWindow() {
        super.didMoveToWindow()
        if window == nil { releaseTouches() }
    }

    func releaseTouches() {
        guard !heldTouches.isEmpty else { return }
        heldTouches.removeAll()
        action?(false)
    }
}
//struct ContentView_Previews: PreviewProvider {
//    static var previews: some View {
//        ContentView()
//            .previewInterfaceOrientation(.landscapeLeft)
//    }
//}

/// A single touch owns the pad. Releasing or cancelling always releases motion;
/// dragging between sectors changes direction without stacking held buttons.
private struct CircularPadTouchSurface: UIViewRepresentable {
    let inputGeneration: Int
    let action: (Int, Int) -> Void

    func makeUIView(context: Context) -> CircularPadTouchView {
        let view = CircularPadTouchView()
        view.isMultipleTouchEnabled = false
        view.isAccessibilityElement = true
        view.accessibilityLabel = "Directional pad"
        view.accessibilityHint = "Drag in a direction; release to stop"
        view.action = action
        view.inputGeneration = inputGeneration
        return view
    }

    func updateUIView(_ view: CircularPadTouchView, context: Context) {
        view.action = action
        view.inputGeneration = inputGeneration
    }

    static func dismantleUIView(_ view: CircularPadTouchView, coordinator: ()) {
        view.release()
        view.action = nil
    }
}

private final class CircularPadTouchView: UIView {
    var action: ((Int, Int) -> Void)?
    var inputGeneration = 0 {
        didSet { if oldValue != inputGeneration { release() } }
    }
    private var trackedTouch: UITouch?
    private var lastDirection = (0, 0)

    private func update(_ touch: UITouch) {
        let p = touch.location(in: self)
        let dx = Double(p.x - bounds.midX)
        let dy = Double(bounds.midY - p.y)
        let distance = hypot(dx, dy)
        let x: Int
        let y: Int
        if distance < 17 {
            x = 0; y = 0
        } else {
            let angle = atan2(dy, dx)
            let sector = Int((angle / (.pi / 4)).rounded())
            let vectors = [(1,0), (1,1), (0,1), (-1,1),
                           (-1,0), (-1,-1), (0,-1), (1,-1)]
            let index = (sector + 8) % 8
            (x, y) = vectors[index]
        }
        if x != lastDirection.0 || y != lastDirection.1 {
            lastDirection = (x, y)
            action?(x, y)
        }
    }

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard trackedTouch == nil, let touch = touches.first else { return }
        trackedTouch = touch
        update(touch)
    }
    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = trackedTouch, touches.contains(touch) else { return }
        update(touch)
    }
    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        if let touch = trackedTouch, touches.contains(touch) { release() }
    }
    override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
        touchesEnded(touches, with: event)
    }
    override func didMoveToWindow() {
        super.didMoveToWindow()
        if window == nil { release() }
    }
    func release() {
        trackedTouch = nil
        lastDirection = (0, 0)
        action?(0, 0)
    }
}
