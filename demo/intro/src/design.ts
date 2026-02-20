export const palette = {
  ink: "#111827",
  inkMuted: "#5B6475",
  bg: "#FFF8F5",
  bgPanel: "#FFFFFF",
  bgPanelSoft: "#FFF1EA",
  line: "rgba(17,24,39,0.12)",
  accent: "#FF6154",
  accentSoft: "rgba(255,97,84,0.2)",
  cool: "#3B82F6",
  coolSoft: "rgba(59,130,246,0.14)",
  mint: "#16A34A",
} as const;

export const fonts = {
  display: "'Avenir Next', 'Trebuchet MS', 'Segoe UI', sans-serif",
  mono: "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace",
} as const;

export const shadows = {
  panel: "0 18px 48px rgba(17, 24, 39, 0.12), 0 1px 0 rgba(255,255,255,0.85) inset",
  glow: "0 0 28px rgba(255, 97, 84, 0.14)",
} as const;
