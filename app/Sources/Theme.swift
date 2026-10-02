import SwiftUI
import UIKit

/// ODYS (D119, from Abram's design files): warm ink on charcoal, one amber light, Newsreader serif for what matters
/// and the system font for the rest. Dark always (`.preferredColorScheme(.dark)` at the root), so every colour here is
/// fixed. The older token names (surface, inkSoft, accentFill …) are kept, so every screen picks up the new look.
enum Theme {
    // ---- colours ---------------------------------------------------------------------------------
    static let uiBackground = UIColor(hex: 0x111317)
    static let uiInk = UIColor(hex: 0xF4EBDD)

    static let background = Color(hex: 0x111317)     // the phone
    static let calm = Color(hex: 0x0B0C0E)           // "Now": the screen gets quieter while you're out
    static let surface = Color(hex: 0x1A1D23)        // cards and tiles
    static let deep = Color(hex: 0x15171C)           // the day's curve and the map
    static let surfaceHigh = Color(hex: 0x2A2E36)    // a chosen tab, a field
    static let selected = Color(hex: 0x241F17)       // a chosen tile: a little warmth
    static let ink = Color(hex: 0xF4EBDD)
    static let inkSoft = Color(hex: 0xCFC6B8)
    static let inkTertiary = Color(hex: 0xB5AB9C)
    static let muted = Color(hex: 0xA89F92)          // labels; 7:1 on the background
    static let line = Color(hex: 0x2C2F36)           // the arch's frame, the path not yet walked
    static let outline = Color(hex: 0xF4EBDD).opacity(0.12)
    static let outlineStrong = Color(hex: 0xF4EBDD).opacity(0.18)
    static let hairline = Color(hex: 0xF4EBDD).opacity(0.07)
    /// The one light: amber for text, icons, fills and the tint.
    static let accent = Color(hex: 0xFFC665)
    static let accentFill = accent
    static let amberDeep = Color(hex: 0xE5A93C)      // eyebrows, a pressed button
    static let amberLight = Color(hex: 0xFFE7B0)     // the top of the arch's light
    static let onAccent = Color(hex: 0x111317)
    // Help & safety: one red, only for emergencies
    static let danger = Color(hex: 0xE5484D)         // "Call 999"
    static let emergencyBg = Color(hex: 0x3A1416)
    static let emergencyBorder = Color(hex: 0x7A2A2E)
    static let emergencyTitle = Color(hex: 0xFFDCDC)
    static let emergencyText = Color(hex: 0xF6D2D2)
    // The share card is cream, so it reads the same wherever it's sent
    static let cream = Color(hex: 0xF4EBDD)
    static let creamInk = Color(hex: 0x111317)
    static let creamSoft = Color(hex: 0x6B5E4C)
    static let creamQuote = Color(hex: 0x3A3128)

    // ---- type: serif for titles, answers and reactions; system for the rest. All scale with Dynamic Type --------
    static let serifName = "Newsreader16pt-Regular"   // the variable font's default instance (Sources/Fonts)
    static let italicName = "Newsreader16pt-Italic"   // D119: reactions, feel words, quotes

    static func serif(_ size: CGFloat, relativeTo style: Font.TextStyle) -> Font {
        .custom(serifName, size: size, relativeTo: style)
    }

    static func italic(_ size: CGFloat, relativeTo style: Font.TextStyle) -> Font {
        .custom(italicName, size: size, relativeTo: style)
    }

    static let hero = serif(44, relativeTo: .largeTitle)      // "Now"
    static let display = serif(40, relativeTo: .largeTitle)   // Welcome
    static let h1 = serif(34, relativeTo: .largeTitle)        // each screen's title
    static let title = serif(28, relativeTo: .title)
    static let title2 = serif(24, relativeTo: .title2)
    static let title3 = serif(21, relativeTo: .title3)
    static let option = serif(22, relativeTo: .title3)        // an answer on a tile
    static let reaction = italic(20, relativeTo: .title3)     // "Got it: …", in amber

    /// Navigation bars on the page colour, for the few screens that keep one (sheets, the moment card).
    static func applyAppearance() {
        let bar = UINavigationBarAppearance()
        bar.configureWithOpaqueBackground()
        bar.backgroundColor = uiBackground
        bar.shadowColor = .clear
        bar.largeTitleTextAttributes = [.foregroundColor: uiInk]
        bar.titleTextAttributes = [.foregroundColor: uiInk]
        // at the top of a page the bar is clear, so the moment card's photo runs under it; once scrolled, it's solid
        let edge = UINavigationBarAppearance()
        edge.configureWithTransparentBackground()
        edge.titleTextAttributes = [.foregroundColor: uiInk]
        edge.largeTitleTextAttributes = [.foregroundColor: uiInk]
        UINavigationBar.appearance().standardAppearance = bar
        UINavigationBar.appearance().scrollEdgeAppearance = edge
        UINavigationBar.appearance().compactAppearance = bar
    }
}

extension UIColor {
    convenience init(hex: UInt32) {
        self.init(red: CGFloat((hex >> 16) & 0xFF) / 255, green: CGFloat((hex >> 8) & 0xFF) / 255,
                  blue: CGFloat(hex & 0xFF) / 255, alpha: 1)
    }
}

extension Color {
    init(hex: UInt32) {
        self.init(uiColor: UIColor(hex: hex))
    }
}

/// A screen's title in the serif, at the top of its content (the ODYS screens have no navigation-bar titles).
struct PageTitle: View {
    let text: String
    var font: Font = Theme.h1

    var body: some View {
        Text(text)
            .font(font)
            .foregroundStyle(Theme.ink)
            .fixedSize(horizontal: false, vertical: true)
            .accessibilityAddTraits(.isHeader)
            .frame(maxWidth: .infinity, alignment: .leading)
    }
}

extension View {
    /// The screen's title, inline in the navigation bar and in the serif (m150), for sheets that keep a bar.
    /// `navigationTitle` is still set, for VoiceOver and the back button.
    func serifTitle(_ title: String) -> some View {
        navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(title)
                        .font(Theme.serif(19, relativeTo: .headline))
                        .foregroundStyle(Theme.ink)
                        .lineLimit(1)
                        .accessibilityAddTraits(.isHeader)
                }
            }
    }

    /// Lists and forms on the page colour instead of the system grey, with the rows on the card colour.
    func themedList() -> some View {
        scrollContentBackground(.hidden).background(Theme.background)
    }

    /// On screens without a navigation bar: what scrolls up under the status bar goes behind the page colour.
    func statusBarShade() -> some View {
        safeAreaInset(edge: .top, spacing: 0) {
            Color.clear.frame(height: 0).background(Theme.background)
        }
    }

    /// A rounded card on the surface colour.
    func surfaceCard(padding: CGFloat = 16, radius: CGFloat = 18) -> some View {
        self.padding(padding)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: radius))
    }
}
