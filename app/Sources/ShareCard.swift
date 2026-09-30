import SwiftUI
import UIKit

/// D114: the card a person can share after rating a stop: the moment's photo, their own rating, "Planned with Days
/// out". Never the model's "worth £X". No rewards. The photo is openly licensed, so its credit goes on the card.
struct ShareCardView: View {
    let stop: Stop
    let rating: Int

    var body: some View {
        let found = CardPhotos.photo(for: stop.momentId)
        VStack(alignment: .leading, spacing: 0) {
            Group {
                if let image = found?.1 {
                    Image(uiImage: image).resizable().scaledToFill()
                } else {
                    LinearGradient(colors: [Theme.accentFill, Theme.surface], startPoint: .topLeading,
                                   endPoint: .bottomTrailing)
                }
            }
            .frame(width: 360, height: 262)
            .clipped()
            VStack(alignment: .leading, spacing: 8) {
                Text(stop.title)
                    .font(Theme.title2)
                    .foregroundStyle(Theme.ink)
                    .lineLimit(3)
                    .minimumScaleFactor(0.8)
                HStack(spacing: 6) {
                    ForEach(1...5, id: \.self) { n in
                        Image(systemName: n <= rating ? "circle.fill" : "circle")
                            .font(.caption)
                            .foregroundStyle(n <= rating ? Theme.accentFill : Theme.inkSoft)
                    }
                    Text("My rating: \(rating) of 5, \(Labels.feel[max(0, min(4, rating - 1))].lowercased())")
                        .font(.subheadline)
                        .foregroundStyle(Theme.ink)
                }
                Spacer(minLength: 0)
                HStack(alignment: .bottom) {
                    Text("Planned with Days out")
                        .font(.footnote.weight(.semibold))
                        .foregroundStyle(Theme.ink)
                    Spacer()
                }
                if let photo = found?.0 {
                    Text("Photo: \(photo.author), \(photo.licence), Wikimedia Commons (cropped)")
                        .font(.system(size: 8))
                        .foregroundStyle(Theme.inkSoft)
                        .lineLimit(2)
                }
            }
            .padding(18)
            .frame(width: 360, height: 188, alignment: .topLeading)
            .background(Theme.background)
        }
        .frame(width: 360, height: 450)
        .accessibilityElement(children: .combine)
    }

    /// The card as a picture (1080 × 1350), always in the light look so it reads the same wherever it's sent.
    @MainActor static func render(stop: Stop, rating: Int) -> UIImage? {
        let renderer = ImageRenderer(content: ShareCardView(stop: stop, rating: rating)
            .environment(\.colorScheme, .light))
        renderer.scale = 3
        return renderer.uiImage
    }
}

/// The system share sheet, with its outcome: which app it went to, or that it was cancelled.
enum ShareSheet {
    @MainActor static func present(_ items: [Any], done: @escaping @MainActor (_ to: String?, _ sent: Bool) -> Void) {
        let sheet = UIActivityViewController(activityItems: items, applicationActivities: nil)
        sheet.completionWithItemsHandler = { type, completed, _, _ in
            let to = type?.rawValue
            Task { @MainActor in done(to, completed) }
        }
        let window = UIApplication.shared.connectedScenes.compactMap { ($0 as? UIWindowScene)?.keyWindow }.first
        guard var top = window?.rootViewController else { return }
        while let next = top.presentedViewController { top = next }
        sheet.popoverPresentationController?.sourceView = top.view
        top.present(sheet, animated: true)
    }
}
