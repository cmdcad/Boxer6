//
//  ContentView.swift
//  Boxer0
//

import SpriteKit
import SwiftUI
import UIKit

final class IdlePlayback: ObservableObject {
    let scene: IdleTestScene

    @Published var isPlaying = true
    @Published var frameIndex = 0
    @Published var frameCount = 4
    @Published var showsGuides = true
    @Published var clipName = FighterClip.idle.rawValue
    @Published var positionX = 0
    @Published var velocityX = 0
    @Published var inputGeneration = 0
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
    }

    func togglePlayback() {
        scene.togglePlayback()
        syncFromScene()
    }

    func step() {
        scene.stepFrame()
        syncFromScene()
    }

    func toggleGuides() {
        scene.toggleGuides()
        syncFromScene()
    }

    func setAdvance(_ held: Bool) {
        scene.setAdvanceHeld(held)
        syncFromScene()
    }

    func setRetreat(_ held: Bool) {
        scene.setRetreatHeld(held)
        syncFromScene()
    }

    func cancelMovement() {
        holdAdvance = false
        holdRetreat = false
        scene.cancelMovement()
        syncFromScene()
    }
}

struct ContentView: View {
    @StateObject private var playback = IdlePlayback()
    // Development presentation only; hiding it does not change locomotion.
    var showsDevelopmentDiagnostics = true

    var body: some View {
        VStack(spacing: 0) {
            SpriteView(scene: playback.scene)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .layoutPriority(0)

            VStack(spacing: 8) {
                HStack(alignment: .bottom, spacing: 12) {
                    PressHoldButton(title: "Hold Retreat", pressed: playback.holdRetreat, inputGeneration: playback.inputGeneration, action: playback.setRetreat)
                    Spacer()
                    if showsDevelopmentDiagnostics { statusLabel }
                    Spacer()
                    PressHoldButton(title: "Hold Advance", pressed: playback.holdAdvance, inputGeneration: playback.inputGeneration, action: playback.setAdvance)
                }
                .frame(minHeight: 52)
                if showsDevelopmentDiagnostics { debugControls }
            }
            .fixedSize(horizontal: false, vertical: true)
            .padding(.horizontal, 12)
            .padding(.bottom, 8)
            .frame(maxWidth: .infinity)
            .background(Color(red: 0.85, green: 0.89, blue: 0.93))
            .layoutPriority(1)
        }
        .background(Color(red: 0.91, green: 0.933, blue: 0.957).ignoresSafeArea())
        .preferredColorScheme(ColorScheme.light)
        .onReceive(NotificationCenter.default.publisher(for: UIApplication.willResignActiveNotification)) { _ in
            playback.cancelMovement()
        }
        .onDisappear {
            playback.cancelMovement()
        }
    }

    private var statusLabel: some View {
        VStack(spacing: 2) {
            Text("3B · \(playback.clipName)")
            Text("x \(playback.positionX) · v \(playback.velocityX)")
        }
            .font(.system(size: 13, weight: .semibold, design: .monospaced))
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 8, style: .continuous))
    }

    private var debugControls: some View {
        HStack(spacing: 8) {
            controlButton(playback.isPlaying ? "Pause" : "Resume", action: playback.togglePlayback)
            controlButton("Step \(playback.frameIndex + 1)/\(playback.frameCount)", action: playback.step)
            controlButton(playback.showsGuides ? "Guides on" : "Guides off", action: playback.toggleGuides)
        }
        .padding(.horizontal, 8)
        .frame(height: 54)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    private func controlButton(_ title: String, action: @escaping () -> Void) -> some View {
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
    let action: (Bool) -> Void

    func makeUIView(context: Context) -> HoldTouchView {
        let view = HoldTouchView()
        view.isMultipleTouchEnabled = true
        view.isAccessibilityElement = true
        view.accessibilityTraits = .button
        view.action = action
        view.inputGeneration = inputGeneration
        view.accessibilityLabel = title
        view.accessibilityHint = "Touch and hold to move"
        return view
    }

    func updateUIView(_ view: HoldTouchView, context: Context) {
        view.action = action
        view.inputGeneration = inputGeneration
        view.accessibilityLabel = title
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
    private var heldTouches = Set<UITouch>()

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
