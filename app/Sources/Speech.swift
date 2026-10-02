import AVFoundation
import Observation
import Speech

/// D115: "Tell it instead" on screen 4. The phone turns speech into text on the device itself (on-device recognition
/// only, never Apple's servers), live into the answer box. No sound is recorded, saved or sent: only the text is, as if
/// typed (CLAUDE.md: transcribe, never keep raw recordings). If this phone can't recognise speech on the device, the
/// button isn't offered and the keyboard's own mic still works.
@MainActor
@Observable
final class Dictation {
    var listening = false
    var problem: String?

    private let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-GB"))
    private let engine = AVAudioEngine()
    @ObservationIgnored private var request: SFSpeechAudioBufferRecognitionRequest?
    @ObservationIgnored private var task: SFSpeechRecognitionTask?

    /// On-device recognition only. CI screenshots (demo mode) always show the button.
    var available: Bool { AppConfig.demo || recognizer?.supportsOnDeviceRecognition == true }

    /// Starts listening; `onText` gets the whole transcript so far, each time it changes.
    func start(onText: @escaping @MainActor (String) -> Void) async {
        problem = nil
        guard let recognizer, recognizer.supportsOnDeviceRecognition else {
            problem = "Speaking isn't available on this phone. You can type, or use the mic on your keyboard."
            return
        }
        let status = await withCheckedContinuation { (c: CheckedContinuation<SFSpeechRecognizerAuthorizationStatus, Never>) in
            SFSpeechRecognizer.requestAuthorization { c.resume(returning: $0) }
        }
        guard status == .authorized else {
            problem = "To speak your answer, allow speech recognition for ODYS in Settings. Or just type."
            return
        }
        guard await AVAudioApplication.requestRecordPermission() else {
            problem = "To speak your answer, allow the microphone for ODYS in Settings. Or just type."
            return
        }
        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.record, mode: .measurement, options: .duckOthers)
            try session.setActive(true, options: .notifyOthersOnDeactivation)
            let request = SFSpeechAudioBufferRecognitionRequest()
            request.requiresOnDeviceRecognition = true      // the sound never leaves the phone
            request.shouldReportPartialResults = true
            let input = engine.inputNode
            input.installTap(onBus: 0, bufferSize: 1024, format: input.outputFormat(forBus: 0)) { buffer, _ in
                request.append(buffer)
            }
            engine.prepare()
            try engine.start()
            self.request = request
            listening = true
            task = recognizer.recognitionTask(with: request) { [weak self] result, error in
                let text = result?.bestTranscription.formattedString
                let finished = error != nil || (result?.isFinal ?? false)
                Task { @MainActor in
                    if let text, !text.isEmpty { onText(text) }
                    if finished { self?.finish() }
                }
            }
        } catch {
            problem = "The microphone couldn't start. You can type instead."
            finish()
        }
    }

    /// Stops listening; the last words still arrive, then the task ends.
    func stop() {
        if engine.isRunning {
            engine.stop()
            engine.inputNode.removeTap(onBus: 0)
        }
        request?.endAudio()
        request = nil
        listening = false
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }

    private func finish() {
        stop()
        task = nil
    }
}
