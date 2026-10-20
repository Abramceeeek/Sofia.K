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
                let r: CGFloat = 13
                let spots: [(lat: Double, lon: Double)] = pins.map { (lat: $0.lat, lon: $0.lon) }
                let p: [CGPoint] = Self.layout(spots, size: size, minGap: r * 2.4)
                // a Catmull-Rom curve through the stops, one segment at a time, so walked and unwalked can differ
                for j in 0..<(p.count - 1) {
                    let seg: Path = Self.segment(p, j)
                    let walked: Bool = current.map { pins[j + 1].index <= $0 } ?? false
                    context.stroke(seg, with: .color(Theme.accent.opacity(walked ? 1 : 0.85)),
                                   style: StrokeStyle(lineWidth: 2.5, lineCap: .round, dash: walked ? [] : [2, 7]))
                }
                for (j, pin) in pins.enumerated() {
                    let at = p[j]
                    let lit = current.map { pin.index <= $0 } ?? false
                    if current == pin.index {
                        let halo: CGFloat = r * 1.6
                        context.fill(Circle().path(in: CGRect(x: at.x - halo, y: at.y - halo, width: halo * 2, height: halo * 2)),
                                     with: .color(Theme.accent.opacity(0.22)))
                    }
                    let dot: Path = Circle().path(in: CGRect(x: at.x - r, y: at.y - r, width: r * 2, height: r * 2))
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

    /// The stops' real positions, fitted into the frame (longitude narrowed by the latitude, north up), then spread.
    /// Written out step by step, with types, so the compiler checks it quickly.
    static func layout(_ points: [(lat: Double, lon: Double)], size: CGSize, minGap: CGFloat) -> [CGPoint] {
        let pad: CGFloat = 24
        var latSum: Double = 0
        for q in points { latSum += q.lat }
        let meanLat: Double = latSum / Double(points.count)
        let k: Double = cos(meanLat * Double.pi / 180)
        let xs: [Double] = points.map { (q: (lat: Double, lon: Double)) -> Double in q.lon * k }
        let ys: [Double] = points.map { (q: (lat: Double, lon: Double)) -> Double in -q.lat }
        let minX: Double = xs.min() ?? 0
        let minY: Double = ys.min() ?? 0
        let spanX: Double = max((xs.max() ?? 0) - minX, 1e-6)
        let spanY: Double = max((ys.max() ?? 0) - minY, 1e-6)
        let w: Double = Double(size.width - 2 * pad)
        let h: Double = Double(size.height - 2 * pad)
        let scale: Double = min(w / spanX, h / spanY)
        let ox: Double = Double(pad) + (w - spanX * scale) / 2
        let oy: Double = Double(pad) + (h - spanY * scale) / 2
        var out: [CGPoint] = []
        for j in points.indices {
            let x: Double = ox + (xs[j] - minX) * scale
            let y: Double = oy + (ys[j] - minY) * scale
            out.append(CGPoint(x: x, y: y))
        }
        return spread(out, minGap: minGap, pad: pad, size: size)
    }

    /// One piece of a Catmull-Rom curve through the stops, from stop `j` to stop `j + 1`.
    static func segment(_ p: [CGPoint], _ j: Int) -> Path {
        let a: CGPoint = p[max(j - 1, 0)]
        let b: CGPoint = p[j]
        let c: CGPoint = p[j + 1]
        let d: CGPoint = p[min(j + 2, p.count - 1)]
        let c1 = CGPoint(x: b.x + (c.x - a.x) / 6, y: b.y + (c.y - a.y) / 6)
        let c2 = CGPoint(x: c.x - (d.x - b.x) / 6, y: c.y - (d.y - b.y) / 6)
        var seg = Path()
        seg.move(to: b)
        seg.addCurve(to: c, control1: c1, control2: c2)
        return seg
    }

    /// Stops a few hundred metres apart would sit on top of each other: push any two closer than `minGap` apart, a
    /// little at a time, and keep them inside the frame. The order and the rough shape stay.
    static func spread(_ points: [CGPoint], minGap: CGFloat, pad: CGFloat, size: CGSize) -> [CGPoint] {
        var p = points
        for _ in 0..<40 {
            for a in p.indices {
                for b in p.indices where b > a {
                    var dx: CGFloat = p[b].x - p[a].x
                    var dy: CGFloat = p[b].y - p[a].y
                    var len: CGFloat = (dx * dx + dy * dy).squareRoot()
                    if len >= minGap { continue }
                    if len < 0.5 {
                        dx = 1
                        dy = 0.4
                        len = (dx * dx + dy * dy).squareRoot()
                    }
                    let push: CGFloat = (minGap - len) / 2 / len
                    p[a].x -= dx * push
                    p[a].y -= dy * push
                    p[b].x += dx * push
                    p[b].y += dy * push
                }
            }
            for k in p.indices {
                let x: CGFloat = max(p[k].x, pad)
                let y: CGFloat = max(p[k].y, pad)
                p[k].x = min(x, size.width - pad)
                p[k].y = min(y, size.height - pad)
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
