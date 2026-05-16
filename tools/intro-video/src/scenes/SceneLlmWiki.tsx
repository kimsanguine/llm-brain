import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring } from 'remotion';
import { colors, fonts, FPS } from '../theme';

/**
 * Scene 2 — LLM Wiki (7-20s, 390 frames).
 * raw/ 폴더 → wiki/ 폴더 화살표 애니메이션 + 장점 3가지 순차 등장.
 */
export const SceneLlmWiki: React.FC = () => {
  const frame = useCurrentFrame();

  // 타이틀 페이드인
  const titleOpacity = interpolate(frame, [0, 25], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // raw/ 폴더 등장 — frame 30
  const rawOpacity = interpolate(frame, [30, 55], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 화살표 길이 애니메이션 — frame 60-100
  const arrowWidth = interpolate(frame, [60, 100], [0, 120], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // wiki/ 폴더 등장 — frame 105
  const wikiOpacity = interpolate(frame, [105, 130], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 장점 3가지 — 각 50프레임 간격
  const benefit1Scale = spring({
    frame: frame - 150,
    fps: FPS,
    config: { mass: 0.7, damping: 14, stiffness: 220 },
    from: 0.85,
    to: 1,
  });
  const benefit1Opacity = interpolate(frame, [150, 170], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const benefit2Scale = spring({
    frame: frame - 210,
    fps: FPS,
    config: { mass: 0.7, damping: 14, stiffness: 220 },
    from: 0.85,
    to: 1,
  });
  const benefit2Opacity = interpolate(frame, [210, 230], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const benefit3Scale = spring({
    frame: frame - 270,
    fps: FPS,
    config: { mass: 0.7, damping: 14, stiffness: 220 },
    from: 0.85,
    to: 1,
  });
  const benefit3Opacity = interpolate(frame, [270, 290], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const benefits = [
    { label: 'LLM이 컴파일러 역할', delay: 0, scale: benefit1Scale, opacity: benefit1Opacity },
    { label: 'raw → wiki 2계층 구조', delay: 1, scale: benefit2Scale, opacity: benefit2Opacity },
    { label: '지식이 연결되는 그래프', delay: 2, scale: benefit3Scale, opacity: benefit3Opacity },
  ];

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.bg,
        fontFamily: fonts.display,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '60px 100px',
      }}
    >
      {/* 타이틀 */}
      <div
        style={{
          fontSize: 36,
          fontWeight: 700,
          color: colors.blue,
          opacity: titleOpacity,
          marginBottom: 64,
          letterSpacing: '-0.01em',
        }}
      >
        Andrej Karpathy의 LLM Wiki 패턴
      </div>

      {/* 폴더 다이어그램 */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 0,
          marginBottom: 72,
        }}
      >
        {/* raw/ 폴더 */}
        <div
          style={{
            opacity: rawOpacity,
            textAlign: 'center',
          }}
        >
          <div
            style={{
              width: 100,
              height: 80,
              backgroundColor: colors.surface,
              border: `2px solid ${colors.border}`,
              borderRadius: 8,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 32,
              marginBottom: 12,
            }}
          >
            📁
          </div>
          <div
            style={{
              fontFamily: fonts.mono,
              fontSize: 18,
              color: colors.dim,
            }}
          >
            raw/
          </div>
        </div>

        {/* 화살표 */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            overflow: 'hidden',
            width: arrowWidth + 40,
            marginTop: -24,
          }}
        >
          <div
            style={{
              height: 2,
              width: arrowWidth,
              backgroundColor: colors.blue,
              transition: 'width 0.1s linear',
            }}
          />
          <div
            style={{
              opacity: arrowWidth > 100 ? 1 : 0,
              fontSize: 20,
              color: colors.blue,
              marginLeft: -2,
            }}
          >
            ▶
          </div>
        </div>

        {/* wiki/ 폴더 */}
        <div
          style={{
            opacity: wikiOpacity,
            textAlign: 'center',
          }}
        >
          <div
            style={{
              width: 100,
              height: 80,
              backgroundColor: colors.surface,
              border: `2px solid ${colors.blue}`,
              borderRadius: 8,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 32,
              marginBottom: 12,
              boxShadow: `0 0 20px ${colors.blue}33`,
            }}
          >
            📂
          </div>
          <div
            style={{
              fontFamily: fonts.mono,
              fontSize: 18,
              color: colors.blue,
            }}
          >
            wiki/
          </div>
        </div>
      </div>

      {/* 장점 리스트 */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 20,
          width: '100%',
          maxWidth: 640,
        }}
      >
        {benefits.map((b, i) => (
          <div
            key={i}
            style={{
              opacity: b.opacity,
              transform: `scale(${b.scale})`,
              display: 'flex',
              alignItems: 'center',
              gap: 16,
              backgroundColor: colors.surface,
              border: `1px solid ${colors.border}`,
              borderRadius: 10,
              padding: '16px 24px',
            }}
          >
            <div
              style={{
                width: 28,
                height: 28,
                borderRadius: '50%',
                backgroundColor: colors.green,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 16,
                flexShrink: 0,
              }}
            >
              ✓
            </div>
            <div
              style={{
                fontSize: 22,
                color: colors.text,
                fontWeight: 500,
              }}
            >
              {b.label}
            </div>
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
