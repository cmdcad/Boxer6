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
    @Published var speed: IdlePlaybackSpeed = .normal
    @Published var frameIndex = 0
    @Published var frameCount = 4
    @Published var showsGuides = true
    @Published var clipName = FighterClip.idle.rawValue
    @Published var positionX = 0
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
        speed = scene.playbackSpeed
        frameIndex = scene.frameIndex
        frameCount = scene.activeClip.frameCount
        showsGuides = scene.showsGuides
        clipName = scene.activeClip.rawValue
        positionX = Int(scene.bluePositionX.rounded())
    }

    func togglePlayback() {
        scene.togglePlayback()
        syncFromScene()
    }

    func step() {
        scene.stepFrame()
        syncFromScene()
    }

    func cycleSpeed() {
        let next: IdlePlaybackSpeed = speed == .normal ? .quarter : .normal
        scene.setSpeed(next)
        syncFromScene()
    }

    func toggleGuides() {
        scene.toggleGuides()
        syncFromScene()
    }

    func setAdvance(_ held: Bool) {
        holdAdvance = held
        scene.setAdvanceHeld(held)
        syncFromScene()
    }

    func setRetreat(_ held: Bool) {
        holdRetreat = held
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

    var body: some View {
        ZStack(alignment: .bottom) {
            SpriteView(scene: playback.scene)
                .ignoresSafeArea()

            VStack(spacing: 8) {
                HStack(alignment: .bottom, spacing: 12) {
                    PressHoldButton(title: "Retreat", pressed: playback.holdRetreat, action: playback.setRetreat)
                    Spacer()
                    statusLabel
                    Spacer()
                    PressHoldButton(title: "Advance", pressed: playback.holdAdvance, action: playback.setAdvance)
                }
                debugControls
            }
            .padding(.horizontal, 12)
            .padding(.bottom, 8)
        }
        .preferredColorScheme(ColorScheme.light)
        .onReceive(NotificationCenter.default.publisher(for: UIApplication.willResignActiveNotification)) { _ in
            playback.cancelMovement()
        }
        .onDisappear {
            playback.cancelMovement()
        }
    }

    private var statusLabel: some View {
        Text("\(playback.clipName)  \(playback.positionX)")
            .font(.system(size: 13, weight: .semibold, design: .monospaced))
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 8, style: .continuous))
    }

    private var debugControls: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                controlButton(playback.isPlaying ? "Pause" : "Resume", action: playback.togglePlayback)
                controlButton("Step \(playback.frameIndex + 1)/\(playback.frameCount)", action: playback.step)
                controlButton(playback.speed.label, action: playback.cycleSpeed)
                controlButton(playback.showsGuides ? "Guides on" : "Guides off", action: playback.toggleGuides)
            }
            .padding(8)
        }
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    private func controlButton(_ title: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 13, weight: .semibold, design: .rounded))
                .padding(.horizontal, 10)
                .padding(.vertical, 8)
                .frame(minWidth: 72)
        }
        .buttonStyle(.bordered)
    }
}

struct PressHoldButton: View {
    let title: String
    let pressed: Bool
    let action: (Bool) -> Void

    var body: some View {
        Text(title)
            .font(.system(size: 16, weight: .bold, design: .rounded))
            .padding(.horizontal, 18)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .fill(pressed ? Color.accentColor.opacity(0.28) : Color.white.opacity(0.72))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .stroke(Color.accentColor, lineWidth: 1.5)
            )
            .overlay(HoldTouchSurface(title: title, action: action))
    }
}


// Each surface owns its touches, so lifting one finger cannot release another
// control. UIKit also delivers cancellation when system gestures interrupt input.
private struct HoldTouchSurface: UIViewRepresentable {
    let title: String
    let action: (Bool) -> Void

    func makeUIView(context: Context) -> HoldTouchView {
        let view = HoldTouchView()
        view.isMultipleTouchEnabled = true
        view.isAccessibilityElement = true
        view.accessibilityTraits = .button
        view.action = action
        view.accessibilityLabel = title
        view.accessibilityHint = "Touch and hold to move"
        return view
    }

    func updateUIView(_ view: HoldTouchView, context: Context) {
        view.action = action
        view.accessibilityLabel = title
    }

    static func dismantleUIView(_ view: HoldTouchView, coordinator: ()) {
        view.releaseTouches()
        view.action = nil
    }
}

private final class HoldTouchView: UIView {
    var action: ((Bool) -> Void)?
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

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .previewInterfaceOrientation(.landscapeLeft)
    }
}
