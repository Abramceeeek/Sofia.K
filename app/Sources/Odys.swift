import SwiftUI
import UIKit

// D119: the ODYS parts every screen is built from: the arch, buttons, tiles, the eyebrow, and the motion vocabulary
// from the design files (ODYS Motion). Rules: a response to a tap finishes within 300 ms; ease, never bounce; nothing
// makes you wait for it (taps always go through); with Reduce Motion, things fade or are simply there.

enum Motion {
    static let settle = Animation.timingCurve(0.2, 0.7, 0.2, 1, duration: 0.45)   // content rises 10 pt
    static let press = Animation.easeOut(duration: 0.12)                          // scale .97, a light haptic
    static let select = Animation.easeOut(duration: 0.25)                         // a sweep, then the mark fills
    static let fade = Animation.easeOut(duration: 0.3)
    static let wayIn = Animation.easeInOut(duration: 0.45)                        // a light walks down the path
    static let lift = Animation.timingCurve(0.2, 0.7, 0.2, 1, duration: 0.7)      // the share card tilts up
}

enum Haptics {
    static func light() {
        UIImpactFeedbackGenerator(style: .light).impactOccurred()
    }
}

/// UX checklist (9 Oct): the pushed screens that draw their own "‹ Back" (a day, a trip, a flight, a stay) hide the
/// navigation bar, and iOS then turns off the swipe from the left edge. This keeps that swipe on every pushed screen,
/// and never on a tab's first screen or during a push.
extension UINavigationController: UIGestureRecognizerDelegate {
    override open func viewDidLoad() {
        super.viewDidLoad()
        interactivePopGestureRecognizer?.delegate = self
    }

    public func gestureRecognizerShouldBegin(_ gestureRecognizer: UIGestureRecognizer) -> Bool {
        viewControllers.count > 1 && transitionCoordinator == nil
    }
}

// ---- buttons ------------------------------------------------------------------------------------------------

/// Press (120 ms): scale .97. Used by every tappable card and tile.
struct PressStyle: ButtonStyle {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed && !reduceMotion ? 0.97 : 1)
            .animation(Motion.press, value: configuration.isPressed)
    }
}

/// The pill buttons: amber (the one main action), outlined (the others), red (only "Call 999").
struct PillStyle: ButtonStyle {
    enum Kind { case primary, secondary, danger }
    var kind: Kind = .primary
    var height: CGFloat = 56
    @Environment(\.isEnabled) private var enabled
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    func makeBody(configuration: Configuration) -> some View {
        let pressed = configuration.isPressed
        configuration.label
            .font(kind == .secondary ? .body : .headline)
            .foregroundStyle(foreground)
            .multilineTextAlignment(.center)
            .padding(.horizontal, 20)
            .padding(.vertical, 8)
            .frame(maxWidth: .infinity, minHeight: height)
            .background(fill(pressed), in: Capsule())
            .overlay(Capsule().stroke(kind == .secondary ? Theme.outlineStrong : Color.clear, lineWidth: 1))
            .contentShape(Capsule())
            .scaleEffect(pressed && !reduceMotion ? 0.97 : 1)
            .animation(Motion.press, value: pressed)
    }

    private var foreground: Color {
        guard enabled else { return Theme.muted }
        switch kind {
        case .primary: return Theme.onAccent
        case .secondary: return Theme.ink
        case .danger: return .white
        }
    }

    private func fill(_ pressed: Bool) -> Color {
        guard enabled else { return kind == .secondary ? Color.clear : Theme.surfaceHigh }
        switch kind {
        case .primary: return pressed ? Theme.amberDeep : Theme.accentFill
        case .secondary: return pressed ? Theme.surface : Color.clear
        case .danger: return pressed ? Theme.danger.opacity(0.85) : Theme.danger
        }
    }
}

/// The main action at the bottom of a screen: an amber pill, 56 pt, with a light haptic.
struct PrimaryButton: View {
    let title: String
    var disabled = false
    let action: () -> Void

    var body: some View {
        Button {
            Haptics.light()
            action()
        } label: {
            Text(title)
        }
        .buttonStyle(PillStyle(kind: .primary))
        .disabled(disabled)
    }
}

/// Every other action: an outlined pill, 52 pt.
struct SecondaryButton: View {
    let title: String
    var icon: String?
    var disabled = false
    let action: () -> Void

    var body: some View {
        Button {
            Haptics.light()
            action()
        } label: {
            if let icon {
                Label(title, systemImage: icon)
            } else {
                Text(title)
            }
        }
        .buttonStyle(PillStyle(kind: .secondary, height: 52))
        .disabled(disabled)
    }
}

/// A quiet text button: skipping, going back, opting out. Never louder than the main action (D118).
struct QuietButton: View {
    let title: String
    var color: Color = Theme.muted
    let action: () -> Void

    init(_ title: String, color: Color = Theme.muted, action: @escaping () -> Void) {
        self.title = title
        self.color = color
        self.action = action
    }

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.subheadline)
                .foregroundStyle(color)
                .frame(minHeight: 44)
                .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }
}

/// A line to tick (19 Oct review: consent is agreed to, not switched on): a circle that fills with a check.
struct CheckRow: View {
    let label: String
    @Binding var isOn: Bool

    var body: some View {
        Button {
            Haptics.light()
            isOn.toggle()
        } label: {
            HStack(spacing: 12) {
                Image(systemName: isOn ? "checkmark.circle.fill" : "circle")
                    .font(.title2)
                    .foregroundStyle(isOn ? Theme.accent : Theme.inkSoft)
                Text(label).foregroundStyle(Theme.ink)
                Spacer(minLength: 0)
            }
            .frame(minHeight: 44)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityLabel(label)
        .accessibilityValue(isOn ? "ticked" : "not ticked")
        .accessibilityAddTraits(isOn ? .isSelected : [])
    }
}

/// "‹ Back", in amber, for screens without a navigation bar.
struct BackLink: View {
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 4) {
                Image(systemName: "chevron.left").font(.body.weight(.semibold))
                Text("Back")
            }
            .foregroundStyle(Theme.accent)
            .frame(minHeight: 44)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityLabel("Back")
    }
}

/// "Help" in a pill, on every main screen; a dot when a person has replied (D118).
struct HelpPill: View {
    @Environment(AppModel.self) private var model
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text("Help")
                .font(.subheadline)
                .foregroundStyle(Theme.ink)
                .padding(.horizontal, 14)
                .frame(height: 36)
                .overlay(Capsule().stroke(Theme.outlineStrong, lineWidth: 1))
                .overlay(alignment: .topTrailing) {
                    if model.unreadSafety {
                        Circle().fill(Theme.danger).frame(width: 9, height: 9).offset(x: 2, y: -2)
                    }
                }
                .frame(minHeight: 44)
                .contentShape(Rectangle())
        }
        .buttonStyle(PressStyle())
        .accessibilityLabel(model.unreadSafety ? "Help and safety, new reply" : "Help and safety")
    }
}

/// The top of a main screen: an eyebrow, then Help and "Your data".
struct TopBar: View {
    let eyebrow: String
    var onHelp: (() -> Void)?
    var onData: (() -> Void)?
    var onMenu: (() -> Void)?     // D131: the home's menu: You, your data and the light

    var body: some View {
        HStack(spacing: 10) {
            Eyebrow(eyebrow)
            Spacer(minLength: 8)
            if let onHelp { HelpPill(action: onHelp) }
            if let onMenu {
                Button(action: onMenu) {
                    Image(systemName: "line.3.horizontal")
                        .font(.subheadline)
                        .foregroundStyle(Theme.ink)
                        .frame(width: 36, height: 36)
                        .overlay(Circle().stroke(Theme.outlineStrong, lineWidth: 1))
                        .frame(minWidth: 44, minHeight: 44)
                        .contentShape(Rectangle())
                }
                .buttonStyle(PressStyle())
                .accessibilityLabel("You, your data and the light")
            }
            if let onData {
                Button(action: onData) {
                    Image(systemName: "gearshape")
                        .font(.subheadline)
                        .foregroundStyle(Theme.ink)
                        .frame(width: 36, height: 36)
                        .overlay(Circle().stroke(Theme.outlineStrong, lineWidth: 1))
                        .frame(minWidth: 44, minHeight: 44)
                        .contentShape(Rectangle())
                }
                .buttonStyle(PressStyle())
                .accessibilityLabel("Your data")
            }
        }
        .frame(minHeight: 44)
    }
}

// ---- type ---------------------------------------------------------------------------------------------------

/// The small amber label above a title: 13 pt, uppercase, spaced.
struct Eyebrow: View {
    let text: String
    var color: Color = Theme.amberDeep

    init(_ text: String, color: Color = Theme.amberDeep) {
        self.text = text
        self.color = color
    }

    var body: some View {
        Text(text.uppercased())
            .font(.footnote.weight(.medium))
            .tracking(1.0)
            .foregroundStyle(color)
            .fixedSize(horizontal: false, vertical: true)
            .accessibilityLabel(text)
    }
}

/// A question split into its title and the line under it: "How do you most want to feel on a day out?" and
/// "Pick one or two." The Brain sends them as one string (onboarding.yaml).
enum PromptText {
    static func split(_ text: String) -> (String, String?) {
        guard let q = text.firstIndex(of: "?"), text.index(after: q) < text.endIndex else { return (text, nil) }
        let rest = text[text.index(after: q)...].trimmingCharacters(in: .whitespaces)
        return rest.isEmpty ? (text, nil) : (String(text[...q]), rest)
    }
}

/// Little reaction (70 ms a word): the words come into focus from a blur, in amber italic. Only ever from what the
/// person answered (D117). VoiceOver reads it once.
struct WordReveal: View {
    let text: String
    var font: Font = Theme.reaction
    var color: Color = Theme.accent
    @State private var shown = 0
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        let words = text.split(separator: " ").map(String.init)
        let line = words.indices.reduce(Text(verbatim: "")) { acc, i in
            acc + Text(verbatim: (i == 0 ? "" : " ") + words[i]).foregroundStyle(color.opacity(i < shown ? 1 : 0))
        }
        line
            .font(font)
            .fixedSize(horizontal: false, vertical: true)
            .frame(maxWidth: .infinity, alignment: .leading)
            .blur(radius: reduceMotion || shown >= words.count ? 0 : 2.5)
            .accessibilityLabel(text)
            .task(id: text) {
                if reduceMotion || AppConfig.demo {
                    shown = words.count
                    return
                }
                shown = 0
                for i in 1...max(words.count, 1) {
                    try? await Task.sleep(for: .milliseconds(70))
                    if Task.isCancelled { return }
                    withAnimation(.easeOut(duration: 0.2)) { shown = i }
                }
            }
            .onAppear { UIAccessibility.post(notification: .announcement, argument: text) }
    }
}

// ---- tiles --------------------------------------------------------------------------------------------------

/// A tile that can be chosen. Select (250 ms): a light sweeps across it, then its border and mark turn amber.
struct SelectTile<Content: View>: View {
    let on: Bool
    var radius: CGFloat = 18
    var minHeight: CGFloat = 64
    let action: () -> Void
    @ViewBuilder let content: Content
    @State private var sweep: CGFloat = -1
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        Button {
            Haptics.light()
            action()
        } label: {
            content
                .frame(maxWidth: .infinity, minHeight: minHeight, alignment: .leading)
                .background(on ? Theme.selected : Theme.surface, in: RoundedRectangle(cornerRadius: radius))
                .overlay {
                    GeometryReader { g in
                        LinearGradient(colors: [.clear, Theme.accent.opacity(0.22), .clear],
                                       startPoint: .leading, endPoint: .trailing)
                            .frame(width: g.size.width * 0.5)
                            .offset(x: sweep * g.size.width)
                    }
                    .clipShape(RoundedRectangle(cornerRadius: radius))
                    .allowsHitTesting(false)
                }
                .overlay(RoundedRectangle(cornerRadius: radius).stroke(on ? Theme.accent : Color.clear, lineWidth: 1.5))
                .contentShape(RoundedRectangle(cornerRadius: radius))
                .animation(Motion.select, value: on)
        }
        .buttonStyle(PressStyle())
        .accessibilityAddTraits(on ? .isSelected : [])
        .onChange(of: on) { _, now in
            guard now, !reduceMotion else { return }
            sweep = -0.5
            withAnimation(Motion.select) { sweep = 1 }
        }
    }
}

/// One of several: a ring that fills, just after the sweep.
struct RadioDot: View {
    let on: Bool

    var body: some View {
        Circle()
            .strokeBorder(on ? Theme.accent : Theme.outlineStrong, lineWidth: 1.5)
            .background(Circle().fill(on ? Theme.accent : Color.clear).padding(5))
            .frame(width: 22, height: 22)
            .animation(Motion.select.delay(0.1), value: on)
            .accessibilityHidden(true)
    }
}

/// Pick several (D118: squares mean "more than one").
struct TickBox: View {
    let on: Bool

    var body: some View {
        RoundedRectangle(cornerRadius: 6)
            .strokeBorder(on ? Theme.accent : Theme.outlineStrong, lineWidth: 1.5)
            .background(RoundedRectangle(cornerRadius: 6).fill(on ? Theme.accent : Color.clear))
            .overlay {
                if on {
                    Image(systemName: "checkmark").font(.caption.weight(.bold)).foregroundStyle(Theme.onAccent)
                }
            }
            .frame(width: 22, height: 22)
            .animation(Motion.select.delay(0.1), value: on)
            .accessibilityHidden(true)
    }
}

/// A row of pill chips that wrap: "Today", "Tomorrow"; "Yes", "No".
struct Chip: View {
    let title: String
    let on: Bool
    var height: CGFloat = 48
    let action: () -> Void

    var body: some View {
        Button {
            Haptics.light()
            action()
        } label: {
            Text(title)
                .font(.subheadline.weight(.medium))
                .foregroundStyle(on ? Theme.onAccent : Theme.ink)
                .padding(.horizontal, 16)
                .frame(maxWidth: .infinity, minHeight: height)
                .background(on ? Theme.accentFill : Color.clear, in: Capsule())
                .overlay(Capsule().stroke(on ? Theme.accent : Theme.outline, lineWidth: 1.5))
                .contentShape(Capsule())
                .animation(Motion.select, value: on)
        }
        .buttonStyle(PressStyle())
        .accessibilityAddTraits(on ? .isSelected : [])
    }
}

/// Lays its children out in rows, wrapping when the next one doesn't fit.
struct FlowRow: Layout {
    var spacing: CGFloat = 8
    var lineSpacing: CGFloat = 6

    private func frames(_ maxWidth: CGFloat, _ subviews: Subviews) -> [CGRect] {
        var out: [CGRect] = []
        var x: CGFloat = 0, y: CGFloat = 0, lineHeight: CGFloat = 0
        for v in subviews {
            var size = v.sizeThatFits(.unspecified)
            if size.width > maxWidth { size = v.sizeThatFits(ProposedViewSize(width: maxWidth, height: nil)) }
            if x > 0, x + spacing + size.width > maxWidth {
                x = 0
                y += lineHeight + lineSpacing
                lineHeight = 0
            }
            let left = x == 0 ? 0 : x + spacing
            out.append(CGRect(origin: CGPoint(x: left, y: y), size: size))
            x = left + size.width
            lineHeight = max(lineHeight, size.height)
        }
        return out
    }

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let f = frames(proposal.width ?? .infinity, subviews)
        return CGSize(width: f.map(\.maxX).max() ?? 0, height: f.map(\.maxY).max() ?? 0)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let f = frames(bounds.width, subviews)
        for (i, v) in subviews.enumerated() {
            v.place(at: CGPoint(x: bounds.minX + f[i].minX, y: bounds.minY + f[i].minY),
                    proposal: ProposedViewSize(f[i].size))
        }
    }
}

// ---- motion modifiers ---------------------------------------------------------------------------------------

/// Settle (450 ms): content rises 10 pt as it fades in; `order` staggers it by 60 ms.
struct Settle: ViewModifier {
    let order: Int
    @State private var shown = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    func body(content: Content) -> some View {
        content
            .opacity(shown ? 1 : 0)
            .offset(y: shown || reduceMotion ? 0 : 10)
            .onAppear {
                guard !shown else { return }
                withAnimation(reduceMotion ? Motion.fade : Motion.settle.delay(Double(order) * 0.06)) { shown = true }
            }
    }
}

/// Drift (16 s): an open photo scales and drifts, slowly. Not with Reduce Motion, and not in the CI screenshots.
struct Drift: ViewModifier {
    let active: Bool
    @State private var on = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    func body(content: Content) -> some View {
        content
            .scaleEffect(on ? 1.06 : 1, anchor: .center)
            .offset(x: on ? -6 : 0, y: on ? -4 : 0)
            .onAppear {
                guard active, !reduceMotion, !AppConfig.demo else { return }
                withAnimation(.linear(duration: 16)) { on = true }
            }
    }
}

/// Lift (700 ms): the share card tilts up into place.
struct Lift: ViewModifier {
    @State private var on = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    func body(content: Content) -> some View {
        content
            .rotation3DEffect(.degrees(on || reduceMotion ? 0 : 12), axis: (x: 1, y: 0, z: 0), anchor: .bottom,
                              perspective: 0.6)
            .offset(y: on || reduceMotion ? 0 : 24)
            .opacity(on ? 1 : 0)
            .onAppear { withAnimation(reduceMotion ? Motion.fade : Motion.lift) { on = true } }
    }
}

extension View {
    func settle(_ order: Int = 0) -> some View { modifier(Settle(order: order)) }
}

// ---- the arch -----------------------------------------------------------------------------------------------

/// A doorway: straight sides and a half circle on top, drawn in its own units (the design files' SVG viewBoxes):
/// the logo's light (180 × 220), the logo's frame, the rating arch (120 × 152) and the small glyph (14 × 18).
struct DoorShape: Shape {
    var box: CGSize
    var left: CGFloat
    var right: CGFloat
    var spring: CGFloat           // where the curve starts
    var bottom: CGFloat
    var closed = true

    static let logoLight = DoorShape(box: CGSize(width: 180, height: 220), left: 50, right: 130, spring: 74, bottom: 160)
    static let logoFrame = DoorShape(box: CGSize(width: 180, height: 220), left: 34, right: 146, spring: 70, bottom: 160,
                                     closed: false)
    static let rating = DoorShape(box: CGSize(width: 120, height: 152), left: 30, right: 90, spring: 54, bottom: 120)
    static let glyph = DoorShape(box: CGSize(width: 14, height: 18), left: 1, right: 13, spring: 7, bottom: 18)

    func path(in rect: CGRect) -> Path {
        let s = min(rect.width / box.width, rect.height / box.height)
        let ox = rect.midX - box.width * s / 2, oy = rect.midY - box.height * s / 2
        func pt(_ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: ox + x * s, y: oy + y * s) }
        var p = Path()
        p.move(to: pt(left, bottom))
        p.addLine(to: pt(left, spring))
        // from the left, over the top, to the right (angles grow clockwise on screen)
        p.addRelativeArc(center: pt((left + right) / 2, spring), radius: (right - left) / 2 * s,
                         startAngle: .degrees(180), delta: .degrees(180))
        p.addLine(to: pt(right, bottom))
        if closed { p.closeSubpath() }
        return p
    }
}

/// The light spilling onto the ground in front of the door: a trapezoid, in the same units.
struct PoolShape: Shape {
    var box: CGSize
    var top: CGFloat
    var topLeft: CGFloat
    var topRight: CGFloat
    var bottom: CGFloat
    var bottomLeft: CGFloat
    var bottomRight: CGFloat

    static let logo = PoolShape(box: CGSize(width: 180, height: 220), top: 160, topLeft: 50, topRight: 130,
                                bottom: 214, bottomLeft: 4, bottomRight: 176)
    static let rating = PoolShape(box: CGSize(width: 120, height: 152), top: 121, topLeft: 30, topRight: 90,
                                  bottom: 150, bottomLeft: 4, bottomRight: 116)

    func path(in rect: CGRect) -> Path {
        let s = min(rect.width / box.width, rect.height / box.height)
        let ox = rect.midX - box.width * s / 2, oy = rect.midY - box.height * s / 2
        func pt(_ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: ox + x * s, y: oy + y * s) }
        var p = Path()
        p.move(to: pt(topLeft, top))
        p.addLine(to: pt(topRight, top))
        p.addLine(to: pt(bottomRight, bottom))
        p.addLine(to: pt(bottomLeft, bottom))
        p.closeSubpath()
        return p
    }
}

/// How far the light has risen inside a door: everything below a line that climbs from `bottom` to `top`.
struct RisingLevel: Shape {
    var box: CGSize
    var top: CGFloat
    var bottom: CGFloat
    var level: CGFloat

    var animatableData: CGFloat {
        get { level }
        set { level = newValue }
    }

    func path(in rect: CGRect) -> Path {
        let s = min(rect.width / box.width, rect.height / box.height)
        let oy = rect.midY - box.height * s / 2
        let y = oy + (bottom - max(0, min(1, level)) * (bottom - top)) * s
        return Path(CGRect(x: rect.minX, y: y, width: rect.width, height: max(0, rect.maxY - y)))
    }
}

/// The ODYS mark: a doorway of light in a dark frame, the light spilling out in front, a soft halo behind.
/// Reveal (900 ms): `light` rises in the arch, then `pool` spills.
struct ArchLogo: View {
    var light: CGFloat = 1
    var pool: CGFloat = 1
    var halo = true

    private static let box = CGSize(width: 180, height: 220)

    var body: some View {
        GeometryReader { g in
            let s = min(g.size.width / 180, g.size.height / 220)
            ZStack {
                if halo {
                    Ellipse()
                        .fill(RadialGradient(colors: [Theme.accent.opacity(0.22 * light), Theme.accent.opacity(0)],
                                             center: UnitPoint(x: 0.5, y: 0.55), startRadius: 0, endRadius: 100 * s))
                        .frame(width: 180 * s, height: 200 * s)
                }
                DoorShape.logoFrame.stroke(Theme.line, lineWidth: 10 * s)
                DoorShape.logoLight
                    .fill(LinearGradient(colors: [Theme.amberLight, Theme.accent, Theme.amberDeep],
                                         startPoint: UnitPoint(x: 0.5, y: 34 / 220), endPoint: UnitPoint(x: 0.5, y: 160 / 220)))
                    .mask { RisingLevel(box: Self.box, top: 34, bottom: 160, level: light) }
                PoolShape.logo
                    .fill(LinearGradient(colors: [Theme.accent.opacity(0.55), Theme.accent.opacity(0)],
                                         startPoint: UnitPoint(x: 0.5, y: 160 / 220), endPoint: UnitPoint(x: 0.5, y: 214 / 220)))
                    .opacity(pool)
                Path { p in
                    p.move(to: CGPoint(x: g.size.width / 2 - 76 * s, y: g.size.height / 2 + 50 * s))
                    p.addLine(to: CGPoint(x: g.size.width / 2 + 76 * s, y: g.size.height / 2 + 50 * s))
                }
                .stroke(Theme.line, lineWidth: 2 * s)
            }
            .frame(width: g.size.width, height: g.size.height)
        }
        .aspectRatio(180 / 220, contentMode: .fit)
        .accessibilityHidden(true)
    }
}

/// The small arch, as a bullet ("So far, I've learned…") and beside "Planned with ODYS".
struct ArchGlyph: View {
    var color: Color = Theme.accent
    var width: CGFloat = 14

    var body: some View {
        DoorShape.glyph
            .fill(color)
            .frame(width: width, height: width * 18 / 14)
            .accessibilityHidden(true)
    }
}

/// The "ODYS" wordmark: Newsreader, widely spaced.
struct Wordmark: View {
    var size: CGFloat = 20

    var body: some View {
        Text("ODYS")
            .font(Theme.serif(size, relativeTo: .title3))
            .tracking(size * 0.34)
            .foregroundStyle(Theme.ink)
            .padding(.leading, size * 0.34)      // the tracking adds space after the last letter; balance it
            .accessibilityLabel("ODYS")
    }
}

/// Abram's initial, for "run by one person".
struct AbramAvatar: View {
    var size: CGFloat = 52

    var body: some View {
        Text("A")
            .font(Theme.serif(size * 0.42, relativeTo: .title3))
            .foregroundStyle(Theme.ink)
            .frame(width: size, height: size)
            .background(Circle().fill(RadialGradient(colors: [Color(hex: 0x6B5640), Color(hex: 0x2A231C)],
                                                     center: UnitPoint(x: 0.4, y: 0.35), startRadius: 0,
                                                     endRadius: size * 0.6)))
            .accessibilityHidden(true)
    }
}

/// Listen (2.4 s loop): rings while someone speaks. A still ring with Reduce Motion.
struct ListenRings: View {
    let active: Bool
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        if active && !reduceMotion {
            TimelineView(.animation) { tl in
                let t = tl.date.timeIntervalSinceReferenceDate.truncatingRemainder(dividingBy: 2.4) / 2.4
                ZStack {
                    ForEach(0..<3, id: \.self) { i in
                        let p = (t + Double(i) / 3).truncatingRemainder(dividingBy: 1)
                        Circle()
                            .stroke(Theme.accent.opacity(0.55 * (1 - p)), lineWidth: 1.5)
                            .scaleEffect(1 + p * 0.9)
                    }
                }
            }
            .allowsHitTesting(false)
            .accessibilityHidden(true)
        } else if active {
            Circle().stroke(Theme.accent.opacity(0.45), lineWidth: 1.5).scaleEffect(1.3)
                .allowsHitTesting(false)
                .accessibilityHidden(true)
        }
    }
}

/// Breathe (6 s loop): the glow behind the arch on the "Now" screen, slowly brighter and dimmer. Still with Reduce
/// Motion.
struct BreathingArch: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(AppModel.self) private var model
    var showSun = false
    @State private var sun: Double?    // D130: set once, so the sun never moves while someone is looking

    var body: some View {
        // D130: by day the arch's light takes the sky's colour; on "Now" the sun sits where the real sun is
        let day = model.sky.isDay
        let light = day ? Theme.skyTop(model.sky) : Theme.accent
        let glow = day ? 0.75 : 0.1
        TimelineView(.animation(minimumInterval: 1.0 / 30, paused: reduceMotion)) { tl in
            let t = tl.date.timeIntervalSinceReferenceDate
            let b = reduceMotion ? 0.5 : (1 - cos(t / 6 * 2 * .pi)) / 2
            ZStack {
                Circle()
                    .fill(RadialGradient(colors: [light.opacity(glow + 0.1 * b), light.opacity(0)],
                                         center: .center, startRadius: 0, endRadius: 80))
                    .frame(width: 160, height: 160)
                    .scaleEffect(0.94 + 0.06 * b)
                ArchGlyph(color: Theme.accent.opacity(0.62 + 0.18 * b), width: 40)
                if let sun {
                    // sunrise on the left, sunset on the right, over the arch
                    let a = Double.pi * (1 - sun)
                    ZStack {
                        Circle().fill(Theme.amberLight.opacity(0.5)).frame(width: 22, height: 22)
                        Circle().fill(Theme.accent).frame(width: 12, height: 12)
                    }
                    .offset(x: 62 * cos(a), y: 160 * 0.12 - 62 * sin(a))
                }
            }
        }
        .frame(width: 160, height: 160)
        .accessibilityHidden(true)
        .onAppear { if showSun, model.sky.isDay { sun = Sun.dayFraction(.now) } }
    }
}

// ---- pictures -----------------------------------------------------------------------------------------------

/// A field of colour standing in for a photo, one per kind of moment (the design files' fields).
struct Field: View {
    let feel: String?

    var body: some View {
        switch feel {
        case "Drifting", "Big views":
            LinearGradient(stops: [.init(color: Color(hex: 0x22304A), location: 0), .init(color: Color(hex: 0x4A5C78), location: 0.4),
                                   .init(color: Color(hex: 0xD49A5A), location: 0.6), .init(color: Color(hex: 0x1A1C22), location: 1)],
                           startPoint: .top, endPoint: .bottom)
        default:
            RadialGradient(colors: Self.colors(feel), center: UnitPoint(x: 0.4, y: 0.2), startRadius: 0, endRadius: 340)
        }
    }

    static func colors(_ feel: String?) -> [Color] {
        let hex: [UInt32]
        switch feel {
        case "Lively", "Lunch": hex = [0xC0663A, 0x5E2618, 0x17120F]
        case "Awe", "Wonder": hex = [0xE7B77A, 0x9A6A3E, 0x3B2A1E, 0x15130F]
        case "Calm", "Resting": hex = [0x86A870, 0x3B5532, 0x141A12]
        case "Curious": hex = [0x8A7A62, 0x4A3F33, 0x1B1814]
        case "Browsing", "Wandering": hex = [0xC8C0B2, 0x6E675E, 0x22201D]
        case "Active", "Absorbed": hex = [0x5D8BA8, 0x27455A, 0x101519]
        default: hex = [0x9A7A58, 0x4A3A2A, 0x15130F]
        }
        return hex.map { Color(hex: $0) }
    }
}

/// A moment's photo (openly licensed, with its credit shown nearby), or its field of colour.
struct MomentImage: View {
    let momentId: String
    let feel: String?
    var drift = false

    var body: some View {
        if let found = CardPhotos.photo(for: momentId) {
            Image(uiImage: found.1)
                .resizable()
                .scaledToFill()
                .modifier(Drift(active: drift))
                .accessibilityLabel("Photo of the place")
        } else {
            Field(feel: feel)
        }
    }
}
