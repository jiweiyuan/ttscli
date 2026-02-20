import {
  AbsoluteFill,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import React from "react";
import { fonts, palette } from "../design";
import { Backdrop } from "../effects/Backdrop";
import { Waveform, FlatlineWaveform } from "../effects/Waveform";
import { narrationCues } from "../narrationCues";

const bd = narrationCues.scenes.story.beatDurations;
const beatStart = (i: number) => bd.slice(0, i).reduce((a, b) => a + b, 0);

/* ── Beat 1: Hook — "AI coding agents are everywhere" ──────────── */

const BeatHook: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame: frame - 4, fps, config: { damping: 12, stiffness: 140, mass: 0.7 } });
  const scale = interpolate(enter, [0, 1], [1.15, 1]);

  return (
    <AbsoluteFill>
      <Backdrop tone="warm" motionSpeed={0.5} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ textAlign: "center", opacity: enter, transform: `scale(${scale})` }}>
          <div
            style={{
              fontFamily: fonts.display,
              fontSize: 88,
              fontWeight: 800,
              color: palette.ink,
              letterSpacing: -3,
              lineHeight: 1.05,
              maxWidth: 1200,
            }}
          >
            AI coding agents
            <br />
            are <span style={{ color: palette.accent }}>everywhere</span>.
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── Beat 2: Logo wall — agent names ─────────────────────────────── */

const agentNames = [
  { name: "Claude Code", color: "#D97706" },
  { name: "Cursor", color: palette.cool },
  { name: "Codex", color: palette.mint },
  { name: "Gemini CLI", color: "#4F46E5" },
  { name: "OpenCode", color: "#DB2777" },
  { name: "OpenClaw", color: palette.accent },
];

const BeatAgents: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill>
      <Backdrop tone="cool" motionSpeed={0.4} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 20, justifyContent: "center", maxWidth: 1100 }}>
          {agentNames.map(({ name, color }, i) => {
            const enter = spring({
              frame: frame - 4 - i * 6,
              fps,
              config: { damping: 13, stiffness: 130, mass: 0.7 },
            });
            const y = interpolate(enter, [0, 1], [20, 0]);
            return (
              <div
                key={name}
                style={{
                  opacity: enter,
                  transform: `translateY(${y}px)`,
                  borderRadius: 16,
                  border: `1px solid ${color}44`,
                  background: `${color}14`,
                  padding: "18px 32px",
                  fontFamily: fonts.display,
                  fontSize: 36,
                  fontWeight: 700,
                  color: palette.ink,
                  letterSpacing: -0.5,
                }}
              >
                {name}
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── Beat 3: Capabilities — rich cards with mini-illustrations ──── */

const CodeSnippet: React.FC<{ progress: number }> = ({ progress }) => {
  const lines = [
    { indent: 0, tokens: [{ text: "def ", color: "#C678DD" }, { text: "solve", color: "#61AFEF" }, { text: "(ctx):", color: palette.inkMuted }] },
    { indent: 1, tokens: [{ text: "plan", color: "#61AFEF" }, { text: " = ", color: palette.inkMuted }, { text: "analyze", color: "#E5C07B" }, { text: "(ctx)", color: palette.inkMuted }] },
    { indent: 1, tokens: [{ text: "return ", color: "#C678DD" }, { text: "implement", color: "#61AFEF" }, { text: "(plan)", color: palette.inkMuted }] },
  ];
  const visibleLines = Math.floor(progress * (lines.length + 0.5));

  return (
    <div style={{ fontFamily: fonts.mono, fontSize: 16, lineHeight: 1.8, textAlign: "left" }}>
      {lines.map((line, i) => (
        <div key={i} style={{ opacity: i < visibleLines ? 1 : 0, paddingLeft: line.indent * 20 }}>
          {line.tokens.map((t, j) => (
            <span key={j} style={{ color: t.color }}>{t.text}</span>
          ))}
        </div>
      ))}
    </div>
  );
};

const ThinkingSteps: React.FC<{ progress: number; frame: number }> = ({ progress, frame }) => {
  const steps = [
    { icon: "🔍", text: "read codebase..." },
    { icon: "🧠", text: "analyzing deps..." },
    { icon: "📋", text: "plan: 3 steps" },
  ];
  const cursorBlink = Math.floor(frame / 15) % 2 === 0;

  return (
    <div style={{ fontFamily: fonts.mono, fontSize: 15, lineHeight: 2, textAlign: "left" }}>
      {steps.map((step, i) => {
        const visible = progress > i / (steps.length + 0.5);
        const done = progress > (i + 0.7) / (steps.length + 0.5);
        return (
          <div key={i} style={{ opacity: visible ? 1 : 0 }}>
            <span>{step.icon}</span>{" "}
            <span style={{ color: done ? palette.ink : palette.inkMuted }}>{step.text}</span>
            {visible && !done && (
              <span style={{ opacity: cursorBlink ? 1 : 0, color: "#8B5CF6" }}> ▌</span>
            )}
          </div>
        );
      })}
    </div>
  );
};

const ToolPipeline: React.FC<{ progress: number; frame: number }> = ({ progress, frame }) => {
  const tools = ["git", "test", "deploy"];
  const cursorBlink = Math.floor(frame / 15) % 2 === 0;

  return (
    <div style={{ fontFamily: fonts.mono, fontSize: 15, lineHeight: 1.8, textAlign: "left" }}>
      <div style={{ color: palette.inkMuted }}>
        <span style={{ color: palette.mint }}>$</span> running pipeline...
      </div>
      {tools.map((tool, i) => {
        const visible = progress > (i + 1) / (tools.length + 1);
        const done = progress > (i + 1.5) / (tools.length + 1);
        return (
          <div key={tool} style={{ opacity: visible ? 1 : 0 }}>
            <span style={{ color: done ? palette.mint : palette.accent }}>
              {done ? "✓" : "›"}
            </span>{" "}
            <span style={{ color: palette.ink }}>{tool}</span>{" "}
            <span style={{ color: palette.inkMuted }}>{done ? "done" : "..."}</span>
          </div>
        );
      })}
      {progress > 0.9 && (
        <div>
          <span style={{ color: palette.mint }}>$</span>
          <span style={{ opacity: cursorBlink ? 1 : 0, color: palette.mint }}> ▌</span>
        </div>
      )}
    </div>
  );
};

const CapabilityCard: React.FC<{
  label: string;
  subtitle: string;
  color: string;
  delay: number;
  children: React.ReactNode;
}> = ({ label, subtitle, color, delay, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - delay, fps, config: { damping: 13, stiffness: 110, mass: 0.75 } });
  const y = interpolate(enter, [0, 1], [40, 0]);
  const scale = interpolate(enter, [0, 1], [0.92, 1]);

  return (
    <div
      style={{
        opacity: enter,
        transform: `translateY(${y}px) scale(${scale})`,
        width: 380,
        borderRadius: 24,
        background: palette.bgPanel,
        border: `1px solid ${palette.line}`,
        boxShadow: `0 20px 50px rgba(17,24,39,0.10), 0 1px 0 rgba(255,255,255,0.85) inset`,
        overflow: "hidden",
      }}
    >
      {/* Color accent bar */}
      <div style={{ height: 4, background: `linear-gradient(90deg, ${color}, ${color}88)` }} />

      <div style={{ padding: "28px 32px 28px" }}>
        <div style={{ fontFamily: fonts.display, fontSize: 32, fontWeight: 800, color: palette.ink, letterSpacing: -1 }}>
          {label}
        </div>
        <div style={{ fontFamily: fonts.display, fontSize: 18, color: palette.inkMuted, marginTop: 4, marginBottom: 20 }}>
          {subtitle}
        </div>

        {/* Mini illustration */}
        <div
          style={{
            borderRadius: 14,
            background: palette.bgPanelSoft,
            border: `1px solid ${palette.line}`,
            padding: "20px 22px",
            height: 160,
            display: "flex",
            alignItems: "center",
          }}
        >
          <div style={{ width: "100%" }}>{children}</div>
        </div>
      </div>
    </div>
  );
};

/* Animated connector arrow between cards */
const ConnectorArrow: React.FC<{ delay: number }> = ({ delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - delay, fps, config: { damping: 16, stiffness: 100, mass: 0.8 } });
  const dashOffset = frame * 0.4;

  return (
    <div style={{ opacity: enter, display: "flex", alignItems: "center", marginTop: 20 }}>
      <svg width="50" height="24" viewBox="0 0 50 24">
        <line
          x1="4" y1="12" x2="38" y2="12"
          stroke={palette.accent}
          strokeWidth="2"
          strokeDasharray="6 4"
          strokeDashoffset={-dashOffset}
          strokeLinecap="round"
        />
        <polyline
          points="34 6 42 12 34 18"
          fill="none"
          stroke={palette.accent}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
};

const BeatCapabilities: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame: frame - 2, fps, config: { damping: 14, stiffness: 120, mass: 0.7 } });
  const codeProgress = interpolate(frame, [20, 70], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const thinkProgress = interpolate(frame, [30, 85], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const toolProgress = interpolate(frame, [40, 100], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <Backdrop tone="neutral" motionSpeed={0.4} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        {/* Title */}
        <div
          style={{
            position: "absolute",
            top: 160,
            opacity: titleEnter,
            fontFamily: fonts.display,
            fontSize: 48,
            fontWeight: 800,
            color: palette.ink,
            letterSpacing: -2,
          }}
        >
          They can...
        </div>

        {/* Cards row */}
        <div style={{ display: "flex", alignItems: "center", gap: 0, marginTop: 50 }}>
          <CapabilityCard
            label="Write Code"
            subtitle="Generate & refactor"
            color={palette.cool}
            delay={6}
          >
            <CodeSnippet progress={codeProgress} />
          </CapabilityCard>

          <ConnectorArrow delay={20} />

          <CapabilityCard
            label="Reason"
            subtitle="Plan & analyze"
            color="#8B5CF6"
            delay={16}
          >
            <ThinkingSteps progress={thinkProgress} frame={frame} />
          </CapabilityCard>

          <ConnectorArrow delay={30} />

          <CapabilityCard
            label="Run Tools"
            subtitle="Execute & verify"
            color={palette.mint}
            delay={26}
          >
            <ToolPipeline progress={toolProgress} frame={frame} />
          </CapabilityCard>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── Beat 4: "But none of them can speak." ──────────────────────── */

const BeatGap: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame: frame - 2, fps, config: { damping: 20, stiffness: 200, mass: 0.5 } });

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", backgroundColor: "#FFFFFF" }}>
      <div style={{ textAlign: "center", opacity: enter }}>
        <div style={{ fontFamily: fonts.display, fontSize: 100, fontWeight: 800, color: palette.ink, letterSpacing: -4 }}>
          But none of them
          <br />
          can <span style={{ color: palette.accent }}>speak</span>.
        </div>
        <div style={{ marginTop: 30, display: "flex", justifyContent: "center" }}>
          <FlatlineWaveform width={500} height={50} color={palette.inkMuted} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ── Beat 5: Reveal — "TTS CLI gives them a mouth" ──────────────── */

const BeatReveal: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame: frame - 4, fps, config: { damping: 11, stiffness: 120, mass: 0.8 } });
  const y = interpolate(enter, [0, 1], [40, 0]);
  const waveProgress = interpolate(frame, [12, 55], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <Backdrop tone="warm" motionSpeed={0.5} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ textAlign: "center", opacity: enter, transform: `translateY(${y}px)` }}>
          <div
            style={{
              fontFamily: fonts.display,
              fontSize: 178,
              fontWeight: 800,
              color: palette.ink,
              letterSpacing: -8,
              lineHeight: 0.9,
            }}
          >
            TTS CLI
          </div>
          <div style={{ marginTop: 20, fontFamily: fonts.display, fontSize: 36, color: palette.inkMuted }}>
            gives them a mouth
          </div>
          <div style={{ marginTop: 24, display: "flex", justifyContent: "center" }}>
            <Waveform
              width={500}
              height={70}
              color={palette.accent}
              colorEnd={palette.cool}
              alive={true}
              progress={waveProgress}
            />
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── Beat 6: Tagline + privacy pills ────────────────────────────── */

const BeatTagline: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame: frame - 4, fps, config: { damping: 14, stiffness: 100, mass: 0.85 } });
  const pills = ["No Cloud", "No API Keys", "100% Private"];

  return (
    <AbsoluteFill>
      <Backdrop tone="warm" motionSpeed={0.45} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ textAlign: "center", opacity: enter }}>
          <div
            style={{
              fontFamily: fonts.display,
              fontSize: 64,
              fontWeight: 700,
              color: palette.ink,
              letterSpacing: -2,
              maxWidth: 1100,
              lineHeight: 1.15,
            }}
          >
            Local text-to-speech that runs
            <br />
            entirely on your machine.
          </div>
          <div style={{ display: "flex", gap: 16, justifyContent: "center", marginTop: 36 }}>
            {pills.map((pill, i) => {
              const pillEnter = spring({
                frame: frame - 18 - i * 8,
                fps,
                config: { damping: 14, stiffness: 120, mass: 0.7 },
              });
              return (
                <div
                  key={pill}
                  style={{
                    opacity: pillEnter,
                    transform: `translateY(${interpolate(pillEnter, [0, 1], [12, 0])}px)`,
                    borderRadius: 999,
                    border: `1px solid ${palette.accentSoft}`,
                    background: "rgba(255,97,84,0.1)",
                    color: palette.ink,
                    fontFamily: fonts.mono,
                    fontSize: 22,
                    padding: "12px 24px",
                    letterSpacing: 0.3,
                  }}
                >
                  {pill}
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

export const OpenClawStory: React.FC = () => {
  const frame = useCurrentFrame();
  const totalDur = narrationCues.scenes.story.duration;
  const fadeOut = interpolate(frame, [totalDur - 15, totalDur], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const beats = [BeatHook, BeatAgents, BeatCapabilities, BeatGap, BeatReveal, BeatTagline];

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
