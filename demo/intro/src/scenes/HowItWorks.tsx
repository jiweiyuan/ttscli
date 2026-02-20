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
import { TerminalChrome, PromptLine, Cursor, codeTheme } from "../effects/TerminalChrome";
import { Waveform } from "../effects/Waveform";
import { narrationCues } from "../narrationCues";

const bd = narrationCues.scenes.tech.beatDurations;
const beatStart = (i: number) => bd.slice(0, i).reduce((a, b) => a + b, 0);

/* ── Beat 8: Engine — Qwen3 TTS ─────────────────────────────────── */

const BeatEngine: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame: frame - 4, fps, config: { damping: 12, stiffness: 110, mass: 0.8 } });
  const slideX = interpolate(enter, [0, 1], [60, 0]);

  return (
    <AbsoluteFill>
      <Backdrop tone="cool" motionSpeed={0.45} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 50, opacity: enter, transform: `translateX(${slideX}px)` }}>
          <div style={{ textAlign: "left" }}>
            <div style={{ fontFamily: fonts.mono, fontSize: 20, color: palette.accent, letterSpacing: 1, textTransform: "uppercase" }}>
              Speech Engine
            </div>
            <div
              style={{
                marginTop: 10,
                fontFamily: fonts.display,
                fontSize: 72,
                fontWeight: 800,
                color: palette.ink,
                letterSpacing: -3,
              }}
            >
              Qwen3 TTS
            </div>
            <div style={{ marginTop: 14, fontFamily: fonts.display, fontSize: 28, color: palette.inkMuted, maxWidth: 520 }}>
              State-of-the-art neural speech synthesis
            </div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
            <div
              style={{
                padding: "20px 30px",
                borderRadius: 20,
                border: `1px solid ${palette.line}`,
                background: palette.bgPanel,
                boxShadow: shadows.panel,
                fontFamily: fonts.mono,
                fontSize: 22,
                color: palette.ink,
              }}
            >
              Text Input
            </div>
            <svg width="24" height="40" viewBox="0 0 24 40" fill="none" stroke={palette.accent} strokeWidth="2">
              <line x1="12" y1="0" x2="12" y2="32" /><polyline points="6 26 12 34 18 26" />
            </svg>
            <Waveform width={260} height={50} bars={20} color={palette.cool} alive={true} />
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── Beat 9: Backends — PyTorch vs MLX ──────────────────────────── */

const BackendCard: React.FC<{
  title: string;
  tags: string[];
  color: string;
  delay: number;
}> = ({ title, tags, color, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - delay, fps, config: { damping: 13, stiffness: 120, mass: 0.75 } });
  const y = interpolate(enter, [0, 1], [24, 0]);

  return (
    <div
      style={{
        flex: 1,
        borderRadius: 24,
        border: `1px solid ${color}44`,
        background: palette.bgPanel,
        boxShadow: shadows.panel,
        padding: "40px 36px",
        opacity: enter,
        transform: `translateY(${y}px)`,
        textAlign: "center",
      }}
    >
      <div style={{ fontFamily: fonts.display, fontSize: 48, fontWeight: 800, color: palette.ink, letterSpacing: -1.5 }}>
        {title}
      </div>
      <div style={{ marginTop: 8, height: 4, borderRadius: 999, width: 80, margin: "12px auto 0", background: color }} />
      <div style={{ display: "flex", gap: 10, justifyContent: "center", marginTop: 24 }}>
        {tags.map((tag) => (
          <div
            key={tag}
            style={{
              borderRadius: 999,
              border: `1px solid ${color}44`,
              background: `${color}14`,
              color: palette.ink,
              fontFamily: fonts.mono,
              fontSize: 20,
              padding: "8px 18px",
            }}
          >
            {tag}
          </div>
        ))}
      </div>
    </div>
  );
};

const BeatBackends: React.FC = () => (
  <AbsoluteFill>
    <Backdrop tone="cool" motionSpeed={0.4} />
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 160px" }}>
      <div style={{ display: "flex", gap: 40 }}>
        <BackendCard title="PyTorch" tags={["CUDA", "CPU"]} color={palette.cool} delay={4} />
        <BackendCard title="MLX" tags={["M-Series"]} color={palette.mint} delay={14} />
      </div>
    </AbsoluteFill>
  </AbsoluteFill>
);

/* ── Beat 10: One command — terminal type-on ─────────────────────── */

const BeatOneCommand: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const termIn = spring({ frame: frame - 4, fps, config: { damping: 13, stiffness: 120, mass: 0.78 } });
  const cursorOn = Math.floor(frame / 15) % 2 === 0;

  const cmd1 = "curl -fsSL https://raw.githubusercontent.com/.../install.sh | bash";
  const cmd2 = "tts init";
  const cmd1Len = Math.min(cmd1.length, Math.max(0, Math.floor((frame - 12) * 1.8)));
  const cmd2Len = Math.min(cmd2.length, Math.max(0, Math.floor((frame - 45) * 1.5)));
  const check1 = frame > 42;
  const check2 = frame > 60;

  return (
    <AbsoluteFill>
      <Backdrop tone="neutral" motionSpeed={0.4} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "0 180px" }}>
      <div style={{ width: "100%", opacity: termIn }}>
        <TerminalChrome>
          <PromptLine>
            <span style={{ color: codeTheme.text }}>{cmd1.slice(0, cmd1Len)}</span>
            {!check1 && <Cursor visible={cursorOn} />}
          </PromptLine>
          {check1 && (
            <div style={{ color: codeTheme.success, marginTop: 4 }}>
              ✓ Installed ttscli v0.1.1
            </div>
          )}
          {frame > 40 && (
            <div style={{ marginTop: 14 }}>
              <PromptLine>
                <span style={{ color: codeTheme.text }}>{cmd2.slice(0, cmd2Len)}</span>
                {!check2 && <Cursor visible={cursorOn} />}
              </PromptLine>
            </div>
          )}
          {check2 && (
            <div style={{ color: codeTheme.success, marginTop: 4 }}>
              ✓ Model downloaded, environment ready
            </div>
          )}
        </TerminalChrome>
      </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── Beat 11: Ready ──────────────────────────────────────────────── */

const BeatReady: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame: frame - 3, fps, config: { damping: 10, stiffness: 150, mass: 0.6 } });
  const scale = interpolate(enter, [0, 1], [0.7, 1]);

  return (
    <AbsoluteFill>
      <Backdrop tone="warm" motionSpeed={0.5} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ opacity: enter, transform: `scale(${scale})`, display: "flex", flexDirection: "column", alignItems: "center" }}>
          <svg width="100" height="100" viewBox="0 0 24 24" fill="none" stroke={palette.mint} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          <div
            style={{
              marginTop: 24,
              fontFamily: fonts.display,
              fontSize: 88,
              fontWeight: 800,
              color: palette.ink,
              letterSpacing: -3,
            }}
          >
            Ready.
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── Main scene ──────────────────────────────────────────────────── */

export const HowItWorks: React.FC = () => {
  const frame = useCurrentFrame();
  const totalDur = narrationCues.scenes.tech.duration;
  const fadeOut = interpolate(frame, [totalDur - 15, totalDur], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const beats = [BeatEngine, BeatBackends, BeatOneCommand, BeatReady];

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
