import SwiftUI
import UIKit

/// The moment cards' photos (Abram, 30 Sep): openly licensed photos from Wikimedia Commons, bundled with their
/// credits in `Photos/photo-credits.json`, until Abram's own replace them. A card without one keeps the satellite
/// view. The list, with each licence, is `design/photo-credits.md`.
struct CardPhoto: Decodable {
    let file: String
    let title: String
    let author: String
    let licence: String
    let source: URL
    let licenceURL: URL?
    /// m258: cleared for the share card: CC0 or CC BY, its credit confirmed and no notice on its page limiting use
    /// (brain/data/photo_checks.yaml). Missing means no: an uncertain photo is never shared.
    let share: Bool?

    /// The credit the licence asks for (title, author, source, licence), shown under the picture.
    var credit: String { "“\(title)” by \(author), \(licence), Wikimedia Commons (resized)" }
    /// m258: on the share card, which crops the photo: the title, the photographer, the licence and the change.
    var shareCredit: String { "Photo: “\(title)” by \(author), \(licence), Wikimedia Commons (cropped)" }
    /// m258: in the share message, where links are clickable: the licence and the photo's page.
    var shareLines: String {
        "Photo: “\(title)” by \(author), \(licence)" + (licenceURL.map { " (\($0.absoluteString))" } ?? "")
            + ", cropped. \(source.absoluteString)"
    }
}

enum CardPhotos {
    static let all: [String: CardPhoto] = {
        guard let url = Bundle.main.url(forResource: "photo-credits", withExtension: "json"),
              let data = try? Data(contentsOf: url) else { return [:] }
        return (try? JSONDecoder().decode([String: CardPhoto].self, from: data)) ?? [:]
    }()

    /// The card behind a plan stop: "<card>#lunch" is the same card as lunch; "lunch@…" slots have no card.
    static func cardId(_ momentId: String) -> String? {
        momentId.hasPrefix("lunch@") ? nil : String(momentId.split(separator: "#").first ?? "")
    }

    /// m258: the photo only if it's cleared for sharing; otherwise the card keeps its field of colour.
    static func sharePhoto(for momentId: String) -> (CardPhoto, UIImage)? {
        guard let found = photo(for: momentId), found.0.share == true else { return nil }
        return found
    }

    static func photo(for momentId: String) -> (CardPhoto, UIImage)? {
        guard let id = cardId(momentId), let photo = all[id],
              let url = Bundle.main.url(forResource: photo.file, withExtension: nil),
              let image = UIImage(contentsOfFile: url.path) else { return nil }
        return (photo, image)
    }
}
