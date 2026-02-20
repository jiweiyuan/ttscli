#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST="$SCRIPT_DIR/narration/manifest.json"
NARRATION_DIR="$SCRIPT_DIR/narration"

OUT_DIR="$SCRIPT_DIR/out"
AUDIO_DIR="$OUT_DIR/narration"
TRANS_DIR="$OUT_DIR/narration_transcripts"
TIMELINE_JSON="$OUT_DIR/narration_timestamps.json"

CUES_TS="$SCRIPT_DIR/intro/src/narrationCues.ts"
TRANSCRIPT_MD="$SCRIPT_DIR/transcript.md"
FINAL_AUDIO="$OUT_DIR/ttscli_intro.wav"
PUBLIC_AUDIO="$SCRIPT_DIR/intro/public/ttscli_intro.wav"
ROOT_AUDIO="$SCRIPT_DIR/../ttscli_intro.wav"

VOICE="${VOICE:-}"
MODEL="${MODEL:-0.6B}"
RUN_SCRIBE="${RUN_SCRIBE:-1}" # Set RUN_SCRIBE=0 to skip transcription API calls

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[ OK ]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail()  { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing required command: $1"
}

normalize_text() {
  tr '\n' ' ' | sed -E 's/[[:space:]]+/ /g; s/^ //; s/ $//'
}

build_segments() {
  local fps
  fps="$(jq -r '.fps' "$MANIFEST")"

  local entries='[]'
  local current_sec="0"
  local current_frame=0

  local segment_ids=()
  while IFS= read -r line; do
    segment_ids+=("$line")
  done < <(jq -r '.segments[].id' "$MANIFEST")
  if [[ ${#segment_ids[@]} -eq 0 ]]; then
    fail "No segments found in $MANIFEST"
  fi

  for id in "${segment_ids[@]}"; do
    local script_file sequence role beat_index
    script_file="$(jq -r --arg id "$id" '.segments[] | select(.id == $id) | .script' "$MANIFEST")"
    sequence="$(jq -r --arg id "$id" '.segments[] | select(.id == $id) | .sequence' "$MANIFEST")"
    role="$(jq -r --arg id "$id" '.segments[] | select(.id == $id) | .role' "$MANIFEST")"
    beat_index="$(jq -r --arg id "$id" '.segments[] | select(.id == $id) | (.beatIndex // 0)' "$MANIFEST")"

    local script_path="$NARRATION_DIR/$script_file"
    local wav_path="$AUDIO_DIR/$id.wav"
    [ -f "$script_path" ] || fail "Missing script: $script_path"

    info "Generating audio: $id"
    cmd=(tts generate --file "$script_path" --output "$wav_path" --model "$MODEL")
    if [[ -n "$VOICE" ]]; then
      cmd+=(--voice "$VOICE")
    fi
    "${cmd[@]}"

    local duration text
    if [[ "$RUN_SCRIBE" == "1" ]]; then
      if scribe transcribe "$wav_path" -f json -o "$TRANS_DIR" >/dev/null 2>&1; then
        local json_path="$TRANS_DIR/$id.json"
        duration="$(jq -r '.metadata.duration' "$json_path")"
        text="$(jq -r '.text' "$json_path" | normalize_text)"
      else
        warn "scribe failed for $id, falling back to ffprobe + source script text"
        duration="$(ffprobe -v error -show_entries format=duration -of default=nokey=1:noprint_wrappers=1 "$wav_path")"
        text="$(normalize_text < "$script_path")"
      fi
    else
      duration="$(ffprobe -v error -show_entries format=duration -of default=nokey=1:noprint_wrappers=1 "$wav_path")"
      text="$(normalize_text < "$script_path")"
    fi

    local start_sec="$current_sec"
    local end_sec
    end_sec="$(awk "BEGIN { printf \"%.6f\", $start_sec + $duration }")"
    local duration_frames
    duration_frames="$(awk "BEGIN { printf \"%d\", ($duration * $fps) + 0.5 }")"
    local start_frame="$current_frame"
    local end_frame=$((start_frame + duration_frames))

    local obj
    obj="$(jq -n \
      --arg id "$id" \
      --arg sequence "$sequence" \
      --arg role "$role" \
      --argjson beat_index "$beat_index" \
      --arg script "$script_file" \
      --arg text "$text" \
      --argjson start_sec "$start_sec" \
      --argjson end_sec "$end_sec" \
      --argjson duration_sec "$duration" \
      --argjson start_frame "$start_frame" \
      --argjson end_frame "$end_frame" \
      --argjson duration_frames "$duration_frames" \
      '{
        id: $id,
        sequence: $sequence,
        role: $role,
        beatIndex: $beat_index,
        script: $script,
        text: $text,
        start_sec: $start_sec,
        end_sec: $end_sec,
        duration_sec: $duration_sec,
        start_frame: $start_frame,
        end_frame: $end_frame,
        duration_frames: $duration_frames
      }')"

    entries="$(jq --argjson obj "$obj" '. + [$obj]' <<<"$entries")"
    current_sec="$end_sec"
    current_frame="$end_frame"
  done

  jq -n \
    --argjson fps "$fps" \
    --arg model "$MODEL" \
    --arg voice "${VOICE:-default}" \
    --argjson total_seconds "$current_sec" \
    --argjson total_frames "$current_frame" \
    --argjson segments "$entries" \
    '{
      fps: $fps,
      model: $model,
      voice: $voice,
      total_seconds: $total_seconds,
      total_frames: $total_frames,
      segments: $segments
    }' > "$TIMELINE_JSON"

  ok "Wrote timeline: $TIMELINE_JSON"
}

concat_audio() {
  local concat_list="$AUDIO_DIR/concat.txt"
  : > "$concat_list"
  while IFS= read -r id; do
    printf "file '%s'\n" "$AUDIO_DIR/$id.wav" >> "$concat_list"
  done < <(jq -r '.segments[].id' "$MANIFEST")

  ffmpeg -y \
    -f concat -safe 0 -i "$concat_list" \
    -ar 24000 -ac 1 \
    "$FINAL_AUDIO" >/dev/null 2>&1

  cp "$FINAL_AUDIO" "$PUBLIC_AUDIO"
  cp "$FINAL_AUDIO" "$ROOT_AUDIO"

  ok "Merged narration audio: $FINAL_AUDIO"
  ok "Updated audio for Remotion: $PUBLIC_AUDIO"
}

write_cues_ts() {
  local fps total_frames
  fps="$(jq -r '.fps' "$TIMELINE_JSON")"
  total_frames="$(jq -r '.total_frames' "$TIMELINE_JSON")"

  # Extract unique sequence names in manifest order
  local sequences=()
  while IFS= read -r line; do
    sequences+=("$line")
  done < <(jq -r 'reduce .segments[].sequence as $s ([]; if IN(.[]; $s) then . else . + [$s] end) | .[]' "$TIMELINE_JSON")

  # Build per-sequence data
  local scene_blocks=""
  local running_from=0

  for seq in "${sequences[@]}"; do
    local seq_duration
    seq_duration="$(jq --arg s "$seq" '[.segments[] | select(.sequence==$s) | .duration_frames] | add // 0' "$TIMELINE_JSON")"

    local beat_durations
    beat_durations="$(jq -c --arg s "$seq" '[.segments[] | select(.sequence==$s) | .duration_frames]' "$TIMELINE_JSON")"

    scene_blocks+="    ${seq}: { from: ${running_from}, duration: ${seq_duration}, beatDurations: ${beat_durations} },
"
    running_from=$((running_from + seq_duration))
  done

  cat > "$CUES_TS" <<EOF
export const narrationCues = {
  fps: ${fps},
  totalFrames: ${total_frames},
  scenes: {
${scene_blocks}  },
} as const;
EOF

  ok "Updated cues: $CUES_TS"
}

write_transcript_md() {
  local fps total_frames total_seconds
  fps="$(jq -r '.fps' "$TIMELINE_JSON")"
  total_frames="$(jq -r '.total_frames' "$TIMELINE_JSON")"
  total_seconds="$(jq -r '.total_seconds' "$TIMELINE_JSON")"

  {
    echo "# ttscli_intro.wav — Transcript with Timestamps"
    echo
    echo "**Total duration:** $(printf '%.2f' "$total_seconds")s (${total_frames} frames @ ${fps}fps)"
    echo
    echo "| Segment | Start | End | Frame | Text |"
    echo "|---|---:|---:|---:|---|"
    while IFS=$'\t' read -r id start end frame text; do
      safe_text="${text//|/\\|}"
      printf "| %s | %.2fs | %.2fs | %s | %s |\n" "$id" "$start" "$end" "$frame" "$safe_text"
    done < <(jq -r '.segments[] | [.id, .start_sec, .end_sec, .start_frame, .text] | @tsv' "$TIMELINE_JSON")
    echo
    echo "## Sequence Cues"
    echo
    jq -r '
      .segments
      | group_by(.sequence)
      | map({
          sequence: .[0].sequence,
          start: .[0].start_frame,
          end: .[-1].end_frame,
          duration: (map(.duration_frames) | add)
        })
      | .[]
      | "- \(.sequence): frame \(.start) -> \(.end) (\(.duration) frames)"
    ' "$TIMELINE_JSON"
  } > "$TRANSCRIPT_MD"

  ok "Updated transcript markdown: $TRANSCRIPT_MD"
}

main() {
  require_cmd jq
  require_cmd ffmpeg
  require_cmd ffprobe
  require_cmd tts
  if [[ "$RUN_SCRIBE" == "1" ]]; then
    require_cmd scribe
  fi
  [ -f "$MANIFEST" ] || fail "Missing manifest: $MANIFEST"

  mkdir -p "$OUT_DIR" "$AUDIO_DIR" "$TRANS_DIR" "$SCRIPT_DIR/intro/public"

  info "Building narration audio from per-beat scripts"
  info "Model: $MODEL  Voice: ${VOICE:-default}  Scribe: $RUN_SCRIBE"

  build_segments
  concat_audio
  write_cues_ts
  write_transcript_md

  ok "Narration pipeline complete"
}

main "$@"
