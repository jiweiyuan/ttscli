import React from "react";
import { fonts, palette, shadows } from "../design";

const codeTheme = {
  prompt: "#4F46E5",
  text: "#1E293B",
  subtext: "#64748B",
  command: "#2563EB",
  string: "#D97706",
  flag: "#059669",
  success: "#16A34A",
  symbol: "#B45309",
} as const;

export { codeTheme };

export const highlightTokens = (text: string) => {
  const parts = text.split(" ");
  return parts.map((token, index) => {
    let color: string = codeTheme.text;
    if (index === 0) color = codeTheme.command;
    if (token.startsWith("'") || token.endsWith("'")) color = codeTheme.string;
    if (token.startsWith("--") || token.startsWith("-o")) color = codeTheme.flag;
    if (token === "|") color = codeTheme.symbol;
    return (
      <span key={`${token}-${index}`}>
        {index > 0 && " "}
        <span style={{ color }}>{token}</span>
      </span>
    );
  });
};

export const TerminalChrome: React.FC<{
  children: React.ReactNode;
  title?: string;
  opacity?: number;
  transform?: string;
}> = ({ children, title = "ttscli / local shell", opacity = 1, transform }) => (
  <div
    style={{
      width: "100%",
      borderRadius: 28,
      border: `1px solid ${palette.line}`,
      background: palette.bgPanel,
      boxShadow: shadows.panel,
      overflow: "hidden",
      opacity,
      transform,
    }}
  >
    <div
      style={{
        height: 56,
        borderBottom: "1px solid rgba(17,24,39,0.12)",
        display: "flex",
        alignItems: "center",
        padding: "0 22px",
        background: "rgba(248,250,252,0.9)",
      }}
    >
      <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FF5F56" }} />
      <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FFBD2E", marginLeft: 8 }} />
      <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#27C93F", marginLeft: 8 }} />
      <div style={{ marginLeft: 18, color: "#64748B", fontFamily: fonts.mono, fontSize: 16 }}>
        {title}
      </div>
    </div>
    <div
      style={{
        background: "#F8FAFC",
        padding: "24px 28px 30px",
        fontFamily: fonts.mono,
        fontSize: 27,
        color: codeTheme.text,
        lineHeight: 1.75,
        minHeight: 340,
      }}
    >
      {children}
    </div>
  </div>
);

export const PromptLine: React.FC<{
  children?: React.ReactNode;
}> = ({ children }) => (
  <div>
    <span style={{ color: codeTheme.prompt, fontWeight: 700 }}>~</span>{" "}
    <span style={{ color: codeTheme.subtext }}>$</span>{" "}
    {children}
  </div>
);

export const Cursor: React.FC<{ visible: boolean }> = ({ visible }) =>
  visible ? (
    <span
      style={{
        display: "inline-block",
        width: 10,
        height: 24,
        backgroundColor: palette.accent,
        borderRadius: 3,
        marginLeft: 4,
        verticalAlign: "middle",
      }}
    />
  ) : null;
