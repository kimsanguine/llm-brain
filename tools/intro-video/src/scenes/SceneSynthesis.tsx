import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring } from 'remotion';
import { colors, fonts, FPS } from '../theme';

/**
 * Scene 5 — Synthesis (37-46s, 270 frames).
 * LLM Wiki + Second Brain → 중앙 합성 → llm-brain 로고 등장.
 */
export const SceneSynthesis: React.FC = () => {
  const frame = useCurrentFrame();

  // 왼쪽 카드 (LLM Wiki) 슬라이드인
  const leftX = interpolate(frame, [0, 50], [-200, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const leftOpacity = interpolate(frame, [0, 40], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 오른쪽 카드 (Second Brain) 슬라이드인
  const rightX = interpolate(frame, [0, 50], [200, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const rightOpacity = interpolate(frame, [0, 40], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // + 기호
  const plusOpacity = interpolate(frame, [50, 70], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // = 기호 + 로고 등장 — frame 100
  const logoScale = spring({
    frame: frame - 100,
    fps: FPS,
    config: { mass: 0.8, damping: 12, stiffness: 180 },
    from: 0.5,
    to: 1,
  });
  const logoOpacity = interpolate(frame, [100, 130], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 서브 카피 등장 — frame 160
  const subOpacity = interpolate(frame, [160, 190], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const subY = interpolate(frame, [160, 190], [12, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.bg,
        fontFamily: fonts.display,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '60px 80px',
      }}
    >
      {/* 합성 다이어그램 */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 32,
          marginBottom: 64,
        }}
      >
        {/* LLM Wiki 카드 */}
        <div
          style={{
            opacity: leftOpacity,
            transform: `translateX(${leftX}px)`,
            backgroundColor: colors.surface,
            border: `2px solid ${colors.blue}`,
            borderRadius: 16,
            padding: '24px 36px',
            textAlign: 'center',
            minWidth: 180,
          }}
        >
          <div style={{ fontSize: 32, marginBottom: 8 }}>📂</div>
          <div
            style={{
              fontSize: 20,
              fontWeight: 700,
              color: colors.blue,
              marginBottom: 6,
            }}
          >
            LLM Wiki
          </div>
          <div style={{ fontSize: 14, color: colors.dim }}>raw → wiki 컴파일</div>
        </div>

        {/* + */}
        <div
          style={{
            opacity: plusOpacity,
            fontSize: 40,
            fontWeight: 300,
            color: colors.dim,
          }}
        >
          +
        </div>

        {/* Second Brain 카드 */}
        <div
          style={{
            opacity: rightOpacity,
            transform: `translateX(${rightX}px)`,
            backgroundColor: colors.surface,
            border: `2px solid ${colors.purple}`,
            borderRadius: 16,
            padding: '24px 36px',
            textAlign: 'center',
            minWidth: 180,
          }}
        >
          <div style={{ fontSize: 32, marginBottom: 8 }}>🧠</div>
          <div
            style={{
              fontSize: 20,
              fontWeight: 700,
              color: colors.purple,
              marginBottom: 6,
            }}
          >
            Second Brain
          </div>
          <div style={{ fontSize: 14, color: colors.dim }}>CODE 프레임워크</div>
        </div>
      </div>

      {/* llm-brain 로고 */}
      <div
        style={{
          opacity: logoOpacity,
          transform: `scale(${logoScale})`,
          textAlign: 'center',
        }}
      >
        <div
          style={{
            fontSize: 72,
            fontWeight: 900,
            fontFamily: fonts.mono,
            background: `linear-gradient(135deg, ${colors.blue}, ${colors.purple})`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            letterSpacing: '-0.03em',
            lineHeight: 1,
          }}
        >
          llm-brain
        </div>
      </div>

      {/* 서브 카피 */}
      <div
        style={{
          opacity: subOpacity,
          transform: `translateY(${subY}px)`,
          marginTop: 32,
          textAlign: 'center',
        }}
      >
        <div
          style={{
            fontSize: 24,
            color: colors.text,
            fontWeight: 500,
            lineHeight: 1.6,
          }}
        >
          LLM이 Distill을 대행한다.
          <br />
          <span style={{ color: colors.gold, fontWeight: 700 }}>당신은 Express에 집중하라.</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
