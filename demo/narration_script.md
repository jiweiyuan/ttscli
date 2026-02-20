# Narration Scripts (Fast-Cut, 22 Beats)

This demo uses a fast-cut structure: 22 beats across 5 acts, ~2-4 seconds per beat.

## Acts & Beats

### Act 1: The AI Agent Story (6 beats, ~16s)
- `01_hook.txt` — "AI coding agents are everywhere."
- `02_stars.txt` — "Claude Code, Cursor, Codex, Gemini CLI, and many more."
- `03_capabilities.txt` — "They write code, reason through problems, and run tools across your entire system."
- `04_gap.txt` — "But none of them can speak."
- `05_silence.txt` — "TTS CLI gives them a mouth."
- `06_reveal.txt` — "Local text-to-speech that runs entirely on your machine."

### Act 2: How It Works (4 beats, ~11s)
- `08_engine.txt` — "Powered by Qwen 3 TTS, a state of the art neural speech model."
- `09_backends.txt` — "Choose PyTorch for GPU and CPU, or MLX for Apple Silicon."
- `10_one_command.txt` — "One command to install, one command to initialize."
- `11_ready.txt` — "And you're ready to go."

### Act 3: Feature Highlights (6 beats, ~17s)
- `12_voice_cloning.txt` — "Clone any voice from a short reference clip."
- `13_streaming.txt` — "Streaming playback starts audio before generation finishes."
- `14_model_sizes.txt` — "Two model sizes: one point seven B for quality, zero point six B for speed."
- `15_scriptable.txt` — "Pipe text, chain commands, automate entire workflows."
- `16_export.txt` — "Export clean WAV files ready for any pipeline."
- `17_apple_silicon.txt` — "Native Apple Silicon acceleration built in."

### Act 4: Live Demo (3 beats, ~9.5s)
- `18_demo_say.txt` — "Run tts say and hear speech instantly."
- `19_demo_generate.txt` — "Run tts generate to save a WAV file."
- `20_demo_clone.txt` — "Add a voice clone in one line."

### Act 5: CTA (3 beats, ~8s)
- `21_github_cta.txt` — "Check it out on GitHub."
- `22_star.txt` — "Star the repo if it helps your project."
- `23_closing.txt` — "TTS CLI. Local voice, zero compromise."

## Build Pipeline

`demo/build_narration.sh` does all of the following:

1. Generates WAV audio per beat using `tts generate`.
2. Uses `scribe transcribe` per segment to verify transcript and duration.
3. Concatenates all segments into one narration file:
   - `demo/out/ttscli_intro.wav`
   - `demo/intro/public/ttscli_intro.wav`
   - `ttscli_intro.wav` (repo root)
4. Produces exact timestamp metadata:
   - `demo/out/narration_timestamps.json`
   - `demo/transcript.md`
5. Writes Remotion timing constants:
   - `demo/intro/src/narrationCues.ts`

## Run

```bash
cd demo
./build_narration.sh
```

Optional environment variables:

- `VOICE=james` (or any configured voice)
- `MODEL=0.6B` (or `1.7B`)
- `RUN_SCRIBE=0` to skip `scribe` API calls
