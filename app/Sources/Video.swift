import AVFoundation
import AVKit
import SwiftUI
import UIKit

/// D117: Abram's own short videos, bundled inside the app (no third-party hosting, nothing streamed):
/// - `founder`: a 20–30 s hello after the example day (its own screen; skippable);
/// - `ask_moment`: Abram asking the "great moment" question (screen 4);
/// - `thanks`: a 5–8 s thank-you on "So far, I've learned…", before the first plan.
/// Each is `Video/<name>.mp4` (or .mov), with its captions in `Video/<name>.srt`. Until a file is in the app, its place
/// is simply left out (CI screenshots show a placeholder instead). Format and size: `design/video-spec.md`.
enum BundledVideo {
    static func url(_ name: String) -> URL? {
        for ext in ["mp4", "mov", "m4v"] {
            if let u = Bundle.main.url(forResource: name, withExtension: ext) { return u }
        }
        return nil
    }

    static func exists(_ name: String) -> Bool { url(name) != nil }

    static func captions(_ name: String) -> [Caption] {
        guard let u = Bundle.main.url(forResource: name, withExtension: "srt"),
              let text = try? String(contentsOf: u, encoding: .utf8) else { return [] }
        return Caption.parseSRT(text)
    }
}

/// One timed caption line, from a standard .srt file (most editors export one).
struct Caption: Equatable {
    let start: Double
    let end: Double
    let text: String

    static func parseSRT(_ srt: String) -> [Caption] {
        let blocks = srt.replacingOccurrences(of: "\r\n", with: "\n").components(separatedBy: "\n\n")
        return blocks.compactMap { block in
            let lines = block.split(separator: "\n", omittingEmptySubsequences: true).map(String.init)
            guard let timing = lines.firstIndex(where: { $0.contains("-->") }) else { return nil }
            let parts = lines[timing].components(separatedBy: "-->").map { $0.trimmingCharacters(in: .whitespaces) }
            guard parts.count == 2, let a = seconds(parts[0]), let b = seconds(parts[1]) else { return nil }
            let text = lines[(timing + 1)...].joined(separator: "\n")
            return text.isEmpty ? nil : Caption(start: a, end: b, text: text)
        }
    }

    /// "00:00:03,250" → 3.25
    private static func seconds(_ s: String) -> Double? {
        let p = s.replacingOccurrences(of: ",", with: ".").split(separator: ":").compactMap { Double($0) }
        return p.count == 3 ? p[0] * 3600 + p[1] * 60 + p[2] : nil
    }
}

/// Plays one bundled video and keeps the current caption. Autoplays only if the person allows video autoplay
/// (Settings → Accessibility → Motion). The sound follows the ring/silent switch; the captions are always on.
@MainActor
@Observable
final class ClipPlayer {
    let player: AVPlayer
    var caption: String?
    var playing = false
    var ended = false
    var watched: Double = 0
    @ObservationIgnored private var timeObserver: Any?
    @ObservationIgnored private var endObserver: NSObjectProtocol?

    init(url: URL, captions: [Caption]) {
        player = AVPlayer(url: url)
        timeObserver = player.addPeriodicTimeObserver(forInterval: CMTime(seconds: 0.1, preferredTimescale: 600),
                                                      queue: .main) { [weak self] t in
            let now = t.seconds
            MainActor.assumeIsolated {
                guard let self else { return }
                self.watched = max(self.watched, now)
                self.caption = captions.first { now >= $0.start && now < $0.end }?.text
                self.playing = self.player.rate > 0
            }
        }
        endObserver = NotificationCenter.default.addObserver(forName: .AVPlayerItemDidPlayToEndTime,
                                                             object: player.currentItem, queue: .main) { [weak self] _ in
            MainActor.assumeIsolated {
                self?.ended = true
                self?.playing = false
            }
        }
    }

    func play() {
        // .ambient: the silent switch mutes it (captions carry it then), and dictation's .record setting is undone
        try? AVAudioSession.sharedInstance().setCategory(.ambient)
        try? AVAudioSession.sharedInstance().setActive(true)
        if ended { player.seek(to: .zero); ended = false }
        player.play()
        playing = true
    }

    func pause() {
        player.pause()
        playing = false
    }

    func toggle() { playing ? pause() : play() }
}

/// The caption style: white on a dark band, in the system font so it scales with Dynamic Type.
struct CaptionText: View {
    let text: String

    var body: some View {
        Text(text)
            .font(.subheadline.weight(.medium))
            .foregroundStyle(.white)
            .multilineTextAlignment(.center)
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(.black.opacity(0.65), in: RoundedRectangle(cornerRadius: 8))
            .fixedSize(horizontal: false, vertical: true)
    }
}

/// The founder video, full width, with the system controls (play, pause, scrub) and the captions over it.
struct FounderVideoView: View {
    @Environment(AppModel.self) private var model
    @State private var clip: ClipPlayer?

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            PageTitle(text: "A hello from Abram")
            Text("Why this app exists, in half a minute. Skip any time.")
                .foregroundStyle(Theme.inkSoft)
            Group {
                if let clip {
                    VideoPlayer(player: clip.player) {
                        VStack {
                            Spacer()
                            if let c = clip.caption { CaptionText(text: c).padding(.bottom, 56) }
                        }
                        .padding(.horizontal, 12)
                        .frame(maxWidth: .infinity)
                    }
                } else {
                    VideoPlaceholder(title: "Abram's hello, 20–30 s", note: "Video to come: bundled in the app, with captions")
                }
            }
            .aspectRatio(9 / 16, contentMode: .fit)
            .clipShape(RoundedRectangle(cornerRadius: 16))
            .frame(maxWidth: .infinity)
            .accessibilityLabel("Video: a hello from Abram, with captions")
            PrimaryButton(title: clip?.ended == true ? "Continue" : "Skip") {
                clip?.pause()
                model.founderVideoDone(seconds: clip?.watched ?? 0, ended: clip?.ended ?? false)
            }
        }
        .padding(20)
        .background(Theme.background)
        .onAppear {
            if clip == nil, let url = BundledVideo.url("founder") {
                clip = ClipPlayer(url: url, captions: BundledVideo.captions("founder"))
            }
            if UIAccessibility.isVideoAutoplayEnabled { clip?.play() }
        }
        .onDisappear { clip?.pause() }
    }
}

/// A short clip as a small portrait tile beside the screen's own words, like a video call: tap to play or pause.
/// The captions run underneath, full width. Left out entirely until the file is in the app (a placeholder in CI).
struct ClipTile<Content: View>: View {
    let name: String
    let label: String
    var small = false              // D118: on "So far" the tile stays small, so the answers lead
    @ViewBuilder let content: Content
    @State private var clip: ClipPlayer?

    var body: some View {
        if BundledVideo.exists(name) || AppConfig.demo {
            VStack(alignment: .leading, spacing: 8) {
                HStack(alignment: .top, spacing: 14) {
                    VStack(spacing: 4) {
                        tile
                            .frame(width: small ? 56 : 104, height: small ? 100 : 185)
                            .clipShape(RoundedRectangle(cornerRadius: small ? 10 : 14))
                        if small {
                            Text("A note from Abram").font(.caption2).foregroundStyle(Theme.inkSoft)
                                .multilineTextAlignment(.center).frame(width: 64)
                        }
                    }
                    content
                }
                if let c = clip?.caption {
                    Text(c)
                        .font(.footnote)
                        .foregroundStyle(Theme.inkSoft)
                        .accessibilityHidden(true)   // the same words are read out from the video's own label
                }
            }
            .onAppear {
                if clip == nil, let url = BundledVideo.url(name) {
                    clip = ClipPlayer(url: url, captions: BundledVideo.captions(name))
                }
                if UIAccessibility.isVideoAutoplayEnabled { clip?.play() }
            }
            .onDisappear { clip?.pause() }
        } else {
            content
        }
    }

    @ViewBuilder private var tile: some View {
        if let clip {
            ZStack {
                PlayerLayer(player: clip.player)
                if !clip.playing {
                    Image(systemName: clip.ended ? "arrow.counterclockwise" : "play.fill")
                        .font(.title3)
                        .foregroundStyle(.white)
                        .padding(10)
                        .background(.black.opacity(0.5), in: Circle())
                }
            }
            .contentShape(Rectangle())
            .onTapGesture { clip.toggle() }
            .accessibilityElement()
            .accessibilityLabel(label)
            .accessibilityAddTraits(.startsMediaSession)
            .accessibilityAction { clip.toggle() }
        } else {
            VideoPlaceholder(title: small ? "" : "Abram", note: small ? "" : "Clip to come")
        }
    }
}

/// The video frame without controls, filling its tile.
struct PlayerLayer: UIViewRepresentable {
    let player: AVPlayer

    final class LayerView: UIView {
        override static var layerClass: AnyClass { AVPlayerLayer.self }
        var playerLayer: AVPlayerLayer { layer as! AVPlayerLayer }
    }

    func makeUIView(context: Context) -> LayerView {
        let v = LayerView()
        v.playerLayer.player = player
        v.playerLayer.videoGravity = .resizeAspectFill
        v.backgroundColor = .black
        return v
    }

    func updateUIView(_ uiView: LayerView, context: Context) {
        uiView.playerLayer.player = player
    }
}

/// Where a video will go, for the CI screenshots before the file exists.
struct VideoPlaceholder: View {
    let title: String
    let note: String

    var body: some View {
        ZStack {
            Theme.surfaceHigh
            VStack(spacing: 8) {
                Image(systemName: "play.circle")
                    .font(.system(size: 34))
                    .foregroundStyle(Theme.accent)
                Text(title).font(.footnote.weight(.semibold)).foregroundStyle(Theme.ink)
                Text(note).font(.caption2).foregroundStyle(Theme.inkSoft).multilineTextAlignment(.center)
            }
            .padding(8)
        }
    }
}
