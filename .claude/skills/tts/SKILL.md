---
name: tts
description: Convert text to speech using the tts CLI. Use when the user asks to read text aloud, generate audio, speak something, or convert text to speech.
---

# TTS - Text to Speech Skill

You have access to the `tts` CLI for text-to-speech with voice cloning, powered by Qwen3-TTS running locally.

## How to use

When the user asks you to speak, read aloud, or generate audio from text, use the `tts` CLI via the Bash tool.

### Core commands

**Speak text aloud (with streaming playback):**
```bash
tts say "Text to speak"
```

**Save to a WAV file:**
```bash
tts say "Text to speak" --save output.wav --no-play
```

**Speak and save simultaneously:**
```bash
tts say "Text to speak" --save output.wav
```

**Generate audio file (no playback):**
```bash
tts generate "Text to speak" -o output.wav
```

### Options

| Flag | Description |
|------|-------------|
| `-v, --voice NAME` | Use a specific cloned voice |
| `-l, --language CODE` | Language code (default: en, also: zh, ja, ko, etc.) |
| `-m, --model SIZE` | Model: 1.7B (quality) or 0.6B (speed) |
| `-i, --instruct TEXT` | Speaking style instruction (e.g., "Speak slowly and calmly") |
| `-s, --save PATH` | Save audio to WAV file |
| `--no-play` | Don't play audio, only save |
| `--no-stream` | Disable streaming (generate all then play) |
| `--seed INT` | Random seed for reproducibility |
| `-f, --file PATH` | Read text from file instead of argument |

### Voice management

```bash
tts voice list                    # List available voices
tts voice add recording.wav --text "transcript" --voice myvoice  # Add a voice
tts voice default myvoice         # Set default voice
tts voice info myvoice            # Show voice details
```

### Piping text

```bash
echo "Hello world" | tts say
```

## Guidelines

1. **Interpret $ARGUMENTS as the text to speak or as instructions about what to generate.** If the user provides plain text, speak it directly. If they provide instructions (e.g., "read the README aloud"), follow them.
2. **Default to `tts say`** for quick playback. Use `tts generate` only when the user explicitly wants a file without playback.
3. **Always include `--instruct "Speak at a moderate, natural pace"`** by default for a comfortable listening speed. Adjust the instruct text based on context:
   - Short notifications/alerts: `"Speak clearly and at a normal pace"`
   - Long paragraphs/explanations: `"Speak at a slightly slower, clear pace for easy listening"`
   - If the user asks for faster/slower speed, adjust accordingly (e.g., `"Speak quickly"`, `"Speak very slowly"`)
   - Combine speed with tone when appropriate (e.g., `"Speak slowly and calmly"`, `"Speak quickly with excitement"`)
4. **Ask about voice preference** only if the user hasn't specified one and has multiple voices available. Otherwise use the default voice.
5. **For long text from files**, use `tts say --file <path>` or pipe the content.
6. **Use `--instruct`** when the user describes a tone or speaking style (e.g., "read this excitedly", "speak in a calm voice").
7. **Language detection**: If the text is clearly in a non-English language, set `--language` appropriately (zh for Chinese, ja for Japanese, ko for Korean, etc.).
8. **For saving files**, default to `.wav` format and suggest a descriptive filename based on the content.
9. **Run tts commands with a timeout** of 300000ms (5 minutes) since audio generation can take time for long text.
