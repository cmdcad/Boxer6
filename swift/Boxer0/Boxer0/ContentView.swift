//
//  ContentView.swift
//  Boxer0
//

import SpriteKit
import SwiftUI

final class IdlePlayback: ObservableObject {
    let scene: IdleTestScene

    @Published var isPlaying = true
    @Published var speed: IdlePlaybackSpeed = .normal
    @Published var frameIndex = 0
    @Published var showsGuides = true

    init() {
        let scene = IdleTestScene(size: CGSize(width: 844, height: 390))
        scene.scaleMode = .resizeFill
        self.scene = scene
        scene.onFrameChange = { [weak self] index in
            DispatchQueue.main.async {
                self?.frameIndex = index
            }
        }
    }

    func togglePlayback() {
        scene.togglePlayback()
        isPlaying = scene.isPlaying
    }

    func step() {
        scene.stepFrame()
        isPlaying = scene.isPlaying
        frameIndex = scene.frameIndex
    }

    func cycleSpeed() {
        let next: IdlePlaybackSpeed = speed == .normal ? .quarter : .normal
        scene.setSpeed(next)
        speed = next
    }

    func toggleGuides() {
        scene.toggleGuides()
        showsGuides = scene.showsGuides
    }
}

struct ContentView: View {
    @StateObject private var playback = IdlePlayback()

    var body: some View {
        ZStack(alignment: .bottom) {
            SpriteView(scene: playback.scene)
                .ignoresSafeArea()

            controls
                .padding(.horizontal, 12)
                .padding(.bottom, 8)
        }
        .preferredColorScheme(ColorScheme.light)
    }

    private var controls: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                controlButton(playback.isPlaying ? "Pause" : "Resume", action: playback.togglePlayback)
                controlButton("Step \(playback.frameIndex + 1)/4", action: playback.step)
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

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .previewInterfaceOrientation(.landscapeLeft)
    }
}
