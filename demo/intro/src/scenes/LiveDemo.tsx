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
import {
  TerminalChrome,
  PromptLine,
  Cursor,
  codeTheme,
  highlightTokens,
} from "../effects/TerminalChrome";
import { narrationCues } from "../narrationCues";

const bd = narrationCues.scenes.demo.beatDurations;
const beatStart = (i: number) => bd.slice(0, i).reduce((a, b) => a + b, 0);
const totalDemoDuration = bd.reduce((a, b) => a + b, 0);

const typedChars = (frame: number, start: number, speed: number, text: string) =>
  Math.min(text.length, Math.max(0, Math.floor((frame - start) * speed)));

/**
 * Persistent terminal that accumulates commands across all 3 beats.
 * Uses the global scene frame (not per-beat frame) to keep state.
 */
const DemoTerminal: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cursorOn = Math.floor(frame / 15) % 2 === 0;

  const termIn = spring({ frame: frame - 3, fps, config: { damping: 13, stiffness: 120, mass: 0.78 } });

  /* ── Command 1: tts say ─────────────────────────────────────── */
  const cmd1 = "tts say 'Hello from OpenClaw'";
  const cmd1Start = 8;
  const cmd1Chars = typedChars(frame, cmd1Start, 1.5, cmd1);
  const cmd1Done = cmd1Chars >= cmd1.length;
  const showOut1 = frame > cmd1Start + 30;
  const out1Enter = showOut1
    ? spring({ frame: frame - (cmd1Start + 30), fps, config: { damping: 18, stiffness: 85, mass: 0.72 } })
    : 0;

  /* ── Command 2: tts generate ────────────────────────────────── */
  const beat2Start = beatStart(1);
  const cmd2 = "tts generate 'Welcome' -o welcome.wav";
  const cmd2Start = beat2Start + 8;
  const cmd2Active = frame >= beat2Start;
  const cmd2Chars = typedChars(frame, cmd2Start, 1.4, cmd2);
  const cmd2Done = cmd2Chars >= cmd2.length;
  const showOut2 = frame > cmd2Start + 28;
  const out2Enter = showOut2
    ? spring({ frame: frame - (cmd2Start + 28), fps, config: { damping: 18, stiffness: 85, mass: 0.72 } })
    : 0;

  /* ── Command 3: voice clone ─────────────────────────────────── */
  const beat3Start = beatStart(2);
  const cmd3 = "tts voice add james ref.wav";
  const cmd3Start = beat3Start + 8;
  const cmd3Active = frame >= beat3Start;
  const cmd3Chars = typedChars(frame, cmd3Start, 1.4, cmd3);
  const cmd3Done = cmd3Chars >= cmd3.length;
  const showOut3 = frame > cmd3Start + 25;
  const out3Enter = showOut3
    ? spring({ frame: frame - (cmd3Start + 25), fps, config: { damping: 18, stiffness: 85, mass: 0.72 } })
    : 0;

  return (
    <AbsoluteFill>
      <Backdrop tone="warm" motionSpeed={0.45} />
      <AbsoluteFill style={{ justifyContent: "center", padding: "60px 140px" }}>
        <div style={{ opacity: termIn, width: "100%" }}>
          <TerminalChrome>
            {/* Command 1 */}
            <PromptLine>
              {highlightTokens(cmd1.slice(0, cmd1Chars))}
              {!cmd1Done && frame >= cmd1Start && <Cursor visible={cursorOn} />}
            </PromptLine>
            {showOut1 && (
              <div style={{
                marginTop: 8,
                opacity: out1Enter as number,
                transform: `translateY(${interpolate(out1Enter as number, [0, 1], [5, 0])}px)`,
              }}>
                <div style={{ color: codeTheme.subtext }}>
                  Streaming audio...
                </div>
                <div style={{ color: codeTheme.success, marginTop: 2 }}>
                  OK <span style={{ color: codeTheme.subtext }}>(2.1s)</span>
                </div>
              </div>
            )}

            {/* Command 2 */}
            {cmd2Active && (
              <div style={{ marginTop: 14 }}>
                <PromptLine>
                  {highlightTokens(cmd2.slice(0, cmd2Chars))}
                  {!cmd2Done && frame >= cmd2Start && <Cursor visible={cursorOn} />}
                </PromptLine>
              </div>
            )}
            {showOut2 && (
              <div style={{
                marginTop: 8,
                opacity: out2Enter as number,
                transform: `translateY(${interpolate(out2Enter as number, [0, 1], [5, 0])}px)`,
              }}>
                <div style={{ color: codeTheme.success }}>
                  ✓ <span style={{ color: codeTheme.command }}>welcome.wav</span> saved{" "}
                  <span style={{ color: codeTheme.subtext }}>(1.8s)</span>
                </div>
              </div>
            )}

            {/* Command 3 */}
            {cmd3Active && (
              <div style={{ marginTop: 14 }}>
                <PromptLine>
                  {highlightTokens(cmd3.slice(0, cmd3Chars))}
                  {!cmd3Done && frame >= cmd3Start && <Cursor visible={cursorOn} />}
                </PromptLine>
              </div>
            )}
            {showOut3 && (
              <div style={{
                marginTop: 8,
                opacity: out3Enter as number,
                transform: `translateY(${interpolate(out3Enter as number, [0, 1], [5, 0])}px)`,
              }}>
                <div style={{ color: codeTheme.success }}>
                  Voice <span style={{ color: codeTheme.string }}>james</span> registered OK
                </div>
              </div>
            )}

            {/* Final prompt */}
            {showOut3 && (
              <div style={{ marginTop: 14 }}>
                <PromptLine>
                  <Cursor visible={cursorOn} />
                </PromptLine>
              </div>
            )}
          </TerminalChrome>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ── Main scene — single persistent terminal across 3 beats ────── */

export const LiveDemo: React.FC = () => {
  const frame = useCurrentFrame();
  const fadeOut = interpolate(frame, [totalDemoDuration - 15, totalDemoDuration], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ opacity: fadeOut }}>
      <DemoTerminal />
    </AbsoluteFill>
  );
};
