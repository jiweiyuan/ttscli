import { AbsoluteFill, useCurrentFrame } from "remotion";
import React from "react";
import { palette } from "../design";

type BackdropTone = "warm" | "cool" | "neutral";

const toneMap: Record<
  BackdropTone,
  {
    glowA: string;
    glowB: string;
  }
> = {
  warm: {
    glowA: "rgba(255,97,84,0.16)",
    glowB: "rgba(251,146,60,0.12)",
  },
  cool: {
    glowA: "rgba(59,130,246,0.14)",
    glowB: "rgba(16,185,129,0.1)",
  },
  neutral: {
    glowA: "rgba(148,163,184,0.14)",
    glowB: "rgba(255,97,84,0.1)",
  },
};

export const Backdrop: React.FC<{
  tone?: BackdropTone;
  motionSpeed?: number;
}> = ({ tone = "neutral", motionSpeed = 1 }) => {
  const frame = useCurrentFrame();
  const colors = toneMap[tone];

  const x = 50 + 2.6 * Math.sin(frame * 0.003 * motionSpeed);
  const y = 26 + 2.2 * Math.cos(frame * 0.0028 * motionSpeed);

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: palette.bg }}>
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(165deg, #FFFDFC 0%, #FFF7F2 55%, #FFF2EC 100%)",
        }}
      />

      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at ${x}% ${y}%, ${colors.glowA}, transparent 58%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 78% 78%, ${colors.glowB}, transparent 56%)`,
        }}
      />

      <AbsoluteFill
        style={{
          opacity: 0.08,
          backgroundImage:
            "linear-gradient(rgba(17,24,39,0.14) 1px, transparent 1px), linear-gradient(90deg, rgba(17,24,39,0.14) 1px, transparent 1px)",
          backgroundSize: "140px 140px",
        }}
      />
    </AbsoluteFill>
  );
};
