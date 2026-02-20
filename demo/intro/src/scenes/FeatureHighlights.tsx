import {
  AbsoluteFill,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import React from "react";
import { fonts, palette, shadows } from "../design";
import { Backdrop } from "../effects/Backdrop";
import { Waveform } from "../effects/Waveform";
import { TerminalChrome, PromptLine, Cursor, codeTheme, highlightTokens } from "../effects/TerminalChrome";
import { narrationCues } from "../narrationCues";

const bd = narrationCues.scenes.features.beatDurations;
const beatStart = (i: number) => bd.slice(0, i).reduce((a, b) => a + b, 0);

/* ── Icons ───────────────────────────────────────────────────────── */

const MicIcon: React.FC<{ color: string; size?: number }> = ({ color, size = 64 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" /><path d="M19 10v2a7 7 0 0 1-14 0v-2" /><line x1="12" y1="19" x2="12" y2="23" /><line x1="8" y1="23" x2="16" y2="23" />
  </svg>
);

const BoltIcon: React.FC<{ color: string; size?: number }> = ({ color, size = 64 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" /></svg>
);

const TerminalIcon: React.FC<{ color: string; size?: number }> = ({ color, size = 64 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><polyline points="4 17 10 11 4 5" /><line x1="12" y1="19" x2="20" y2="19" /></svg>
);

const DownloadIcon: React.FC<{ color: string; size?: number }> = ({ color, size = 64 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>
);

const CpuIcon: React.FC<{ color: string; size?: number }> = ({ color, size = 64 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" /><rect x="9" y="9" width="6" height="6" /><line x1="9" y1="1" x2="9" y2="4" /><line x1="15" y1="1" x2="15" y2="4" /><line x1="9" y1="20" x2="9" y2="23" /><line x1="15" y1="20" x2="15" y2="23" /><line x1="20" y1="9" x2="23" y2="9" /><line x1="20" y1="14" x2="23" y2="14" /><line x1="1" y1="9" x2="4" y2="9" /><line x1="1" y1="14" x2="4" y2="14" /></svg>
);

const AppleIcon: React.FC<{ color: string; size?: number }> = ({ color, size = 64 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={color}>
    <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z" />
  </svg>
);

/* ── Beat 12: Voice Cloning ──────────────────────────────────────── */

const BeatVoiceCloning: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - 4, fps, config: { damping: 12, stiffness: 110, mass: 0.8 } });
  const morphProgress = interpolate(frame, [15, 55], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <Backdrop tone="neutral" motionSpeed={0.4} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ opacity: enter, textAlign: "center" }}>
          <div style={{ fontFamily: fonts.display, fontSize: 52, fontWeight: 800, color: palette.ink, letterSpacing: -2, marginBottom: 40 }}>
            Voice Cloning
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 40, justifyContent: "center" }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontFamily: fonts.mono, fontSize: 24, color: palette.inkMuted, marginBottom: 14 }}>Reference</div>
              <Waveform width={360} height={80} bars={26} color={palette.inkMuted} alive={false} />
            </div>

            <svg width="60" height="40" viewBox="0 0 60 40" fill="none" stroke={palette.accent} strokeWidth="2.5" strokeLinecap="round">
              <line x1="5" y1="20" x2={5 + 40 * morphProgress} y2="20" />
              <polyline points="40 12 50 20 40 28" opacity={morphProgress} />
            </svg>

            <div style={{ textAlign: "center" }}>
              <div style={{ fontFamily: fonts.mono, fontSize: 24, color: palette.accent, marginBottom: 14 }}>Cloned Output</div>
              <Waveform width={360} height={80} bars={26} color={palette.accent} alive={morphProgress > 0.5} progress={morphProgress} />
            </div>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── Beat 13: Streaming ──────────────────────────────────────────── */

const BeatStreaming: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - 4, fps, config: { damping: 13, stiffness: 100, mass: 0.8 } });

  const genProgress = interpolate(frame, [10, 80], [0.3, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const playProgress = interpolate(frame, [10, 80], [0.1, 0.85], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const barW = 700;

  return (
    <AbsoluteFill>
      <Backdrop tone="cool" motionSpeed={0.4} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ opacity: enter, textAlign: "center" }}>
          <div style={{ fontFamily: fonts.display, fontSize: 52, fontWeight: 800, color: palette.ink, letterSpacing: -2, marginBottom: 40 }}>
            Streaming Playback
          </div>

          <div style={{ width: barW, margin: "0 auto" }}>
            <div style={{ fontFamily: fonts.mono, fontSize: 18, color: palette.inkMuted, textAlign: "left", marginBottom: 8 }}>
              Generating...
            </div>
            <div style={{ width: barW, height: 16, borderRadius: 999, background: "rgba(17,24,39,0.08)", overflow: "hidden" }}>
              <div style={{ width: `${genProgress * 100}%`, height: "100%", borderRadius: 999, background: `linear-gradient(90deg, ${palette.cool}, ${palette.accent})` }} />
            </div>

            <div style={{ fontFamily: fonts.mono, fontSize: 18, color: palette.inkMuted, textAlign: "left", marginTop: 20, marginBottom: 8 }}>
              Playing...
            </div>
            <div style={{ width: barW, height: 16, borderRadius: 999, background: "rgba(17,24,39,0.08)", overflow: "hidden", position: "relative" }}>
              <div style={{ width: `${playProgress * 100}%`, height: "100%", borderRadius: 999, background: palette.accent }} />
              <div
                style={{
                  position: "absolute",
                  top: -4,
                  left: `${playProgress * 100}%`,
                  width: 24,
                  height: 24,
                  borderRadius: "50%",
                  background: palette.accent,
                  border: "3px solid white",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
                  transform: "translateX(-50%)",
                }}
              />
            </div>
            <div style={{ fontFamily: fonts.mono, fontSize: 16, color: palette.inkMuted, textAlign: "left", marginTop: 8 }}>
              Audio plays while still generating
            </div>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── Beat 14: Model Sizes ────────────────────────────────────────── */

const BeatModelSizes: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - 4, fps, config: { damping: 14, stiffness: 110, mass: 0.8 } });

  const bar1W = interpolate(enter, [0, 1], [0, 600]);
  const bar2W = interpolate(enter, [0, 1], [0, 360]);

  return (
    <AbsoluteFill>
      <Backdrop tone="neutral" motionSpeed={0.4} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ opacity: enter, textAlign: "center" }}>
          <div style={{ fontFamily: fonts.display, fontSize: 52, fontWeight: 800, color: palette.ink, letterSpacing: -2, marginBottom: 50 }}>
            Two Model Sizes
          </div>

          <div style={{ display: "inline-block" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 20, marginBottom: 30 }}>
              <div style={{ fontFamily: fonts.mono, fontSize: 26, color: palette.ink, fontWeight: 700, width: 80, textAlign: "right" }}>1.7B</div>
              <div style={{ height: 44, width: bar1W, borderRadius: 12, background: "linear-gradient(90deg, #4F46E5, #6366F1)", display: "flex", alignItems: "center", paddingLeft: 20 }}>
                <span style={{ fontFamily: fonts.mono, fontSize: 20, color: "#FFFFFF", fontWeight: 600 }}>Quality</span>
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
              <div style={{ fontFamily: fonts.mono, fontSize: 26, color: palette.ink, fontWeight: 700, width: 80, textAlign: "right" }}>0.6B</div>
              <div style={{ height: 44, width: bar2W, borderRadius: 12, background: `linear-gradient(90deg, ${palette.accent}, #FF8A80)`, display: "flex", alignItems: "center", paddingLeft: 20 }}>
                <span style={{ fontFamily: fonts.mono, fontSize: 20, color: "#FFFFFF", fontWeight: 600 }}>Speed</span>
              </div>
            </div>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── Beat 15: Scriptable ─────────────────────────────────────────── */

const BeatScriptable: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - 4, fps, config: { damping: 13, stiffness: 110, mass: 0.78 } });
  const cursorOn = Math.floor(frame / 15) % 2 === 0;

  const cmd = "echo \"Hello\" | tts say";
  const cmdLen = Math.min(cmd.length, Math.max(0, Math.floor((frame - 10) * 1.4)));
  const showOutput = frame > 40;

  return (
    <AbsoluteFill>
      <Backdrop tone="neutral" motionSpeed={0.4} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "0 180px" }}>
      <div style={{ width: "100%", opacity: enter }}>
        <div style={{ fontFamily: fonts.display, fontSize: 52, fontWeight: 800, color: palette.ink, letterSpacing: -2, marginBottom: 30 }}>
          Fully Scriptable
        </div>
        <TerminalChrome>
          <PromptLine>
            <span>{highlightTokens(cmd.slice(0, cmdLen))}</span>
            {!showOutput && <Cursor visible={cursorOn} />}
          </PromptLine>
          {showOutput && (
            <div style={{ marginTop: 8 }}>
              <div style={{ color: codeTheme.subtext }}>Speaking...</div>
              <div style={{ color: codeTheme.success, marginTop: 4 }}>OK (1.2s)</div>
            </div>
          )}
        </TerminalChrome>
      </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── Beat 16: Export ──────────────────────────────────────────────── */

const BeatExport: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - 4, fps, config: { damping: 13, stiffness: 110, mass: 0.8 } });

  const targets = ["Edit", "Publish", "Automate"];

  return (
    <AbsoluteFill>
      <Backdrop tone="neutral" motionSpeed={0.4} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ opacity: enter, display: "flex", alignItems: "center", gap: 50 }}>
          <div style={{ textAlign: "center" }}>
            <DownloadIcon color="#DB2777" size={72} />
            <div
              style={{
                marginTop: 14,
                fontFamily: fonts.mono,
                fontSize: 36,
                fontWeight: 700,
                color: palette.ink,
              }}
            >
              .wav
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {targets.map((target, i) => {
              const arrowEnter = spring({
                frame: frame - 14 - i * 8,
                fps,
                config: { damping: 14, stiffness: 120, mass: 0.7 },
              });
              return (
                <div key={target} style={{ display: "flex", alignItems: "center", gap: 16, opacity: arrowEnter }}>
                  <svg width="50" height="24" viewBox="0 0 50 24" fill="none" stroke="#DB2777" strokeWidth="2" strokeLinecap="round">
                    <line x1="0" y1="12" x2="38" y2="12" /><polyline points="32 6 40 12 32 18" />
                  </svg>
                  <div
                    style={{
                      borderRadius: 999,
                      border: "1px solid #DB277744",
                      background: "#DB277714",
                      color: palette.ink,
                      fontFamily: fonts.mono,
                      fontSize: 24,
                      padding: "10px 24px",
                      fontWeight: 600,
                    }}
                  >
                    {target}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── Beat 17: Apple Silicon ──────────────────────────────────────── */

const BeatAppleSilicon: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - 3, fps, config: { damping: 12, stiffness: 130, mass: 0.7 } });
  const scale = interpolate(enter, [0, 1], [0.85, 1]);

  const platforms = ["macOS", "Linux", "Windows"];

  return (
    <AbsoluteFill>
      <Backdrop tone="cool" motionSpeed={0.45} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ textAlign: "center", opacity: enter, transform: `scale(${scale})` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16, justifyContent: "center" }}>
            <AppleIcon color={palette.ink} size={72} />
            <CpuIcon color={palette.mint} size={80} />
          </div>
          <div style={{ marginTop: 18, fontFamily: fonts.display, fontSize: 64, fontWeight: 800, color: palette.ink, letterSpacing: -2 }}>
            MLX Native
          </div>
          <div style={{ display: "flex", gap: 14, justifyContent: "center", marginTop: 28 }}>
            {platforms.map((p, i) => {
              const pillEnter = spring({ frame: frame - 14 - i * 6, fps, config: { damping: 14, stiffness: 120, mass: 0.7 } });
              return (
                <div
                  key={p}
                  style={{
                    opacity: pillEnter,
                    borderRadius: 999,
                    border: `1px solid ${palette.line}`,
                    background: palette.bgPanel,
                    color: palette.ink,
                    fontFamily: fonts.mono,
                    fontSize: 23,
                    padding: "11px 26px",
                  }}
                >
                  {p}
                </div>
              );
            })}
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── Main scene ──────────────────────────────────────────────────── */

export const FeatureHighlights: React.FC = () => {
  const frame = useCurrentFrame();
  const totalDur = narrationCues.scenes.features.duration;
  const fadeOut = interpolate(frame, [totalDur - 15, totalDur], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const beats = [BeatVoiceCloning, BeatStreaming, BeatModelSizes, BeatScriptable, BeatExport, BeatAppleSilicon];

  return (
    <AbsoluteFill style={{ opacity: fadeOut }}>
      {beats.map((Beat, i) => (
        <Sequence key={i} from={beatStart(i)} durationInFrames={bd[i]}>
          <Beat />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
