# Abram's three videos: format and size (D117)

**Decision first:** record three portrait videos on your iPhone. Send them with their captions, or with the exact words you say. They are bundled inside the app, with no YouTube or Vimeo and nothing streamed. The app already has a place for each one. It shows a video as soon as its file is in the app, and leaves that place out until then.

## The three videos

| File name | Where it plays | Length | What you say (suggested) |
|---|---|---|---|
| `founder` | Its own screen, after the example day (before "Before we start"). It's skippable, and its "Skip" button becomes "Continue" when it ends | 20–30 s | Who you are, why you're building this (Big Ben left you flat, the boat and the street food didn't), and that it's a research test |
| `ask_moment` | A small tile beside the "great moment" question (screen 4) | about 5–10 s | The question itself: "Tell me about a great moment from a recent day out. Where were you, and how did it feel?" |
| `thanks` | A small tile on "So far, I've learned…", before the first plan | 5–8 s | "Thank you. Here's what I've picked up so far. If anything's wrong, change it." |

## Format

- **Portrait (vertical), 1080 × 1920**, 30 frames a second.
  - The founder video fills the screen width.
  - The two short clips play in a small portrait tile, cropped to fill it. Keep your face in the middle, with some space above your head.
- **.mp4 or .mov**, H.264 or HEVC, with AAC sound. That's what the iPhone camera records by default, so no export settings need changing.
- **Sound:** a quiet room, phone at arm's length or on a stand, facing a window. The app follows the phone's silent switch, so many people will watch with captions only.
- **Captions (required):** one `.srt` caption file per video, with the same name (`founder.srt`, `ask_moment.srt`, `thanks.srt`). Most video editing apps can export one. If yours can't, send me the exact words you say and I'll write the `.srt`, timed by word count. You then check it on the screenshot page. The app draws the captions itself, so don't burn them into the picture.

## Size limits

- **Per file: under 25 MB.** That's GitHub's limit for a file added through the website ("no larger than 25 MiB", GitHub Docs, read 1 Oct 2026). It's the easy way to hand them over:
  1. On github.com, open the branch's `app/Sources/` folder.
  2. Choose "Add file → Upload files".
  3. Upload into a new `Video` folder.
- **All three together: about 25 MB or less** (my budget, so the app stays a quick download).
  - At 1080p, about 4 Mbit/s for the picture plus 128 kbit/s for the sound, 30 s is about 15.5 MB.
  - A 30 s iPhone 1080p HEVC clip is usually smaller.
  - If a file is bigger than 25 MB, send it however is easiest (AirDrop to a computer, then upload a compressed copy). I can't compress video in this environment.
- **Apple's limit is far above this:** a 4 GB uncompressed app for iOS 9 and later (Apple, "Maximum build file sizes", read 1 Oct 2026). Videos of this size don't come near it.

## What happens in the app

- **Autoplay:** each video plays when its screen opens, unless the person has turned off video autoplay (Settings → Accessibility → Motion). Then it waits for a tap.
- **Captions are always on.** The sound follows the silent switch.
- **The founder video:** how far people watch is sent as one event after they agree to take part (seconds watched, and whether it ended). It's the Test A measure for this screen.
- **No video host:** the videos are part of the app download itself (TestFlight, later the App Store), with no YouTube, Vimeo or streaming.
- **Your time:** about 1–1.5 h (writing what to say, three takes each, picking the best).
- **My time once the files arrive:**
  - about 0.5 h: captions if needed, checking each file plays, new screenshots;
  - plus one TestFlight build.
