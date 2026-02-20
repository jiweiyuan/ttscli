import { AbsoluteFill, useCurrentFrame } from "remotion";
import React from "react";
import { palette } from "../design";

export const RhythmOverlay: React.FC<{
  totalFrames: number;
  cueFrames: number[];
}> = ({ totalFrames, cueFrames }) => {
  const frame = useCurrentFrame();
  const progress = Math.min(1, frame / Math.max(totalFrames - 1, 1));

  const pulse = cueFrames.reduce((sum, cue) => {
    const distance = Math.abs(frame - cue);
    return sum + Math.max(0, 1 - distance / 28);
  }, 0);

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: 104,
          right: 104,
          bottom: 34,
          height: 8,
          borderRadius: 999,
          background: "rgba(17,24,39,0.08)",
          overflow: "hidden",
          boxShadow: "0 4px 16px rgba(17,24,39,0.12)",
        }}
      >
        <div
          style={{
            width: `${progress * 100}%`,
            height: "100%",
            borderRadius: 999,
            background: `linear-gradient(90deg, ${palette.accent}, ${palette.cool})`,
            boxShadow: "0 0 14px rgba(255,97,84,0.36)",
          }}
        />
      </div>

      {cueFrames.map((cue) => {
        const x = (cue / totalFrames) * 100;
        const cuePulse = Math.max(0, 1 - Math.abs(frame - cue) / 24);
        return (
          <div
            key={cue}
            style={{
              position: "absolute",
              left: `calc(${x}% - 6px)`,
              bottom: 30,
              width: 12,
              height: 12,
              borderRadius: "50%",
              backgroundColor: palette.accent,
              boxShadow: `0 0 ${8 + cuePulse * 14}px rgba(255,97,84,0.55)`,
              transform: `scale(${1 + cuePulse * 0.32})`,
              opacity: 0.42 + cuePulse * 0.42,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
