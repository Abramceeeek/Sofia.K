# Area 1 — Conversational onboarding (voice/video)

**Decision:**
- **Test A (Phase 3):** run a Wizard-of-Oz test over Telegram voice notes, with typing offered as an equal choice rather than a fallback. Answer mode (voice or text) is recorded for every participant. No build is needed, only about 3 founder hours for scripts.
- **v0 (Phase 4):** build a Telegram bot (aiogram) that transcribes voice notes through a hosted API and reads back what it heard. An LLM then turns the transcript into *quoted evidence* in a fixed schema. The βs come from the Area 3 model and never straight from the LLM. **About 10 founder hours.**
- **Deferred:** the real-time web video host (Pipecat + Silero VAD + Smart Turn, about 15–20 hours) waits until Test A shows that voice beats typing. A live avatar is only priced, as the premium tier in Phase 2.

## What exists (ranked)

| # | Name | Maturity | Licence | Why it matters |
|---|---|---|---|---|
| 1 | [Telegram Bot API](https://core.telegram.org/bots/api) + [aiogram](https://github.com/aiogram/aiogram) | ★5.9k, last commit 2026-08-25, Py 3.10+ | MIT | Voice capture with no infrastructure. Voice notes are push-to-talk, so the user ends their own turn and no turn detection is needed. Downloads are OGG/Opus, up to 20 MB |
| 2 | Hosted transcription: OpenAI gpt-4o-mini-transcribe (~$0.003/min), gpt-4o-transcribe / whisper-1 (~$0.006/min); Deepgram Nova-3 batch ($0.0043/min) | Production | Commercial API | A 10-minute onboarding costs about $0.03–0.06. Prices come from third-party pages, so re-check them in Phase 2 |
| 3 | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | ★25.6k, last commit 2025-11-19 (slow), Py ≥3.9 | MIT | Self-hosted fallback. Up to 4× faster than Whisper, and its built-in Silero VAD filter strips silence |
| 4 | [Silero VAD](https://github.com/snakers4/silero-vad) + [ricky0123/vad](https://github.com/ricky0123/vad) (browser) | ★10.3k / ★2.1k, both committed Sep 2026 | MIT | Detects start and end of speech in the browser for a web-video variant, at under 1 ms per audio chunk |
| 5 | [Pipecat](https://github.com/pipecat-ai/pipecat) + [Smart Turn v3.2](https://github.com/pipecat-ai/smart-turn) | ★15.9k (2026-09-26, Py ≥3.11) / ★1.6k (2026-01-29) | BSD-2 | Real-time voice pipeline. Its semantic end-of-turn model (8 MB, about 12–65 ms on CPU) avoids cutting people off mid-thought, which matters for "no time limit" |
| 6 | [LiveKit Agents](https://github.com/livekit/agents) | ★14.4k, 2026-09-25, Py 3.10–3.14 | Apache-2.0, but the turn-detector weights are under the LiveKit Model License | Alternative to Pipecat, but the model licence ties the turn detector to LiveKit |
| 7 | [Geiecke & Jaravel interview platform](https://github.com/friedrichgeiecke/interviews) | ★71, 2026-02-09 | PolyForm **Noncommercial** | The best-evidenced LLM interviewer design. We can copy its ideas (probes, prompt structure) but not the code |
| 8 | Live avatars: Tavus ($0.37/min overage), HeyGen LiveAvatar (~$0.20/min) | Production | Commercial | Only used to cost the premium tier |

## What the evidence says

- **Conversations beat forms for open answers.**
  - Chatbot vs Qualtrics (N≈600): chatbot surveys collected 39% more information, measured in bits (F(1,576)=38.55, p<.01, partial η²=0.06). Answers were also more relevant, specific and clear (Xiao et al. 2020).
  - Chatbot respondents satisficed less, and a casual tone reduced it further (Kim et al. 2019).
  - Reliability matched a standard questionnaire, and most users preferred the conversation (Celino & Re Calegari 2020).
- **LLM interviewers work at scale.**
  - An AI interview produced 148% more words than an open text box (N=462).
  - In a GPT-4o voice interview (N=354), 55% would choose another AI interview and 54% preferred voice to text. Experts rated the transcripts as comparable to human interviews (Geiecke & Jaravel, accepted at REStud).
  - LLM follow-up probes raise answer quality (Jacobsen et al., CHI 2025, N=64). Their *idiographic* probe ("describe one specific event") is exactly our "best hour of your last trip".
- **Active listening helps, but it has to respond to the speaker.**
  - Text chatbots that paraphrase, summarise and reflect emotion beat a baseline on both answer quality and engagement (Xiao et al., CHI 2020, N=206).
  - On video, listener nods that *respond* to the speaker built rapport, while a pre-recorded avatar that didn't respond did not (Gratch et al. 2007).
  - So a looping "nodding" clip is probably not enough. Nod or "mm" clips should fire on detected pauses, with spoken paraphrase on top.
- **Voice gives richer answers but loses people.**
  - Voice answers are more than twice as long and cover more topics (Höhne et al. 2024, N=1,001).
  - But asking for voice answers caused about 45% break-off against about 13% for text (Gavras & Höhne 2020, N=2,402). A replication found 51% against 24% (Höhne et al. 2024). The authors advise letting respondents choose.
  - Only about 40% of a German panel were willing to answer by voice (Lenzner & Höhne 2022, N=2,146).
  - Routing people who can't talk to a text box reduced nonresponse (Revilla et al. 2020).
- **Disclosing that the host is AI costs no candour.** People who believed the interviewer was automated disclosed more (Lucas et al. 2014).
- **Transcription errors are biased, not random.**
  - Whisper invents phrases in about 1% of transcripts, and 38% of those are harmful (Koenecke et al. 2024).
  - On survey voice answers, Whisper added words, while Google failed on long files (JSSAM 2025).
  - British English is recognised worse than American English (JASA-EL 2024), and regional accents worse still.
- **Structured extraction guarantees the format, not the content.**
  - Constrained decoding produces valid JSON 100% of the time on OpenAI's own evals.
  - LLM coding of open answers is close to human on concrete categories: Claude-1.3 scored 93.9% against 94.7% for a second human coder (Mellon et al. 2024). In a 2025 study, κ was above 0.6 on concrete themes and weaker on abstract ones.
  - LLM *numeric* ratings drift between repeated runs ("Rating Roulette", 2025). So the LLM should output categorical evidence with quotes, and the statistical model should turn that into numbers.

## Gaps we'd have to fill ourselves

- **Extraction schema (~3 h).** Map speech to our attributes as evidence records: `{attribute, direction, strength: weak|strong, quote, place}`.
- **Gold set (~2 h).** 20 Test A transcripts coded by Abram, to measure LLM-vs-human κ and run-to-run stability.
- **Adaptive follow-ups.** For example, a mention of queues leads to a crowds probe. Start with a short rule list; Area 3 covers optimal question design.
- **Responsive listening video for the web variant.** Pause-triggered clips; nothing off the shelf does this.

## Risks / unknowns

- **Voice dropout could sink the ≥70% completion threshold.** *Decided 2026-09-26:* Test A records answer mode as a variable. It reports the voice/text choice, then completion and "felt understood" for each mode separately.
- **ASR hallucinations could create false preferences.** Read back a one-line summary before saving ("So: boats yes, queues no?"). This doubles as active listening.
- **Audio retention.** *Decided 2026-09-26:* delete audio after transcription by default. Participants can opt in to 30-day retention, which is used only for transcription-accuracy spot-checks.
- **Prices are unconfirmed.** Every price here comes from a third-party page, because vendor pricing pages were blocked when this note was written. Re-check them in Phase 2.
- **UK accent performance for our users is unmeasured.**
