import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring } from 'remotion';
import { colors, fonts, FPS } from '../theme';

/**
 * Scene 7 — CTA (54-60s, 180 frames).
 * GitHub 링크 + 설치 명령어 + 페이드아웃.
 */
export const SceneCta: React.FC = () => {
  const frame = useCurrentFrame();

  // 전체 페이드인
  const fadeIn = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 로고 등장 — spring
  const logoScale = spring({
    frame: frame - 10,
    fps: FPS,
    config: { mass: 0.8, damping: 12, stiffness: 200 },
    from: 0.8,
    to: 1,
  });

  // URL 등장 — frame 40
  const urlOpacity = interpolate(frame, [40, 65], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 명령어 등장 — frame 80
  const cmdOpacity = interpolate(frame, [80, 100], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 서브 메시지 — frame 110
  const subOpacity = interpolate(frame, [110, 130], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 페이드아웃 — frame 155-180
  const fadeOut = interpolate(frame, [155, 180], [1, 0], {
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
        padding: '60px 100px',
        opacity: fadeIn * fadeOut,
      }}
    >
      {/* 로고 타이포 */}
      <div
        style={{
          transform: `scale(${logoScale})`,
          textAlign: 'center',
          marginBottom: 40,
        }}
      >
        <div
          style={{
            fontSize: 80,
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
        <div
          style={{
            fontSize: 22,
            color: colors.dim,
            marginTop: 12,
            fontWeight: 400,
          }}
        >
          당신의 두 번째 뇌를 만드세요
        </div>
      </div>

      {/* GitHub URL */}
      <div
        style={{
          opacity: urlOpacity,
          fontSize: 30,
          fontFamily: fonts.mono,
          color: colors.blue,
          marginBottom: 32,
          letterSpacing: '-0.01em',
        }}
      >
        github.com/kimsanguine/llm-brain
      </div>

      {/* 설치 명령어 */}
      <div
        style={{
          opacity: cmdOpacity,
          backgroundColor: colors.surface,
          border: `1px solid ${colors.border}`,
          borderRadius: 10,
          padding: '16px 32px',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          marginBottom: 36,
        }}
      >
        <span style={{ color: colors.green, fontFamily: fonts.mono, fontSize: 18 }}>❯</span>
        <span style={{ fontFamily: fonts.mono, fontSize: 20, color: colors.text }}>
          bash scripts/setup.sh
        </span>
      </div>

      {/* 서브 메시지 */}
      <div
        style={{
          opacity: subOpacity,
          fontSize: 18,
          color: colors.dim,
          textAlign: 'center',
        }}
      >
        5분 안에 시작하는 두 번째 뇌
      </div>
    </AbsoluteFill>
  );
};
