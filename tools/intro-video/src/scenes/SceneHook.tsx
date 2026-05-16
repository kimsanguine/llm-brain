import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring } from 'remotion';
import { colors, fonts, FPS } from '../theme';

/**
 * Scene 1 — Hook (0-7s, 210 frames).
 * "매일 배우는 것들, 어디로 사라지나요?"
 * 배경: 파편화된 노트 파티클 + 중앙 텍스트 페이드인.
 */
export const SceneHook: React.FC = () => {
  const frame = useCurrentFrame();

  // 배경 파티클 — 30개 고정 위치, 흩어지는 느낌
  const particles = Array.from({ length: 30 }, (_, i) => ({
    x: ((i * 137.5) % 100),
    y: ((i * 83.7) % 100),
    opacity: interpolate(frame, [0, 60], [0, 0.15 + (i % 5) * 0.04], {
      extrapolateRight: 'clamp',
    }),
    size: 4 + (i % 3) * 3,
  }));

  // 서브텍스트 파티클 (TIL · 회의록 등) — 초기에 흩어진 후 서서히 희미해짐
  const subItems = ['TIL', '회의록', '논문', '클리핑', '노트'];
  const subPositions = [
    { x: '15%', y: '25%' },
    { x: '72%', y: '20%' },
    { x: '25%', y: '72%' },
    { x: '68%', y: '68%' },
    { x: '50%', y: '82%' },
  ];

  // Line 1: "매일 배우는 것들," — frame 20에서 등장
  const line1Opacity = interpolate(frame, [20, 50], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const line1Y = interpolate(frame, [20, 50], [16, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Line 2: "어디로 사라지나요?" — frame 80에서 등장 (약 1s 딜레이)
  const line2Opacity = interpolate(frame, [80, 110], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const line2Y = interpolate(frame, [80, 110], [16, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Line 2 보라색 pulse
  const purplePulse = spring({
    frame: frame - 115,
    fps: FPS,
    config: { mass: 0.6, damping: 14 },
    from: 0,
    to: 1,
  });

  const line2Color = purplePulse > 0.4 ? colors.purple : colors.text;

  // 서브 아이템 opacity — frame 130 이후 등장
  const subOpacity = interpolate(frame, [130, 160], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.bg,
        fontFamily: fonts.display,
        overflow: 'hidden',
      }}
    >
      {/* 배경 파티클 */}
      {particles.map((p, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
            borderRadius: 2,
            backgroundColor: i % 3 === 0 ? colors.blue : i % 3 === 1 ? colors.purple : colors.gold,
            opacity: p.opacity,
          }}
        />
      ))}

      {/* 중앙 텍스트 블록 */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          padding: '0 80px',
        }}
      >
        <div
          style={{
            fontSize: 56,
            fontWeight: 700,
            color: colors.dim,
            opacity: line1Opacity,
            transform: `translateY(${line1Y}px)`,
            marginBottom: 20,
            letterSpacing: '-0.01em',
          }}
        >
          매일 배우는 것들,
        </div>
        <div
          style={{
            fontSize: 68,
            fontWeight: 800,
            color: line2Color,
            opacity: line2Opacity,
            transform: `translateY(${line2Y}px)`,
            letterSpacing: '-0.02em',
          }}
        >
          어디로 사라지나요?
        </div>
      </div>

      {/* 흩어진 서브 아이템 */}
      {subItems.map((item, i) => (
        <div
          key={item}
          style={{
            position: 'absolute',
            left: subPositions[i].x,
            top: subPositions[i].y,
            fontSize: 14,
            fontFamily: fonts.mono,
            color: colors.dim,
            opacity: subOpacity * 0.6,
            border: `1px solid ${colors.border}`,
            padding: '4px 10px',
            borderRadius: 4,
            backgroundColor: colors.surface,
          }}
        >
          {item}
        </div>
      ))}
    </AbsoluteFill>
  );
};
