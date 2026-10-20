import SwiftUI
import UIKit

/// ODYS (D119, from Abram's design files): warm ink, one amber light, Newsreader serif for what matters and the system
/// font for the rest. D130 (Daylight): every colour is a night and a day value; the root sets the colour scheme from
/// London's light (`AppModel.sky`), so each screen and sheet follows it. The night values are the D119 look. The same
/// values as android/…/Theme.kt, where ThemeTest checks every text colour is 4.5:1 or better on every ground and sky.
enum Theme {
    // ---- colours ---------------------------------------------------------------------------------
    /// A colour with its night value and its day value.
    static func ui(_ night: UInt32, _ day: UInt32, _ nightAlpha: CGFloat = 1, _ dayAlpha: CGFloat = 1) -> UIColor {
        UIColor { $0.userInterfaceStyle == .light ? UIColor(hex: day, alpha: dayAlpha) : UIColor(hex: night, alpha: nightAlpha) }
    }

    static func pair(_ night: UInt32, _ day: UInt32, _ nightAlpha: CGFloat = 1, _ dayAlpha: CGFloat = 1) -> Color {
        Color(uiColor: ui(night, day, nightAlpha, dayAlpha))
    }

    static let uiBackground = ui(0x111317, 0xF4F1EA)
    static let uiInk = ui(0xF4EBDD, 0x1E2326)

    static let background = pair(0x111317, 0xF4F1EA)     // the phone
    static let calm = pair(0x0B0C0E, 0xF4F1EA)           // "Now": the screen gets quieter while you're out
    static let surface = pair(0x1A1D23, 0xFFFDF8)        // cards and tiles
    static let deep = pair(0x15171C, 0xECE8DF)           // the day's curve and the map
    static let surfaceHigh = pair(0x2A2E36, 0xE7E2D8)    // a chosen tab, a field
    static let selected = pair(0x241F17, 0xF5E8D2)       // a chosen tile: a little warmth
    static let ink = pair(0xF4EBDD, 0x1E2326)
    static let inkSoft = pair(0xCFC6B8, 0x3B4044)
    static let inkTertiary = pair(0xB5AB9C, 0x4C5156)
    static let muted = pair(0xA89F92, 0x5A5F64)          // labels
    static let line = pair(0x2C2F36, 0xD6D0C4)           // the arch's frame, the path not yet walked
    static let outline = pair(0xF4EBDD, 0x1E2326, 0.12, 0.16)
    static let outlineStrong = pair(0xF4EBDD, 0x1E2326, 0.18, 0.24)
    static let hairline = pair(0xF4EBDD, 0x1E2326, 0.07, 0.09)
    /// The one light: amber for text, icons, fills and the tint (deepened by day so it reads on paper).
    static let accent = pair(0xFFC665, 0x80521A)
    static let accentFill = accent
    static let amberDeep = pair(0xE5A93C, 0x6E4614)      // eyebrows, a pressed button
    static let amberLight = pair(0xFFE7B0, 0xE8B76A)     // the top of the arch's light
    static let onAccent = pair(0x111317, 0xFFFDF8)
    // Help & safety: one red, only for emergencies
    static let danger = pair(0xD0363B, 0xB8262C)         // "Call 999": white on it is 4.9:1 at night, 6.3:1 by day
    static let dangerInk = pair(0xFF8A8D, 0xB8262C)      // red as text (D130: the fill was 3.8:1 as text at night)
    static let emergencyBg = pair(0x3A1416, 0xFBE4E2)
    static let emergencyBorder = pair(0x7A2A2E, 0xE7AEAD)
    static let emergencyTitle = pair(0xFFDCDC, 0x7A1518)
    static let emergencyText = pair(0xF6D2D2, 0x6A2023)
    // Small parts that had their own colours
    static let track = pair(0x3A3E46, 0xCFC8BB)          // a progress track, a timeline
    static let ring = pair(0x4A4E57, 0xA9A398)           // a step not yet done
    static let warnBg = pair(0x3A1F1C, 0xF8E1DC)
    static let warnInk = pair(0xF0A090, 0x8A2A1C)
    static let okBg = pair(0x1F3A2A, 0xDDEFE3)
    static let okInk = pair(0x9BE0B0, 0x1F5A35)
    static let savedBg = pair(0x3A2F1C, 0xF5E8D2)
    // The share card is cream, so it reads the same wherever it's sent
    static let cream = Color(hex: 0xF4EBDD)
    static let creamInk = Color(hex: 0x111317)
    static let creamSoft = Color(hex: 0x6B5E4C)
    static let creamQuote = Color(hex: 0x3A3128)

    /// D130: the sky at the top of the main screens, which fades into the page.
    static func skyTop(_ sky: Sky) -> Color {
        switch sky {
        case .morning: return Color(hex: 0xE9DCE3)
        case .day: return Color(hex: 0xDDEBE6)
        case .golden: return Color(hex: 0xF4D6B3)
        case .rain: return Color(hex: 0xD5DCE2)
        case .night: return Color(hex: 0x1A2030)
        }
    }

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
    convenience init(hex: UInt32, alpha: CGFloat = 1) {
        self.init(red: CGFloat((hex >> 16) & 0xFF) / 255, green: CGFloat((hex >> 8) & 0xFF) / 255,
                  blue: CGFloat(hex & 0xFF) / 255, alpha: alpha)
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
