import { interpolate, useCurrentFrame } from "remotion";
import React from "react";

export const Waveform: React.FC<{
  width?: number;
  height?: number;
  bars?: number;
  color?: string;
  colorEnd?: string;
  alive?: boolean;
  progress?: number;
}> = ({
  width = 400,
  height = 80,
  bars = 32,
  color = "#FF6154",
  colorEnd,
  alive = true,
  progress = 1,
}) => {
  const frame = useCurrentFrame();
  const barWidth = (width / bars) * 0.6;
  const gap = (width / bars) * 0.4;

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <defs>
        {colorEnd && (
          <linearGradient id="waveGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor={color} />
            <stop offset="100%" stopColor={colorEnd} />
          </linearGradient>
        )}
      </defs>
      {Array.from({ length: bars }).map((_, i) => {
        const ratio = i / bars;
        const visibleProgress = interpolate(progress, [0, 1], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

        const barAlive = alive && ratio <= visibleProgress;
        const amplitude = barAlive
          ? 0.3 + 0.7 * Math.abs(Math.sin(frame * 0.08 + i * 0.5)) *
            Math.abs(Math.cos(frame * 0.04 + i * 0.3))
          : 0.05;

        const barHeight = height * amplitude;
        const x = i * (barWidth + gap);
        const y = (height - barHeight) / 2;

        return (
          <rect
            key={i}
            x={x}
            y={y}
            width={barWidth}
            height={barHeight}
            rx={barWidth / 2}
            fill={colorEnd ? "url(#waveGrad)" : color}
            opacity={barAlive ? 0.85 : 0.2}
          />
        );
      })}
    </svg>
  );
};

export const FlatlineWaveform: React.FC<{
  width?: number;
  height?: number;
  bars?: number;
  color?: string;
}> = ({ width = 400, height = 60, bars = 32, color = "#5B6475" }) => {
  const barWidth = (width / bars) * 0.6;
  const gap = (width / bars) * 0.4;

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {Array.from({ length: bars }).map((_, i) => {
        const barHeight = 3;
        const x = i * (barWidth + gap);
        const y = (height - barHeight) / 2;
        return (
          <rect
            key={i}
            x={x}
            y={y}
            width={barWidth}
            height={barHeight}
            rx={barWidth / 2}
            fill={color}
            opacity={0.3}
          />
        );
      })}
    </svg>
  );
};
