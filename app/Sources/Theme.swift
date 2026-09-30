import SwiftUI
import UIKit

/// "Sensory Cartography" (D112, from Abram's Stitch explorations): charcoal surfaces, one amber accent and
/// Newsreader serif titles, applied as a theme on standard SwiftUI parts. Colours and fonts only: no custom
/// controls. Light mode uses warm paper with a deeper amber, so text keeps its contrast.
enum Theme {
    // ---- colours (dark / light) -------------------------------------------------------------
    static let uiBackground = dynamic(dark: 0x111317, light: 0xFAF7F0)
    static let uiSurface = dynamic(dark: 0x1E2023, light: 0xFFFFFF)
    static let uiInk = dynamic(dark: 0xE2E2E6, light: 0x1C1B18)

    static let background = Color(uiColor: uiBackground)
    static let surface = Color(uiColor: uiSurface)
    static let surfaceHigh = Color(uiColor: dynamic(dark: 0x282A2D, light: 0xF1ECE2))
    static let ink = Color(uiColor: uiInk)
    static let inkSoft = Color(uiColor: dynamic(dark: 0xD4C4B0, light: 0x5E5446))
    static let outline = Color(uiColor: dynamic(dark: 0x504535, light: 0xD8CDBA))
    /// Amber for text, icons and the tint: bright on charcoal, deep on paper.
    static let accent = Color(uiColor: dynamic(dark: 0xFFC665, light: 0x7E5700))
    /// Amber fills (the main button, chips, map pins), with `onAccent` text in both modes.
    static let accentFill = Color(uiColor: UIColor(hex: 0xFFC665))
    static let onAccent = Color(uiColor: UIColor(hex: 0x432C00))
    static let danger = Color(uiColor: UIColor(hex: 0xC62828))   // "Call 999": one red, white text in both modes

    // ---- type: serif titles, system text; everything scales with Dynamic Type ----------------
    static let serifName = "Newsreader16pt-Regular"   // the font's default instance (Sources/Fonts)

    static func serif(_ size: CGFloat, relativeTo style: Font.TextStyle) -> Font {
        .custom(serifName, size: size, relativeTo: style)
    }

    static let display = serif(34, relativeTo: .largeTitle)
    static let title = serif(28, relativeTo: .title)
    static let title2 = serif(23, relativeTo: .title2)
    static let title3 = serif(20, relativeTo: .title3)

    /// Navigation bars on the page colour. Called once at launch. Titles are set per screen with `serifTitle` (m150):
    /// in CI on iOS 26, bar titles styled here came out blank or in the system font.
    static func applyAppearance() {
        let bar = UINavigationBarAppearance()
        bar.configureWithOpaqueBackground()
        bar.backgroundColor = uiBackground
        bar.shadowColor = .clear
        bar.largeTitleTextAttributes = [.foregroundColor: uiInk]
        bar.titleTextAttributes = [.foregroundColor: uiInk]
        UINavigationBar.appearance().standardAppearance = bar
        UINavigationBar.appearance().scrollEdgeAppearance = bar
        UINavigationBar.appearance().compactAppearance = bar
    }

    private static func dynamic(dark: UInt32, light: UInt32) -> UIColor {
        UIColor { $0.userInterfaceStyle == .dark ? UIColor(hex: dark) : UIColor(hex: light) }
    }
}

extension UIColor {
    convenience init(hex: UInt32) {
        self.init(red: CGFloat((hex >> 16) & 0xFF) / 255, green: CGFloat((hex >> 8) & 0xFF) / 255,
                  blue: CGFloat(hex & 0xFF) / 255, alpha: 1)
    }
}

/// A big serif title at the top of a page's content (screens 2 and 3), in place of a large navigation title.
struct PageTitle: View {
    let text: String

    var body: some View {
        Text(text)
            .font(Theme.display)
            .foregroundStyle(Theme.ink)
            .accessibilityAddTraits(.isHeader)
            .frame(maxWidth: .infinity, alignment: .leading)
    }
}

extension View {
    /// The screen's title, inline in the navigation bar and in the serif (m150). `navigationTitle` is still set, for
    /// VoiceOver and the back button.
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

    /// Lists and forms on the page colour instead of the system grey.
    func themedList() -> some View {
        scrollContentBackground(.hidden).background(Theme.background)
    }

    /// A rounded surface card, used for the plan summary, the approach line and the example shot card.
    func surfaceCard(padding: CGFloat = 16) -> some View {
        self.padding(padding)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 14))
            .overlay(RoundedRectangle(cornerRadius: 14).stroke(Theme.outline, lineWidth: 1))
    }
}
