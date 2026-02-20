#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

OUT_DIR="out"
mkdir -p "$OUT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[ OK ]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail()  { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }

# ---------------------------------------------------------------------------
# Timing plan (must match audio beats in ttscli_intro.wav = 84.8s)
# ---------------------------------------------------------------------------
# Segment        Start   Duration  Frames
# Intro          0:00    28s       840
# Label 1        0:28    2s        60
# Terminal 1     0:30    16s       480    (Install & Setup)
# Label 2        0:46    2s        60
# Terminal 2     0:48    16s       480    (Voice Cloning & Speech)
# Label 3        1:04    2s        60
# Terminal 3     1:06    16s       480    (Generate, Export & Workflow)
# Total                  82s       2460
# ---------------------------------------------------------------------------

SEGMENT_DURATION_TERMINAL=16  # seconds per terminal segment

check_deps() {
  local missing=()
  command -v node   >/dev/null 2>&1 || missing+=(node)
  command -v npx    >/dev/null 2>&1 || missing+=(npx)
  command -v ffmpeg >/dev/null 2>&1 || missing+=(ffmpeg)

  if (( ${#missing[@]} > 0 )); then
    fail "Missing required tools: ${missing[*]}"
  fi
  ok "Dependencies: node, npx, ffmpeg"
}

# ---------------------------------------------------------------------------
# Step 1: Render all Remotion compositions
# ---------------------------------------------------------------------------
build_remotion() {
  info "Rendering Remotion compositions..."
  cd "$SCRIPT_DIR/intro"

  if [ ! -d node_modules ]; then
    info "Installing dependencies..."
    npm install --silent
  fi

  local compositions=("TtsIntro" "Label1" "Label2" "Label3")
  local outputs=("intro" "label1" "label2" "label3")

  for i in "${!compositions[@]}"; do
    local comp="${compositions[$i]}"
    local out="${outputs[$i]}"
    info "  Rendering ${comp}..."
    npx remotion render "$comp" \
      --output "$SCRIPT_DIR/$OUT_DIR/${out}.mp4" \
      --codec h264 2>&1 | tail -1
  done

  cd "$SCRIPT_DIR"
  ok "All Remotion compositions rendered"
}

# ---------------------------------------------------------------------------
# Step 2: Record 3 VHS terminal demos
# ---------------------------------------------------------------------------
build_terminals() {
  if ! command -v vhs >/dev/null 2>&1; then
    warn "VHS not installed (brew install charmbracelet/tap/vhs)"
    warn "Checking for existing terminal recordings..."

    local all_exist=true
    for i in 1 2 3; do
      [ -f "$OUT_DIR/terminal${i}.mp4" ] || all_exist=false
    done

    if $all_exist; then
      info "Using existing terminal recordings"
      return 0
    else
      fail "Missing terminal recordings and VHS not installed"
    fi
  fi

  local tapes=("terminal_voices" "terminal_speech" "terminal_config")
  local names=("Install & Setup" "Voice Cloning & Speech" "Generate, Export & Workflow")

  for i in "${!tapes[@]}"; do
    info "  Recording: ${names[$i]}..."
    vhs "${tapes[$i]}.tape" 2>&1 | tail -1
  done

  ok "All terminal demos recorded"
}

# ---------------------------------------------------------------------------
# Step 3: Trim terminals to exact duration & concat all segments
# ---------------------------------------------------------------------------
merge_video() {
  local AUDIO="../ttscli_intro.wav"
  local CONCAT_LIST="$OUT_DIR/concat_list.txt"
  local CONCAT_VIDEO="$OUT_DIR/concat.mp4"
  local FINAL="$OUT_DIR/ttscli_demo.mp4"

  # Verify all inputs
  local segments=("intro" "label1" "terminal1" "label2" "terminal2" "label3" "terminal3")
  for seg in "${segments[@]}"; do
    [ -f "$OUT_DIR/${seg}.mp4" ] || fail "Missing $OUT_DIR/${seg}.mp4"
  done
  [ -f "$AUDIO" ] || fail "Missing audio: ttscli_intro.wav"

  info "Trimming terminal segments to ${SEGMENT_DURATION_TERMINAL}s each..."

  # Trim each terminal to exact duration for beat sync
  for i in 1 2 3; do
    ffmpeg -y -i "$OUT_DIR/terminal${i}.mp4" \
      -t "$SEGMENT_DURATION_TERMINAL" \
      -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -r 30 -an \
      "$OUT_DIR/terminal${i}_trimmed.mp4" 2>/dev/null
  done

  ok "Terminal segments trimmed"

  info "Concatenating 7 segments..."

  # Build concat list in order
  cat > "$CONCAT_LIST" <<EOF
file 'intro.mp4'
file 'label1.mp4'
file 'terminal1_trimmed.mp4'
file 'label2.mp4'
file 'terminal2_trimmed.mp4'
file 'label3.mp4'
file 'terminal3_trimmed.mp4'
EOF

  # Concatenate (re-encode to ensure matching params)
  ffmpeg -y \
    -f concat -safe 0 -i "$CONCAT_LIST" \
    -c:v libx264 -preset fast -crf 18 \
    -pix_fmt yuv420p -r 30 -an \
    "$CONCAT_VIDEO" 2>/dev/null

  ok "Video concatenated"

  info "Merging audio (ttscli_intro.wav)..."

  ffmpeg -y \
    -i "$CONCAT_VIDEO" \
    -i "$AUDIO" \
    -c:v copy \
    -c:a aac -b:a 128k -ar 44100 -ac 2 \
    -shortest \
    -movflags +faststart \
    "$FINAL" 2>/dev/null

  ok "Audio merged"

  # Clean up intermediates
  rm -f "$CONCAT_VIDEO" "$CONCAT_LIST"
  rm -f "$OUT_DIR"/terminal*_trimmed.mp4

  # Summary
  echo ""
  echo "============================================"
  echo "  Build Complete"
  echo "============================================"
  local duration
  duration=$(ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$FINAL")
  local size
  size=$(du -h "$FINAL" | cut -f1)
  echo "  File:       $FINAL"
  echo "  Duration:   ${duration}s"
  echo "  Size:       ${size}"
  echo "  Resolution: 1920x1080 @ 30fps"
  echo "  Audio:      AAC stereo 44.1kHz"
  echo "============================================"
  echo ""
  info "Play: open $FINAL"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  echo ""
  echo "  ttscli Demo Video Builder"
  echo "  ========================="
  echo ""

  check_deps

  case "${1:-all}" in
    remotion)  build_remotion ;;
    terminals) build_terminals ;;
    merge)     merge_video ;;
    all)
      build_remotion
      build_terminals
      merge_video
      ;;
    *)
      echo "Usage: $0 [remotion|terminals|merge|all]"
      exit 1
      ;;
  esac
}

main "$@"
