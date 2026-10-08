import SwiftUI
import UIKit

/// D114, D119: the card a person can share after rating a stop, in the ODYS cream: the moment's photo with the word they
/// rated it, "I think you'd love this", the title, their own reason in their own voice (D115), and "Planned with ODYS".
/// Never the model's "worth £X". No rewards. The photo is openly licensed, so its credit goes on the card. Fixed sizes,
/// so the picture is the same wherever it's sent (1080 × 1350).
struct ShareCardView: View {
    let stop: Stop
    let rating: Int

    var body: some View {
        let found = CardPhotos.photo(for: stop.momentId)
        let word = Labels.feel[max(0, min(4, rating - 1))]
        VStack(alignment: .leading, spacing: 0) {
            ZStack(alignment: .topLeading) {
                Color.clear
                    .frame(width: 360, height: 236)
                    .overlay {
                        if let image = found?.1 {
                            Image(uiImage: image).resizable().scaledToFill()
                        } else {
                            Field(feel: stop.feelWord)
                        }
                    }
                    .clipped()
                // their own rating, as a word
                Text("Rated: \(word)")
                    .font(.custom(Theme.italicName, fixedSize: 15))
                    .foregroundStyle(Theme.accent)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Theme.creamInk.opacity(0.62), in: Capsule())
                    .padding(16)
            }
            VStack(alignment: .leading, spacing: 8) {
                Text("I think you'd love this")
                    .font(.system(size: 14))
                    .foregroundStyle(Theme.creamSoft)
                Text(stop.title)
                    .font(.custom(Theme.serifName, fixedSize: 25))
                    .foregroundStyle(Theme.creamInk)
                    .lineLimit(3)
                    .minimumScaleFactor(0.7)
                if let why = stop.reasons?.compactMap(\.me).first {
                    // D115: the plain-language reason, from the sharer's answers (journey round 2: not a quote)
                    Text(why)
                        .font(.custom(Theme.italicName, fixedSize: 17))
                        .foregroundStyle(Theme.creamQuote)
                        .lineLimit(3)
                        .minimumScaleFactor(0.8)
                        .fixedSize(horizontal: false, vertical: true)
                }
                Spacer(minLength: 0)
                HStack(spacing: 8) {
                    ArchGlyph(color: Theme.amberDeep, width: 10)
                    Text("Planned with ODYS")
                        .font(.system(size: 13))
                        .foregroundStyle(Theme.creamSoft)
                }
                if let photo = found?.0 {
                    Text("Photo: \(photo.author), \(photo.licence), Wikimedia Commons (cropped)")
                        .font(.system(size: 8))
                        .foregroundStyle(Theme.creamSoft)
                        .lineLimit(2)
                }
            }
            .padding(20)
            .frame(width: 360, height: 214, alignment: .topLeading)
            .background(Theme.cream)
        }
        .frame(width: 360, height: 450)
        .background(Theme.cream)
        .accessibilityElement(children: .combine)
    }

    /// The card as a picture (1080 × 1350).
    @MainActor static func render(stop: Stop, rating: Int) -> UIImage? {
        let renderer = ImageRenderer(content: ShareCardView(stop: stop, rating: rating))
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
