# Viva AI Gemini — Kivy Android APK

This is a Python/Kivy Android starter intended to be written and built from Termux.

The current UI follows the supplied MYRA-style reference direction: AMOLED-black Crimson Core theme, red pulsing central assistant orb, greeting header, Voice Mode and Neural Lens cards, rounded Ask Viva field, red send control, and camera/microphone controls.

## Features in this starter

- Bengali Gemini chat through the Gemini REST API
- API-key Settings popup stored in app-private storage
- Android microphone speech recognition using `SpeechRecognizer`
- Android Bengali TTS using the phone's installed TTS engine
- Live Camera Vision preview sampled every 4 seconds
- Gemini object detection, scene understanding, image analysis, and visual Q&A
- Safe YouTube/Chrome/search browser actions
- User-editable `commands.json` custom command file
- Dark neon MYRA-inspired UI with pulsing red assistant orb

## Termux prerequisites

Install the Termux app and Termux:API from F-Droid or the same trusted source. For APK compilation, the most reliable route is GitHub Actions; local Buildozer builds on a phone may require a large amount of storage and RAM.

```bash
pkg update && pkg upgrade -y
pkg install python git clang make autoconf automake libtool pkg-config zlib libffi openssl -y
pip install --upgrade pip
pip install buildozer cython==0.29.34
```

## Build APK in Termux

```bash
cd viva-gemini-kivy
buildozer android debug
```

The first build downloads Android SDK/NDK components and can take a long time. The APK appears in `bin/`.

If the phone runs out of storage or memory, push the same folder to GitHub and use the included GitHub Actions workflow instead.

## Gemini key

Do not hardcode the key in `main.py`. Install the APK, open **API Key**, and paste the key there. It is stored in the app's private data directory. The app uses:

- Chat model: `gemini-3.8-flash` by default
- Android TTS for the first APK prototype

You can change the chat model through an environment variable during desktop testing:

```bash
export VIVA_CHAT_MODEL=gemini-3.8-flash
```

## Custom commands

Edit `commands.json` **before building the APK**. On first launch, the app copies it into its private app data directory and checks these commands before calling Gemini. A command can return a fixed reply and run one safe action:

```json
{
  "phrases": ["অফিস খোলো"],
  "match": "exact",
  "action": {"type": "open_url", "url": "https://example.com"},
  "reply": "জান, অফিসের website খুলছি।"
}
```

Supported action types are `reply`, `open_url` (only `http`/`https`), `youtube_search`, `open_settings`, `volume_up`, `volume_down`, and `open_app` with an Android package name. Use `match: "contains"` when the phrase may have extra words.

The app intentionally does **not** execute arbitrary shell commands from the file. Arbitrary shell execution could let a malformed command, downloaded file, or Gemini response delete data or change the phone. New Android actions should be added as explicit allowlisted handlers in `main.py`.

## Important Android notes

The microphone requires the Android RECORD_AUDIO permission. The phone's selected Bengali TTS engine controls the voice quality and gender in this first APK. Gemini cloud TTS, floating ORB, foreground background service, and accessibility automation are deliberately separate next-stage additions because they require more native Android integration and user permissions.

## Live Camera Vision

Press **LIVE VISION** inside the app and grant camera permission. Viva keeps a camera preview open and sends one frame about every 4 seconds to Gemini. It reports a changed scene/object summary in Bengali and speaks it through Android TTS. Press **STOP VISION** to stop the camera and network sampling.

This is not continuous video streaming: only sampled still frames are uploaded. Every uploaded frame consumes Gemini multimodal quota/data, so stop Live Vision when it is not needed. The code does not save a permanent gallery copy; it replaces the temporary `live_frame.png` inside app-private storage.
