import SwiftUI

/// D130 (the day as a path): the day's stops drawn where they really are, joined by a gentle line and numbered in
/// order. The part already walked is solid, the rest dotted, and the stop you're at is lit. No map tiles: the list of
/// stops and times sits straight under it. `current` is the stop you're at (nil before the day starts). The same as
/// android/…/DayPath.kt.
struct DayPath: View {
    let stops: [Stop]
    var current: Int?
    var height: CGFloat = 180

    private var pins: [(index: Int, lat: Double, lon: Double)] {
        stops.enumerated().compactMap { i, s in
            guard let lat = s.pin?.lat, let lon = s.pin?.lon else { return nil }
            return (i, lat, lon)
        }
    }

    private var label: String {
        guard let first = stops.first, let last = stops.last else { return "" }
        var text = "The day as a path: \(stops.count) stops, from \(first.title) to \(last.title)"
        if let current, current < stops.count { text += ". You're at stop \(current + 1), \(stops[current].title)" }
        return text
    }

    var body: some View {
        let pins = self.pins
        if pins.count >= 2 {
            Canvas { context, size in
                let pad: CGFloat = 24
                let r: CGFloat = 13
                let k = cos(pins.map { $0.lat }.reduce(0, +) / Double(pins.count) * .pi / 180)
                let xs = pins.map { $0.lon * k }
                let ys = pins.map { -$0.lat }
                let spanX = max(xs.max()! - xs.min()!, 1e-6)
                let spanY = max(ys.max()! - ys.min()!, 1e-6)
                let w = Double(size.width - 2 * pad)
                let h = Double(size.height - 2 * pad)
                let scale = min(w / spanX, h / spanY)
                let ox = Double(pad) + (w - spanX * scale) / 2
                let oy = Double(pad) + (h - spanY * scale) / 2
                let p = Self.spread(pins.indices.map { j in
                    CGPoint(x: ox + (xs[j] - xs.min()!) * scale, y: oy + (ys[j] - ys.min()!) * scale)
                }, minGap: r * 2.4, pad: pad, size: size)
                // a Catmull-Rom curve through the stops, one segment at a time, so walked and unwalked can differ
                for j in 0..<(p.count - 1) {
                    let a = p[max(j - 1, 0)], b = p[j], c = p[j + 1], d = p[min(j + 2, p.count - 1)]
                    var seg = Path()
                    seg.move(to: b)
                    seg.addCurve(to: c, control1: CGPoint(x: b.x + (c.x - a.x) / 6, y: b.y + (c.y - a.y) / 6),
                                 control2: CGPoint(x: c.x - (d.x - b.x) / 6, y: c.y - (d.y - b.y) / 6))
                    let walked = current.map { pins[j + 1].index <= $0 } ?? false
                    context.stroke(seg, with: .color(Theme.accent.opacity(walked ? 1 : 0.85)),
                                   style: StrokeStyle(lineWidth: 2.5, lineCap: .round, dash: walked ? [] : [2, 7]))
                }
                for (j, pin) in pins.enumerated() {
                    let at = p[j]
                    let lit = current.map { pin.index <= $0 } ?? false
                    if current == pin.index {
                        context.fill(Circle().path(in: CGRect(x: at.x - r * 1.6, y: at.y - r * 1.6, width: r * 3.2, height: r * 3.2)),
                                     with: .color(Theme.accent.opacity(0.22)))
                    }
                    let dot = Circle().path(in: CGRect(x: at.x - r, y: at.y - r, width: r * 2, height: r * 2))
                    context.fill(dot, with: .color(lit ? Theme.accent : Theme.surface))
                    context.stroke(dot, with: .color(Theme.accent), lineWidth: 2)
                    context.draw(Text("\(pin.index + 1)").font(.caption.weight(.semibold))
                        .foregroundStyle(lit ? Theme.onAccent : Theme.accent), at: at)
                }
            }
            .frame(height: height)
            .frame(maxWidth: .infinity)
            .accessibilityElement()
            .accessibilityLabel(label)
        }
    }

    /// Stops a few hundred metres apart would sit on top of each other: push any two closer than `minGap` apart, a
    /// little at a time, and keep them inside the frame. The order and the rough shape stay.
    static func spread(_ points: [CGPoint], minGap: CGFloat, pad: CGFloat, size: CGSize) -> [CGPoint] {
        var p = points
        for _ in 0..<40 {
            for a in p.indices {
                for b in p.indices where b > a {
                    var dx = p[b].x - p[a].x, dy = p[b].y - p[a].y
                    var len = (dx * dx + dy * dy).squareRoot()
                    if len >= minGap { continue }
                    if len < 0.5 { dx = 1; dy = 0.4; len = (dx * dx + dy * dy).squareRoot() }
                    let push = (minGap - len) / 2 / len
                    p[a].x -= dx * push; p[a].y -= dy * push
                    p[b].x += dx * push; p[b].y += dy * push
                }
            }
            for k in p.indices {
                p[k].x = min(max(p[k].x, pad), size.width - pad)
                p[k].y = min(max(p[k].y, pad), size.height - pad)
            }
        }
        return p
    }
}

/// D130 (Daylight): the sky at the top of the main screens, fading into the page. It changes only between steps.
struct SkyBackground: ViewModifier {
    @Environment(AppModel.self) private var model
    var base: Color = Theme.background

    func body(content: Content) -> some View {
        content.background(alignment: .top) {
            ZStack(alignment: .top) {
                base
                LinearGradient(colors: [Theme.skyTop(model.sky), base], startPoint: .top, endPoint: .bottom)
                    .frame(height: 440)
            }
            .ignoresSafeArea()
        }
    }
}

/// What scrolls up under the status bar goes behind the sky's colour, so the sky reaches the top of the screen.
struct SkyShade: ViewModifier {
    @Environment(AppModel.self) private var model

    func body(content: Content) -> some View {
        content.safeAreaInset(edge: .top, spacing: 0) {
            Color.clear.frame(height: 0).background(Theme.skyTop(model.sky))
        }
    }
}

extension View {
    func skyBackground(base: Color = Theme.background) -> some View { modifier(SkyBackground(base: base)) }
    func skyStatusBarShade() -> some View { modifier(SkyShade()) }
}
