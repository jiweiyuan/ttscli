---
name: product-demo
description: Create a polished product demo video with motion graphics intro, narrated audio, and terminal recordings. Use when the user asks to build a demo video, product walkthrough, or promotional clip for a CLI tool or software project.
---

# Product Demo Video — End-to-End Skill

Build a professional product demo video combining **narrated audio** (TTS), **motion graphics** (Remotion), and **terminal recordings** (VHS). The final output is a single `.mp4` with synced audio.

---

## Architecture Overview

A demo video has **three layers** assembled in a pipeline:

```
1. Narration Audio   →  TTS CLI generates speech from scripts
2. Motion Graphics   →  Remotion renders animated intro/transitions
3. Terminal Demos    →  VHS records scripted terminal sessions
4. Assembly          →  ffmpeg concatenates video + merges audio
```

Directory structure:

```
demo/
├── build.sh                  # Master build script (orchestrates everything)
├── build_narration.sh        # Narration pipeline: TTS → scribe → cues
├── narration_script.md       # Narration plan & source file list
├── transcript.md             # Final transcript with timestamps & beat markers
├── narration/                # Per-beat narration scripts (one sentence each)
│   ├── manifest.json         # Beat manifest (id, sequence, role, beatIndex, script)
│   ├── 01_hook.txt           # Act 1 beats (story)
│   ├── 02_stars.txt
│   ├── ...
│   ├── 08_engine.txt         # Act 2 beats (tech)
│   ├── ...
│   ├── 12_voice_cloning.txt  # Act 3 beats (features)
│   ├── ...
│   ├── 18_demo_say.txt       # Act 4 beats (demo)
│   ├── ...
│   └── 23_closing.txt        # Act 5 beats (cta)
├── terminal_voices.tape      # VHS tape: install & setup
├── terminal_speech.tape      # VHS tape: voice cloning & speech
├── terminal_config.tape      # VHS tape: generate, export & workflow
├── ttscli_demo.tape          # VHS tape: full demo (alternative single-take)
├── intro/                    # Remotion project
│   ├── package.json
│   ├── remotion.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── public/               # Static assets (audio, images)
│   │   └── ttscli_intro.wav
│   └── src/
│       ├── Root.tsx           # Remotion entry — registers compositions
│       ├── TtsIntro.tsx       # Main composition — scene sequencing
│       ├── design.ts          # Shared palette, fonts, shadows
│       ├── narrationCues.ts   # Auto-generated timing constants from scribe
│       ├── index.ts
│       ├── style.css
│       ├── scenes/            # One component per visual act
│       │   ├── OpenClawStory.tsx     # Act 1: AI Agent story (6 beats)
│       │   ├── HowItWorks.tsx        # Act 2: Engine, backends, install (4 beats)
│       │   ├── FeatureHighlights.tsx  # Act 3: 6 unique feature beats
│       │   ├── LiveDemo.tsx          # Act 4: Persistent terminal (3 beats)
│       │   └── CallToAction.tsx      # Act 5: GitHub CTA + logo lock (3 beats)
│       └── effects/           # Reusable visual effects
│           ├── Backdrop.tsx
│           ├── RhythmOverlay.tsx
│           ├── TerminalChrome.tsx   # Shared terminal window chrome
│           └── Waveform.tsx         # Animated waveform SVG
└── out/                       # Build artifacts (gitignored)
    ├── ttscli_demo.mp4
    ├── intro.mp4
    ├── terminal1.mp4
    ├── terminal2.mp4
    ├── terminal3.mp4
    ├── narration/             # Per-segment WAV files
    │   ├── 01_title.wav
    │   ├── 02_tech.wav
    │   └── ...
    ├── narration_transcripts/ # Scribe JSON outputs per segment
    │   ├── 01_title.json
    │   ├── 02_tech.json
    │   └── ...
    └── narration_timestamps.json  # Combined timeline with all beat markers
```

---

## Step 1: Write the Narration Script

Plan the story arc first. A good demo narration follows this structure:

| Act | Purpose | Beats | Duration |
|-----|---------|-------|----------|
| **Story / Hook** | Grab attention, establish the problem | 5–7 | 12–18s |
| **How It Works** | Engine, backends, install | 3–5 | 10–14s |
| **Feature Highlights** | One unique visual per feature | 4–6 | 14–20s |
| **Live Demo** | Terminal with accumulating commands | 3 | 8–12s |
| **CTA** | GitHub link + logo lock | 2–3 | 6–10s |

### Guidelines

- **Fast-cut structure**: ~2–4 seconds per beat, one sentence each.
- Split into **separate text files** per beat (easier to re-generate individually).
- Aim for **60–80 seconds** total — attention drops fast.
- Each act = one Remotion scene component with internal `<Sequence>` per beat.

### Beat manifest (`narration/manifest.json`)

Define all beats, their ordering, and their sequence grouping:

```json
{
  "fps": 30,
  "segments": [
    { "id": "01_hook",     "sequence": "story",    "role": "beat", "beatIndex": 0, "script": "01_hook.txt" },
    { "id": "02_agents",   "sequence": "story",    "role": "beat", "beatIndex": 1, "script": "02_stars.txt" },
    ...
    { "id": "07_engine",   "sequence": "tech",     "role": "beat", "beatIndex": 0, "script": "08_engine.txt" },
    ...
    { "id": "22_closing",  "sequence": "cta",      "role": "beat", "beatIndex": 2, "script": "23_closing.txt" }
  ]
}
```

Fields:
- **`id`** — Unique segment identifier (used as filename for WAV + scribe JSON)
- **`sequence`** — Groups beats into Remotion scenes (`story`, `tech`, `features`, `demo`, `cta`)
- **`role`** — Always `"beat"` in the fast-cut architecture
- **`beatIndex`** — Zero-based index within the sequence (drives internal `<Sequence>` positioning)
- **`script`** — Filename of the narration text file in `narration/`

### Generate audio with TTS CLI

```bash
# Generate per-segment audio
tts generate "Hey, meet TTS CLI, a text-to-speech tool that runs entirely on your machine." \
  --voice james -o demo/out/01_title.wav

# Or from a file
tts generate --file demo/narration/01_title.txt --voice james -o demo/out/01_title.wav
```

### Concatenate segments with ffmpeg

```bash
# Build a concat list
for f in demo/out/0*.wav; do echo "file '$f'"; done > demo/out/concat.txt

# Concatenate
ffmpeg -f concat -safe 0 -i demo/out/concat.txt -c copy demo/out/narration.wav
```

### Extract timestamps with Scribe

After generating audio, use **scribe** to transcribe each segment and extract precise timestamps. Scribe is a CLI that calls the ElevenLabs transcription API and returns word-level timing data — this is what drives the Remotion animation timeline.

#### Setup

```bash
# Install (Node.js CLI)
npm install -g scribe-cli

# Authenticate with ElevenLabs API key (one-time)
scribe auth
```

#### Transcribe individual segments

```bash
# Transcribe a single audio segment to JSON (includes duration + word timestamps)
scribe transcribe demo/out/narration/01_title.wav -f json -o demo/out/narration_transcripts/

# Output formats: json, md, txt, srt, all
scribe transcribe demo/out/narration/01_title.wav -f all -o demo/out/narration_transcripts/

# Print to stdout instead of file
scribe transcribe demo/out/narration/01_title.wav -f json --stdout
```

#### Scribe CLI options

| Flag | Description |
|------|-------------|
| `-f, --format <type>` | Output format: `json`, `md`, `txt`, `srt`, `all` (default: `json`) |
| `-o, --output-dir <dir>` | Output directory (default: `.`) |
| `-d, --diarize` | Enable speaker diarization |
| `-s, --speakers <count>` | Speaker count hint (1–32) |
| `-l, --language <code>` | Language code (ISO-639, e.g. `en`, `zh`) |
| `--stdout` | Print to stdout instead of writing file |
| `-q, --quiet` | Suppress progress output |

#### JSON output structure

Scribe JSON output contains the metadata needed for timeline sync:

```json
{
  "text": "Meet TTS CLI, a fully local text-to-speech toolkit...",
  "metadata": {
    "duration": 15.30,
    "language": "en"
  },
  "words": [
    { "word": "Meet", "start": 0.0, "end": 0.32, "confidence": 0.98 },
    { "word": "TTS", "start": 0.35, "end": 0.72, "confidence": 0.95 },
    ...
  ]
}
```

Key fields:
- **`metadata.duration`** — exact segment length in seconds (more accurate than ffprobe for timing)
- **`text`** — verified transcript (catches TTS mispronunciations)
- **`words[].start` / `words[].end`** — word-level timestamps for fine-grained sync

#### Batch transcription in the narration pipeline

The `demo/build_narration.sh` script automates scribe across all segments:

```bash
# Transcribe each segment, extract duration + text, accumulate running offset
for id in "${segment_ids[@]}"; do
  tts generate --file "$script_path" --output "$wav_path" --model "$MODEL"

  if [[ "$RUN_SCRIBE" == "1" ]]; then
    scribe transcribe "$wav_path" -f json -o "$TRANS_DIR"
    duration="$(jq -r '.metadata.duration' "$TRANS_DIR/$id.json")"
    text="$(jq -r '.text' "$TRANS_DIR/$id.json")"
  else
    # Fallback: ffprobe for duration, source script for text
    duration="$(ffprobe -v error -show_entries format=duration \
      -of default=nokey=1:noprint_wrappers=1 "$wav_path")"
    text="$(cat "$script_path")"
  fi

  # Compute frame offset: start_frame = running_seconds × fps
  start_frame=$(awk "BEGIN { printf \"%d\", $running_sec * 30 + 0.5 }")
  # ... accumulate into timeline JSON
done
```

Control with environment variable:
```bash
RUN_SCRIBE=1 ./build_narration.sh   # Use scribe (default) — accurate timestamps
RUN_SCRIBE=0 ./build_narration.sh   # Skip scribe — use ffprobe fallback (offline/faster)
```

#### From scribe output → beat markers → Remotion cues

The pipeline converts scribe timestamps into three artifacts:

**1. Timeline JSON** (`demo/out/narration_timestamps.json`):
```json
{
  "fps": 30,
  "total_seconds": 84.80,
  "total_frames": 2544,
  "segments": [
    {
      "id": "01_title",
      "sequence": "title",
      "text": "Meet TTS CLI...",
      "start_sec": 0.0,
      "end_sec": 15.30,
      "start_frame": 0,
      "end_frame": 459,
      "duration_frames": 459
    },
    ...
  ]
}
```

**2. Transcript markdown** (`demo/transcript.md`):
```markdown
| Segment | Start | End | Frame | Text |
|---|---:|---:|---:|---|
| 01_title | 0.00s | 15.30s | 0 | Meet TTS CLI... |
| 02_tech | 15.30s | 38.36s | 459 | Under the hood... |
```

Frame number = `start_seconds × 30` (at 30fps).

**3. Remotion narration cues** (`demo/intro/src/narrationCues.ts`):
```typescript
// Auto-generated from scribe transcription timestamps
export const narrationCues = {
  fps: 30,
  totalFrames: 2250,
  scenes: {
    story:    { from: 0,    duration: 480, beatDurations: [75, 90, 105, 60, 75, 75] },
    tech:     { from: 480,  duration: 330, beatDurations: [90, 90, 90, 60] },
    features: { from: 810,  duration: 510, beatDurations: [90, 90, 90, 90, 75, 75] },
    demo:     { from: 1320, duration: 285, beatDurations: [105, 90, 90] },
    cta:      { from: 1605, duration: 240, beatDurations: [75, 75, 90] },
  },
} as const;
```

Each scene has uniform shape: `from` (start frame), `duration` (total frames), `beatDurations[]` (per-beat frame counts). This is auto-generated by `build_narration.sh` from scribe timestamps.

This file is imported by `TtsIntro.tsx` for top-level `<Sequence>` placement, and by each scene component for internal beat `<Sequence>` positioning.

#### Why scribe over ffprobe alone?

| | scribe | ffprobe fallback |
|---|---|---|
| **Duration accuracy** | From speech model — accounts for silence trimming | File-level — includes trailing silence |
| **Verified transcript** | Catches TTS errors (mispronunciations, skipped words) | Uses source script (assumes TTS was perfect) |
| **Word-level timing** | Available — enables per-word animation sync | Not available |
| **Offline use** | ❌ Requires ElevenLabs API | ✅ Fully offline |
| **Speed** | ~2-5s per segment (API call) | Instant |

**Recommendation:** Use scribe for the final build (accurate timing), use ffprobe fallback during rapid iteration.

### Single-segment regeneration (iterating on one beat)

TTS output has randomness — the same text produces different results each run. When a segment sounds bad, **generate 3 versions, let the user pick, then patch** all downstream artifacts.

#### 1. Generate multiple candidates

```bash
# Generate 3 versions for comparison (run in parallel)
tts generate --file demo/narration/05_silence.txt --output demo/out/narration/05_reveal_v1.wav --model 0.6B
tts generate --file demo/narration/05_silence.txt --output demo/out/narration/05_reveal_v2.wav --model 0.6B
tts generate --file demo/narration/05_silence.txt --output demo/out/narration/05_reveal_v3.wav --model 0.6B
```

Present durations to the user so they can audition and pick.

#### 2. Replace and get new duration

```bash
cp demo/out/narration/05_reveal_v2.wav demo/out/narration/05_reveal.wav
ffprobe -v error -show_entries format=duration -of default=nokey=1:noprint_wrappers=1 demo/out/narration/05_reveal.wav
```

#### 3. Update timestamps JSON (recompute all offsets)

Use `jq` to patch the single segment's duration and recompute all subsequent offsets:

```bash
jq '
  .segments |= (
    map(if .id == "SEGMENT_ID" then .duration_sec = NEW_DUR | .duration_frames = (NEW_DUR * 30 | round) else . end) |
    reduce range(length) as $i (
      .;
      if $i == 0 then
        .[$i].start_sec = 0 | .[$i].start_frame = 0 |
        .[$i].end_sec = .[$i].duration_sec | .[$i].end_frame = .[$i].duration_frames
      else
        .[$i].start_sec = .[$i-1].end_sec | .[$i].start_frame = .[$i-1].end_frame |
        .[$i].end_sec = (.[$i].start_sec + .[$i].duration_sec) |
        .[$i].end_frame = (.[$i].start_frame + .[$i].duration_frames)
      end
    )
  ) |
  .total_seconds = .segments[-1].end_sec |
  .total_frames = .segments[-1].end_frame
' demo/out/narration_timestamps.json > tmp.json && mv tmp.json demo/out/narration_timestamps.json
```

#### 4. Rebuild all downstream artifacts

After patching timestamps JSON, regenerate these three (can run in parallel):

- **Re-concat audio** — rebuild `concat.txt` from manifest order, `ffmpeg -y -f concat`, copy to `public/` and root
- **Regenerate `narrationCues.ts`** — rebuild scene blocks from timeline JSON (same logic as `write_cues_ts()`)
- **Regenerate `transcript.md`** — rebuild markdown table from timeline JSON (same logic as `write_transcript_md()`)

#### Summary: single-segment patch checklist

1. Generate 3 candidate WAVs (parallel)
2. User picks → copy to official filename
3. `ffprobe` → get new duration
4. `jq` → patch timestamps JSON + recompute offsets
5. Re-concat audio + copy to `public/` and root
6. Regenerate `narrationCues.ts`
7. Regenerate `transcript.md`

This avoids re-generating all other segments and takes ~10 seconds vs minutes for the full pipeline.

---

## Step 2: Build Motion Graphics with Remotion

### Project setup

```bash
cd demo
npx create-video@latest intro --template blank --tailwind
cd intro && npm install
```

### Design system (`design.ts`)

Define a shared palette, fonts, and shadows so all scenes look consistent:

```typescript
export const palette = {
  ink: "#111827",
  inkMuted: "#5B6475",
  bg: "#FFF8F5",
  bgPanel: "#FFFFFF",
  accent: "#FF6154",
  cool: "#3B82F6",
  // ...
} as const;

export const fonts = {
  display: "'Avenir Next', sans-serif",
  mono: "'JetBrains Mono', monospace",
} as const;
```

### Scene components

Each scene is a React component using Remotion primitives:

- **`useCurrentFrame()`** — current frame number (drives all animation)
- **`useVideoConfig()`** — fps, width, height, duration
- **`spring()`** — physics-based easing for entrances
- **`interpolate()`** — map frame ranges to CSS values (opacity, translateY, scale)
- **`<Sequence>`** — place a component at a specific time range

**Pattern for a scene component:**

```tsx
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const TitleCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance animation
  const enter = spring({ frame: frame - 8, fps, config: { damping: 14, stiffness: 120 } });

  // Fade-out before next scene
  const fadeOut = interpolate(frame, [437, 487], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ opacity: fadeOut }}>
      <div style={{
        opacity: enter,
        transform: `translateY(${interpolate(enter, [0, 1], [34, 0])}px)`,
        fontSize: 178,
        fontWeight: 800,
      }}>
        TTS CLI
      </div>
    </AbsoluteFill>
  );
};
```

### Audio-synced timeline (`TtsIntro.tsx`)

The main composition sequences scenes using beat markers from the transcript:

```tsx
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";

export const TtsIntro: React.FC = () => (
  <AbsoluteFill>
    <Audio src={staticFile("ttscli_intro.wav")} />
    <Sequence from={0} durationInFrames={520}>
      <TitleCard />
    </Sequence>
    <Sequence from={487} durationInFrames={723}>
      <TechOverview />
    </Sequence>
    {/* ... more scenes ... */}
  </AbsoluteFill>
);
```

### Narration cues file (`narrationCues.ts`)

Auto-generate this from transcript timestamps so scene timing stays in sync:

```typescript
export const narrationCues = {
  fps: 30,
  totalFrames: 2544,
  scenes: {
    title:    { from: 0,    duration: 520  },
    tech:     { from: 487,  duration: 723  },
    features: { from: 1177, duration: 891  },
    terminal: { from: 2035, duration: 509  },
  },
};
```

### Render

```bash
cd demo/intro
npx remotion render TtsIntro --output ../out/intro.mp4 --codec h264
```

### Tips for motion graphics

- **Start simple** — animate one element at a time, iterate.
- **Use `spring()`** for entrances — feels natural, avoids linear motion.
- **Cross-fades:** overlap scenes by ~30 frames (1s) and use `interpolate()` for fade-out on the outgoing scene.
- **Feature pills/badges:** small animated labels that pop in one by one with staggered delays.
- **Avoid small decorative icons next to titles** — stroke-based SVG icons (bolt, mic, terminal) render poorly at small sizes in video (broken borders, barely visible). If the scene content already illustrates the concept (e.g., progress bars for streaming, waveforms for voice cloning, terminal chrome for scripting), the title text alone is cleaner. Only use icons when they are the primary visual element (e.g., Apple logo + CPU chip for "MLX Native").
- **Background effects:** subtle particle/grid animations add depth without distracting (see `Backdrop.tsx`).
- **Consistent resolution:** always 1920×1080 @ 30fps across all segments.

### Card layout guidelines

When building capability/feature cards in a row:

- **Fixed-height illustration boxes** — when showing multiple cards side-by-side, give the illustration area a fixed `height` (e.g. 160px) so all cards match visually. Use `display: "flex", alignItems: "center"` inside to vertically center varied content.
- **Card sizing** — for a 3-card row on 1920px canvas, 380px per card with connector arrows between them works well. Don't go below 320px or text gets cramped.
- **Centering SVG + text** — when stacking an SVG icon above text, use `display: "flex", flexDirection: "column", alignItems: "center"` on the container instead of `textAlign: "center"`. The latter won't reliably center inline SVG elements.

### Themed scenes (e.g. GitHub-style)

When a scene references an external brand or platform, define a local token object for that theme instead of using the global `palette`. This keeps the scene self-contained and visually distinct.

```tsx
// GitHub light theme tokens — scoped to one scene
const gh = {
  bg: "#ffffff",
  bgSubtle: "#f6f8fa",
  cardBg: "#ffffff",
  border: "#d0d7de",
  text: "#1f2328",
  textMuted: "#656d76",
  btnBg: "#f6f8fa",
  btnBorder: "#d0d7de",
  starYellow: "#e3b341",
  link: "#0969da",
} as const;
```

Tips for themed scenes:
- **Skip the shared `<Backdrop>`** — use a flat `backgroundColor` matching the platform's style instead.
- **Reproduce recognizable UI elements** — e.g., GitHub repo card with icon, description, star button, language dot, topic tags. These are instantly familiar and more engaging than abstract placeholders.
- **Animate interactions** — e.g., a star button "click" with `spring()` pop, a counter rolling from N to N+1. Makes the scene feel alive.
- **Prefer light themes** when the overall video uses a light design system. Dark-themed scenes create jarring contrast.

### Concrete vs abstract illustrations

Prefer **concrete, terminal-style** content inside card illustration boxes over abstract graphics:

| Abstract (avoid) | Concrete (prefer) |
|---|---|
| Neural network dots | Agent thinking steps: 🔍 `read codebase...` → 🧠 `analyzing...` → 📋 `plan: 3 steps` |
| Floating particles | Code snippet with syntax highlighting |
| Generic waveform | Terminal pipeline: `$ running...` → `✓ git done` → `✓ test done` |

Concrete illustrations are more readable at video resolution and immediately communicate what the feature does.

---

## Step 3: Record Terminal Demos with VHS

[VHS](https://github.com/charmbracelet/vhs) records scripted terminal sessions as video.

### Install

```bash
brew install charmbracelet/tap/vhs
```

### Write a `.tape` file

Each terminal segment gets its own tape file:

```tape
# Terminal Scene: Install & Setup
Output out/terminal1.mp4
Set Width 1920
Set Height 1080
Set Framerate 30
Set FontFamily "Menlo"
Set FontSize 22
Set Theme "Github"
Set Padding 40
Set TypingSpeed 30ms
Set CursorBlink true
Set Shell zsh

Sleep 400ms

Type "curl -fsSL https://example.com/install.sh | bash"
Sleep 150ms
Enter
Sleep 4000ms

Type "mytool --version"
Sleep 150ms
Enter
Sleep 1500ms

Sleep 400ms
```

### Tape file guidelines

| Setting | Recommended Value | Why |
|---------|------------------|-----|
| `Width` / `Height` | 1920 × 1080 | Match Remotion resolution |
| `Framerate` | 30 | Match Remotion fps |
| `Theme` | Github (light) or Dracula (dark) | Consistent look |
| `TypingSpeed` | 30ms | Fast enough to not bore, slow enough to read |
| `Sleep` after Enter | 2000–4000ms | Let output render before next command |

### Record

```bash
vhs terminal_voices.tape
vhs terminal_speech.tape
vhs terminal_config.tape
```

### Tips

- Target **16 seconds per segment** — trim in the assembly step.
- Plan **3 terminal segments** covering: setup, core features, advanced/workflow.
- Keep commands **short and readable** — avoid long flags when possible.
- End each tape with a `Sleep 400ms` buffer.

---

## Step 4: Assemble the Final Video

The build script (`demo/build.sh`) orchestrates everything:

### Timing plan

```
Segment        Start   Duration  Frames
Intro (motion) 0:00    28s       840
Label 1        0:28    2s        60      (optional title card)
Terminal 1     0:30    16s       480
Label 2        0:46    2s        60
Terminal 2     0:48    16s       480
Label 3        1:04    2s        60
Terminal 3     1:06    16s       480
```

### Trim terminals to exact duration

```bash
ffmpeg -y -i out/terminal1.mp4 -t 16 \
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -r 30 -an \
  out/terminal1_trimmed.mp4
```

### Concatenate segments

```bash
cat > out/concat_list.txt <<EOF
file 'intro.mp4'
file 'label1.mp4'
file 'terminal1_trimmed.mp4'
file 'label2.mp4'
file 'terminal2_trimmed.mp4'
file 'label3.mp4'
file 'terminal3_trimmed.mp4'
EOF

ffmpeg -y -f concat -safe 0 -i out/concat_list.txt \
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -r 30 -an \
  out/concat.mp4
```

### Merge narration audio

```bash
ffmpeg -y -i out/concat.mp4 -i ttscli_intro.wav \
  -c:v copy -c:a aac -b:a 128k -ar 44100 -ac 2 \
  -shortest -movflags +faststart \
  out/ttscli_demo.mp4
```

### Run the full pipeline

```bash
cd demo
./build.sh           # Build everything
./build.sh remotion  # Only re-render motion graphics
./build.sh terminals # Only re-record terminal demos
./build.sh merge     # Only re-assemble final video
```

---

## Quick-Start Checklist

When asked to create a product demo, follow these steps:

1. **[ ] Write narration script** — Plan 4 scenes, ~60–90s total, one sentence per feature. Create `narration/manifest.json` + per-segment `.txt` files.
2. **[ ] Generate audio** — Use `tts generate` per segment, concatenate with ffmpeg.
3. **[ ] Transcribe with scribe** — Run `scribe transcribe` on each segment to get accurate durations and verified text. Compute beat markers (frame = seconds × fps).
4. **[ ] Generate timing artifacts** — Write `narration_timestamps.json`, `transcript.md`, and `narrationCues.ts` from scribe output. Or run `build_narration.sh` to automate steps 2–4.
5. **[ ] Create design system** — Define palette, fonts, shadows in `design.ts`.
6. **[ ] Build Remotion scenes** — One component per scene, use `spring()` + `interpolate()`, sync to audio beat markers from `narrationCues.ts`.
7. **[ ] Write VHS tapes** — One `.tape` per terminal segment, 1920×1080 @ 30fps, ~16s each.
8. **[ ] Record terminals** — `vhs <tape>.tape` for each.
9. **[ ] Assemble** — Trim terminals, concatenate all segments, merge audio with ffmpeg.
10. **[ ] Review & iterate** — Watch the full video, adjust timing, re-render individual pieces as needed.

## Required Tools

| Tool | Install | Purpose |
|------|---------|---------|
| `tts` | `pip install tts-cli` | Narration audio generation |
| `node` / `npx` | `brew install node` | Remotion rendering |
| `remotion` | `npx create-video@latest` | Motion graphics |
| `vhs` | `brew install charmbracelet/tap/vhs` | Terminal recording |
| `ffmpeg` | `brew install ffmpeg` | Video/audio processing |
| `scribe` | `npm install -g scribe-cli` + `scribe auth` | Transcription for accurate timestamps (ElevenLabs API) |

## Reference Files

- Existing demo: `demo/` directory in this repo
- Video build script: `demo/build.sh` — renders Remotion, records VHS, assembles final MP4
- Narration build script: `demo/build_narration.sh` — TTS generation → scribe transcription → timestamp extraction → narrationCues.ts
- Segment manifest: `demo/narration/manifest.json` — defines segment order, roles, and script files
- Narration scripts: `demo/narration/0*.txt` — one text file per segment
- Remotion project: `demo/intro/`
- Remotion timing cues: `demo/intro/src/narrationCues.ts` (auto-generated from scribe)
- VHS tapes: `demo/terminal_*.tape`
- Narration plan: `demo/narration_script.md`
- Transcript & beat markers: `demo/transcript.md`
- Remotion tips: `remotion-tip.md`
