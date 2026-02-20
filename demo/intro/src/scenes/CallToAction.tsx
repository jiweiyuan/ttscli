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
import { narrationCues } from "../narrationCues";

const bd = narrationCues.scenes.cta.beatDurations;
const beatStart = (i: number) => bd.slice(0, i).reduce((a, b) => a + b, 0);

/* ── Icons ───────────────────────────────────────────────────────── */

const GithubIcon: React.FC<{ size?: number }> = ({ size = 48 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={palette.ink}>
    <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.6.11.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z" />
  </svg>
);

const StarIcon: React.FC<{ size?: number; color?: string }> = ({ size = 36, color = palette.accent }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={color} stroke={color} strokeWidth="1.2">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
  </svg>
);

const ArrowRight: React.FC = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" />
  </svg>
);

/* ── Beat 21: GitHub CTA ─────────────────────────────────────────── */

const BeatGithubCta: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame: frame - 4, fps, config: { damping: 13, stiffness: 100, mass: 0.85 } });
  const y = interpolate(enter, [0, 1], [24, 0]);

  return (
    <AbsoluteFill>
      <Backdrop tone="warm" motionSpeed={0.45} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ textAlign: "center", opacity: enter, transform: `translateY(${y}px)` }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 18 }}>
            <GithubIcon size={56} />
            <div style={{ fontFamily: fonts.display, fontWeight: 800, fontSize: 72, color: palette.ink, letterSpacing: -3 }}>
              ttscli
            </div>
          </div>
          <div
            style={{
              marginTop: 20,
              fontFamily: fonts.mono,
              fontSize: 26,
              color: palette.inkMuted,
              letterSpacing: 0.3,
            }}
          >
            github.com/jiweiyuan/ttscli
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── GitHub light theme tokens ────────────────────────────────────── */

const gh = {
  bg: "#ffffff",
  bgSubtle: "#f6f8fa",
  cardBg: "#ffffff",
  border: "#d0d7de",
  text: "#1f2328",
  textMuted: "#656d76",
  btnBg: "#f6f8fa",
  btnBorder: "#d0d7de",
  btnHoverBg: "#f3f4f6",
  starYellow: "#e3b341",
  link: "#0969da",
  green: "#1a7f37",
} as const;

/* ── Beat 22: Star ───────────────────────────────────────────────── */

const BeatStar: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cardEnter = spring({ frame: frame - 4, fps, config: { damping: 14, stiffness: 100, mass: 0.9 } });
  const cardY = interpolate(cardEnter, [0, 1], [30, 0]);

  // Star button "click" animation — triggers at frame 18
  const clickFrame = 18;
  const starred = frame >= clickFrame;
  const starPop = spring({ frame: frame - clickFrame, fps, config: { damping: 8, stiffness: 200, mass: 0.5 } });
  const starScale = starred ? interpolate(starPop, [0, 1], [1.4, 1]) : 1;
  const starFillOpacity = starred ? starPop : 0;

  // Counter rolling animation — rapidly counts up after click
  const countDelay = 3;
  const countProgress = starred
    ? spring({ frame: frame - clickFrame - countDelay, fps, config: { damping: 18, stiffness: 80, mass: 0.6 } })
    : 0;
  const startCount = 42;
  const endCount = 128;
  const displayCount = starred
    ? Math.round(interpolate(countProgress, [0, 1], [startCount, endCount]))
    : startCount;
  // Digit roll Y offset for the last two digits
  const digitRollY = starred
    ? interpolate(countProgress, [0, 0.95, 1], [6, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 0;

  return (
    <AbsoluteFill style={{ backgroundColor: gh.bg }}>
      {/* Subtle warm gradient overlay */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse at 50% 0%, rgba(9,105,218,0.04) 0%, transparent 60%)",
        }}
      />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div
          style={{
            opacity: cardEnter,
            transform: `translateY(${cardY}px)`,
            background: gh.cardBg,
            border: `1px solid ${gh.border}`,
            borderRadius: 12,
            padding: "36px 48px",
            width: 560,
          }}
        >
          {/* Repo header */}
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
            <svg width="20" height="20" viewBox="0 0 16 16" fill={gh.textMuted}>
              <path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z" />
            </svg>
            <span style={{ fontFamily: fonts.mono, fontSize: 22, color: gh.link, fontWeight: 600 }}>
              jiweiyuan<span style={{ color: gh.textMuted }}>/</span>ttscli
            </span>
          </div>

          {/* Description */}
          <div
            style={{
              fontFamily: fonts.display,
              fontSize: 17,
              color: gh.textMuted,
              marginBottom: 24,
              lineHeight: 1.5,
            }}
          >
            Local text-to-speech CLI with voice cloning. Powered by Qwen 3 TTS.
          </div>

          {/* Star button row */}
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                background: starred ? "rgba(227,179,65,0.1)" : gh.btnBg,
                border: `1px solid ${starred ? "rgba(227,179,65,0.5)" : gh.btnBorder}`,
                borderRadius: 6,
                padding: "8px 16px",
                cursor: "pointer",
                transition: "all 0.2s",
              }}
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 16 16"
                style={{ transform: `scale(${starScale})` }}
              >
                {/* Filled star (yellow when starred) */}
                <path
                  d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"
                  fill={starred ? gh.starYellow : "none"}
                  stroke={starred ? gh.starYellow : gh.textMuted}
                  strokeWidth={starred ? 0 : 1}
                  opacity={starred ? starFillOpacity : 1}
                />
                {/* Outline star (visible when not starred) */}
                {!starred && (
                  <path
                    d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Zm0 2.445L6.615 5.5a.75.75 0 0 1-.564.41l-3.097.45 2.24 2.184a.75.75 0 0 1 .216.664l-.528 3.084 2.769-1.456a.75.75 0 0 1 .698 0l2.77 1.456-.53-3.084a.75.75 0 0 1 .216-.664l2.24-2.183-3.096-.45a.75.75 0 0 1-.564-.41L8 2.694Z"
                    fill={gh.textMuted}
                  />
                )}
              </svg>
              <span
                style={{
                  fontFamily: fonts.display,
                  fontSize: 15,
                  fontWeight: 600,
                  color: starred ? gh.starYellow : gh.text,
                }}
              >
                {starred ? "Starred" : "Star"}
              </span>
            </div>

            {/* Star count badge */}
            <div
              style={{
                fontFamily: fonts.mono,
                fontSize: 14,
                fontWeight: 600,
                color: starred ? gh.starYellow : gh.text,
                background: gh.btnBg,
                border: `1px solid ${gh.btnBorder}`,
                borderRadius: 6,
                padding: "8px 12px",
                overflow: "hidden",
              }}
            >
              <span style={{ transform: `translateY(${digitRollY}px)`, display: "inline-block" }}>
                {displayCount}
              </span>
            </div>
          </div>

          {/* Language / topic tags */}
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div style={{ width: 12, height: 12, borderRadius: 6, background: "#3572A5" }} />
              <span style={{ fontFamily: fonts.mono, fontSize: 14, color: gh.textMuted }}>Python</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              {["tts", "voice-cloning", "cli", "local-ai"].map((tag) => (
                <span
                  key={tag}
                  style={{
                    fontFamily: fonts.mono,
                    fontSize: 13,
                    color: gh.link,
                    background: "rgba(9,105,218,0.08)",
                    borderRadius: 999,
                    padding: "3px 10px",
                  }}
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── Main scene ──────────────────────────────────────────────────── */

export const CallToAction: React.FC = () => {
  const frame = useCurrentFrame();
  const totalDur = narrationCues.scenes.cta.duration;
  const fadeOut = interpolate(frame, [totalDur - 10, totalDur], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const beats = [BeatGithubCta, BeatStar];

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
